from enum import Enum

CHERI_ROOT = "/opt/cheri"
CHERIBUILD = "/opt/cheribuild/cheribuild.py"
BBV_PLUGIN = f"{CHERI_ROOT}/qemu/contrib/plugins/libbbv.so"
DEFAULT_OUTPUT_DIR = "/workspace/out"

RISCV64_ARCH = "riscv64"
PURECAP_ARCH = "riscv64-purecap"
ARCHS = (RISCV64_ARCH, PURECAP_ARCH)

NO_TRACE = "none"
TEXT_TRACE = "text"
TRACE_EXTENSIONS = {
    "cvtrace": ".bin",
    TEXT_TRACE: ".trace.txt",
    "champsim": ".champsimtrace",
    "champsimcheri": ".champsimcheritrace",
}
TRACE_FORMATS = (NO_TRACE, *TRACE_EXTENSIONS)

COMPRESSION_EXTENSIONS = {
    "xz": ".xz",
    "gzip": ".gz",
    "bzip2": ".bz2",
}

DEFAULT_BBV_INTERVAL = 100_000_000
MAX_TB_SIZE_MIB = 2048


class QtraceMode(str, Enum):
    USER = "user"
    SIMPOINT = "simpoint"
    BBV = "bbv"


class BbvMethod(str, Enum):
    INLINE = "inline instruction counting"
    PLUGIN = "plugin (deprecated)"


def disk_image_path(arch, image_suffix):
    return f"{CHERI_ROOT}/output/cheribsd-{arch}-{image_suffix}.img"
