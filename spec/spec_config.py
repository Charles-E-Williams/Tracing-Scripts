#!/usr/bin/env python3

SPEC_2006_ADDRESSES = {
    "perlbench":   {"start": 0x8890c,  "end": 0x12c530},
    "bzip2":       {"start": 0x2b10e,  "end": 0x4adb0},
    "gcc":         {"start": 0x116a1c, "end": 0x319ef0},
    "mcf":         {"start": 0x2a0bc,  "end": 0x424e0},
    "milc":        {"start": 0x2ecd6,  "end": 0x5fac0},
    "namd":        {"start": 0x5e92e,  "end": 0x86100},
    "gobmk":       {"start": 0x14b088, "end": 0x198b50},
    "dealII":      {"start": 0x29d7f0, "end": 0x371f40},
    "soplex":      {"start": 0x6328c,  "end": 0x1028b0},
    "povray":      {"start": 0xd65bc,  "end": 0x1308a0},
    "hmmer":       {"start": 0x446be,  "end": 0x7e730},
    "sjeng":       {"start": 0x43f04,  "end": 0x5ff60},
    "libquantum":  {"start": 0x30290,  "end": 0x47270},
    "h264ref":     {"start": 0x68e0e,  "end": 0xd3b50},
    "lbm":         {"start": 0x2b57c,  "end": 0x425d0},
    "omnetpp":     {"start": 0xbbc5e,  "end": 0x151950},
    "astar":       {"start": 0x37362,  "end": 0x5e4a0},
    "sphinx3":     {"start": 0x33a46,  "end": 0x66ab0},
    "xalancbmk":   {"start": 0x3ba7e4, "end": 0x42c710},
}

SPEC_2006_PURECAP_ADDRESSES = {
    "perlbench":   {"start": 0xd3716,  "end": 0x1851d0},
    "bzip2":       {"start": 0x3e786,  "end": 0x62710},
    "gcc":         {"start": 0x1bcce4, "end": 0x3f75d0},
    "mcf":         {"start": 0x3ceb0,  "end": 0x5bd80},
    "milc":        {"start": 0x462a8,  "end": 0x849b0},
    "namd":        {"start": 0x85ac6,  "end": 0xb6ab0},
    "gobmk":       {"start": 0x24f4e6, "end": 0x2ad6f0},
    "dealII":      {"start": 0x396622, "end": 0x491080},
    "soplex":      {"start": 0xa63bc,  "end": 0x161340},
    "povray":      {"start": 0x121a7a, "end": 0x18c2a0},
    "hmmer":       {"start": 0x64e00,  "end": 0xac980},
    "sjeng":       {"start": 0x5cf36,  "end": 0x7fb40},
    "libquantum":  {"start": 0x43a1a,  "end": 0x5d000},
    "h264ref":     {"start": 0x8f1aa,  "end": 0x1157a0},
    "lbm":         {"start": 0x3e97c,  "end": 0x5c020},
    "omnetpp":     {"start": 0x1375f2, "end": 0x1e7020},
    "astar":       {"start": 0x5481c,  "end": 0x85520},
    "sphinx3":     {"start": 0x52968,  "end": 0x8b6b0},
    "xalancbmk":   {"start": 0x52b32a, "end": 0x5b1f90},
}

SPEC_2017_ADDRESSES = {
    "perlbench":   {"start": 0xef310,  "end": 0x21b0a0},
    "gcc":         {"start": 0x20c636, "end": 0x81dd40},
    "mcf":         {"start": 0x2a148,  "end": 0x44030},
    "lbm":         {"start": 0x2bc6a,  "end": 0x42cc0},
    "omnetpp":     {"start": 0x14eb66, "end": 0x28dac0},
    "xalancbmk":   {"start": 0x3b7f84, "end": 0x48cb60},
    "x264":        {"start": 0x9edc0,  "end": 0xbc7d0},
    "deepsjeng":   {"start": 0x38d1c,  "end": 0x528f0},
    "imagick":     {"start": 0x163958, "end": 0x2033e0},
    "leela":       {"start": 0x5bd20,  "end": 0xe8430},
    "nab":         {"start": 0x30c04,  "end": 0x6f620},
    "xz":          {"start": 0x36696,  "end": 0x63ed0},
}

