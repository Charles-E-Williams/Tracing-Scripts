Scripts to produce ChampSim traces using CHERI QEMU.

https://github.com/Charles-E-Williams/qemu/tree/qemu-cheri

Requires Python 3.10+, `pexpect`, and cheribuild at `/opt/cheribuild` with its source root at `/opt/cheri`.

## Usage

```
./run.py --benchmark-suite speccpu --spec-suite 2017 --workload mcf --input ref --arch riscv64-purecap [options]
./run.py --benchmark-suite gapbs   --kernel bfs --graph road --arch riscv64-purecap [options]
./run.py --benchmark-suite xsbench --size small --lookups 15 --grid hash --arch riscv64 [options]
```

`./run.py --benchmark-suite <suite> --help` lists every option for that suite.

Common flows:

```
# 1. BBV profiling (writes <name>.bb.gz)
./run.py --benchmark-suite speccpu ... --bbv-profiling [--process-filter]

# 2. SimPoint traces (one compressed trace per simpoint; QEMU exits after the last one)
./run.py --benchmark-suite speccpu ... --trace-format champsimcheri --qtrace simpoint \
    --simpoints-file mcf.simpoints --simpoint-instructions 100000000 [--warmup-instructions N] [--process-filter]

# 3. Full trace of the benchmark's user-mode execution
./run.py --benchmark-suite speccpu ... --trace-format champsim --qtrace user [--compress]

# 4. Readable text dump for debugging
./run.py --benchmark-suite speccpu ... --trace-format text --qtrace user
```

## Arguments

### Benchmark selection

| Argument | Description |
|---|---|
| `--benchmark-suite {speccpu,gapbs,xsbench}` | **Required.** Suite to run. Decides which of the suite options below apply. |

**`speccpu`**

| Argument | Description |
|---|---|
| `--spec-suite {2006,2017,2026}` | **Required.** SPEC CPU version. |
| `--workload NAME` | **Required.** Benchmark short name, e.g. `gcc`, `mcf`, `lbm`. An unknown name prints the list for that suite. |
| `--input {test,train,ref}` | **Required.** Input size. SPEC 2026 has no `train` commands, and `gcc`/`llvm` in 2026 have no commands at all. |

**`gapbs`**

| Argument | Description |
|---|---|
| `--kernel {bc,bfs,cc,pr,sssp,tc}` | **Required.** GAPBS kernel. |
| `--graph {twitter,web,road,kron,urand}` | **Required.** Input graph. Also selects the disk image `cheribsd-<arch>-<graph>.img`. |

**`xsbench`**

| Argument | Description |
|---|---|
| `--size {small,large,XL,XXL}` | **Required.** Problem size (`-s`). |
| `--lookups N` | **Required.** Cross-section lookups per particle history (`-l`). Must be positive. |
| `--grid {unionized,nuclide,hash}` | **Required.** Grid search type (`-G`). |
| `--method {history,event}` | Simulation method (`-m`). Default `history`. |
| `--threads N` | OpenMP threads (`-t`). Default 1, which keeps tracing deterministic. |
| `--particles N` | Number of particle histories (`-p`). |
| `--hash-bins N` | Number of hash bins (`-h`). Only with `--grid hash`. |
| `--kernel-id N` | Optimized kernel ID (`-k`). |

### Target

| Argument | Description |
|---|---|
| `--arch {riscv64,riscv64-purecap}` | **Required.** Guest architecture. Selects the cheribuild target `run-dm-<arch>` and disk image. |
| `--trace-format {none,cvtrace,champsim,champsimcheri,text}` | Instruction trace format. Default `none` (no trace). `champsim` needs `--arch riscv64`; `champsimcheri` needs `--arch riscv64-purecap`. `text` writes a human-readable `.trace.txt`. |

### Trace options

| Argument | Description |
|---|---|
| `--qtrace {user,simpoint}` | Runs the benchmark under `qtrace`. `user` (`qtrace -u`) traces only the benchmark's user-mode instructions. `simpoint` (`qtrace -s`) is required with `--simpoints-file`. Needs a `--trace-format`. |
| `--compress` | Compresses a full (non-SimPoint) trace while it is written, through a FIFO. SimPoint traces are always compressed, and BBV output is always gzipped by QEMU, so it is rejected with `--bbv-profiling`/`--bbv`. |
| `--compression-algorithm {xz,gzip,bzip2}` | Compressor for `--compress` and SimPoint traces. Default `xz`. |
| `--xz-threads N` | Threads per xz compressor (`xz -TN`; 0 = one per core). Only with `xz`. Default: xz's own setting. |
| `--trace-perthread` | Sets `hw.qemu_trace_perthread=1`, which stops tracing while the benchmark's thread is preempted. Has no effect with `--process-filter`. |
| `--process-filter` | Counts, profiles and traces only the benchmark's process (`filter=process`). Use it for both the BBV run and the matching SimPoint run. Needs `--bbv-profiling`, `--bbv` or `--simpoints-file`; not supported with `--pc-simpoints`. |

