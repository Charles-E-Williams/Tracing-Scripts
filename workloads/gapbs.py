from tracing.workload import AddressError, Workload, redirect_output

GAPBS_DIR = "/gapbs"
GRAPH_DIR = f"{GAPBS_DIR}/benchmark/graphs"
GRAPHS = ("twitter", "web", "road", "kron", "urand")

KERNELS = {
    "bfs": (".sg", "-n64"),
    "pr": (".sg", "-i1000 -t1e-4 -n16"),
    "cc": (".sg", "-n16"),
    "bc": (".sg", "-i4 -n16"),
    "tc": ("U.sg", "-n3"),
    "sssp": (".wsg", "-n64"),
}
SSSP_DELTA = {"road": 50000}

ADDRESSES = {
    "riscv64": {
        "tc": (0x53848, None),
        "cc": (0x5435a, None),
        "bc": (0x54c24, None),
        "sssp": (0x52d12, None),
        "pr": (0x535d6, None),
        "bfs": (0x53ff6, None),
    },
    "riscv64-purecap": {
        "tc": (0x886ee, 0x11f7c0),
        "cc": (0x896c4, 0x121300),
        "bc": (0x8a062, 0x1215e0),
        "sssp": (0x87dec, 0x114980),
        "pr": (0x884a4, 0x11f940),
        "bfs": (0x89132, 0x11f340),
    },
}


class Gapbs(Workload):
    name = "gapbs"
    help = "GAP Benchmark Suite"

    def add_args(self, parser):
        g = parser.add_argument_group("GAPBS")
        g.add_argument("--kernel", required=True, choices=sorted(KERNELS))
        g.add_argument("--graph", required=True, choices=GRAPHS)

    def label(self, args):
        return f"{args.kernel}_{args.graph}"

    def descriptor(self, args):
        return f"{args.kernel}.{args.graph}"

    def disk(self, args):
        return args.graph

    def addresses(self, args):
        start, end = ADDRESSES[args.arch].get(args.kernel, (None, None))
        if start is None or end is None:
            raise AddressError(f"no start/end addresses recorded for kernel "
                               f"'{args.kernel}' on {args.arch}")
        return start, end

    def commands(self, args):
        ext, opts = KERNELS[args.kernel]
        cmd = f"{GAPBS_DIR}/{args.kernel} -f {GRAPH_DIR}/{args.graph}{ext} {opts}"
        if args.kernel == "sssp":
            cmd += f" -d{SSSP_DELTA.get(args.graph, 2)}"
        return [(None, redirect_output(cmd, self.label(args)))]

    def info(self, args):
        return {"Kernel": args.kernel, "Graph": args.graph}
