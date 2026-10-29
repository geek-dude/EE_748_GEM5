# Maintainer workflow

## Repository identity and publication

This repository preserves the personal fork's history through
`9ddfa52b2` and merges official tag `v26.0.0.0`, commit
`fed0e07e930fecf1e73dce94dd44e69a5bf70c46`. The working branch is
`codex/ee748-setup`. It is a separate repository, not a change to the personal fork.

There is exactly one named remote, `upstream`, fetching
`https://github.com/gem5/gem5.git`. Its push URL is `DISABLED`, and
`push.default=nothing` prevents implicit pushes. There is no automatic pull,
upstream tracking branch or scheduled update. These are safeguards against
accidents, not access controls against an explicit URL push.

The public course repository is `geek-dude/EE_748_GEM5`, with default branch
`main`. Publish updates by URL without adding a second named remote:

```bash
git push https://github.com/geek-dude/EE_748_GEM5.git codex/ee748-setup:main
```

After validation, create a course tag and publish that specific tag by the same
URL. The GitHub repo is the publication destination; `upstream` remains the sole
configured remote. Never use a mirror push to update the shared course repository. Students
may use a one-time mirror push to initialize their own empty private repository.

Before enabling inherited GitHub Actions, review the upstream workflows: some
are gem5-maintainer infrastructure and may require unavailable secrets or
self-hosted runners. Review these settings before relying on hosted CI results.

For a local handoff before publication, copy the entire workspace including
`gem5/.git`, or clone the local repository into a fresh workspace's `gem5`
directory. Do not copy a `.git` alternates file pointing to a temporary checkout.
For maintainer clones, configure the one-remote policy explicitly:

```bash
git remote remove origin
git remote add upstream https://github.com/gem5/gem5.git
git remote set-url --push upstream DISABLED
git config push.default nothing
```

Student clones instead retain `origin` pointing to their private team repository.

## Freeze the validated year

After step 2 succeeds:

1. Record gem5 commit, container image digest and architecture, tool versions,
   commands, benchmark checksums and outcomes in a validation record.
2. Replace the dependency image tag in `util/ee748/container.env` with the
   validated manifest digest (or keep a documented digest alongside the tag).
3. Commit fixes and tag the course snapshot, e.g. `ee748-course-v1`.
4. Push the branch and that specific tag by course repository URL. Give students
   the frozen tag. Do not update their baseline during an assignment.

## Annual upstream upgrade

Start with a clean, committed course tree. Fetching does not alter working files.
Choose an actual published stable release tag after reviewing its release notes;
do not automatically merge the moving stable or develop branch.

```bash
git fetch upstream --tags
git switch -c codex/ee748-next-release
git merge --no-ff --no-commit NEW_STABLE_TAG
# Resolve and review conflicts; preserve course files and source extensions.
# Run static checks, then commit the reviewed merge before runtime validation.
```

Update the base version in README/provenance and review the dependency image.
Repeat container build and benchmark validation. Restore the previous course
branch if the candidate fails; keep experimental fixes off the published tag.
Source compatibility can require more than changing a version string.

Cache extensions are retained in three classic hierarchies under
`src/python/gem5/components/cachehierarchies/classic/`. New course parameters
are keyword-only so existing upstream positional signatures still work. The
custom MAX_INSTS mapping is in `src/python/gem5/simulate/exit_event.py`.
These files deserve explicit merge review on each upstream upgrade.

## v25 fallback

Do not merge v25 into the v26 branch: that does not downgrade the tree. Branch
from `v25.1.0.1`, then port the **course delta**, excluding v26 upstream commits.
For example, export the candidate delta relative to v26 into the parent workspace:

```bash
git diff --binary v26.0.0.0 codex/ee748-setup > ../ee748-course.patch
git switch -c codex/ee748-v25 v25.1.0.1
git apply --3way ../ee748-course.patch
```

Review conflicts and adapt version-specific constructors, particularly the v26
processor `clk_freq` argument. Update documentation and rerun validation. This
is a porting recipe, not an already tested fallback. Prefer a separate checkout
when preserving v26 build output. Never reuse checkpoints across versions
without establishing compatibility.

## Validation checklist

- Receive the remote machine's SSH address/user and the authorized benchmark
  source/location. Verify architecture, Docker access, resources and KVM/perf.
- Run Docker setup/container setup, inspect native image architecture and record
  its digest. Build `build/X86/gem5.opt` in the container.
- Check `se.py --help`, then a tiny workload, then phase transitions with and
  without fast-forward. Validate detailed-phase stats boundaries and instruction
  counts rather than treating a zero exit code as sufficient.
- Check cache options in generated config files, and KVM overshoot/correction
  behavior separately. Investigate multicore semantics before advertising them.
- Resolve the HMMER/control-file discrepancies in BENCHMARKS.md using the actual
  files, prepare Sphinx inputs and test MILC stdin and NAMD argument handling.
- Run each requested workload, then serial/parallel batches. Verify distinct
  outputs, failure propagation, useful stats and workload completion.
- Review checkpoint examples independently before recommending them.
- If v26 fails for a release-specific reason, port to v25.1.0.1 and repeat checks.

## Validation status

The instructor reports that all eight CPU2006 batch simulations completed
successfully with gem5 v26.0.0.0 in the dependency container, using x86 KVM
and four concurrent jobs. The initial run required KVM group membership,
`kernel.perf_event_paranoid=1`, and five missing Sphinx audio inputs.
HMMER used `nph3.hmm` and `swiss41`; Sphinx used `ctlfile`.

The revised CPU-count-based concurrency default still needs the final course
validation run. Benchmark distribution instructions are pending. Completion
does not establish detailed-phase instruction accounting, multicore correctness,
checkpoint restoration or portability to other host platforms. Retain the
checklist above for those checks and record the image digest before freezing
the student snapshot.

## Development and configuration reference

Rerun SCons after changing `src/`; standalone configuration changes normally
do not need rebuilding. For major release/toolchain changes, move the old build
directory aside and build afresh. Do not mix host/container build artifacts.

Course scripts retain the personal fork's cache latency and associativity
extensions. The former exercise to expose these options is already completed.
`se.py` uses ATOMIC fast-forward, TIMING warmup and O3 detailed execution.
`se_kvm.py` adds KVM followed by a short ATOMIC correction; positive KVM
fast-forward counts must exceed 10,000,000 instructions. Even a zero count
requires KVM support when selecting that script. Limits are per thread/core.

Students derive fast-forward instruction counts from the supplied SimPoints
and replace `None` entries in `configs/ee748/run_benchmarks.py`. Both batch
runners reject unset/invalid selected entries before launching any simulation.
The parallel wrapper defaults to KVM; `--mode atomic` selects the fallback.
Keep worked answers out of the published tree, including maintainer examples.
Earlier published Git history contains historical counts; removing them from
the current tree is not secrecy and does not erase that history.

Checkpoint examples in `configs/ee748/Checkpoint_Scripts` remain experimental;
review their paths, instruction-stop APIs and restoration before recommending
them. They are not part of the student batch workflow.

To generate source documentation inside the container:

```bash
cd /EE_748_gem5/gem5/src
doxygen
```

Open `gem5/src/doxygen/html/index.html` from the host workspace.

## Configuration options and argument handling

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
multicore phase accounting has been checked. Read the configuration
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
