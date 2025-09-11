# Custom configs for gem5

This fork of gem5 has been created with the intention of storing and tracking my custom gem5 configs. Minor modifications have been made to a few files in the gem5 source code to provide some useful command-line options in my config scripts. It also contains some useful bash scripts for running multiple benchmarks parallely or serially.

## se.py

The older versions of gem5 contained a very useful configuration script by Jason Lowe-power called se.py. It has many command-line options which is useful for people who quickly wanted to run some baseline configs with standard benchmarks by doing some parameter sweeping such as varying cache sizes or associativity. Since this script has been deprecated, I have written my own version of it. It is available in ./configs/my_configs.

### Launch command syntax and some options

A simple launch command with bare minimum options: (This whole thing is a single-line command split into multiple lines to improve the readability. You will have to copy-paste all the lines into your terminal in one go, not one line after the other.)

```bash
./build/X86/gem5.opt --outdir=../gem5_out/gcc \
--stats-file=gcc_stats.txt \
../gem5_configs/se.py \
--fastforward-insts 1_000_000 \
--warmup-insts 2_000_000 \
--detailed-insts 4_000_000 \
--binary ../benchmarks/gcc/gcc_base.gcc41-64bit \
--inputs ../benchmarks/gcc/166.in
```

A much more detailed launch command with all the options will look something like this:

```bash
/build/X86/gem5.opt --outdir=../gem5_out/gcc \
--stats-file=gcc_stats.txt \
../gem5_configs/se.py \
--fastforward-insts 1_000_000 \
--warmup-insts 2_000_000 \
--detailed-insts 4_000_000 \
--binary ../benchmarks/gcc/gcc_base.gcc41-64bit \
--inputs ../benchmarks/gcc/166.in \
--num-cores 1 \
--clk-freq 3GHz \
--mem-size 8GiB \
--l1i-size 32KiB \
--l1d-size 32KiB \
--l2-size 256KiB \
--l1i-assoc 8 \
--l1d-assoc 8 \
--l2-assoc 16
```

To see a complete list of options and their descriptions, run:

```bash
./build/X86/gem5.opt ../gem5_configs/se.py --help
```

### Required options

Note that the options --warmup-insts, --detailed-insts, --binary are mandatory and cannot be left unspecified. However, the rest of the options can be left unspecified, and in such scenarios, they will assume some default values. You can open the config se.py to see all the default values. Alternatively, you can also look at config.ini in your output folder after the simulation to get complete information about the config you just simulated. The --inuputs is not mandatory because simple programs like hello-world won't take an input.

### Launch command for benchmarks with their own options

 In special scenarios like in the case of namd benchmark, the benchmark has its own options (Eg: ./namd --input namd.input --iterations 38). In such cases as GEM5 will have difficulty parsing the benchmarks inputs, they are supposed to be put inside a text file (Ex: namd_inputs.txt) and the --input-file option should be used instead of --inputs to pass this file to ensure that the benchmarks inputs are passed in correctly. An example gem5 launch command for this scenario:

```bash
./build/X86/gem5.opt -d ../gem5_out/baseline \
--stats-file=namd_stats.log \
./configs/my_configs/se_kvm.py \
--fastforward-insts 1645_800_000_000 \
--warmup-insts 200_000_000 \
--detailed-insts 50_000_000 \
--binary ../EE_748/CPU2006/444.namd/exe/namd_base.gcc44-64bit \
--input-file ../EE_748/CPU2006/444.namd/data/all/input/namd_inputs.txt
```

In this case, the contents of namd_inputs.txt are:

```bash
--input /home/sagar/Documents/EE_748/CPU2006/444.namd/data/all/input/namd.input --iterations 38
```

## se_kvm.py

The file se_kvm.py is functionally equivalent to the script se.py. The key difference is that it uses a KVM CPU instead of an Atomic CPU for the initial fast forwarding before switching to Atomic. Unlike the remaining three CPUs (atomic, timing, and O3), the KVM CPU is not simulated in GEM5; instead, it represents the actual CPU present in your hardware, and therefore, it is very fast. So use this file instead of the regular se.py to drastically speed up the fast-forward section of your simulation, as you may need to simulate billions of instructions for the fast-forward phase. It has the same options as se.py, and launching it from the command line is no different from launching se.py. However, before running this script, ensure that the KVM feature is available on your system.

Refer to the instructions at:
https://www.gem5.org/documentation/general_docs/using_kvm/

Also, run the command below before launching a simulation. It is sufficient to run this command once per boot and does not need to be run before every simulation run:

```bash
sudo sysctl kernel/perf_event_paranoid=1
```

> [!IMPORTANT]
> If you don't run the above command, you will see some error along the lines of:

```bash
src/cpu/kvm/perfevent.cc:176: panic: PerfKvmCounter::attach received error EACCESS.
  This error may be caused by a too restrictive setting
  in the file '/proc/sys/kernel/perf_event_paranoid'.
  The default value was changed to 2 in kernel 4.6.
  A value greater than 1 prevents gem5 from making
  the syscall to perf_event_open.
```

## Checkpoint scripts

> [!WARNING]
> Although, the checkpoint scripts at ./configs/my_configs/Checkpoint_Scripts have been tested once and seem to be working, it wasn't a thogourh test. Also, these scripts use direct c++ methods of base cpu that are exposed through pybind instead of relying on the cleaner interfaces exposed through the simulator component to control the flow of the simulation. Before blindly using these scripts, first very their correctness once and also refactor them to use cleaner methods to control simulation flow.

