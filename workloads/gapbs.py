from tracing.config import PURECAP_ARCH, RISCV64_ARCH
from tracing.workload import Workload, redirect_output

GAPBS_DIR = "/gapbs"
GRAPH_DIR = f"{GAPBS_DIR}/benchmark/graphs"
GRAPHS = ("twitter", "web", "road", "kron", "urand")

KERNEL_GRAPH_SUFFIX_AND_OPTIONS = {
    "bfs": (".sg", "-n64"),
    "pr": (".sg", "-i1000 -t1e-4 -n16"),
    "cc": (".sg", "-n16"),
    "bc": (".sg", "-i4 -n16"),
    "tc": ("U.sg", "-n3"),
    "sssp": (".wsg", "-n64"),
}
SSSP_DELTA_BY_GRAPH = {"road": 50000}
DEFAULT_SSSP_DELTA = 2

START_END_ADDRESSES = {
    RISCV64_ARCH: {
        "tc": (0x53848, None),
        "cc": (0x5435a, None),
        "bc": (0x54c24, None),
        "sssp": (0x52d12, None),
        "pr": (0x535d6, None),
        "bfs": (0x53ff6, None),
    },
    PURECAP_ARCH: {
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
        gapbs_group = parser.add_argument_group("GAPBS")
        gapbs_group.add_argument("--kernel", required=True, choices=sorted(KERNEL_GRAPH_SUFFIX_AND_OPTIONS))
        gapbs_group.add_argument("--graph", required=True, choices=GRAPHS)

    def display_name(self, args):
        return f"GAPBS kernel '{args.kernel}'"

    def trace_name(self, args):
        return f"{args.kernel}_{args.graph}"

    def simpoint_trace_prefix(self, args):
        return f"{args.kernel}.{args.graph}"

    def disk_image_suffix(self, args):
        return args.graph

    def start_end_addresses(self, args):
        return START_END_ADDRESSES[args.arch].get(args.kernel, (None, None))

    def guest_commands(self, args):
        graph_suffix, kernel_options = KERNEL_GRAPH_SUFFIX_AND_OPTIONS[args.kernel]
        command = f"{GAPBS_DIR}/{args.kernel} -f {GRAPH_DIR}/{args.graph}{graph_suffix} {kernel_options}"
        if args.kernel == "sssp":
            command += f" -d{SSSP_DELTA_BY_GRAPH.get(args.graph, DEFAULT_SSSP_DELTA)}"
        return [(None, redirect_output(command, self.trace_name(args)))]

    def info_fields(self, args):
        return {"Kernel": args.kernel, "Graph": args.graph}
