import argparse
import os

from workloads.spec import INPUT_SIZES, SUITES, load_suite_benchmarks


def write_script(script_path, guest_commands):
    lines = ["#!/bin/sh", "set -ex"]
    current_dir = None
    for working_dir, command in guest_commands:
        if working_dir != current_dir:
            lines.append(f"cd {working_dir}")
            current_dir = working_dir
        lines.append(command)
    with open(script_path, "w") as script_file:
        script_file.write("\n".join(lines) + "\n")
    os.chmod(script_path, 0o755)


def main():
    parser = argparse.ArgumentParser(description="Write <benchmark>.<input>.sh scripts to run SPEC inside CheriBSD")
    parser.add_argument("output_dir")
    parser.add_argument("--spec-suite", required=True, choices=SUITES)
    parser.add_argument("--input", default="ref", choices=INPUT_SIZES)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    for benchmark_name, benchmark in load_suite_benchmarks(args.spec_suite).items():
        if benchmark.run_for_input(args.input):
            script_path = os.path.join(args.output_dir, f"{benchmark_name}.{args.input}.sh")
            write_script(script_path, benchmark.guest_commands(args.input))


if __name__ == "__main__":
    main()