## Runscripts

In order to automate the process of firing multiple simulations, it is convenient to use some bash script. The two bash scrips run_all_serial.sh and run_all_parallel.sh can be used as templates for serial and parallel firing bash scripts respectively. The script run_multiple_parallel.sh which will try to run a parallel batch of benchmarks. The batch size is configurable. For example, in this script MAX_JOBS=7 will select 7 benchmarks to launch parallelly. As soon as one of them completes, it will launch some other benchmark to maintain a batch size of 7. You may choose a number for MAX_JOBS based on the number cores available on your PC. It is recommended to leave out atleast one core so that the system doesn't become unresponsive. This script will run both the run_log and stat_log for each benchmark to a folder baseline assuming that you are running the baseline configuration. Change this folder name to something else for the configs that you will compare you baseline against.

What follows below is the README of the original gem5 repo:

# The gem5 Simulator

This is the repository for the gem5 simulator. It contains the full source code
for the simulator and all tests and regressions.

The gem5 simulator is a modular platform for computer-system architecture
research, encompassing system-level architecture as well as processor
microarchitecture. It is primarily used to evaluate new hardware designs,
system software changes, and compile-time and run-time system optimizations.

The main website can be found at <http://www.gem5.org>.

## Testing status

**Note**: These regard tests run on the develop branch of gem5:
<https://github.com/gem5/gem5/tree/develop>.

[![Daily Tests](https://github.com/gem5/gem5/actions/workflows/daily-tests.yaml/badge.svg?branch=develop)](https://github.com/gem5/gem5/actions/workflows/daily-tests.yaml)
[![Weekly Tests](https://github.com/gem5/gem5/actions/workflows/weekly-tests.yaml/badge.svg?branch=develop)](https://github.com/gem5/gem5/actions/workflows/weekly-tests.yaml)
[![Compiler Tests](https://github.com/gem5/gem5/actions/workflows/compiler-tests.yaml/badge.svg?branch=develop)](https://github.com/gem5/gem5/actions/workflows/compiler-tests.yaml)

## Getting started

A good starting point is <http://www.gem5.org/about>, and for
more information about building the simulator and getting started
please see <http://www.gem5.org/documentation> and
<http://www.gem5.org/documentation/learning_gem5/introduction>.

## Building gem5

To build gem5, you will need the following software: g++ or clang,
Python (gem5 links in the Python interpreter), SCons, zlib, m4, and lastly
protobuf if you want trace capture and playback support. Please see
<http://www.gem5.org/documentation/general_docs/building> for more details
concerning the minimum versions of these tools.

Once you have all dependencies resolved, execute
`scons build/ALL/gem5.opt` to build an optimized version of the gem5 binary
(`gem5.opt`) containing all gem5 ISAs. If you only wish to compile gem5 to
include a single ISA, you can replace `ALL` with the name of the ISA. Valid
options include `ARM`, `NULL`, `MIPS`, `POWER`, `RISCV`, `SPARC`, and `X86`
The complete list of options can be found in the build_opts directory.

See https://www.gem5.org/documentation/general_docs/building for more
information on building gem5.

## The Source Tree

The main source tree includes these subdirectories:

* build_opts: pre-made default configurations for gem5
* build_tools: tools used internally by gem5's build process.
* configs: example simulation configuration scripts
* ext: less-common external packages needed to build gem5
* include: include files for use in other programs
* site_scons: modular components of the build system
* src: source code of the gem5 simulator. The C++ source, Python wrappers, and Python standard library are found in this directory.
* system: source for some optional system software for simulated systems
* tests: regression tests
* util: useful utility programs and files

## gem5 Resources

To run full-system simulations, you may need compiled system firmware, kernel
binaries and one or more disk images, depending on gem5's configuration and
what type of workload you're trying to run. Many of these resources can be
obtained from <https://resources.gem5.org>.

More information on gem5 Resources can be found at
<https://www.gem5.org/documentation/general_docs/gem5_resources/>.

## Getting Help, Reporting bugs, and Requesting Features

We provide a variety of channels for users and developers to get help, report
bugs, requests features, or engage in community discussions. Below
are a few of the most common we recommend using.

* **GitHub Discussions**: A GitHub Discussions page. This can be used to start
discussions or ask questions. Available at
<https://github.com/orgs/gem5/discussions>.
* **GitHub Issues**: A GitHub Issues page for reporting bugs or requesting
features. Available at <https://github.com/gem5/gem5/issues>.
* **Jira Issue Tracker**: A Jira Issue Tracker for reporting bugs or requesting
features. Available at <https://gem5.atlassian.net/>.
* **Slack**: A Slack server with a variety of channels for the gem5 community
to engage in a variety of discussions. Please visit
<https://www.gem5.org/join-slack> to join.
* **gem5-users@gem5.org**: A mailing list for users of gem5 to ask questions
or start discussions. To join the mailing list please visit
<https://www.gem5.org/mailing_lists>.
* **gem5-dev@gem5.org**: A mailing list for developers of gem5 to ask questions
or start discussions. To join the mailing list please visit
<https://www.gem5.org/mailing_lists>.

## Contributing to gem5

We hope you enjoy using gem5. When appropriate we advise sharing your
contributions to the project. <https://www.gem5.org/contributing> can help you
get started. Additional information can be found in the CONTRIBUTING.md file.
