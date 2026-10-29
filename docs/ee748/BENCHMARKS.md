# Course workload reference

The benchmark tree is `/EE_748_gem5/benchmarks/CPU2006`. Obtain the actual course
files from the TA; this repository does not download or redistribute them. Binary
names below follow last year's `*_base.gcc44-64bit` collection. Adjust them if the
provided files differ. Run the supplied batch launchers **inside the container**.

In the table, `BENCH` means the individual benchmark directory and `REF` means
`BENCH/data/ref/input`. The argument column describes argv, not a shell command.
Paths are relative to the indicated directory only when explicitly stated.

| Workload | Executable under BENCH/exe | Arguments/input and working directory |
| --- | --- | --- |
| 400.perlbench | perlbench (verify actual suffix) | `BENCH/data/all/input/splitmail.pl 1600 12 26 16 4500`; use `--inputs`. Not yet in the batch list. |
| 401.bzip2 | bzip2_base.gcc44-64bit | `REF/input.source` |
| 416.gamess | gamess (verify actual suffix) | stdin from `cytosine.2.config`; locate it in the supplied tree. Historical binary needs libgfortran.so.3, which is not supplied by libgfortran5. Excluded pending dependency work. |
| 429.mcf | mcf_base.gcc44-64bit | `REF/inp.in` |
| 433.milc | milc_base.gcc44-64bit | `--stdin-file REF/su3imp.in`; no `<` argument |
| 444.namd | namd_base.gcc44-64bit | `--input BENCH/data/all/input/namd.input --iterations 38`; place these in an argument file for `--input-file` |
| 456.hmmer | hmmer_base.gcc44-64bit | `REF/nph3.hmm REF/swiss41` used in the successful course batch. |
| 470.lbm | lbm_base.gcc44-64bit | `3000 OUTPUT/reference.dat 0 0 REF/100_100_130_ldc.of`; give each run its own writable output path |
| 473.astar | astar_base.gcc44-64bit | Run with working directory `REF`, containing both BigLakes2048.cfg and BigLakes2048.bin; argv is `BigLakes2048.cfg` |
| 482.sphinx3 | sphinx_livepretend_base.gcc44-64bit | Working directory `BENCH/build/build_base_gcc44-64bit.0000`; argv `ctlfile . args.an4` |

Sphinx setup: copy `an410-fcaw-b.be.raw`, `an409-fcaw-b.be.raw`,
`an408-fcaw-b.be.raw`, `an407-fcaw-b.be.raw` and `an406-fcaw-b.be.raw` from
`482.sphinx3/data/train/input` to that build working directory. Verify `ctlfile`
and `args.an4` exist and refer to the copied inputs. The validated collection uses `ctlfile`. These inputs must be prepared before
running; consult the TAs if the distributed collection is incomplete.

Default warmup is 200,000,000 and detailed execution 50,000,000 instructions.
These are historical assignment values, not recommended smoke-test lengths.
Workload completion can precede the instruction limits; inspect each run before
using its results. Do not run simultaneous batches against the same ASTAR/Sphinx
working directories until benchmark-generated files have been checked.
