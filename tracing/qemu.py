import os
import re
import shlex
import signal
import subprocess
import sys
from dataclasses import dataclass

import pexpect

from tracing.config import BBV_PLUGIN, CHERI_ROOT, CHERIBUILD, COMPRESSION_EXTENSIONS, NO_TRACE, TEXT_TRACE, BbvMethod, QtraceMode

SHELL_PROMPT_PATTERN = re.compile(rb"root@cheribsd-riscv64(?:-purecap)?:.*?#\s*", re.S)
SIMPOINT_DONE_PATTERN = re.compile(rb"SimPoint tracing complete at [0-9]+ instructions\. Shutting down")


@dataclass(frozen=True)
class BbvOptions:
    method: BbvMethod
    interval: int
    output_name: str
    start_address: int
    end_address: int


@dataclass(frozen=True)
class SimpointOptions:
    simpoints_file: str
    interval: int
    start_address: int
    pc_based: bool = False
    warmup_instructions: int | None = None


@dataclass(frozen=True)
class LaunchOptions:
    disk_image: str
    trace_format: str = NO_TRACE
    ssh_port: int | None = None
    memory: str | None = None
    tb_size: int | None = None
    icount: bool = False
    process_filter: bool = False
    bbv: BbvOptions | None = None
    simpoints: SimpointOptions | None = None


def read_simpoint_ids(simpoints_path):
    with open(simpoints_path) as simpoints_file:
        return [int(line.split()[-1]) for line in simpoints_file if line.strip() and not line.lstrip().startswith("#")]


def compressor_command(algorithm, xz_threads=None):
    if algorithm == "xz" and xz_threads is not None:
        return f"xz -T{xz_threads}"
    return algorithm


