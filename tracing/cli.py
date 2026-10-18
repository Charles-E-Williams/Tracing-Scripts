import argparse
import os
import sys
from dataclasses import dataclass
from datetime import datetime

from tracing.config import ARCHS, BBV_KEYS, COMPRESSION_EXTENSIONS, DEFAULT_BBV_INTERVAL, DEFAULT_OUTPUT_DIR, MAX_TB_SIZE_MIB, NO_TRACE, PURECAP_ARCH, TRACE_EXTENSIONS, TRACE_FORMATS, BbvMethod, QtraceMode, disk_image_path
from tracing.qemu import BbvOptions, LaunchOptions, QemuRunner, SimpointOptions, read_simpoint_ids
from tracing.workload import Workload, option_name


@dataclass(frozen=True)
class RunConfig:
    workload: Workload
    args: argparse.Namespace
    qtrace_mode: QtraceMode | None
    bbv_method: BbvMethod | None
    compress_trace: bool
    simpoint_ids: list
    start_address: int | None
    end_address: int | None


def warn(message):
    print(f"warning: {message}", file=sys.stderr)


def add_common_args(parser):
    target_group = parser.add_argument_group("target")
    target_group.add_argument("--arch", required=True, choices=ARCHS, help="target architecture")
    target_group.add_argument("--trace-format", default=NO_TRACE, choices=TRACE_FORMATS, help="instruction trace format (default: none)")

    trace_group = parser.add_argument_group("trace options")
    trace_group.add_argument("--qtrace", choices=[QtraceMode.USER.value, QtraceMode.SIMPOINT.value], help="qtrace filtering mode (-u for user, -s for simpoint)")
    trace_group.add_argument("--compress", action="store_true", help="compress the trace through a FIFO")
    trace_group.add_argument("--compression-algorithm", default="xz", choices=list(COMPRESSION_EXTENSIONS), help="compression algorithm (default: xz)")
    trace_group.add_argument("--xz-threads", type=int, help="threads per xz compressor (xz -T; 0 = one per core)")
    trace_group.add_argument("--trace-perthread", action="store_true", help="stop tracing when the thread is preempted")
    trace_group.add_argument("--process-filter", action="store_true", help="count, profile and trace only the benchmark's process; use it for both the BBV run and the SimPoint trace run")

    bbv_group = parser.add_argument_group("BBV profiling")
    bbv_method = bbv_group.add_mutually_exclusive_group()
    bbv_method.add_argument("--bbv-profiling", action="store_true", help="collect BBVs with QEMU's inline instruction counting")
    bbv_method.add_argument("--bbv", dest="bbv_plugin", action="store_true", help="DEPRECATED: collect BBVs with the libbbv.so plugin")
    bbv_group.add_argument("--bbv-interval", type=int, default=DEFAULT_BBV_INTERVAL, help=f"BBV interval in instructions (default: {DEFAULT_BBV_INTERVAL})")
    bbv_group.add_argument("--bbv-key", choices=BBV_KEYS, help=f"how QEMU keys basic blocks in the BBV (bbvkey=, default: {DEFAULT_BBV_KEY})")
    
    simpoint_group = parser.add_argument_group("SimPoint options")
    simpoint_group.add_argument("--simpoints-file", help="sorted SimPoints file")
    simpoint_group.add_argument("--simpoint-instructions", type=int, help="instructions per SimPoint interval")
    simpoint_group.add_argument("--warmup-instructions", type=int, help="warmup instructions before each SimPoint")
    simpoint_group.add_argument("--pc-simpoints", action="store_true", help="use PC-based SimPoints")

    qemu_group = parser.add_argument_group("QEMU options")
    qemu_group.add_argument("-o", "--output-dir", default=DEFAULT_OUTPUT_DIR, help=f"base output directory (default: {DEFAULT_OUTPUT_DIR})")
    qemu_group.add_argument("-v", "--verbose", action="store_true", help="mirror QEMU output to stdout")
    qemu_group.add_argument("--ssh-port", type=int, help="SSH forwarding port")
    qemu_group.add_argument("-m", "--memory", help="guest memory (e.g. 4G)")
    qemu_group.add_argument("--tb-size", type=int, help=f"TCG translation block cache size in MiB (max {MAX_TB_SIZE_MIB})")
    qemu_group.add_argument("--disable-aslr", action="store_true", help="disable ASLR")
    qemu_group.add_argument("--disable-revocation", action="store_true", help="disable capability revocation")
    qemu_group.add_argument("--icount", action="store_true", help="deterministic execution with icount")


