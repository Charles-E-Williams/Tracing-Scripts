import argparse
import os

from workloads.spec import INPUTS, SUITES, load_suite


def write_script(path, commands):
    lines = ["#!/bin/sh", "set -ex"]
    cwd = None
    for working_dir, cmd in commands:
        if working_dir != cwd:
            lines.append(f"cd {working_dir}")
            cwd = working_dir
        lines.append(cmd)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    os.chmod(path, 0o755)


def main():
    parser = argparse.ArgumentParser(
        description="Write <benchmark>.<input>.sh scripts to run SPEC inside CheriBSD")
    parser.add_argument("output_dir")
    parser.add_argument("--spec-suite", required=True, choices=SUITES)
    parser.add_argument("--input", default="ref", choices=INPUTS)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    for name, bench in load_suite(args.spec_suite).items():
        if bench.run(args.input):
            write_script(os.path.join(args.output_dir, f"{name}.{args.input}.sh"),
                         bench.commands(args.input))


if __name__ == "__main__":
    main()