SPEC_2017_PURECAP_ADDRESSES = {
    "perlbench":   {"start": 0x150a80, "end": 0x296200},
    "gcc":         {"start": 0x372728, "end": 0xa229c0},
    "mcf":         {"start": 0x3d03a,  "end": 0x5e0b0},
    "lbm":         {"start": 0x3f2d2,  "end": 0x5c980},
    "omnetpp":     {"start": 0x2454ca, "end": 0x3abfe0},
    "xalancbmk":   {"start": 0x52b18a, "end": 0x623d20},
    "x264":        {"start": 0xcb450,  "end": 0xef110},
    "deepsjeng":   {"start": 0x4e9d0,  "end": 0x6f1b0},
    "imagick":     {"start": 0x1d47b4, "end": 0x27f510},
    "leela":       {"start": 0x92f7a,  "end": 0x136c30},
    "nab":         {"start": 0x4a7b6,  "end": 0x94080},
    "xz":          {"start": 0x4d3d8,  "end": 0x806e0},
}


SPEC_2026_ADDRESSES = {
}

SPEC_2026_PURECAP_ADDRESSES = {
    "xz":          {"start": 0x738f0,  "end": 0xe4400},
    "sph_exa":     {"start": 0x86330,  "end": 0x10e980},
    "ntest":       {"start": 0xdb550,  "end": 0x1691a0},
    "cactus":      {"start": 0x1473e4, "end": 0x39bda0},
    "tealeaf":     {"start": 0x3fcba,  "end": 0x63a80},
    "nab":         {"start": 0x4abce,  "end": 0x94270},
    "flac":        {"start": 0xb8998,  "end": 0x115ad0},
    "cppcheck":    {"start": 0x244930, "end": 0x5f3cb0},
    "abc":         {"start": 0x53d91e, "end": 0xc84c00},
    "vpr":         {"start": 0x23c450, "end": 0x6359f0},
    "gem5":        {"start": 0x92470,  "end": 0x12e540},
    "diamond":     {"start": 0x3ae1ce, "end": 0x4f8930},
    "minizinc":    {"start": 0xe9b968, "end": 0xf93a60},
    "ns3":         {"start": 0x9e9980, "end": 0x1609930},
    "graph500":    {"start": 0x748f8,  "end": 0x93bd0},
    "namd":        {"start": 0x7ef52,  "end": 0xafe70},
    "nest":        {"start": 0x334b10, "end": 0x7e0b10},
    "marian":      {"start": 0x32ae3c,  "end": 0x7f4410},
    "neutron":     {"start": 0x4a60a,  "end": 0x625a0},
}

SPEC_2006_SUITE = {
    "perlbench":   "400.perlbench",
    "bzip2":       "401.bzip2",
    "gcc":         "403.gcc",
    "mcf":         "429.mcf",
    "milc":        "433.milc",
    "namd":        "444.namd",
    "gobmk":       "445.gobmk",
    "dealII":      "447.dealII",
    "soplex":      "450.soplex",
    "povray":      "453.povray",
    "hmmer":       "456.hmmer",
    "sjeng":       "458.sjeng",
    "libquantum":  "462.libquantum",
    "h264ref":     "464.h264ref",
    "lbm":         "470.lbm",
    "omnetpp":     "471.omnetpp",
    "astar":       "473.astar",
    "sphinx3":     "482.sphinx3",
    "xalancbmk":   "483.xalancbmk",
}

SPEC_2017_SUITE = {
    "perlbench":   "600.perlbench_s",
    "gcc":         "602.gcc_s",
    "mcf":         "605.mcf_s",
    "lbm":         "619.lbm_s",
    "omnetpp":     "620.omnetpp_s",
    "xalancbmk":   "623.xalancbmk_s",
    "x264":        "625.x264_s",
    "deepsjeng":   "631.deepsjeng_s",
    "imagick":     "638.imagick_s",
    "leela":       "641.leela_s",
    "nab":         "644.nab_s",
    "xz":          "657.xz_s",
}