def validate_common_args(args, report_error):
    purecap = args.arch == PURECAP_ARCH
    instruction_tracing = args.trace_format != NO_TRACE
    bbv_requested = args.bbv_plugin or args.bbv_profiling

    if args.bbv_plugin:
        warn("--bbv (BBV plugin) is deprecated and slower than --bbv-profiling")
    if args.bbv_key and not args.bbv_profiling:
        report_error("--bbv-key requires --bbv-profiling")
    if bbv_requested:
        if args.simpoints_file:
            report_error("BBV profiling and --simpoints-file are mutually exclusive")
        if instruction_tracing:
            report_error("BBV profiling is not compatible with instruction tracing; use --trace-format none")
        if args.compress:
            report_error("BBV output is always gzip-compressed; --compress is not needed")

    if not instruction_tracing:
        for arg_name in ("compress", "qtrace", "simpoints_file"):
            if getattr(args, arg_name):
                report_error(f"{option_name(arg_name)} requires --trace-format")
    if args.trace_format == "champsim" and purecap:
        report_error("--trace-format champsim requires --arch riscv64")
    if args.trace_format == "champsimcheri" and not purecap:
        report_error("--trace-format champsimcheri requires --arch riscv64-purecap")

    if args.simpoints_file:
        if not args.simpoint_instructions:
            report_error("--simpoints-file requires --simpoint-instructions")
        if args.qtrace != QtraceMode.SIMPOINT.value:
            report_error("--simpoints-file requires --qtrace simpoint")
        if args.pc_simpoints and args.warmup_instructions:
            report_error("--pc-simpoints and --warmup-instructions are mutually exclusive")
    else:
        for arg_name in ("simpoint_instructions", "warmup_instructions", "pc_simpoints"):
            if getattr(args, arg_name):
                report_error(f"{option_name(arg_name)} requires --simpoints-file")
        if args.qtrace == QtraceMode.SIMPOINT.value:
            report_error("--qtrace simpoint requires --simpoints-file")

    if args.xz_threads is not None:
        if args.xz_threads < 0:
            report_error("--xz-threads must be 0 (one per core) or more")
        if args.compression_algorithm != "xz":
            report_error("--xz-threads requires --compression-algorithm xz")

    if args.process_filter:
        if not (bbv_requested or args.simpoints_file):
            report_error("--process-filter requires --bbv-profiling, --bbv or --simpoints-file")
        if args.pc_simpoints:
            report_error("--process-filter only supports interval-based SimPoints")
        if args.trace_perthread:
            warn("--trace-perthread has no effect with --process-filter")

    if args.tb_size is not None and not 0 < args.tb_size <= MAX_TB_SIZE_MIB:
        report_error(f"--tb-size must be between 1 and {MAX_TB_SIZE_MIB} MiB")


def build_run_config(workload, args, report_error):
    if args.bbv_profiling:
        bbv_method = BbvMethod.INLINE
    elif args.bbv_plugin:
        bbv_method = BbvMethod.PLUGIN
    else:
        bbv_method = None

    simpoint_ids = []
    if args.simpoints_file:
        try:
            simpoint_ids = read_simpoint_ids(args.simpoints_file)
        except (OSError, ValueError, IndexError) as read_error:
            report_error(f"cannot read SimPoints file {args.simpoints_file}: {read_error}")

    if bbv_method is BbvMethod.INLINE:
        qtrace_mode = QtraceMode.BBV
    elif args.qtrace:
        qtrace_mode = QtraceMode(args.qtrace)
    else:
        qtrace_mode = None

    start_address = end_address = None
    if bbv_method or args.simpoints_file:
        start_address, end_address = workload.start_end_addresses(args)
        if start_address is None or end_address is None:
            report_error(f"no start/end addresses recorded for {workload.display_name(args)} on {args.arch}; BBV profiling and SimPoint tracing need them")

    return RunConfig(
        workload=workload,
        args=args,
        qtrace_mode=qtrace_mode,
        bbv_method=bbv_method,
        compress_trace=args.compress or bool(args.simpoints_file),
        simpoint_ids=simpoint_ids,
        start_address=start_address,
        end_address=end_address,
    )


def parse_run_config(workloads, argv=None):
    workloads_by_suite = {workload.name: workload for workload in workloads}

    suite_parser = argparse.ArgumentParser(add_help=False)
    suite_parser.add_argument("--benchmark-suite")
    workload = workloads_by_suite.get(suite_parser.parse_known_args(argv)[0].benchmark_suite)

    parser = argparse.ArgumentParser(description="Trace benchmarks in CheriBSD under CHERI QEMU", epilog="Add --benchmark-suite SUITE to --help to list that suite's options.")
    parser.add_argument("--benchmark-suite", required=True, choices=workloads_by_suite, help="benchmark suite to run")
    if workload:
        workload.add_args(parser)
    add_common_args(parser)

    args = parser.parse_args(argv)
    validate_common_args(args, parser.error)
    workload.validate(args, parser.error)
    return build_run_config(workload, args, parser.error)


