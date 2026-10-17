#!/usr/bin/env python3

import os
import re
import sys
import time
import subprocess
import pexpect

from shared.trace_config import COMPRESSION_ALGORITHMS


SHELL_PROMPTS = [
    re.compile(rb"(?s)root@cheribsd-riscv64:.*#\s*"),
    re.compile(rb"(?s)root@cheribsd-riscv64-purecap:.*#\s*"),
]

TIME_PATTERN = re.compile(
    rb"[0-9]+\.[0-9]+ real\s+[0-9]+\.[0-9]+ user\s+[0-9]+\.[0-9]+ sys"
)

SIMPOINT_SHUTDOWN_PATTERN = re.compile(
    rb"SimPoint tracing complete at [0-9]+ instructions\. Shutting down"
)


class QemuRunner:

    def __init__(self, arch, output_dir, info_file, verbose=False):
        self.arch = arch
        self.purecap = (arch == "riscv64-purecap")
        self.output_dir = output_dir
        self.info_file = info_file
        self.verbose = verbose
        self.process = None
        self.fifos = []
        self.compress_procs = []

    def _log(self, message):
        self.info_file.write(message + "\n")
        self.info_file.flush()

    def _expect_shell(self):
        self.process.expect(SHELL_PROMPTS, timeout=None)

    def _send_command(self, cmd):
        self.process.sendline(cmd)
        self._expect_shell()

    @staticmethod
    def _get_cheribuild_paths():
        if os.path.exists("/opt/cheri") and os.path.exists(
            "/opt/cheribuild/cheribuild.py"
        ):
            return {
                "cheribuild": "/opt/cheribuild/cheribuild.py",
                "source_root": "/opt/cheri",
            }
        raise RuntimeError("cheribuild installation not found at /opt/cheri")

    def build_launch_command(
        self,
        trace_format,
        memory=None,
        ssh_port=None,
        icount=False,
        bbv=False,
        bbv_interval=None,
        entry_point=None,
        exit_point=None,
        simpoints_file=None,
        simpoint_instructions=None,
        warmup_instructions=None,
        pc_simpoints=False,
        benchmark_name=None,
        disk_image=None,
        tb_size=None,
        bbv_plugin=False,
        process_filter=False,
    ):

        paths = self._get_cheribuild_paths()
        run_target = f"run-dm-{self.arch}"
        disk_target = f"disk-image-{self.arch}"

        parts = [
            paths["cheribuild"],
            run_target,
            "--source-root", paths["source_root"],
            f"--{run_target}/ephemeral",
            "--skip-update",
        ]

        if disk_image:
            parts.extend([f"--{disk_target}/path", disk_image])

        extra = []

        if memory:
            extra.append(f"-m {memory}")

        if tb_size is not None:
            tb_size = int(tb_size)
            if tb_size <= 0:
                raise ValueError(f"tb_size must be a positive number of MiB, got {tb_size}")
            extra.append(f"-accel tcg,tb-size={tb_size}")
            self._log(f"TCG translation cache size: {tb_size} MiB")

        if bbv and bbv_plugin:
            plugin_path = "/opt/cheri/qemu/contrib/plugins/libbbv.so"
            plugin_arg_list = [
                f"arg={benchmark_name}",
                f"arg=0x{entry_point:x}",
                f"arg={bbv_interval}",
                f"arg=0x{exit_point:x}",
            ]
            if process_filter:
                plugin_arg_list.append("arg=process")
            plugin_args = ",".join(plugin_arg_list)
            extra.append(f"-plugin {plugin_path},{plugin_args}")
            self._log(f"BBV plugin: -plugin {plugin_path},{plugin_args}")
        elif bbv:
            sp_parts = [
                f"bbv={self.bbv_output_path(benchmark_name)}",
                f"interval={bbv_interval}",
                f"start_pc=0x{entry_point:x}",
            ]
            if process_filter:
                sp_parts.append("filter=process")
            extra.append(f"-simpoints {','.join(sp_parts)}")
            self._log(f"BBV profiling: -simpoints {','.join(sp_parts)}")

        if simpoints_file:
            sp_parts = [
                f"file={simpoints_file}",
                f"interval={simpoint_instructions}",
                f"start_pc=0x{entry_point:x}",
            ]
            if pc_simpoints:
                sp_parts.append("format=pc")
            elif warmup_instructions:
                sp_parts.append(f"warmup={warmup_instructions}")
            if process_filter:
                sp_parts.append("filter=process")
            extra.append(f"-simpoints {','.join(sp_parts)}")

        if ssh_port:
            parts.append(f"--{run_target}/ssh-forwarding-port={ssh_port}")

        if icount:
            extra.append(
                "-icount shift=0,align=off,sleep=off "
                "-seed 123456789 -smp 1 -rtc base=utc,clock=vm"
            )

        if not bbv and trace_format not in ("text","none"):
            parts.append(f"--{run_target}/{trace_format}")

        if extra:
            parts.append(
                f"--{run_target}/extra-options=\"{' '.join(extra)}\""
            )

        return " ".join(parts)

    def bbv_output_path(self, benchmark_name):
        return os.path.join(self.output_dir, f"{benchmark_name}.bb.gz")

    def launch(self, command):
        log_path = os.path.join(self.output_dir, "qemu.log")
        full_cmd = f"{command} 2>&1 | tee {log_path}"

        self._log(f"RUNNING COMMAND:\n{full_cmd}\n")
        print(full_cmd)

        self.process = pexpect.spawn(
            "/bin/bash", ["-c", full_cmd],
            searchwindowsize=8192,
            cwd=self.output_dir,
        )

        if self.verbose:
            self.process.logfile = sys.stdout.buffer

    def login(self):
        self.process.expect("login:", timeout=None)
        self.process.sendline("root")
        self._expect_shell()

    def setup_monitor_logfile(self, trace_path):
        self.process.sendcontrol("a")
        self.process.send("c")
        self.process.expect("(qemu)", timeout=None)
        self.process.sendline(f"logfile {trace_path}")
        self.process.expect("(qemu)", timeout=None)
        self.process.sendcontrol("a")
        self.process.send("c")

    def configure_system(self, trace_perthread=False, disable_aslr=False, disable_revocation=False):
        if trace_perthread:
            self._send_command("sysctl hw.qemu_trace_perthread=1")

        if disable_aslr:
            self._send_command("sysctl kern.elf64.aslr.enable=0")
            self._send_command("sysctl kern.elf64.aslr.stack=0")
            self._send_command("sysctl kern.elf64.aslr.shared_page=0")
            self._send_command("sysctl kern.elf64.aslr.pie_enable=0")
        
        if disable_revocation:
            self._send_command("sysctl security.cheri.runtime_revocation_default=0")

    def run_commands(self, commands, qtrace_mode=None):
        """qtrace_mode: None, "user", "simpoint" (trace run; QEMU exits when
        the last simpoint is done) or "bbv" (BBV profiling: qtrace -s
        marks the program's start; QEMU keeps running afterwards)."""

        use_qtrace = qtrace_mode is not None
        simpoint_tracing = qtrace_mode == "simpoint"

        if use_qtrace:
            flag = "-u" if qtrace_mode == "user" else "-s"
            prefix = "qtrace {} exec -- ".format(flag)
            if not simpoint_tracing:
                prefix = "time " + prefix
        else:
            prefix = ""

        last_time_match = None

        for idx, (working_dir, cmd) in enumerate(commands):
            if working_dir:
                self._send_command(f"cd {working_dir}")

            traced_cmd = prefix + cmd
            self._log(f"Running command {idx}: {traced_cmd}")
            self.process.sendline(traced_cmd)

            if simpoint_tracing:
                self.process.expect(SIMPOINT_SHUTDOWN_PATTERN, timeout=None)
                shutdown_msg = self.process.match.group(0).decode("utf-8")
                self._log(f"Command {idx}: {shutdown_msg}")
                self.process.expect(pexpect.EOF, timeout=None)
                self._log("QEMU terminated after simpoint completion")
            elif use_qtrace:
                self.process.expect(TIME_PATTERN, timeout=None)
                last_time_match = self.process.match
                self._expect_shell()
                time_str = last_time_match.group(0).decode("utf-8")
                self._log(f"Command {idx} time: {time_str}")
            else:
                self._expect_shell()
                self._log(f"Command {idx} completed")

        return last_time_match, simpoint_tracing

    def run_benchmark(self, benchmark_name, benchmark_input, spec_module,
                      qtrace_mode=None):
        commands = self._get_benchmark_commands(
            benchmark_name, benchmark_input, spec_module
        )
        return self.run_commands(commands, qtrace_mode)

    def shutdown(self):
        print("Terminating qemu...")
        self.process.sendcontrol("a")
        self.process.send("x")
        self.process.expect(pexpect.EOF, timeout=None)
        self.process.wait()

    @staticmethod
    def _compress_command(algorithm, xz_threads=None):
        """Compressor command line; xz_threads (0 = one per core) is appended
        as -T for xz (the last -T on the xz command line wins)."""
        cmd = COMPRESSION_ALGORITHMS[algorithm]["cmd"]
        if xz_threads is not None and algorithm == "xz":
            cmd = f"{cmd} -T{int(xz_threads)}"
        return cmd

    def setup_single_fifo(self, trace_base, algorithm="xz", xz_threads=None):
        algo = COMPRESSION_ALGORITHMS[algorithm]
        fifo_path = f"{trace_base}.fifo"
        output_path = f"{trace_base}{algo['ext']}"

        if os.path.exists(fifo_path):
            os.remove(fifo_path)
        os.mkfifo(fifo_path)

        compress_cmd = (
            f"nice -n 5 {self._compress_command(algorithm, xz_threads)} "
            f"< {fifo_path} > {output_path}"
        )
        compress_proc = subprocess.Popen(compress_cmd, shell=True)

        self._log(f"Created FIFO: {fifo_path}")
        self._log(f"Compression ({compress_cmd}): PID {compress_proc.pid}")

        time.sleep(0.5)

        self.fifos = [fifo_path]
        self.compress_procs = [compress_proc]
        return fifo_path

    def setup_simpoint_fifos(self, benchmark_descriptor, trace_base,
                             simpoint_ids, algorithm="xz", xz_threads=None):
        algo = COMPRESSION_ALGORITHMS[algorithm]
        ext = self._trace_extension(trace_base)

        self.fifos = []
        self.compress_procs = []

        for idx, sp_id in enumerate(simpoint_ids):
            fifo_path = f"{benchmark_descriptor}-{sp_id}B{ext}.fifo"
            output_path = (
                f"{benchmark_descriptor}-{sp_id}B{ext}{algo['ext']}"
            )

            if os.path.exists(fifo_path):
                os.remove(fifo_path)
            os.mkfifo(fifo_path)

            compress_cmd = (
                f"nice -n 5 {self._compress_command(algorithm, xz_threads)} "
                f"< {fifo_path} > {output_path}"
            )
            compress_proc = subprocess.Popen(compress_cmd, shell=True)

            self._log(
                f"FIFO simpoint {sp_id} (index {idx}): {fifo_path}, "
                f"PID {compress_proc.pid}"
            )

            self.fifos.append(fifo_path)
            self.compress_procs.append(compress_proc)

            link_name = os.path.join(
                self.output_dir, f"simpoint_{idx}.trace"
            )
            if os.path.exists(link_name) or os.path.lexists(link_name):
                os.remove(link_name)
            os.symlink(os.path.basename(fifo_path), link_name)
            self._log(
                f"Symlink: simpoint_{idx}.trace -> "
                f"{os.path.basename(fifo_path)} (simpoint ID: {sp_id})"
            )

        time.sleep(0.5)

    def cleanup_compression(self, simpoint_ids=None):
        for idx, (fifo_path, proc) in enumerate(
            zip(self.fifos, self.compress_procs)
        ):
            label = (
                f"simpoint {simpoint_ids[idx]}" if simpoint_ids else "trace"
            )
            self._log(f"Waiting for {label} compression (index {idx})...")

            try:
                proc.wait()
            except subprocess.TimeoutExpired:
                self._log(f"{label} compression timed out, terminating...")
                proc.terminate()
                proc.wait()

            self._log(
                f"{label} compression finished (code {proc.returncode})"
            )

            if os.path.exists(fifo_path):
                os.remove(fifo_path)
                self._log(f"Removed FIFO: {fifo_path}")

        if simpoint_ids:
            for idx in range(len(self.fifos)):
                link_name = os.path.join(
                    self.output_dir, f"simpoint_{idx}.trace"
                )
                if os.path.lexists(link_name):
                    os.remove(link_name)
                    self._log(f"Removed symlink: {link_name}")

        self.fifos = []
        self.compress_procs = []

    @staticmethod
    def _trace_extension(trace_base):
        for ext in (".champsimtrace", ".champsimcheritrace",
                     ".trace.txt", ".bin"):
            if trace_base.endswith(ext):
                return ext
        return ""

    @staticmethod
    def read_simpoint_ids(simpoints_file):
        ids = []
        try:
            with open(simpoints_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        parts = line.split()
                        ids.append(int(parts[-1]))
            return ids
        except Exception as e:
            raise RuntimeError(
                f"Failed to read simpoints from {simpoints_file}: {e}"
            )

    def _get_benchmark_commands(self, name, benchmark_input, spec_module):
        if name not in spec_module.benchmarks:
            raise RuntimeError(
                f"Benchmark '{name}' not found in spec_commands"
            )

        benchmark = spec_module.benchmarks[name]
        workload_obj = getattr(benchmark, benchmark_input)

        current_dir = None
        for setup_cmd in workload_obj.setup:
            setup_cmd = setup_cmd.strip()
            if setup_cmd.startswith("cd "):
                path = setup_cmd[3:]
                if path.startswith("/"):
                    current_dir = path
                elif current_dir and path.startswith("./"):
                    path = path[2:]
                    if path:
                        current_dir = os.path.join(current_dir, path)
                elif current_dir and path == "..":
                    current_dir = os.path.dirname(current_dir)
                elif current_dir:
                    current_dir = os.path.join(current_dir, path)
                else:
                    current_dir = path

        commands = []
        for exec_cmd in workload_obj.execution:
            exec_cmd = exec_cmd.strip()
            if exec_cmd:
                commands.append((current_dir, exec_cmd))

        return commands