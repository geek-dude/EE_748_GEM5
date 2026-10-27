# EE 748 — Advanced Topics in Computer Architecture

Course gem5 repository derived from [geek-dude/gem5](https://github.com/geek-dude/gem5),
with its custom configurations and source extensions retained on official
**gem5 v26.0.0.0**. This is the candidate setup, not yet a validated course
release. Compilation, KVM, phase accounting, checkpoints and benchmark execution
will be validated in step 2. If v26 is unsuitable, the fallback candidate is
v25.1.0.1; see [maintainer instructions](docs/ee748/MAINTAINING.md).

The repository contains gem5 source and course scripts. Docker supplies build
dependencies. Benchmark binaries/inputs are distributed separately by the course;
they are not part of this repository. Initial setup needs Internet access.
Upstream licenses remain in [LICENSE](LICENSE); the original upstream overview
is preserved in [UPSTREAM_README.md](docs/ee748/UPSTREAM_README.md).

## Directory layout

```text
EE_748_gem5/                       # workspace, mounted into Docker
├── run-gem5-container.sh          # installed from the repo's template
├── benchmarks/                   # outside the Git repository
│   ├── CPU2006/                   # course-provided benchmark collection
│   └── gcc/                      # optional small teaching example
├── gem5_out/                     # simulation outputs, outside Git
└── gem5/                         # this repository
    ├── configs/ee748/
    │   ├── se.py
    │   ├── se_kvm.py
    │   ├── run_multiple_serial.sh
    │   ├── run_multiple_parallel.sh
    │   ├── run_benchmarks.py
    │   └── Checkpoint_Scripts/    # experimental examples
    ├── util/ee748/                # Docker setup and launcher template
    ├── docs/ee748/
    └── build/X86/gem5.opt         # generated after compilation
```

The host workspace maps to `/EE_748_gem5` inside the container. Paths written
into argument files must use the container's paths when running in Docker.
Keep all required inputs inside this workspace; host paths outside it are not
mounted. Source, builds and results persist after exiting the container.

## 1. Obtain the course repository

Install Git on the host first (`sudo apt install git` on Ubuntu), then clone
[the public course repository](https://github.com/geek-dude/EE_748_GEM5):

```bash
mkdir -p ~/EE_748_gem5
cd ~/EE_748_gem5
git clone --branch main https://github.com/geek-dude/EE_748_GEM5.git gem5
cd gem5
# Keep only official upstream as a named remote; updates are deliberate.
git remote remove origin
git remote add upstream https://github.com/gem5/gem5.git
git remote set-url --push upstream DISABLED
git config push.default nothing
```

The `main` branch is currently a setup candidate. Once a course snapshot is
validated, use the course tag provided by the TA in place of `main`.
Remote settings are local Git configuration: they are not inherited by a clone.
The personal repository is a provenance source, not a student update remote.

## 2. Install Docker on the host

**Ubuntu:** run this as your normal user, not with `sudo`:

```bash
bash util/ee748/step_1_setup-docker.sh
```

It installs Ubuntu's `docker.io` package if Docker is absent, starts the service,
and adds your user to the Docker group. `sudo` prompts for your password when
needed. A working existing Docker installation is left alone. Log out of the
whole desktop session and log back in if the script requests it, then check:

```bash
docker run --rm hello-world
```

Docker-group membership grants root-equivalent control of the host. This script
is for native Ubuntu with systemd. It does not install Distrobox, and no `newgrp`
subshell is required.

**Other Linux distributions:** install Docker through your distribution or
[Docker's Engine instructions](https://docs.docker.com/engine/install/), then
verify that `docker info` works without sudo. Skip the Ubuntu installer.

**Windows:** install [Docker Desktop with WSL 2](https://docs.docker.com/desktop/setup/install/windows-install/),
enable integration for your Ubuntu WSL distribution and use Linux containers.
Run the Git/setup/launcher commands from the WSL Bash terminal, keeping the
workspace in its Linux home directory. Skip the native Ubuntu Docker installer
when using Desktop integration.

**macOS:** install [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/)
and Git, start Desktop, then use Terminal/Bash for the same setup commands.
The launcher uses the native image architecture. An X86 gem5 build selects the
*simulated* ISA; it does not require emulating an amd64 container on an ARM host.
Non-KVM use on Windows/macOS/ARM is a portability target, pending validation.
For the course's x86 KVM fast-forwarding, use a suitable x86 Linux machine.
Docker standardizes userspace dependencies, not CPU virtualization capabilities.

## 3. Prepare and enter the container

From the cloned `gem5` directory, on the host:

```bash
bash util/ee748/step_2_setup-gem5-container.sh
cd ..
./run-gem5-container.sh
```

The setup script pulls the image named in `util/ee748/container.env`, creates
sibling benchmark/output directories and installs the launcher in the workspace.
Unlike the provisional Moodle installer, it uses your **already-cloned course
repository**, avoiding a second clone of the personal fork. It will not overwrite
a locally modified launcher. Compare it with the tracked template when upgrading.

Current dependency image: `ghcr.io/gem5/ubuntu-24.04_all-dependencies:v24-1`.
This carries forward the image chosen in the earlier setup discussion. Its tag
is independent of the gem5 source version; v26 compatibility and an immutable
image digest will be recorded after step 2. Do not substitute `latest` silently.

The container runs with your UID/GID and a writable home in the mounted
workspace. Exit with `exit`; `--rm` removes the container, not the mounted files.
For noninteractive commands, the launcher also accepts a command and arguments.

## 4. Compile gem5 inside the container

```bash
cd /EE_748_gem5/gem5
scons build/X86/gem5.opt -j2
```

Start with two build jobs on a laptop and increase only if RAM permits. CPU count
alone is not a safe build-job limit. The dependency image supplies the compiler,
Python and SCons; pulling the image does **not** compile or install gem5.
V26 requires Python 3.10+ and a C++20 compiler; see the
[official build guide](https://www.gem5.org/documentation/general_docs/building).

After building, inspect the course options:

```bash
./build/X86/gem5.opt configs/ee748/se.py --help
```

Rerun SCons after editing gem5 sources or its embedded Python library (`src/`).
Editing standalone `configs/ee748/*.py` does not ordinarily require rebuilding.
For an ordinary source update, incremental rebuilding is sufficient. For a major
release/toolchain change, move an existing build directory aside and build afresh
rather than deleting it. Do not mix host-native and container build artifacts.

## 5. Run a simulation

Place the course binaries and inputs in the sibling `benchmarks` directory.
This example assumes the optional GCC teaching files are available; it does not
download them. Run from `/EE_748_gem5/gem5`:

```bash
./build/X86/gem5.opt --outdir=../gem5_out/gcc-example \
  --stats-file=gcc_stats.txt configs/ee748/se.py \
  --fastforward-insts 1_000_000 \
  --warmup-insts 2_000_000 --detailed-insts 4_000_000 \
  --binary ../benchmarks/gcc/gcc_base.gcc41-64bit \
  --inputs ../benchmarks/gcc/166.in \
  --num-cores 1 --clk-freq 3GHz --mem-size 8GiB \
  --l1i-size 32KiB --l1d-size 32KiB --l2-size 256KiB \
  --l1i-assoc 8 --l1d-assoc 8 --l2-assoc 16
```

Copy the entire multiline command together. gem5's options precede the config
path; the configuration's options follow it. Use a new output directory for each
experiment: reusing one can overwrite stats and configuration files. Inspect
`config.ini`/`config.json` for the instantiated system and the selected stats file
for results. A process exiting successfully does not alone prove all requested
phases completed; check its log and instruction counts.

`--binary`, `--warmup-insts` and `--detailed-insts` are required. Fast-forward
defaults to zero. Other defaults are one core, 3 GHz, 8 GiB memory, 32 KiB L1I/L1D,
256 KiB L2, associativity 8/8/4, L1 tag/data/response latency 1/1/1 and L2
10/10/1. The full list is available through `--help`. Cache latency options use
`--l1i-tag-latency`, `--l1i-data-latency`, `--l1i-response-latency` and the
corresponding `l1d`/`l2` names.

These options are enabled by this fork's retained cache extensions. Last year's
exercise about uncommenting the options and exposing them in the hierarchy is
already completed here. The example above intentionally overrides L2
associativity to 16; omitting it retains the original hierarchy default of 4.

`se.py` uses ATOMIC fast-forward, TIMING warmup, then O3 detailed execution.
With zero fast-forward it starts in TIMING. Instruction limits are scheduled per
thread/core, not a total multicore work budget. Use the one-core baseline until
multicore phase accounting has been checked in step 2. Read the configuration
before adapting it to a new experiment; it is a teaching starting point.

### Arguments versus standard input

Use `--inputs` for ordinary positional arguments. For a workload with its own
options, use `--input-file` pointing to a text file containing its argument list:

```text
--input /EE_748_gem5/benchmarks/CPU2006/444.namd/data/all/input/namd.input --iterations 38
```

Pass that file as `--input-file ../benchmarks/CPU2006/444.namd/namd_inputs.txt`.
The file is parsed with shell-style quoting, without executing a shell. Variables,
`~`, pipes and redirection are not expanded. Relative arguments resolve against
the simulation's working directory, not the argument file's directory.

For workloads that read standard input (MILC, GAMESS), use `--stdin-file PATH`.
Do **not** pass `<` through `--inputs` or assume redirecting the gem5 host process
configures the simulated process. `--input-file` supplies argv; `--stdin-file`
supplies the simulated program's stdin.

## Optional x86 KVM fast-forwarding

`se_kvm.py` uses KVM, then a short ATOMIC correction phase, TIMING warmup and O3.
A positive fast-forward count must exceed 10,000,000 instructions because that
many are reserved for the ATOMIC correction. Use `se.py` for short runs. The
KVM script still needs KVM support even if fast-forward is zero.

On a suitable x86 Linux host, enable virtualization in firmware, ensure `/dev/kvm`
exists and grant your account read/write access (normally by joining the `kvm`
group and logging out/in). Follow [gem5's KVM guide](https://www.gem5.org/documentation/general_docs/using_kvm/).
If perf counters are denied by the host policy, the course's historical setting is:

```bash
# Host only; an administrator should apply this if needed, once per boot.
sudo sysctl kernel.perf_event_paranoid=1
```

Then enter from the host workspace:

```bash
./run-gem5-container.sh --kvm
```

This explicit opt-in exposes `/dev/kvm`, adds its numeric group and `PERFMON`, and
disables the container's default seccomp filter to permit perf calls. It does not
use `--privileged`; it is less isolated than the default container and is intended
for trusted course workloads. Kernel policy may still restrict perf. The launcher
does not change the host's sysctl. KVM/perf validation is deferred to step 2;
use the default launcher and `se.py` when KVM is unavailable. Docker Desktop
should not be assumed to expose compatible x86 KVM.

## Benchmarks, batch runs and checkpoints

See [BENCHMARKS.md](docs/ee748/BENCHMARKS.md) for consolidated Moodle workload
notes, input placement and working-directory requirements. These recipes are
provisional until tested on the supplied benchmark collection.

Inside the container, from the repo:

```bash
# Preview paths and commands without launching simulations or creating outputs:
bash configs/ee748/run_multiple_serial.sh --dry-run
# Run selected workloads sequentially:
bash configs/ee748/run_multiple_serial.sh bzip2 mcf
# Two concurrent jobs (tune to available CPU and RAM):
MAX_JOBS=2 bash configs/ee748/run_multiple_parallel.sh --mode kvm astar namd
```

The default mode is ATOMIC; historical instruction budgets can make it very slow.
Use KVM only in the KVM-enabled container. Each benchmark gets its own directory,
`run.log`, `stats.txt`, config files and `exit-code.txt`. Any failed child makes
the batch return nonzero. Existing output directories are refused; select a fresh
`--output-root ../gem5_out/experiment-name`. `--benchmark-root` overrides the
CPU2006 location. Leave CPU and memory headroom when choosing `MAX_JOBS`.

`configs/ee748/Checkpoint_Scripts` preserves the personal fork's experimental
checkpoint examples. Run from the repository root and adapt their GCC paths and
counts. They need a separate correctness review, including checkpoint restoration
and instruction-stop APIs; they are not the recommended baseline workflow.

## Generate source documentation

Inside the container:

```bash
cd /EE_748_gem5/gem5/src
doxygen
```

Open `gem5/src/doxygen/html/index.html` from the host workspace in a browser.
This documents the checked-out source. Generated output is not course source.

## Course maintenance

Only the TA updates the upstream baseline. Students should keep the course
revision fixed during assignments. See [MAINTAINING.md](docs/ee748/MAINTAINING.md)
for publication without an `origin` remote, annual upgrades, fallback, and the
step-2 validation checklist. See [PROVENANCE.md](docs/ee748/PROVENANCE.md) for the
source material and changes made while preparing this repository.
