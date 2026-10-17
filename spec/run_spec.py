#!/usr/bin/env python3
import sys
import os
import argparse
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from spec.spec_config import (
    SUPPORTED_SUITES,
    describe_missing_addresses,
    get_benchmark_descriptor,
    get_start_stop_addr,
    has_start_stop_addr,
    import_spec_commands,
    list_benchmarks,
)
from shared.trace_config import DEFAULT_BBV_INTERVAL, TRACE_EXTENSIONS
from shared.qemu_runner import QemuRunner


def build_output_dir(benchmark_name, benchmark_input, base_dir="/workspace/out"):
    os.makedirs(base_dir, exist_ok=True)
    base = os.path.join(base_dir, f"{benchmark_name}_{benchmark_input}")
    if not os.path.exists(base):
        return base
    counter = 1
    while True:
        candidate = f"{base}_{counter}"
        if not os.path.exists(candidate):
            return candidate
        counter += 1


def warn(message):
    print(f"warning: {message}", file=sys.stderr)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Automated SPEC benchmark tracing in CheriBSD/QEMU",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    required = parser.add_argument_group("required arguments")
    required.add_argument(
        "--workload",
        required=True,
        help="SPEC benchmark name (e.g. gcc, mcf, lbm)",
    )
    required.add_argument(
        "--input",
        required=True,
        choices=["test", "train", "ref"],
        help="benchmark input size",
    )
    required.add_argument(
        "--spec-suite",
        required=True,
        choices=list(SUPPORTED_SUITES),
        help="SPEC CPU suite version",
    )
    required.add_argument(
        "--arch",
        required=True,
        choices=["riscv64", "riscv64-purecap"],
        help="target architecture",
    )
    required.add_argument(
        "--trace-format",
        required=False,
        default="none",
        choices=["none", "cvtrace", "text", "champsim", "champsimcheri"],
        help="instruction trace output format (none for no tracing)",
    )

    trace_opts = parser.add_argument_group("trace options")
    trace_opts.add_argument(
        "--qtrace",
        choices=["user", "simpoint"],
        help="qtrace filtering mode (-u for user, -s for simpoint)",
    )
    trace_opts.add_argument(
        "--compress",
        action="store_true",
        help="enable trace compression via FIFO pipe",
    )
    trace_opts.add_argument(
        "--compression-algorithm",
        choices=["xz", "gzip", "bzip2"],
        default="xz",
        help="compression algorithm (default: xz)",
    )
    trace_opts.add_argument(
        "--trace-perthread",
        action="store_true",
        help="stop tracing when thread is preempted (hw.qemu_trace_perthread)",
    )
    trace_opts.add_argument(
        "--xz-threads",
        type=int,
        help="threads per xz compressor (xz -T; 0 = one per core). "
             "Default: the compressor's own setting",
    )
    trace_opts.add_argument(
        "--process-filter",
        action="store_true",
        help="count, profile and trace only the benchmark's process "
             "(filter=process). Use it for both the BBV run and the "
             "SimPoint trace run",
    )

    bbv_opts = parser.add_argument_group("BBV profiling")
    bbv_opts.add_argument(
        "--bbv-profiling",
        action="store_true",
        help="collect BBVs with QEMU's inline instruction counting "
             "(-simpoints bbv=; no instruction trace). Runs the benchmark "
             "under qtrace -s",
    )
    bbv_opts.add_argument(
        "--bbv",
        action="store_true",
        help="DEPRECATED: collect BBVs with the libbbv.so plugin "
             "(slower than --bbv-profiling)",
    )
    bbv_opts.add_argument(
        "--bbv-interval",
        type=int,
        default=DEFAULT_BBV_INTERVAL,
        help=f"BBV interval in instructions (default: {DEFAULT_BBV_INTERVAL})",
    )

    sp_opts = parser.add_argument_group("SimPoint options")
    sp_opts.add_argument(
        "--simpoints-file",
        help="path to sorted SimPoints file",
    )
    sp_opts.add_argument(
        "--simpoint-instructions",
        type=int,
        help="instructions per SimPoint interval",
    )
    sp_opts.add_argument(
        "--warmup-instructions",
        type=int,
        help="warmup instructions before each SimPoint",
    )
    sp_opts.add_argument(
        "--pc-simpoints",
        action="store_true",
        help="use PC-based SimPoints mode",
    )

    qemu_opts = parser.add_argument_group("QEMU options")
    qemu_opts.add_argument(
        "-o", "--output-dir",
        default="/workspace/out",
        help="base directory for output (default: /workspace/out)",
    )
    qemu_opts.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="mirror all QEMU output to stdout",
    )
    qemu_opts.add_argument(
        "--ssh-port",
        type=int,
        help="SSH forwarding port for CheriBSD",
    )
    qemu_opts.add_argument(
        "-m", "--memory",
        help="QEMU guest memory (e.g. 4G)",
    )
    qemu_opts.add_argument(
        "--tb-size",
        help="Controls the size (in MiB) of the TCG translation block cache. Max 2048",
    )
    qemu_opts.add_argument(
        "--disable-aslr",
        action="store_true",
        help="disable ASLR in CheriBSD",
    )
    qemu_opts.add_argument(
        "--disable-revocation",
        action="store_true",
        help="disable Capability Revocation in CheriBSD. ",
    )
    qemu_opts.add_argument(
        "--icount",
        action="store_true",
        help="enable deterministic execution with icount",
    )

    args = parser.parse_args()
    # Keep the old --bbv (plugin) working; both set args.bbv for the rest
    # of the script, args.bbv_plugin tells them apart.
    if args.bbv and args.bbv_profiling:
        parser.error("--bbv and --bbv-profiling are mutually exclusive")
    args.bbv_plugin = args.bbv
    args.bbv = args.bbv or args.bbv_profiling
    return parser, args


