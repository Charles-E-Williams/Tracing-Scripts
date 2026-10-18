import importlib
import posixpath

from tracing.config import PURECAP_ARCH, RISCV64_ARCH
from tracing.workload import Workload

SUITES = ("2006", "2017", "2026")
INPUT_SIZES = ("test", "train", "ref")


class Run:
    def __init__(self, subdir, *commands):
        self.subdir = subdir
        self.commands = commands


class Benchmark:
    def __init__(self, descriptor, riscv64=None, purecap=None, test=None, train=None, ref=None):
        self.descriptor = descriptor
        self.start_end_addresses = {RISCV64_ARCH: riscv64, PURECAP_ARCH: purecap}
        self.runs_by_input = {"test": test, "train": train, "ref": ref}

    @property
    def root_dir(self):
        return f"/speccpu/{self.descriptor[0]}xx/{self.descriptor}"

    def run_for_input(self, input_size):
        return self.runs_by_input[input_size]

    def guest_commands(self, input_size):
        run = self.run_for_input(input_size)
        working_dir = posixpath.normpath(posixpath.join(self.root_dir, run.subdir))
        return [(working_dir, command) for command in run.commands]


def load_suite_benchmarks(suite):
    return importlib.import_module(f"{__name__}.cpu{suite}").BENCHMARKS


def selected_benchmark(args):
    return load_suite_benchmarks(args.spec_suite).get(args.workload)


class Spec(Workload):
    name = "speccpu"
    help = "SPEC CPU 2006/2017/2026"

    def add_args(self, parser):
        spec_group = parser.add_argument_group("SPEC")
        spec_group.add_argument("--spec-suite", required=True, choices=SUITES)
        spec_group.add_argument("--workload", required=True, help="benchmark name (e.g. gcc, mcf, lbm)")
        spec_group.add_argument("--input", required=True, choices=INPUT_SIZES, help="input size")

    def validate(self, args, report_error):
        benchmark = selected_benchmark(args)
        if benchmark is None:
            available = ", ".join(sorted(load_suite_benchmarks(args.spec_suite)))
            report_error(f"unknown benchmark '{args.workload}' in SPEC {args.spec_suite}. Available: {available}")
        if benchmark.run_for_input(args.input) is None:
            report_error(f"no {args.input} commands for {self.display_name(args)}")

    def display_name(self, args):
        return f"'{args.workload}' in SPEC {args.spec_suite}"

    def trace_name(self, args):
        return args.workload

    def output_dir_name(self, args):
        return f"{args.workload}_{args.input}"

    def simpoint_trace_prefix(self, args):
        return selected_benchmark(args).descriptor

    def disk_image_suffix(self, args):
        return "speccpu"

    def start_end_addresses(self, args):
        return selected_benchmark(args).start_end_addresses[args.arch] or (None, None)

    def guest_commands(self, args):
        return selected_benchmark(args).guest_commands(args.input)

    def info_fields(self, args):
        return {
            "Benchmark": args.workload,
            "Descriptor": selected_benchmark(args).descriptor,
            "Input": args.input,
            "SPEC suite": args.spec_suite,
        }
