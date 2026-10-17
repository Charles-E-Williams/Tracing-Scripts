#!/usr/bin/env python3

COMPRESSION_ALGORITHMS = {
    "xz":    {"ext": ".xz",  "cmd": "xz"},
    "gzip":  {"ext": ".gz",  "cmd": "gzip"},
    "bzip2": {"ext": ".bz2", "cmd": "bzip2"},
}

TRACE_EXTENSIONS = {
    "cvtrace":       ".bin",
    "champsim":      ".champsimtrace",
    "champsimcheri": ".champsimcheritrace",
    "text":          ".trace.txt",
}

DEFAULT_BBV_INTERVAL = 100_000_000