def validate_args(parser, args):
    purecap = args.arch == "riscv64-purecap"

    if args.bbv_plugin:
        warn("--bbv (BBV plugin) is deprecated and slower than "
             "--bbv-profiling (BBVs from inline instruction counting)")
    if args.bbv and not args.bbv_plugin and args.trace_format != "none":
        parser.error("--bbv-profiling is not compatible with instruction "
                     "tracing. Set --trace-format to 'none'.")
    if args.xz_threads is not None:
        if args.xz_threads < 0:
            parser.error("--xz-threads must be 0 (one per core) or more")
        if args.compression_algorithm != "xz":
            parser.error("--xz-threads requires --compression-algorithm xz")
    if args.process_filter:
        if not (args.bbv or args.simpoints_file):
            parser.error("--process-filter requires --bbv-profiling, --bbv "
                         "or --simpoints-file")
        if args.pc_simpoints:
            parser.error("--process-filter only supports interval-based "
                         "SimPoints (not --pc-simpoints)")
        if args.trace_perthread:
            warn("--trace-perthread has no effect with --process-filter "
                 "(QEMU ignores the per-thread qtrace start/stop during "
                 "SimPoint runs)")

    if args.trace_format == "none":
        if args.compress:
            parser.error("--compress requires a trace format")
        if args.simpoints_file:
            parser.error("--simpoints-file requires a trace format")
        if args.qtrace:
            parser.error("--qtrace requires a trace format")

    if args.trace_format == "champsim" and purecap:
        parser.error("--trace-format champsim requires --arch riscv64")

    if args.trace_format == "champsimcheri" and not purecap:
        parser.error( "--trace-format champsimcheri requires --arch riscv64-purecap")

    if args.bbv and args.simpoints_file:
        parser.error("--bbv and --simpoints-file are mutually exclusive")

    if args.bbv and args.compress:
        parser.error(
            "--bbv uses built-in gzip compression; "
            "--compress is not needed")

    if args.bbv and args.trace_format != "none":
        parser.error("--bbv profiling is not compatible with instruction tracing. Set --trace-format to 'none'.")

    if args.simpoints_file:
        if not args.simpoint_instructions:
            parser.error("--simpoints-file requires --simpoint-instructions")

        if args.qtrace != "simpoint":
            parser.error("--simpoints-file requires --qtrace simpoint")

        if not os.path.exists(args.simpoints_file):
            parser.error(f"SimPoints file not found: {args.simpoints_file}")

    if args.simpoint_instructions and not args.simpoints_file:
        parser.error("--simpoint-instructions requires --simpoints-file")

    if args.pc_simpoints and not args.simpoints_file:
        parser.error("--pc-simpoints requires --simpoints-file")

    if args.pc_simpoints and args.warmup_instructions:
        parser.error("--pc-simpoints and --warmup-instructions are mutually exclusive")

    if args.workload not in list_benchmarks(args.spec_suite):
        available = ", ".join(list_benchmarks(args.spec_suite))
        parser.error(
            f"benchmark '{args.workload}' has no descriptor in SPEC "
            f"{args.spec_suite}. Available: {available}"
        )

    spec_module = import_spec_commands(args.spec_suite)
    if args.workload not in spec_module.benchmarks:
        available = ", ".join(sorted(spec_module.benchmarks.keys()))
        parser.error(
            f"benchmark '{args.workload}' not found in SPEC {args.spec_suite}. "
            f"Available: {available}"
        )

    # BBV and SimPoint runs need main/exit addresses. Fail early (before
    # creating an output directory or booting QEMU) if they are missing,
    # e.g. baseline riscv64 for SPEC 2026, or gcc/llvm in SPEC 2026 purecap.
    needs_addresses = args.bbv or args.simpoints_file
    if needs_addresses and not has_start_stop_addr(
        args.workload, purecap, args.spec_suite
    ):
        reason = describe_missing_addresses(
            args.workload, purecap, args.spec_suite
        )
        parser.error(
            f"{reason}; --bbv and --simpoints-file need them. "
            f"Plain runs and full-trace runs still work."
        )


