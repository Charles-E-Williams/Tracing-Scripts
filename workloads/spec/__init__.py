import importlib
import posixpath

from tracing.workload import AddressError, Workload

SUITES = ("2006", "2017", "2026")
INPUTS = ("test", "train", "ref")


class Run:
    def __init__(self, subdir, *commands):
        self.subdir = subdir
        self.commands = commands


class Benchmark:
    def __init__(self, descriptor, riscv64=None, purecap=None, **inputs):
        self.descriptor = descriptor
        self.addresses = {"riscv64": riscv64, "riscv64-purecap": purecap}
        self.inputs = inputs

    @property
    def root(self):
        return f"/speccpu/{self.descriptor[0]}xx/{self.descriptor}"

    def run(self, input_name):
        return self.inputs.get(input_name)

    def commands(self, input_name):
        run = self.run(input_name)
        cwd = posixpath.normpath(posixpath.join(self.root, run.subdir))
        return [(cwd, cmd) for cmd in run.commands]


def load_suite(suite):
    return importlib.import_module(f"{__name__}.cpu{suite}").BENCHMARKS


class Spec(Workload):
    name = "spec"
    help = "SPEC CPU 2006/2017/2026"

    def add_args(self, parser):
        g = parser.add_argument_group("SPEC")
        g.add_argument("--spec-suite", required=True, choices=SUITES)
        g.add_argument("--workload", required=True,
                       help="benchmark name (e.g. gcc, mcf, lbm)")
        g.add_argument("--input", required=True, choices=INPUTS, help="input size")

    def validate(self, args, error):
        suite = load_suite(args.spec_suite)
        bench = suite.get(args.workload)
        if bench is None:
            error(f"unknown benchmark '{args.workload}' in SPEC {args.spec_suite}. "
                  f"Available: {', '.join(sorted(suite))}")
        if bench.run(args.input) is None:
            error(f"no {args.input} commands for '{args.workload}' in SPEC {args.spec_suite}")
        args.benchmark = bench

    def label(self, args):
        return args.workload

    def output_name(self, args):
        return f"{args.workload}_{args.input}"

    def descriptor(self, args):
        return args.benchmark.descriptor

    def disk(self, args):
        return "speccpu"

    def addresses(self, args):
        addresses = args.benchmark.addresses[args.arch]
        if addresses is None:
            raise AddressError(f"no start/end addresses recorded for '{args.workload}' "
                               f"in SPEC {args.spec_suite} on {args.arch}")
        return addresses

    def commands(self, args):
        return args.benchmark.commands(args.input)

    def info(self, args):
        return {
            "Benchmark": args.workload,
            "Descriptor": args.benchmark.descriptor,
            "Input": args.input,
            "SPEC suite": args.spec_suite,
        }
