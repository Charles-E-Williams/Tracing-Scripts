from tracing.config import PURECAP_ARCH, RISCV64_ARCH
from tracing.workload import Workload, option_name, redirect_output

XSBENCH_DIR = "/XSBench/openmp-threading"
SIZES = ("small", "large", "XL", "XXL")
GRIDS = ("unionized", "nuclide", "hash")
METHODS = ("history", "event")

START_END_ADDRESSES = {
    RISCV64_ARCH: (0x2a7da, 0x43190),
    PURECAP_ARCH: (0x3e0b0, 0x595c0),
}

OPTIONAL_XSBENCH_FLAGS = {"gridpoints": "-g", "particles": "-p", "hash_bins": "-h", "kernel_id": "-k"}
POSITIVE_ARGS = ("lookups", "threads", "gridpoints", "particles", "hash_bins")


class XSBench(Workload):
    name = "xsbench"
    help = "XSBench (OpenMP threading)"

    def add_args(self, parser):
        xsbench_group = parser.add_argument_group("XSBench")
        xsbench_group.add_argument("--size", required=True, choices=SIZES, help="problem size (-s)")
        xsbench_group.add_argument("--lookups", required=True, type=int, help="XS lookups per particle history (-l)")
        xsbench_group.add_argument("--grid", required=True, choices=GRIDS, help="grid search type (-G)")
        xsbench_group.add_argument("--method", default="history", choices=METHODS, help="simulation method (-m, default: history)")
        xsbench_group.add_argument("--threads", type=int, default=1, help="OpenMP threads (-t, default: 1)")
        xsbench_group.add_argument("--gridpoints", type=int, help="gridpoints per nuclide (-g, overrides the --size default)")
        xsbench_group.add_argument("--particles", type=int, help="particle histories (-p)")
        xsbench_group.add_argument("--hash-bins", type=int, help="hash bins (-h, --grid hash only)")
        xsbench_group.add_argument("--kernel-id", type=int, help="optimized kernel ID (-k)")

    def validate(self, args, report_error):
        for arg_name in POSITIVE_ARGS:
            value = getattr(args, arg_name)
            if value is not None and value <= 0:
                report_error(f"{option_name(arg_name)} must be a positive integer")
        if args.hash_bins is not None and args.grid != "hash":
            report_error("--hash-bins requires --grid hash")

    def display_name(self, args):
        return "XSBench"

    def config_tag(self, args):
        return f"{args.size}{args.lookups}{args.grid}"

    def trace_name(self, args):
        return f"xs_{self.config_tag(args)}"

    def simpoint_trace_prefix(self, args):
        return f"xs.{self.config_tag(args)}"

    def disk_image_suffix(self, args):
        return "xsbench"

    def start_end_addresses(self, args):
        return START_END_ADDRESSES[args.arch]

    def guest_commands(self, args):
        xsbench_args = ["./XSBench", "-m", args.method, "-s", args.size, "-l", str(args.lookups), "-G", args.grid, "-t", str(args.threads)]
        for arg_name, xsbench_flag in OPTIONAL_XSBENCH_FLAGS.items():
            value = getattr(args, arg_name)
            if value is not None:
                xsbench_args += [xsbench_flag, str(value)]
        command = redirect_output(" ".join(xsbench_args), self.trace_name(args))
        return [(XSBENCH_DIR, command)]

    def info_fields(self, args):
        fields = {"Workload": "XSBench", "Size": args.size, "Lookups": args.lookups, "Grid": args.grid, "Method": args.method, "Threads": args.threads}
        for arg_name in OPTIONAL_XSBENCH_FLAGS:
            value = getattr(args, arg_name)
            if value is not None:
                fields[arg_name.replace("_", " ").capitalize()] = value
        return fields
