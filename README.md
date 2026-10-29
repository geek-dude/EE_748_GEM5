# EE 748 — Advanced Topics in Computer Architecture

This repository provides **gem5 v26.0.0.0**, course simulation configurations,
and a Docker workflow. The instructor has confirmed successful completion of
the eight-benchmark KVM batch. Benchmark distribution instructions and a final
validation run are still pending before student release.

Benchmark binaries and inputs are supplied separately by the course. Keep them
and simulation results outside Git. Initial setup needs Internet access.

## 1. Make your team's private copy

Install Git first (`sudo apt install git` on Ubuntu). On GitHub, create an
**empty private repository** named `EE_748_2026_Team_ID_GEM5`, replacing `ID`
with your assigned team ID. Use the assignment year for future offerings.
Do not initialize it with a README, license or `.gitignore`. Invite your
teammates and the TAs as directed by the course.

Set your GitHub owner and team repository name below. These commands follow
[GitHub's repository duplication procedure](https://docs.github.com/en/repositories/creating-and-managing-repositories/duplicating-a-repository):

```bash
GITHUB_OWNER=YOUR_GITHUB_USERNAME
TEAM_REPO=EE_748_2026_Team_ID_GEM5
mkdir -p ~/EE_748_gem5
cd ~/EE_748_gem5
git clone --bare https://github.com/geek-dude/EE_748_GEM5.git course-import.git
git -C course-import.git push --mirror "https://github.com/$GITHUB_OWNER/$TEAM_REPO.git"
git clone --branch main "https://github.com/$GITHUB_OWNER/$TEAM_REPO.git" gem5
cd gem5
git remote -v
```

Authenticate using your configured GitHub credential manager/token or use SSH
URLs if you have configured a GitHub SSH key. The mirror push is **only for
initializing your empty private repository**; do not repeat it after team work
has started. `course-import.git` is a temporary bare copy, not your working
directory; it can be deleted after the push and clone succeed.

Work in `~/EE_748_gem5/gem5`. Its `origin` should point to your private team
repository. Commit assignment changes there and use ordinary `git push origin
main` (or your team's branch). Keep the course baseline fixed during assignments;
only apply course updates when instructed by the TAs.

## Workspace layout

```text
EE_748_gem5/
├── run-gem5-container.sh       # installed by setup
├── benchmarks/CPU2006/        # course binaries and inputs, outside Git
├── gem5_out/                  # simulation results, outside Git
└── gem5/                      # your private repository's working copy
    ├── configs/ee748/         # course configurations and batch runners
    ├── util/ee748/            # Docker setup scripts
    └── build/X86/gem5.opt     # created by compilation
```

The host workspace is mounted at `/EE_748_gem5` inside Docker. Keep all inputs
within it and use container paths in argument files. Source, builds and outputs
persist after the container exits.

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

## 3. Prepare the container and build gem5

On the **host**, from `~/EE_748_gem5/gem5`:

```bash
bash util/ee748/step_2_setup-gem5-container.sh
cd ..
./run-gem5-container.sh
```

Setup pulls `ghcr.io/gem5/ubuntu-24.04_all-dependencies:v24-1`, creates sibling
benchmark/output directories and installs the launcher. It uses your existing
clone and will not overwrite a locally modified launcher. The container runs
with your UID/GID.

**Inside the container:**

```bash
cd /EE_748_gem5/gem5
scons build/X86/gem5.opt -j2
./build/X86/gem5.opt configs/ee748/se.py --help
exit
```

Start with two build jobs and increase only if RAM permits. Build parallelism
is separate from simulation parallelism; compilation can use substantial RAM.
Pulling the image does not compile gem5.

## 4. Obtain the benchmarks

Course server details and the exact `rsync` command will be added here before
release. The destination is `~/EE_748_gem5/benchmarks/CPU2006`, **outside** the
`gem5` repository. Do not commit benchmark binaries or inputs to your team repo.
See [workload notes](docs/ee748/BENCHMARKS.md) for required files and Sphinx
input preparation; ask the TAs if any files are missing.

## 5. Enable KVM on the host

Use an x86 Linux machine with virtualization enabled in its firmware and
`/dev/kvm` available. Run these commands on the **host**, not inside Docker:

```bash
ls -l /dev/kvm
sudo usermod -aG kvm "$USER"
```

Log out completely and log back in (or reconnect SSH) to activate group
membership. Then run on the host:

```bash
test -r /dev/kvm && test -w /dev/kvm && echo "KVM access OK"
sudo sysctl -w kernel.perf_event_paranoid=1
cat /proc/sys/kernel/perf_event_paranoid
cd ~/EE_748_gem5
./run-gem5-container.sh --kvm
```

The kernel setting must be applied again after reboot; the displayed value
should be `1`. See [gem5's KVM guide](https://www.gem5.org/documentation/general_docs/using_kvm/).
The launcher exposes KVM and enables container perf access. It does not change
the host kernel setting itself. If access checks or KVM execution fail, consult
the **TAs** and use the regular fast-forward fallback below. Docker Desktop
and ARM hosts should not be assumed to provide compatible x86 KVM.

## 6. Run all benchmarks in parallel (recommended)

Before launching, inspect the SimPoint files supplied in the benchmark tree.
Determine the fast-forward instruction count for each workload using the
assignment instructions. In `configs/ee748/run_benchmarks.py`, replace the
`None` in each selected workload's `specs` entry with your computed integer
instruction count. Do not use a SimPoint identifier directly as an instruction
count or substitute zero just to bypass the exercise. Ask the TAs if the
SimPoint files or assignment conventions are unclear. Commit your completed
configuration to your private team repository.

The runner refuses to launch if any selected workload still has an unset or
invalid count, including during `--dry-run`. A justified zero is allowed;
positive KVM counts must exceed 10,000,000 for its correction phase. Consult
the TAs or use ATOMIC mode if your derived count is below that limit.

Inside the KVM-enabled container, after completing those entries:

```bash
cd /EE_748_gem5/gem5
bash configs/ee748/run_multiple_parallel.sh --output-root ../gem5_out/baseline-kvm
```

The script runs all eight workloads using your fast-forward counts, then
200 million warmup and 50 million detailed instructions. It defaults to KVM
and **one fewer concurrent
job than the CPUs available to the container**, with a minimum of one. At most
eight jobs run for the eight-workload batch. These are separate simulations,
not extra cores in each simulated system.

**Your PC may become sluggish.** Each job also consumes memory. Reduce
concurrency if RAM is limited or you need to keep working, for example:

```bash
MAX_JOBS=4 bash configs/ee748/run_multiple_parallel.sh --output-root ../gem5_out/baseline-limited
```

Choose a fresh output root for each experiment. Existing benchmark output
directories are refused. Do not run overlapping batches against the same
benchmark tree. To select workloads, append their names, for example `astar
bzip2`; the complete set is `astar bzip2 hmmer lbm mcf milc namd sphinx`.
`--dry-run` previews commands without running them or checking input existence.

### If KVM does not work

Consult the TAs. Exit the container and re-enter **from the host** without KVM:

```bash
cd ~/EE_748_gem5
./run-gem5-container.sh
```

Then run **inside the container**:

```bash
cd /EE_748_gem5/gem5
bash configs/ee748/run_multiple_parallel.sh --mode atomic --output-root ../gem5_out/baseline-atomic
```

This uses regular ATOMIC fast-forwarding with your same fast-forward counts and
can take much longer. The fallback is explicit; the runner does not silently
restart failed KVM jobs. `MAX_JOBS` also works in this mode.

### Check results

Each benchmark directory under the chosen output root contains `run.log`,
`stats.txt`, `config.ini`/`config.json`, and `exit-code.txt`. An exit code of
`0` means the process succeeded; any failed workload makes the batch return
nonzero. Check logs and detailed-phase statistics before using results, since
a workload can exit before a requested instruction limit.

From the host, for example:

```bash
tail -f ~/EE_748_gem5/gem5_out/baseline-kvm/astar/run.log
cat ~/EE_748_gem5/gem5_out/baseline-kvm/*/exit-code.txt
```

Keep the terminal connected during a run, or launch it in a `screen`/`tmux`
session when using SSH. The serial runner is available for diagnosis:
`bash configs/ee748/run_multiple_serial.sh --mode kvm astar`.

## Further reference

Use the configuration's `--help` for individual experiments and follow the
assignment's parameters. Repository development, upstream upgrades, validation
records are in [MAINTAINING.md](docs/ee748/MAINTAINING.md).
[PROVENANCE.md](docs/ee748/PROVENANCE.md) records the source history. Upstream
licenses remain in [LICENSE](LICENSE), and the original project overview is in
[UPSTREAM_README.md](docs/ee748/UPSTREAM_README.md).
