CHERI_ROOT = "/opt/cheri"
CHERIBUILD = "/opt/cheribuild/cheribuild.py"
BBV_PLUGIN = f"{CHERI_ROOT}/qemu/contrib/plugins/libbbv.so"
DEFAULT_OUTPUT_DIR = "/workspace/out"

ARCHS = ("riscv64", "riscv64-purecap")
PURECAP = "riscv64-purecap"

COMPRESSION_ALGORITHMS = {
    "xz": ".xz",
    "gzip": ".gz",
    "bzip2": ".bz2",
}

TRACE_EXTENSIONS = {
    "cvtrace": ".bin",
    "champsim": ".champsimtrace",
    "champsimcheri": ".champsimcheritrace",
    "text": ".trace.txt",
}

DEFAULT_BBV_INTERVAL = 100_000_000
MAX_TB_SIZE = 2048


def disk_image(arch, suffix):
    return f"{CHERI_ROOT}/output/cheribsd-{arch}-{suffix}.img"
