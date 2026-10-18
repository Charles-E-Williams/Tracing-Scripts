import argparse
import os
import sys
from datetime import datetime

from tracing.config import (
    ARCHS,
    COMPRESSION_ALGORITHMS,
    DEFAULT_BBV_INTERVAL,
    DEFAULT_OUTPUT_DIR,
    MAX_TB_SIZE,
    PURECAP,
    TRACE_EXTENSIONS,
    disk_image,
)
from tracing.qemu import QemuRunner, read_simpoint_ids
from tracing.workload import AddressError


def warn(message):
    print(f"warning: {message}", file=sys.stderr)


def flag(dest):
    return "--" + dest.replace("_", "-")


def add_common_args(parser):
    g = parser.add_argument_group("target")
    g.add_argument("--arch", required=True, choices=ARCHS,
                   help="target architecture")
    g.add_argument("--trace-format", default="none",
                   choices=["none", *TRACE_EXTENSIONS],
                   help="instruction trace format (default: none)")

    g = parser.add_argument_group("trace options")
    g.add_argument("--qtrace", choices=["user", "simpoint"],
                   help="qtrace filtering mode (-u for user, -s for simpoint)")
    g.add_argument("--compress", action="store_true",
                   help="compress the trace through a FIFO")
    g.add_argument("--compression-algorithm", default="xz",
                   choices=list(COMPRESSION_ALGORITHMS),
                   help="compression algorithm (default: xz)")
    g.add_argument("--xz-threads", type=int,
                   help="threads per xz compressor (xz -T; 0 = one per core)")
    g.add_argument("--trace-perthread", action="store_true",
                   help="stop tracing when the thread is preempted")
    g.add_argument("--process-filter", action="store_true",
                   help="count, profile and trace only the benchmark's process; "
                        "use it for both the BBV run and the SimPoint trace run")

    g = parser.add_argument_group("BBV profiling")
    m = g.add_mutually_exclusive_group()
    m.add_argument("--bbv-profiling", action="store_true",
                   help="collect BBVs with QEMU's inline instruction counting")
    m.add_argument("--bbv", dest="bbv_plugin", action="store_true",
                   help="DEPRECATED: collect BBVs with the libbbv.so plugin")
    g.add_argument("--bbv-interval", type=int, default=DEFAULT_BBV_INTERVAL,
                   help=f"BBV interval in instructions (default: {DEFAULT_BBV_INTERVAL})")

    g = parser.add_argument_group("SimPoint options")
    g.add_argument("--simpoints-file", help="sorted SimPoints file")
    g.add_argument("--simpoint-instructions", type=int,
                   help="instructions per SimPoint interval")
    g.add_argument("--warmup-instructions", type=int,
                   help="warmup instructions before each SimPoint")
    g.add_argument("--pc-simpoints", action="store_true",
                   help="use PC-based SimPoints")

    g = parser.add_argument_group("QEMU options")
    g.add_argument("-o", "--output-dir", default=DEFAULT_OUTPUT_DIR,
                   help=f"base output directory (default: {DEFAULT_OUTPUT_DIR})")
    g.add_argument("-v", "--verbose", action="store_true",
                   help="mirror QEMU output to stdout")
    g.add_argument("--ssh-port", type=int, help="SSH forwarding port")
    g.add_argument("-m", "--memory", help="guest memory (e.g. 4G)")
    g.add_argument("--tb-size", type=int,
                   help=f"TCG translation block cache size in MiB (max {MAX_TB_SIZE})")
    g.add_argument("--disable-aslr", action="store_true", help="disable ASLR")
    g.add_argument("--disable-revocation", action="store_true",
                   help="disable capability revocation")
    g.add_argument("--icount", action="store_true",
                   help="deterministic execution with icount")


def validate(args, error):
    purecap = args.arch == PURECAP
    tracing = args.trace_format != "none"

    if args.bbv_plugin:
        warn("--bbv (BBV plugin) is deprecated and slower than --bbv-profiling")
    if args.bbv:
        if args.simpoints_file:
            error("BBV profiling and --simpoints-file are mutually exclusive")
        if tracing:
            error("BBV profiling is not compatible with instruction tracing; "
                  "use --trace-format none")
        if args.compress:
            error("BBV output is always gzip-compressed; --compress is not needed")

    if not tracing:
        for dest in ("compress", "qtrace", "simpoints_file"):
            if getattr(args, dest):
                error(f"{flag(dest)} requires --trace-format")
    if args.trace_format == "champsim" and purecap:
        error("--trace-format champsim requires --arch riscv64")
    if args.trace_format == "champsimcheri" and not purecap:
        error("--trace-format champsimcheri requires --arch riscv64-purecap")

    if args.simpoints_file:
        if not args.simpoint_instructions:
            error("--simpoints-file requires --simpoint-instructions")
        if args.qtrace != "simpoint":
            error("--simpoints-file requires --qtrace simpoint")
        if args.pc_simpoints and args.warmup_instructions:
            error("--pc-simpoints and --warmup-instructions are mutually exclusive")
        try:
            args.simpoint_ids = read_simpoint_ids(args.simpoints_file)
        except (OSError, ValueError, IndexError) as e:
            error(f"cannot read SimPoints file {args.simpoints_file}: {e}")
    else:
        for dest in ("simpoint_instructions", "warmup_instructions", "pc_simpoints"):
            if getattr(args, dest):
                error(f"{flag(dest)} requires --simpoints-file")
        if args.qtrace == "simpoint":
            error("--qtrace simpoint requires --simpoints-file")

    if args.xz_threads is not None:
        if args.xz_threads < 0:
            error("--xz-threads must be 0 (one per core) or more")
        if args.compression_algorithm != "xz":
            error("--xz-threads requires --compression-algorithm xz")

    if args.process_filter:
        if not (args.bbv or args.simpoints_file):
            error("--process-filter requires --bbv-profiling, --bbv or --simpoints-file")
        if args.pc_simpoints:
            error("--process-filter only supports interval-based SimPoints")
        if args.trace_perthread:
            warn("--trace-perthread has no effect with --process-filter")

    if args.tb_size is not None and not 0 < args.tb_size <= MAX_TB_SIZE:
        error(f"--tb-size must be between 1 and {MAX_TB_SIZE} MiB")


