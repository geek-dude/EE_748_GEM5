#!/usr/bin/env python3
"""EE 748 batch driver, distributed under the repository LICENSE."""

import argparse
import shlex
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("benchmarks", nargs="*")
parser.add_argument("--jobs", type=int, default=1)
parser.add_argument("--mode", choices=["atomic", "kvm"], default="atomic")
parser.add_argument(
    "--benchmark-root", type=Path, default=REPO.parent / "benchmarks/CPU2006"
)
parser.add_argument(
    "--output-root", type=Path, default=REPO.parent / "gem5_out/baseline"
)
parser.add_argument("--warmup-insts", type=int, default=200_000_000)
parser.add_argument("--detailed-insts", type=int, default=50_000_000)
parser.add_argument("--dry-run", action="store_true")
args = parser.parse_args()
if min(args.jobs, args.warmup_insts, args.detailed_insts) < 1:
    parser.error(
        "jobs, warmup and detailed instruction counts must be positive"
    )
root = args.benchmark_root.resolve()
output = args.output_root.resolve()
# Replace each None with the instruction count derived from its SimPoints.
# None deliberately prevents launching with an unanswered assignment value.
specs = {
    "astar": ("473.astar", "astar", None),
    "bzip2": ("401.bzip2", "bzip2", None),
    "hmmer": ("456.hmmer", "hmmer", None),
    "lbm": ("470.lbm", "lbm", None),
    "mcf": ("429.mcf", "mcf", None),
    "milc": ("433.milc", "milc", None),
    "namd": ("444.namd", "namd", None),
    "sphinx": ("482.sphinx3", "sphinx_livepretend", None),
}
selected = args.benchmarks or list(specs)
if len(set(selected)) != len(selected):
    parser.error("Do not repeat benchmark names in a batch")
if set(selected) - specs.keys():
    parser.error("Unknown benchmark; choose: " + ", ".join(specs))
for name in selected:
    count = specs[name][2]
    if type(count) is not int or count < 0:
        parser.error(
            f"{name}: replace None in run_benchmarks.py with your "
            "nonnegative integer fast-forward count derived from SimPoints"
        )
    if args.mode == "kvm" and 0 < count <= 10_000_000:
        parser.error(
            f"{name}: positive KVM fast-forward counts must exceed "
            "10,000,000; consult the TAs or use --mode atomic"
        )


def run(name):
    folder, executable, fastforward = specs[name]
    bench = root / folder
    ref = bench / "data/ref/input"
    out = output / name
    cwd = out
    stdin = None
    if name == "astar":
        cwd = ref
        inputs = ["BigLakes2048.cfg"]
    elif name == "bzip2":
        inputs = [str(ref / "input.source")]
    elif name == "hmmer":
        inputs = [str(ref / "nph3.hmm"), str(ref / "swiss41")]
    elif name == "lbm":
        inputs = [
            "3000",
            str(out / "reference.dat"),
            "0",
            "0",
            str(ref / "100_100_130_ldc.of"),
        ]
    elif name == "mcf":
        inputs = [str(ref / "inp.in")]
    elif name == "milc":
        inputs = []
        stdin = ref / "su3imp.in"
    elif name == "namd":
        inputs = [
            "--input",
            str(bench / "data/all/input/namd.input"),
            "--iterations",
            "38",
        ]
    else:
        cwd = bench / "build/build_base_gcc44-64bit.0000"
        inputs = ["ctlfile", ".", "args.an4"]
    binary = bench / f"exe/{executable}_base.gcc44-64bit"
    config = (
        REPO
        / "configs/ee748"
        / ("se_kvm.py" if args.mode == "kvm" else "se.py")
    )
    command = [
        str(REPO / "build/X86/gem5.opt"),
        "-d",
        str(out),
        "--stats-file=stats.txt",
        str(config),
        "--fastforward-insts",
        str(fastforward),
        "--warmup-insts",
        str(args.warmup_insts),
        "--detailed-insts",
        str(args.detailed_insts),
        "--binary",
        str(binary),
    ]
    if stdin:
        command += ["--stdin-file", str(stdin)]
    if name == "namd":
        command += ["--input-file", str(out / "arguments.txt")]
    elif inputs:
        command += ["--inputs", *inputs]
    if args.dry_run:
        print(
            f"{name}: cd {shlex.quote(str(cwd))} && {shlex.join(command)}",
            flush=True,
        )
        if name == "namd":
            print("arguments.txt: " + shlex.join(inputs), flush=True)
        return 0
    if out.exists():
        print(
            f"{name}: output already exists: {out}; choose a new output root"
        )
        return 1
    if not binary.is_file() or not Path(command[0]).is_file():
        print(f"{name}: missing gem5 binary or benchmark: {binary}")
        return 1
    print(f"{name}: starting ({args.mode}); logs in {out}", flush=True)
    out.mkdir(parents=True)
    if name == "namd":
        (out / "arguments.txt").write_text(shlex.join(inputs) + "\n")
    try:
        with (out / "run.log").open("w") as log:
            result = subprocess.run(
                command,
                cwd=cwd,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=False,
            )
        (out / "exit-code.txt").write_text(str(result.returncode) + "\n")
        print(f"{name}: exit {result.returncode}; {out}", flush=True)
        return result.returncode
    except OSError as error:
        print(f"{name}: {error}", flush=True)
        return 1


with ThreadPoolExecutor(max_workers=args.jobs) as pool:
    statuses = list(pool.map(run, selected))
raise SystemExit(1 if any(statuses) else 0)