SPEC_2026_SUITE = {
    "xz":          "801.xz_s",
    "sph_exa":     "803.sph_exa_s",
    "ntest":       "807.ntest_s",
    "cactus":      "809.cactus_s",
    "tealeaf":     "811.tealeaf_s",
    "nab":         "816.nab_s",
    "flac":        "817.flac_s",
    "gcc":         "821.gcc_s",
    "llvm":        "823.llvm_s",
    "cppcheck":    "827.cppcheck_s",
    "abc":         "829.abc_s",
    "vpr":         "834.vpr_s",
    "gem5":        "835.gem5_s",
    "diamond":     "838.diamond_s",
    "minizinc":    "846.minizinc_s",
    "ns3":         "853.ns3_s",
    "graph500":    "854.graph500_s",
    "namd":        "857.namd_s",
    "nest":        "867.nest_s",
    "marian":      "872.marian_s",
    "neutron":     "881.neutron_s",
}

SUPPORTED_SUITES = ("2006", "2017", "2026")


def _check_suite(spec_suite):
    if spec_suite not in SUPPORTED_SUITES:
        raise RuntimeError(
            f"Unknown SPEC suite: {spec_suite}. "
            f"Supported: {', '.join(SUPPORTED_SUITES)}"
        )


def get_suite_map(spec_suite):
    _check_suite(spec_suite)
    table = {
        "2006": SPEC_2006_SUITE,
        "2017": SPEC_2017_SUITE,
        "2026": SPEC_2026_SUITE,
    }
    return table[spec_suite]


def get_address_map(spec_suite, purecap):
    _check_suite(spec_suite)
    table = {
        ("2006", False): SPEC_2006_ADDRESSES,
        ("2006", True):  SPEC_2006_PURECAP_ADDRESSES,
        ("2017", False): SPEC_2017_ADDRESSES,
        ("2017", True):  SPEC_2017_PURECAP_ADDRESSES,
        ("2026", False): SPEC_2026_ADDRESSES,
        ("2026", True):  SPEC_2026_PURECAP_ADDRESSES,
    }
    return table[(spec_suite, purecap)]


def get_benchmark_descriptor(benchmark_name, spec_suite):
    suite = get_suite_map(spec_suite)
    if benchmark_name not in suite:
        available = ", ".join(sorted(suite.keys()))
        raise RuntimeError(
            f"No descriptor for '{benchmark_name}' in SPEC {spec_suite}. "
            f"Available: {available}"
        )
    return suite[benchmark_name]


def has_start_stop_addr(benchmark_name, purecap, spec_suite):
    return benchmark_name in get_address_map(spec_suite, purecap)


def describe_missing_addresses(benchmark_name, purecap, spec_suite):
    arch = "riscv64-purecap" if purecap else "riscv64"
    addresses = get_address_map(spec_suite, purecap)
    if not addresses:
        return (
            f"No start/end addresses have been recorded for SPEC "
            f"{spec_suite} on {arch} yet"
        )
    if benchmark_name in get_suite_map(spec_suite):
        return (
            f"No start/end addresses recorded for '{benchmark_name}' in "
            f"SPEC {spec_suite} on {arch} (symbols not found or not yet "
            f"measured)"
        )
    available = ", ".join(sorted(addresses.keys()))
    return (
        f"No addresses for '{benchmark_name}' in SPEC {spec_suite} "
        f"({arch}). Available: {available}"
    )


def get_start_stop_addr(benchmark_name, purecap, spec_suite):
    addresses = get_address_map(spec_suite, purecap)
    if benchmark_name not in addresses:
        raise RuntimeError(
            describe_missing_addresses(benchmark_name, purecap, spec_suite)
        )
    entry = addresses[benchmark_name]
    return entry["start"], entry["end"]


def list_benchmarks(spec_suite):
    return sorted(get_suite_map(spec_suite).keys())


def import_spec_commands(spec_suite):
    if spec_suite == "2006":
        import spec.spec06_commands as mod
    elif spec_suite == "2017":
        import spec.spec17_commands as mod
    elif spec_suite == "2026":
        import spec.spec26_commands as mod
    else:
        raise RuntimeError(f"Unknown SPEC suite: {spec_suite}")
    return mod