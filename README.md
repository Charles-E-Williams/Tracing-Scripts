Scripts to produce ChampSim traces using CHERI QEMU.

https://github.com/Charles-E-Williams/qemu/tree/qemu-cheri

## Usage

```
./run.py spec    --spec-suite 2017 --workload mcf --input ref --arch riscv64-purecap [options]
./run.py gapbs   --kernel bfs --graph road --arch riscv64-purecap [options]
./run.py xsbench --size small --lookups 15 --grid hash --arch riscv64 [options]
```

`./run.py <workload> --help` lists all options. Common flows:

```
# BBV profiling
./run.py spec ... --bbv-profiling [--process-filter]

# SimPoint traces (one compressed trace per simpoint)
./run.py spec ... --trace-format champsimcheri --qtrace simpoint \
    --simpoints-file mcf.simpoints --simpoint-instructions 100000000 [--warmup-instructions N]

# Full trace
./run.py spec ... --trace-format champsim --qtrace user --compress
```

Generate standalone SPEC run scripts for the guest:

```
python3 -m workloads.spec.gen_scripts OUT_DIR --spec-suite 2006 --input ref
```

## Layout

```
run.py                  entry point
tracing/
  cli.py                shared options, validation and run pipeline
  qemu.py               QEMU/CheriBSD session and trace compression
  config.py             paths and constants
  workload.py           interface implemented by each workload
workloads/
  gapbs.py
  xsbench.py
  spec/
    __init__.py         SPEC workload
    cpu2006.py ...      per-suite descriptors, start/end addresses and commands
    gen_scripts.py
```

Adding a workload means subclassing `tracing.workload.Workload` and listing it in `workloads/__init__.py`.
