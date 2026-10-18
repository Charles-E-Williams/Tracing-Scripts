from tracing.workload import Workload, redirect_output

XSBENCH_DIR = "/XSBench/openmp-threading"
SIZES = ("small", "large", "XL", "XXL")
GRIDS = ("unionized", "nuclide", "hash")
METHODS = ("history", "event")

ADDRESSES = {
    "riscv64": (0x2a7da, 0x43190),
    "riscv64-purecap": (0x3e0b0, 0x595c0),
}

OPTIONAL_FLAGS = {"particles": "-p", "hash_bins": "-h", "kernel_id": "-k"}


class XSBench(Workload):
    name = "xsbench"
    help = "XSBench (OpenMP threading)"

    def add_args(self, parser):
        g = parser.add_argument_group("XSBench")
        g.add_argument("--size", required=True, choices=SIZES, help="problem size (-s)")
        g.add_argument("--lookups", required=True, type=int,
                       help="XS lookups per particle history (-l)")
        g.add_argument("--grid", required=True, choices=GRIDS, help="grid search type (-G)")
        g.add_argument("--method", default="history", choices=METHODS,
                       help="simulation method (-m, default: history)")
        g.add_argument("--threads", type=int, default=1,
                       help="OpenMP threads (-t, default: 1)")
        g.add_argument("--particles", type=int, help="particle histories (-p)")
        g.add_argument("--hash-bins", type=int, help="hash bins (-h, --grid hash only)")
        g.add_argument("--kernel-id", type=int, help="optimized kernel ID (-k)")

    def validate(self, args, error):
        for dest in ("lookups", "threads", "particles", "hash_bins"):
            value = getattr(args, dest)
            if value is not None and value <= 0:
                error(f"--{dest.replace('_', '-')} must be a positive integer")
        if args.hash_bins is not None and args.grid != "hash":
            error("--hash-bins requires --grid hash")

    def tag(self, args):
        return f"{args.size}{args.lookups}{args.grid}"

    def label(self, args):
        return f"xs_{self.tag(args)}"

    def descriptor(self, args):
        return f"xs.{self.tag(args)}"

    def disk(self, args):
        return "xsbench"

    def addresses(self, args):
        return ADDRESSES[args.arch]

    def commands(self, args):
        parts = ["./XSBench", "-m", args.method, "-s", args.size,
                 "-l", str(args.lookups), "-G", args.grid, "-t", str(args.threads)]
        for dest, opt in OPTIONAL_FLAGS.items():
            value = getattr(args, dest)
            if value is not None:
                parts += [opt, str(value)]
        return [(XSBENCH_DIR, redirect_output(" ".join(parts), self.label(args)))]

    def info(self, args):
        fields = {"Workload": "XSBench", "Size": args.size, "Lookups": args.lookups,
                  "Grid": args.grid, "Method": args.method, "Threads": args.threads}
        for dest in OPTIONAL_FLAGS:
            value = getattr(args, dest)
            if value is not None:
                fields[dest.replace("_", " ").capitalize()] = value
        return fields