def build_launch_options(config):
    args = config.args
    bbv = simpoints = None
    if config.bbv_method:
        bbv = BbvOptions(config.bbv_method, args.bbv_interval, config.workload.trace_name(args), config.start_address, config.end_address, args.bbv_key or DEFAULT_BBV_KEY)
    if args.simpoints_file:
        simpoints = SimpointOptions(args.simpoints_file, args.simpoint_instructions, config.start_address, args.pc_simpoints, args.warmup_instructions)
    return LaunchOptions(
        disk_image=disk_image_path(args.arch, config.workload.disk_image_suffix(args)),
        trace_format=args.trace_format,
        ssh_port=args.ssh_port,
        memory=args.memory,
        tb_size=args.tb_size,
        icount=args.icount,
        process_filter=args.process_filter,
        bbv=bbv,
        simpoints=simpoints,
    )


def create_unique_output_dir(base_path):
    output_dir, suffix = base_path, 0
    while True:
        try:
            os.makedirs(output_dir)
            return output_dir
        except FileExistsError:
            suffix += 1
            output_dir = f"{base_path}_{suffix}"


def collect_info_fields(config):
    args = config.args
    fields = {**config.workload.info_fields(args), "Architecture": args.arch, "Trace format": args.trace_format}
    if config.start_address is not None:
        fields["Entry point"] = f"{config.start_address:#x}"
        fields["Exit point"] = f"{config.end_address:#x}"
    if args.qtrace:
        fields["qtrace mode"] = args.qtrace
    if config.bbv_method:
        fields["BBV collection"] = config.bbv_method.value
        fields["BBV interval"] = args.bbv_interval
        if config.bbv_method is BbvMethod.INLINE:
            fields["BBV key"] = args.bbv_key or DEFAULT_BBV_KEY
    if args.simpoints_file:
        fields["SimPoints file"] = args.simpoints_file
        fields["SimPoints mode"] = "PC-based" if args.pc_simpoints else "interval-based"
        fields["SimPoint interval"] = args.simpoint_instructions
        if args.warmup_instructions:
            fields["Warmup instructions"] = args.warmup_instructions
    if config.compress_trace:
        fields["Compression"] = args.compression_algorithm
    if args.xz_threads is not None:
        fields["xz threads"] = args.xz_threads
    if args.process_filter:
        fields["Process filter"] = "enabled"
    if args.tb_size:
        fields["TCG translation cache"] = f"{args.tb_size} MiB"
    fields["Timestamp"] = datetime.now().isoformat()
    return fields


def run_workload(runner, config):
    args, workload = config.args, config.workload
    trace_name = workload.trace_name(args)
    trace_extension = TRACE_EXTENSIONS.get(args.trace_format)
    monitor_logfile = None

    if config.bbv_method:
        runner.log(f"BBV output: {os.path.basename(runner.bbv_output_path(trace_name))}")
    elif args.simpoints_file:
        runner.log(f"Simpoints ({len(config.simpoint_ids)}): {config.simpoint_ids}")
        trace_prefix = os.path.join(runner.output_dir, workload.simpoint_trace_prefix(args))
        runner.start_simpoint_compressors(trace_prefix, trace_extension, config.simpoint_ids, args.compression_algorithm, args.xz_threads)
    elif trace_extension:
        monitor_logfile = os.path.join(runner.output_dir, trace_name + trace_extension)
        if config.compress_trace:
            monitor_logfile = runner.start_trace_compressor(monitor_logfile, args.compression_algorithm, args.xz_threads)

    runner.launch(runner.build_launch_command(build_launch_options(config)))
    runner.login()
    if monitor_logfile:
        runner.set_monitor_logfile(monitor_logfile)
    runner.configure_system(args.trace_perthread, args.disable_aslr, args.disable_revocation)

    runner.run_benchmark_commands(workload.guest_commands(args), config.qtrace_mode)
    runner.log("Benchmark completed\n")
    if not args.verbose:
        print("Benchmark completed")

    if config.qtrace_mode is not QtraceMode.SIMPOINT:
        runner.shutdown()
    runner.wait_for_compressors()
    runner.log("Done.")


def main(workloads, argv=None):
    config = parse_run_config(workloads, argv)
    output_dir = create_unique_output_dir(os.path.join(config.args.output_dir, config.workload.output_dir_name(config.args)))
    print(f"Output directory: {output_dir}")

    with open(os.path.join(output_dir, "info.txt"), "w") as info_file:
        runner = QemuRunner(config.args.arch, output_dir, info_file, config.args.verbose)
        for field_name, value in collect_info_fields(config).items():
            runner.log(f"{field_name}: {value}")
        runner.log()
        try:
            run_workload(runner, config)
        except BaseException:
            runner.kill_all()
            raise