def main():
    parser, args = parse_args()
    validate_args(parser, args)

    purecap = args.arch == "riscv64-purecap"
    spec_module = import_spec_commands(args.spec_suite)
    descriptor = get_benchmark_descriptor(args.workload, args.spec_suite)

    needs_addresses = args.bbv or args.simpoints_file
    entry_point = exit_point = None
    if needs_addresses:
        entry_point, exit_point = get_start_stop_addr(
            args.workload, purecap, args.spec_suite
        )

    output_dir = build_output_dir(
        args.workload, args.input, args.output_dir
    )
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")

    use_compression = args.compress or args.simpoints_file

    with open(os.path.join(output_dir, "info.txt"), "w") as info_file:

        info_file.write(f"Benchmark: {args.workload}\n")
        info_file.write(f"Descriptor: {descriptor}\n")
        info_file.write(f"Input: {args.input}\n")
        info_file.write(f"SPEC suite: {args.spec_suite}\n")
        info_file.write(f"Architecture: {args.arch}\n")
        info_file.write(f"Trace format: {args.trace_format}\n")
        if entry_point is not None:
            info_file.write(f"Entry point: {entry_point:#x}\n")
            info_file.write(f"Exit point: {exit_point:#x}\n")
        if args.qtrace:
            info_file.write(f"qtrace mode: {args.qtrace}\n")
        if args.bbv:
            info_file.write(f"BBV profiling: enabled\n")
            info_file.write(f"BBV interval: {args.bbv_interval}\n")
            info_file.write("BBV collection: "
                            + ("plugin (deprecated)" if args.bbv_plugin
                               else "inline instruction counting") + "\n")
        if args.simpoints_file:
            mode = "PC-based" if args.pc_simpoints else "interval-based"
            info_file.write(f"SimPoints file: {args.simpoints_file}\n")
            info_file.write(f"SimPoints mode: {mode}\n")
            info_file.write(
                f"SimPoint interval: {args.simpoint_instructions}\n"
            )
            if args.warmup_instructions:
                info_file.write(f"Warmup instructions: {args.warmup_instructions}\n")
        if use_compression:
            info_file.write(f"Compression: {args.compression_algorithm}\n")
        if args.process_filter:
            info_file.write("Process filter: enabled\n")
        if args.xz_threads is not None:
            info_file.write(f"xz threads: {args.xz_threads}\n")
        info_file.write(f"Timestamp: {datetime.now().isoformat()}\n\n")

        runner = QemuRunner(
            arch=args.arch,
            output_dir=output_dir,
            info_file=info_file,
            verbose=args.verbose,
        )

        trace_ofile = None
        simpoint_ids = []

        if args.bbv:
            info_file.write(
                f"BBV output: {args.workload}.bb.gz\n"
            )
        elif args.trace_format != "none":
            ext = TRACE_EXTENSIONS[args.trace_format]
            trace_base = os.path.join(
                output_dir, f"{args.workload}{ext}"
            )

            if use_compression:
                if args.simpoints_file:
                    simpoint_ids = QemuRunner.read_simpoint_ids(
                        args.simpoints_file
                    )
                    info_file.write(
                        f"Simpoints ({len(simpoint_ids)}): "
                        f"{simpoint_ids}\n"
                    )
                    runner.setup_simpoint_fifos(
                        os.path.join(output_dir, descriptor),
                        trace_base,
                        simpoint_ids,
                        algorithm=args.compression_algorithm,
                        xz_threads=args.xz_threads,
                    )
                else:
                    trace_ofile = runner.setup_single_fifo(
                        trace_base, algorithm=args.compression_algorithm,
                        xz_threads=args.xz_threads,
                    )
            else:
                trace_ofile = trace_base

        cmd = runner.build_launch_command(
            trace_format=args.trace_format,
            memory=args.memory,
            ssh_port=args.ssh_port,
            icount=args.icount,
            bbv=args.bbv,
            bbv_interval=args.bbv_interval,
            entry_point=entry_point,
            exit_point=exit_point,
            simpoints_file=args.simpoints_file,
            simpoint_instructions=args.simpoint_instructions,
            warmup_instructions=args.warmup_instructions,
            pc_simpoints=args.pc_simpoints,
            bbv_plugin=args.bbv_plugin,
            process_filter=args.process_filter,
            benchmark_name=args.workload,
            disk_image=f"/opt/cheri/output/cheribsd-{args.arch}-speccpu.img",
            tb_size=args.tb_size,
        )

        # --bbv-profiling needs qtrace -s to mark the program's start.
        qtrace_mode = args.qtrace
        if args.bbv and not args.bbv_plugin:
            qtrace_mode = "bbv"

        runner.launch(cmd)
        runner.login()

        if not args.bbv and not args.simpoints_file and trace_ofile:
            runner.setup_monitor_logfile(trace_ofile)

        runner.configure_system(
            trace_perthread=args.trace_perthread,
            disable_aslr=args.disable_aslr,
            disable_revocation=args.disable_revocation,
        )

        time_match, qemu_exited = runner.run_benchmark(
            benchmark_name=args.workload,
            benchmark_input=args.input,
            spec_module=spec_module,
            qtrace_mode=qtrace_mode,
        )

        if time_match is not None:
            time_str = time_match.group(0).decode("utf-8")
            info_file.write(f"Total time: {time_str}\n\n")
            if not args.verbose:
                print(f"Total time: {time_str}")
        else:
            info_file.write("Benchmark completed\n\n")
            if not args.verbose:
                print("Benchmark completed")

        if not qemu_exited:
            runner.shutdown()

        if use_compression and runner.fifos:
            runner.cleanup_compression(
                simpoint_ids=simpoint_ids if simpoint_ids else None
            )

        info_file.write("Done.\n\n")


if __name__ == "__main__":
    main()