### BBV profiling

BBV profiling and SimPoint tracing need the benchmark's start and end addresses. The run stops with an error if they aren't recorded (currently SPEC 2026 and GAPBS on `riscv64`).

| Argument | Description |
|---|---|
| `--bbv-profiling` | Collects basic block vectors with QEMU's inline instruction counting into `<name>.bb.gz`. Use with `--trace-format none`. |
| `--bbv` | Deprecated and slower: collects BBVs with the `libbbv.so` plugin. Cannot be combined with `--bbv-profiling`. |
| `--bbv-interval N` | Instructions per BBV interval. Default 100000000. |
| `--bbv-key {start,end,startend,all}` | The way QEMU keys basic blocks in the BBV (`bbvkey=`). Start PC, End PC, Start & End PC, or all at once. Only with `--bbv-profiling`. Default `end`. |

### SimPoint options

| Argument | Description |
|---|---|
| `--simpoints-file PATH` | Sorted SimPoints file; the last number on each non-comment line is the simpoint ID. Needs a `--trace-format`, `--qtrace simpoint` and `--simpoint-instructions`. Writes one compressed trace per simpoint, named `<prefix>-<id>B<ext>`. |
| `--simpoint-instructions N` | Instructions per SimPoint interval. Must match the BBV interval used to pick the simpoints. |
| `--warmup-instructions N` | Warmup instructions traced before each simpoint. Not with `--pc-simpoints`. |
| `--pc-simpoints` | Uses PC-based SimPoints instead of interval-based. |

### QEMU and guest options

| Argument | Description |
|---|---|
| `-o, --output-dir DIR` | Base output directory. Default `/workspace/out`. |
| `-v, --verbose` | Mirrors all QEMU console output to stdout. |
| `--ssh-port PORT` | SSH forwarding port for the guest. |
| `-m, --memory SIZE` | Guest memory, e.g. `24G`. |
| `--tb-size MIB` | TCG translation block cache size, 1 to 2048 MiB. |
| `--disable-aslr` | Disables ASLR in the guest (`kern.elf64.aslr.{enable,stack,shared_page,pie_enable}=0`). |
| `--disable-revocation` | Disables capability revocation (`security.cheri.runtime_revocation_default=0`). |
| `--icount` | Deterministic execution: `-icount shift=0,align=off,sleep=off -seed 123456789 -smp 1 -rtc base=utc,clock=vm`. |

## Output

Each run creates a new directory under `--output-dir`. A `_1`, `_2`, ... suffix is added if the name is taken.

| Suite | Directory | Full trace / BBV name | SimPoint trace prefix |
|---|---|---|---|
| speccpu | `<workload>_<input>` | `<workload>` | SPEC descriptor, e.g. `619.lbm_s` |
| gapbs | `<kernel>_<graph>` | `<kernel>_<graph>` | `<kernel>.<graph>` |
| xsbench | `xs_<size><lookups><grid>` | same as directory | `xs.<size><lookups><grid>` |

The directory contains `info.txt` (run settings and progress), `qemu.log` (the QEMU console), and the trace or `.bb.gz` file. Inside the guest, each benchmark command's stdout and stderr go to `.out` and `.err` files next to it.

## SPEC run scripts

Writes a `<benchmark>.<input>.sh` script per benchmark for running SPEC by hand inside CheriBSD:

```
python3 -m workloads.spec.gen_scripts OUT_DIR --spec-suite {2006,2017,2026} [--input {test,train,ref}]
```

`--input` defaults to `ref`.

## Layout

```
run.py                      entry point
tracing/
  cli.py                    shared options, validation and run pipeline
  qemu.py                   QEMU/CheriBSD session and trace compression
  config.py                 paths, constants and mode enums
  workload.py               interface implemented by each suite
workloads/
  gapbs.py
  xsbench.py
  spec/
    __init__.py             SPEC suite
    cpu2006.py ...          per-suite descriptors, start/end addresses and commands
    cpu2026_full.py         full SPEC 2026 command set, kept for reference (not used by run.py)
    gen_scripts.py
```

Adding a suite means subclassing `tracing.workload.Workload` and listing it in `workloads/__init__.py`.
