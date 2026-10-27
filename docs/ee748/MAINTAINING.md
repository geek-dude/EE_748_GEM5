# Maintainer workflow

## Repository identity and publication

This candidate preserves the personal fork's history through
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
configured remote. Never use a mirror push.

Before enabling inherited GitHub Actions, review the upstream workflows: some
are gem5-maintainer infrastructure and may require unavailable secrets or
self-hosted runners. Review these settings before relying on hosted CI results.

For a local handoff before publication, copy the entire workspace including
`gem5/.git`, or clone the local repository into a fresh workspace's `gem5`
directory. Do not copy a `.git` alternates file pointing to a temporary checkout.
Set up the one-remote policy in each fresh clone as documented in README.md.

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

## Step 2 (intentionally not performed during step 1)

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
