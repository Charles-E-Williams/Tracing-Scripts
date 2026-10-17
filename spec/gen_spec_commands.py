#!/usr/bin/env python3

import spec_commands_subset as SPEC
import spec_commands_purecap_subset as SPEC_pc
import os
import os.path
import argparse


def write_benchmark_script(output_dir, output_name, benchmark_variant):
	output_path = os.path.join(output_dir, output_name)
	# NOTE using an opener of os.open with a umask of 022 yields execute permissions on the generated files
	with open(output_path, "w", opener=os.open) as output_file:
		output_file.write("#!/bin/sh\n")
		output_file.write("set -ex\n")
		for command in benchmark_variant.setup + benchmark_variant.execution:
			output_file.write(f"{command}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates SPEC2006 benchmark scripts for running within cheribsd.")
    parser.add_argument("output_dir", type=str, metavar="path", help="Output directory path")
    parser.add_argument("-c", "--capability", action="store_true", dest="capability_enabled",
        help="Use SPEC_pc.benchmarks instead of SPEC.benchmarks")
    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        raise RuntimeError(f"Output directory path not valid: '{args.output_dir}'")

    # Select the appropriate benchmark module based on capability flag
    benchmark_module = SPEC_pc if args.capability_enabled else SPEC
    
    os.umask(0o022) # NOTE this is likely the default already, but setting to be sure
    for benchmark_name in benchmark_module.benchmarks:
        benchmark = benchmark_module.benchmarks[benchmark_name]
        # write_benchmark_script(args.output_dir, f"{benchmark_name}.test.sh", benchmark.test)
        # write_benchmark_script(args.output_dir, f"{benchmark_name}.train.sh", benchmark.train)
        write_benchmark_script(args.output_dir, f"{benchmark_name}.ref.sh", benchmark.ref)