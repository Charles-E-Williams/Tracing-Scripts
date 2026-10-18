import os
import re
import shlex
import signal
import subprocess
import sys
import time

import pexpect

from tracing.config import BBV_PLUGIN, CHERI_ROOT, CHERIBUILD, COMPRESSION_ALGORITHMS

SHELL_PROMPT = re.compile(rb"root@cheribsd-riscv64(?:-purecap)?:.*?#\s*", re.S)
SIMPOINT_DONE = re.compile(
    rb"SimPoint tracing complete at [0-9]+ instructions\. Shutting down"
)


def read_simpoint_ids(path):
    with open(path) as f:
        return [
            int(line.split()[-1])
            for line in f
            if line.strip() and not line.lstrip().startswith("#")
        ]


def compress_command(algorithm, xz_threads=None):
    if algorithm == "xz" and xz_threads is not None:
        return f"xz -T{xz_threads}"
    return algorithm


class QemuRunner:

    def __init__(self, arch, output_dir, info_file, verbose=False):
        self.arch = arch
        self.output_dir = output_dir
        self.info_file = info_file
        self.verbose = verbose
        self.process = None
        self.compressors = []
        self.symlinks = []

    def log(self, message=""):
        self.info_file.write(message + "\n")
        self.info_file.flush()

    def _expect_shell(self):
        self.process.expect(SHELL_PROMPT, timeout=None)

    def _send_command(self, cmd):
        self.process.sendline(cmd)
        self._expect_shell()

    def bbv_output_path(self, name):
        return os.path.join(self.output_dir, f"{name}.bb.gz")

    def launch_command(self, args, name, disk_image, entry_point, exit_point):
        target = f"run-dm-{self.arch}"
        parts = [
            CHERIBUILD, target,
            "--source-root", CHERI_ROOT,
            f"--{target}/ephemeral",
            "--skip-update",
            f"--disk-image-{self.arch}/path", disk_image,
        ]
        if args.ssh_port:
            parts.append(f"--{target}/ssh-forwarding-port={args.ssh_port}")
        if args.trace_format not in ("none", "text"):
            parts.append(f"--{target}/{args.trace_format}")

        process_filter = ["filter=process"] if args.process_filter else []
        extra = []
        if args.memory:
            extra.append(f"-m {args.memory}")
        if args.tb_size:
            extra.append(f"-accel tcg,tb-size={args.tb_size}")
        if args.bbv_plugin:
            plugin_args = [name, f"0x{entry_point:x}", args.bbv_interval, f"0x{exit_point:x}"]
            if args.process_filter:
                plugin_args.append("process")
            extra.append(f"-plugin {BBV_PLUGIN}," + ",".join(f"arg={a}" for a in plugin_args))
        elif args.bbv_profiling:
            extra.append("-simpoints " + ",".join([
                f"bbv={self.bbv_output_path(name)}",
                f"interval={args.bbv_interval}",
                f"start_pc=0x{entry_point:x}",
                *process_filter,
            ]))
        if args.simpoints_file:
            opts = [
                f"file={args.simpoints_file}",
                f"interval={args.simpoint_instructions}",
                f"start_pc=0x{entry_point:x}",
            ]
            if args.pc_simpoints:
                opts.append("format=pc")
            elif args.warmup_instructions:
                opts.append(f"warmup={args.warmup_instructions}")
            extra.append("-simpoints " + ",".join(opts + process_filter))
        if args.icount:
            extra.append(
                "-icount shift=0,align=off,sleep=off "
                "-seed 123456789 -smp 1 -rtc base=utc,clock=vm"
            )
        if extra:
            parts.append(f"--{target}/extra-options={' '.join(extra)}")
        return shlex.join(parts)

    def launch(self, command):
        log_path = os.path.join(self.output_dir, "qemu.log")
        full_cmd = f"{command} 2>&1 | tee {shlex.quote(log_path)}"
        self.log(f"RUNNING COMMAND:\n{full_cmd}\n")
        print(full_cmd)
        self.process = pexpect.spawn(
            "/bin/bash", ["-c", full_cmd],
            searchwindowsize=8192,
            cwd=self.output_dir,
        )
        if self.verbose:
            self.process.logfile = sys.stdout.buffer

    def login(self):
        self.process.expect_exact("login:", timeout=None)
        self.process.sendline("root")
        self._expect_shell()

    def set_monitor_logfile(self, path):
        self.process.sendcontrol("a")
        self.process.send("c")
        self.process.expect_exact("(qemu)", timeout=None)
        self.process.sendline(f"logfile {path}")
        self.process.expect_exact("(qemu)", timeout=None)
        self.process.sendcontrol("a")
        self.process.send("c")

    def configure_system(self, trace_perthread=False, disable_aslr=False,
                         disable_revocation=False):
        settings = []
        if trace_perthread:
            settings.append("hw.qemu_trace_perthread=1")
        if disable_aslr:
            settings += [f"kern.elf64.aslr.{k}=0" for k in
                         ("enable", "stack", "shared_page", "pie_enable")]
        if disable_revocation:
            settings.append("security.cheri.runtime_revocation_default=0")
        if settings:
            self._send_command("sysctl " + " ".join(settings))

    def run_commands(self, commands, qtrace_mode=None):
        """qtrace_mode: None, "user", "simpoint" (QEMU exits after the last
        simpoint) or "bbv" (qtrace -s marks the start; QEMU keeps running)."""
        prefix = ""
        if qtrace_mode:
            prefix = f"qtrace {'-u' if qtrace_mode == 'user' else '-s'} exec -- "

        cwd = None
        for idx, (working_dir, cmd) in enumerate(commands):
            if working_dir and working_dir != cwd:
                self._send_command(f"cd {shlex.quote(working_dir)}")
                cwd = working_dir
            cmd = prefix + cmd
            self.log(f"Running command {idx}: {cmd}")
            self.process.sendline(cmd)

            if qtrace_mode == "simpoint":
                self.process.expect(SIMPOINT_DONE, timeout=None)
                self.log(f"Command {idx}: {self.process.match.group(0).decode()}")
                self.process.expect(pexpect.EOF, timeout=None)
                self.log("QEMU terminated after simpoint completion")
                break
            self._expect_shell()
            self.log(f"Command {idx} completed")

    def shutdown(self):
        print("Terminating qemu...")
        self.process.sendcontrol("a")
        self.process.send("x")
        self.process.expect(pexpect.EOF, timeout=None)
        self.process.wait()

    def _start_compressor(self, fifo, output, algorithm, xz_threads):
        if os.path.lexists(fifo):
            os.remove(fifo)
        os.mkfifo(fifo)
        cmd = (f"nice -n 5 {compress_command(algorithm, xz_threads)} "
               f"< {shlex.quote(fifo)} > {shlex.quote(output)}")
        proc = subprocess.Popen(cmd, shell=True)
        self.compressors.append((fifo, proc))
        self.log(f"Compressor ({cmd}): PID {proc.pid}")

    def start_trace_compressor(self, trace_path, algorithm, xz_threads=None):
        fifo = f"{trace_path}.fifo"
        self._start_compressor(fifo, trace_path + COMPRESSION_ALGORITHMS[algorithm],
                               algorithm, xz_threads)
        time.sleep(0.5)
        return fifo

    def start_simpoint_compressors(self, prefix, ext, simpoint_ids, algorithm,
                                   xz_threads=None):
        for idx, sp_id in enumerate(simpoint_ids):
            trace = f"{prefix}-{sp_id}B{ext}"
            fifo = f"{trace}.fifo"
            self._start_compressor(fifo, trace + COMPRESSION_ALGORITHMS[algorithm],
                                   algorithm, xz_threads)
            link = os.path.join(self.output_dir, f"simpoint_{idx}.trace")
            if os.path.lexists(link):
                os.remove(link)
            os.symlink(os.path.basename(fifo), link)
            self.symlinks.append(link)
            self.log(f"Symlink: {os.path.basename(link)} -> {os.path.basename(fifo)} "
                     f"(simpoint {sp_id})")
        time.sleep(0.5)

    def _remove_pipes(self):
        for path in [fifo for fifo, _ in self.compressors] + self.symlinks:
            if os.path.lexists(path):
                os.remove(path)
        self.compressors = []
        self.symlinks = []

    def finish_compression(self):
        for fifo, proc in self.compressors:
            self.log(f"Waiting for compressor {os.path.basename(fifo)}...")
            proc.wait()
            self.log(f"Compressor finished (code {proc.returncode})")
        self._remove_pipes()

    def abort(self):
        if self.process is not None and self.process.isalive():
            try:
                os.killpg(self.process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            self.process.close(force=True)
        for _, proc in self.compressors:
            if proc.poll() is None:
                proc.kill()
        self._remove_pipes()
