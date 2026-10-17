#!/usr/bin/env python3

GRAPH_DIR = "/gapbs/benchmark/graphs"

GAPBS_ADDRESSES = {
    "tc":   {"start": 0x53848},
    "cc":   {"start": 0x5435a},
    "bc":   {"start": 0x54c24},
    "sssp": {"start": 0x52d12},
    "pr":   {"start": 0x535d6},
    "bfs":  {"start": 0x53ff6},
}

GAPBS_PURECAP_ADDRESSES = {
    "tc":   {"start": 0x886ee, "end": 0x11f7c0},
    "cc":   {"start": 0x896c4, "end": 0x121300},
    "bc":   {"start": 0x8a062, "end": 0x1215e0},
    "sssp": {"start": 0x87dec, "end": 0x114980},
    "pr":   {"start": 0x884a4, "end": 0x11f940},
    "bfs":  {"start": 0x89132, "end": 0x11f340},
}

BENCHMARK_COMMANDS = {
    "bfs": {
        "executable": "/gapbs/bfs",
        "args": ["-f", "{input_file}", "-n64"],
        "input_extension": ".sg",
    },
    "pr": {
        "executable": "/gapbs/pr",
        "args": ["-f", "{input_file}", "-i1000", "-t1e-4", "-n16"],
        "input_extension": ".sg",
    },
    "cc": {
        "executable": "/gapbs/cc",
        "args": ["-f", "{input_file}", "-n16"],
        "input_extension": ".sg",
    },
    "bc": {
        "executable": "/gapbs/bc",
        "args": ["-f", "{input_file}", "-i4", "-n16"],
        "input_extension": ".sg",
    },
    "tc": {
        "executable": "/gapbs/tc",
        "args": ["-f", "{input_file}", "-n3"],
        "input_extension": "U.sg",
    },
    "sssp": {
        "executable": "/gapbs/sssp",
        "args": ["-f", "{input_file}", "-n64"],
        "input_extension": ".wsg",
        "graph_specific_args": {
            "twitter": ["-d2"],
            "web":     ["-d2"],
            "road":    ["-d50000"],
            "kron":    ["-d2"],
            "urand":   ["-d2"],
        },
    },
}

GRAPHS = ["twitter", "web", "road", "kron", "urand"]


def get_address_map(purecap):
    if purecap:
        return GAPBS_PURECAP_ADDRESSES
    return GAPBS_ADDRESSES


def get_start_stop_addr(kernel, purecap):
    addresses = get_address_map(purecap)
    if kernel not in addresses:
        available = ", ".join(sorted(addresses.keys()))
        raise RuntimeError(
            f"No addresses for kernel '{kernel}' (purecap={purecap}). "
            f"Available: {available}"
        )
    entry = addresses[kernel]
    return entry["start"], entry["end"]


def list_kernels():
    return sorted(BENCHMARK_COMMANDS.keys())


def list_graphs():
    return list(GRAPHS)


def build_benchmark_command(kernel, graph):
    """Build the shell command string for a GAPBS benchmark."""
    if kernel not in BENCHMARK_COMMANDS:
        available = ", ".join(sorted(BENCHMARK_COMMANDS.keys()))
        raise RuntimeError(
            f"Unknown kernel '{kernel}'. Available: {available}"
        )

    config = BENCHMARK_COMMANDS[kernel]
    input_file = f"{GRAPH_DIR}/{graph}{config['input_extension']}"
    parts = [config["executable"]]

    args = list(config["args"])
    if kernel == "sssp" and graph in config.get("graph_specific_args", {}):
        args.extend(config["graph_specific_args"][graph])

    parts.extend(
        arg.replace("{input_file}", input_file) for arg in args
    )
    return " ".join(parts)