class QemuRunner:

    def __init__(self, arch, output_dir, info_file, verbose=False):
        self.arch = arch
        self.output_dir = output_dir
        self.info_file = info_file
        self.verbose = verbose
        self.qemu_process = None
        self.compressors = []
        self.simpoint_symlinks = []

    def log(self, message=""):
        self.info_file.write(message + "\n")
        self.info_file.flush()

    def _wait_for_prompt(self):
        self.qemu_process.expect(SHELL_PROMPT_PATTERN, timeout=None)

    def _run_shell_command(self, command):
        self.qemu_process.sendline(command)
        self._wait_for_prompt()

    def bbv_output_path(self, trace_name):
        return os.path.join(self.output_dir, f"{trace_name}.bb.gz")

    def build_launch_command(self, options):
        run_target = f"run-dm-{self.arch}"
        cheribuild_args = [
            CHERIBUILD, run_target,
            "--source-root", CHERI_ROOT,
            f"--{run_target}/ephemeral",
            "--skip-update",
            f"--disk-image-{self.arch}/path", options.disk_image,
        ]
        if options.ssh_port:
            cheribuild_args.append(f"--{run_target}/ssh-forwarding-port={options.ssh_port}")
        if options.trace_format not in (NO_TRACE, TEXT_TRACE):
            cheribuild_args.append(f"--{run_target}/{options.trace_format}")

        process_filter_option = ["filter=process"] if options.process_filter else []
        qemu_options = []
        if options.memory:
            qemu_options.append(f"-m {options.memory}")
        if options.tb_size:
            qemu_options.append(f"-accel tcg,tb-size={options.tb_size}")

        bbv = options.bbv
        if bbv and bbv.method is BbvMethod.PLUGIN:
            plugin_args = [bbv.output_name, f"0x{bbv.start_address:x}", bbv.interval, f"0x{bbv.end_address:x}"]
            if options.process_filter:
                plugin_args.append("process")
            qemu_options.append(f"-plugin {BBV_PLUGIN}," + ",".join(f"arg={plugin_arg}" for plugin_arg in plugin_args))
        elif bbv:
            qemu_options.append("-simpoints " + ",".join([
                f"bbv={self.bbv_output_path(bbv.output_name)}",
                f"interval={bbv.interval}",
                f"start_pc=0x{bbv.start_address:x}",
                *process_filter_option,
            ]))

        simpoints = options.simpoints
        if simpoints:
            simpoint_options = [
                f"file={simpoints.simpoints_file}",
                f"interval={simpoints.interval}",
                f"start_pc=0x{simpoints.start_address:x}",
            ]
            if simpoints.pc_based:
                simpoint_options.append("format=pc")
            elif simpoints.warmup_instructions:
                simpoint_options.append(f"warmup={simpoints.warmup_instructions}")
            qemu_options.append("-simpoints " + ",".join(simpoint_options + process_filter_option))

        if options.icount:
            qemu_options.append("-icount shift=0,align=off,sleep=off -seed 123456789 -smp 1 -rtc base=utc,clock=vm")
        if qemu_options:
            cheribuild_args.append(f"--{run_target}/extra-options={' '.join(qemu_options)}")
        return shlex.join(cheribuild_args)

    def launch(self, launch_command):
        log_path = os.path.join(self.output_dir, "qemu.log")
        logged_command = f"{launch_command} 2>&1 | tee {shlex.quote(log_path)}"
        self.log(f"RUNNING COMMAND:\n{logged_command}\n")
        print(logged_command)
        self.qemu_process = pexpect.spawn("/bin/bash", ["-c", logged_command], searchwindowsize=8192, cwd=self.output_dir)
        if self.verbose:
            self.qemu_process.logfile = sys.stdout.buffer

    def login(self):
        self.qemu_process.expect_exact("login:", timeout=None)
        self.qemu_process.sendline("root")
        self._wait_for_prompt()

    def _toggle_monitor(self):
        self.qemu_process.sendcontrol("a")
        self.qemu_process.send("c")

    def set_monitor_logfile(self, trace_path):
        self._toggle_monitor()
        self.qemu_process.expect_exact("(qemu)", timeout=None)
        self.qemu_process.sendline(f"logfile {trace_path}")
        self.qemu_process.expect_exact("(qemu)", timeout=None)
        self._toggle_monitor()

    def configure_system(self, trace_perthread=False, disable_aslr=False, disable_revocation=False):
        sysctl_settings = []
        if trace_perthread:
            sysctl_settings.append("hw.qemu_trace_perthread=1")
        if disable_aslr:
            sysctl_settings += [f"kern.elf64.aslr.{aslr_setting}=0" for aslr_setting in ("enable", "stack", "shared_page", "pie_enable")]
        if disable_revocation:
            sysctl_settings.append("security.cheri.runtime_revocation_default=0")
        if sysctl_settings:
            self._run_shell_command("sysctl " + " ".join(sysctl_settings))

    def run_benchmark_commands(self, guest_commands, qtrace_mode=None):
        """With QtraceMode.SIMPOINT, QEMU exits by itself after the last simpoint."""
        qtrace_prefix = ""
        if qtrace_mode:
            qtrace_flag = "-u" if qtrace_mode is QtraceMode.USER else "-s"
            qtrace_prefix = f"qtrace {qtrace_flag} exec -- "

        current_dir = None
        for command_index, (working_dir, command) in enumerate(guest_commands):
            if working_dir and working_dir != current_dir:
                self._run_shell_command(f"cd {shlex.quote(working_dir)}")
                current_dir = working_dir
            command = qtrace_prefix + command
            self.log(f"Running command {command_index}: {command}")
            self.qemu_process.sendline(command)

            if qtrace_mode is QtraceMode.SIMPOINT:
                self.qemu_process.expect(SIMPOINT_DONE_PATTERN, timeout=None)
                done_message = self.qemu_process.match.group(0).decode()
                self.log(f"Command {command_index}: {done_message}")
                self.qemu_process.expect(pexpect.EOF, timeout=None)
                self.log("QEMU terminated after simpoint completion")
                break
            self._wait_for_prompt()
            self.log(f"Command {command_index} completed")

    def shutdown(self):
        print("Terminating qemu...")
        self.qemu_process.sendcontrol("a")
        self.qemu_process.send("x")
        self.qemu_process.expect(pexpect.EOF, timeout=None)
        self.qemu_process.wait()

    def _start_compressor(self, fifo_path, output_path, algorithm, xz_threads):
        if os.path.lexists(fifo_path):
            os.remove(fifo_path)
        os.mkfifo(fifo_path)
        shell_command = f"nice -n 5 {compressor_command(algorithm, xz_threads)} < {shlex.quote(fifo_path)} > {shlex.quote(output_path)}"
        compressor = subprocess.Popen(shell_command, shell=True)
        self.compressors.append((fifo_path, compressor))
        self.log(f"Compressor ({shell_command}): PID {compressor.pid}")

    def start_trace_compressor(self, trace_path, algorithm, xz_threads=None):
        fifo_path = f"{trace_path}.fifo"
        self._start_compressor(fifo_path, trace_path + COMPRESSION_EXTENSIONS[algorithm], algorithm, xz_threads)
        return fifo_path

    def start_simpoint_compressors(self, trace_prefix, trace_extension, simpoint_ids, algorithm, xz_threads=None):
        for simpoint_index, simpoint_id in enumerate(simpoint_ids):
            trace_path = f"{trace_prefix}-{simpoint_id}B{trace_extension}"
            fifo_path = f"{trace_path}.fifo"
            self._start_compressor(fifo_path, trace_path + COMPRESSION_EXTENSIONS[algorithm], algorithm, xz_threads)
            symlink_path = os.path.join(self.output_dir, f"simpoint_{simpoint_index}.trace")
            if os.path.lexists(symlink_path):
                os.remove(symlink_path)
            os.symlink(os.path.basename(fifo_path), symlink_path)
            self.simpoint_symlinks.append(symlink_path)
            self.log(f"Symlink: {os.path.basename(symlink_path)} -> {os.path.basename(fifo_path)} (simpoint {simpoint_id})")

    def _remove_fifos_and_symlinks(self):
        fifo_paths = [fifo_path for fifo_path, _ in self.compressors]
        for path in fifo_paths + self.simpoint_symlinks:
            if os.path.lexists(path):
                os.remove(path)
        self.compressors = []
        self.simpoint_symlinks = []

    def wait_for_compressors(self):
        for fifo_path, compressor in self.compressors:
            self.log(f"Waiting for compressor {os.path.basename(fifo_path)}...")
            compressor.wait()
            self.log(f"Compressor finished (code {compressor.returncode})")
        self._remove_fifos_and_symlinks()

    def kill_all(self):
        if self.qemu_process is not None and self.qemu_process.isalive():
            try:
                os.killpg(self.qemu_process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            self.qemu_process.close(force=True)
        for _, compressor in self.compressors:
            if compressor.poll() is None:
                compressor.kill()
        self._remove_fifos_and_symlinks()