def parse_args(workloads, argv=None):
    parser = argparse.ArgumentParser(
        description="Trace benchmarks in CheriBSD under CHERI QEMU")
    sub = parser.add_subparsers(dest="command", required=True, metavar="WORKLOAD")
    for w in workloads:
        p = sub.add_parser(w.name, help=w.help, description=w.help)
        w.add_args(p)
        add_common_args(p)
        p.set_defaults(workload_impl=w, error=p.error)

    args = parser.parse_args(argv)
    workload, error = args.workload_impl, args.error
    args.bbv = args.bbv_plugin or args.bbv_profiling

    validate(args, error)
    workload.validate(args, error)

    args.entry_point = args.exit_point = None
    if args.bbv or args.simpoints_file:
        try:
            args.entry_point, args.exit_point = workload.addresses(args)
        except AddressError as e:
            error(f"{e}; BBV profiling and SimPoint tracing need start/end addresses")
    return workload, args


def make_output_dir(base):
    path, n = base, 0
    while True:
        try:
            os.makedirs(path)
            return path
        except FileExistsError:
            n += 1
            path = f"{base}_{n}"


def info_fields(workload, args):
    fields = {**workload.info(args),
              "Architecture": args.arch,
              "Trace format": args.trace_format}
    if args.entry_point is not None:
        fields["Entry point"] = f"{args.entry_point:#x}"
    if args.exit_point is not None:
        fields["Exit point"] = f"{args.exit_point:#x}"
    if args.qtrace:
        fields["qtrace mode"] = args.qtrace
    if args.bbv:
        fields["BBV collection"] = ("plugin (deprecated)" if args.bbv_plugin
                                    else "inline instruction counting")
        fields["BBV interval"] = args.bbv_interval
    if args.simpoints_file:
        fields["SimPoints file"] = args.simpoints_file
        fields["SimPoints mode"] = "PC-based" if args.pc_simpoints else "interval-based"
        fields["SimPoint interval"] = args.simpoint_instructions
        if args.warmup_instructions:
            fields["Warmup instructions"] = args.warmup_instructions
    if args.compress or args.simpoints_file:
        fields["Compression"] = args.compression_algorithm
    if args.xz_threads is not None:
        fields["xz threads"] = args.xz_threads
    if args.process_filter:
        fields["Process filter"] = "enabled"
    if args.tb_size:
        fields["TCG translation cache"] = f"{args.tb_size} MiB"
    fields["Timestamp"] = datetime.now().isoformat()
    return fields


def trace(runner, workload, args):
    name = workload.label(args)
    ext = TRACE_EXTENSIONS.get(args.trace_format)
    trace_file = None

    if args.bbv:
        runner.log(f"BBV output: {os.path.basename(runner.bbv_output_path(name))}")
    elif args.simpoints_file:
        runner.log(f"Simpoints ({len(args.simpoint_ids)}): {args.simpoint_ids}")
        runner.start_simpoint_compressors(
            os.path.join(runner.output_dir, workload.descriptor(args)), ext,
            args.simpoint_ids, args.compression_algorithm, args.xz_threads)
    elif ext:
        trace_file = os.path.join(runner.output_dir, name + ext)
        if args.compress:
            trace_file = runner.start_trace_compressor(
                trace_file, args.compression_algorithm, args.xz_threads)

    runner.launch(runner.launch_command(
        args, name, disk_image(args.arch, workload.disk(args)),
        args.entry_point, args.exit_point))
    runner.login()
    if trace_file:
        runner.set_monitor_logfile(trace_file)
    runner.configure_system(args.trace_perthread, args.disable_aslr,
                            args.disable_revocation)

    qtrace_mode = "bbv" if args.bbv_profiling else args.qtrace
    runner.run_commands(workload.commands(args), qtrace_mode)
    runner.log("Benchmark completed\n")
    if not args.verbose:
        print("Benchmark completed")

    if qtrace_mode != "simpoint":
        runner.shutdown()
    runner.finish_compression()
    runner.log("Done.")


def main(workloads, argv=None):
    workload, args = parse_args(workloads, argv)
    output_dir = make_output_dir(os.path.join(args.output_dir, workload.output_name(args)))
    print(f"Output directory: {output_dir}")

    with open(os.path.join(output_dir, "info.txt"), "w") as info_file:
        runner = QemuRunner(args.arch, output_dir, info_file, args.verbose)
        for key, value in info_fields(workload, args).items():
            runner.log(f"{key}: {value}")
        runner.log()
        try:
            trace(runner, workload, args)
        except BaseException:
            runner.abort()
            raise
