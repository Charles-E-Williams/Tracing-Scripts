#!/usr/bin/env python3


XSBENCH_ADDRESSES = {
    "start": 0x2a7da,
    "end":   0x43190,
}

XSBENCH_PURECAP_ADDRESSES = {
    "start": 0x3e0b0,
    "end":   0x595c0,
}


VALID_SIZES   = ["small", "large", "XL", "XXL"]
VALID_GRIDS   = ["unionized", "nuclide", "hash"]
VALID_METHODS = ["history", "event"]

# In the guest, the rootfs is mounted at / so the binary lives here.
XSBENCH_DIR    = "/XSBench/openmp-threading"
XSBENCH_BINARY = "./XSBench"


def get_address_map(purecap):
    return XSBENCH_PURECAP_ADDRESSES if purecap else XSBENCH_ADDRESSES


def get_start_stop_addr(purecap):
    addrs = get_address_map(purecap)
    if addrs["start"] is None or addrs["end"] is None:
        variant = "purecap" if purecap else "non-purecap (riscv64)"
        raise RuntimeError(
            f"No XSBench start/end addresses defined for {variant}. "
            f"Populate xsbench_config.XSBENCH{'_PURECAP' if purecap else ''}"
            f"_ADDRESSES with the entry point and _exit address from the "
            f"corresponding binary."
        )
    return addrs["start"], addrs["end"]


def build_benchmark_command(size, lookups, grid, method="history",
                            threads=None, particles=None,
                            hash_bins=None, kernel_id=None):
    parts = [
        XSBENCH_BINARY,
        "-m", method,
        "-s", size,
        "-l", str(lookups),
        "-G", grid,
    ]
    if threads is not None:
        parts.extend(["-t", str(threads)])
    if particles is not None:
        parts.extend(["-p", str(particles)])
    if hash_bins is not None:
        parts.extend(["-h", str(hash_bins)])
    if kernel_id is not None:
        parts.extend(["-k", str(kernel_id)])
    return " ".join(parts)


def build_config_tag(size, lookups, grid):
    return f"{size}{lookups}{grid}"


def list_sizes():
    return list(VALID_SIZES)


def list_grids():
    return list(VALID_GRIDS)


def list_methods():
    return list(VALID_METHODS)