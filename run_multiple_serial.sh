#!/bin/bash

sudo sysctl kernel/perf_event_paranoid=1

# === ASTAR ===
cd ~/Documents/EE_748/CPU2006/473.astar/data/ref/input/ || exit 1

echo "Running ASTAR benchmark..."
cmd="~/Documents/gem5/build/X86/gem5.opt -d ~/Documents/gem5_out/baseline \
--stats-file=astar_stats.log \
~/Documents/gem5/configs/my_configs/se_kvm.py \
--fastforward-insts 180_800_000_000 \
--warmup-insts 200_000_000 \
--detailed-insts 50_000_000 \
--binary ../../../exe/astar_base.gcc44-64bit \
--inputs ./BigLakes2048.cfg"

echo "Command: $cmd"
{ time eval $cmd ; } > ~/Documents/gem5_out/astar_run.log 2>&1
echo "ASTAR benchmark completed. Logs in ../gem5_out/astar_run.log"
cd ~/Documents/gem5/ || exit 1

# === BZIP2 ===
echo "Running BZIP2 benchmark..."
cmd="./build/X86/gem5.opt -d ../gem5_out/baseline \
--stats-file=bzip_stats.log \
./configs/my_configs/se_kvm.py \
--fastforward-insts 54_800_000_000 \
--warmup-insts 200_000_000 \
--detailed-insts 50_000_000 \
--binary ../EE_748/CPU2006/401.bzip2/exe/bzip2_base.gcc44-64bit \
--inputs ../EE_748/CPU2006/401.bzip2/data/ref/input/input.source"

echo "Command: $cmd"
{ time eval $cmd ; } > ../gem5_out/bzip2_run.log 2>&1
echo "BZIP2 benchmark completed. Logs in ../gem5_out/bzip_run.log"

# === HMMER ===
echo "Running HMMER benchmark..."
cmd="./build/X86/gem5.opt -d ../gem5_out/baseline \
--stats-file=hmmer_stats.log \
./configs/my_configs/se_kvm.py \
--fastforward-insts 15_800_000_000 \
--warmup-insts 200_000_000 \
--detailed-insts 50_000_000 \
--binary ../EE_748/CPU2006/456.hmmer/exe/hmmer_base.gcc44-64bit \
--inputs ../EE_748/CPU2006/456.hmmer/data/ref/input/nph3.hmm ../EE_748/CPU2006/456.hmmer/data/ref/input/swiss41"

echo "Command: $cmd"
{ time eval $cmd ; } > ../gem5_out/hmmer_run.log 2>&1
echo "HMMER benchmark completed. Logs in ../gem5_out/hmmer_run.log"

# === LBM ===
echo "Running LBM benchmark..."
cmd="./build/X86/gem5.opt -d ../gem5_out/baseline \
--stats-file=lbm_stats.log \
./configs/my_configs/se_kvm.py \
--fastforward-insts 92_800_000_000 \
--warmup-insts 200_000_000 \
--detailed-insts 50_000_000 \
--binary ../EE_748/CPU2006/470.lbm/exe/lbm_base.gcc44-64bit \
--inputs 3000 reference.dat 0 0 ../EE_748/CPU2006/470.lbm/data/ref/input/100_100_130_ldc.of"

echo "Command: $cmd"
{ time eval $cmd ; } > ../gem5_out/lbm_run.log 2>&1
echo "LBM benchmark completed. Logs in ../gem5_out/lbm_run.log"

# === MCF ===
echo "Running MCF benchmark..."
cmd="./build/X86/gem5.opt -d ../gem5_out/baseline \
--stats-file=mcf_stats.log \
./configs/my_configs/se_kvm.py \
--fastforward-insts 305_800_000_000 \
--warmup-insts 200_000_000 \
--detailed-insts 50_000_000 \
--binary ../EE_748/CPU2006/429.mcf/exe/mcf_base.gcc44-64bit \
--inputs ../EE_748/CPU2006/429.mcf/data/ref/input/inp.in"

echo "Command: $cmd"
{ time eval $cmd ; } > ../gem5_out/mcf_run.log 2>&1
echo "MCF benchmark completed. Logs in ../gem5_out/mcf_run.log"

# === MILC ===
echo "Running MILC benchmark..."
cmd="./build/X86/gem5.opt -d ../gem5_out/baseline \
--stats-file=milc_stats.log \
./configs/my_configs/se_kvm.py \
--fastforward-insts 6_800_000_000 \
--warmup-insts 200_000_000 \
--detailed-insts 50_000_000 \
--binary ../EE_748/CPU2006/433.milc/exe/milc_base.gcc44-64bit \
--inputs < ../EE_748/CPU2006/433.milc/data/ref/input/su3imp.in"

echo "Command: $cmd"
{ time eval $cmd ; } > ../gem5_out/milc_run.log 2>&1
echo "MILC benchmark completed. Logs in ../gem5_out/milc_run.log"

# === NAMD ===
echo "Running NAMD benchmark..."
cmd="./build/X86/gem5.opt -d ../gem5_out/baseline \
--stats-file=namd_stats.log \
./configs/my_configs/se_kvm.py \
--fastforward-insts 1645_800_000_000 \
--warmup-insts 200_000_000 \
--detailed-insts 50_000_000 \
--binary ../EE_748/CPU2006/444.namd/exe/namd_base.gcc44-64bit \
--input-file ../EE_748/CPU2006/444.namd/data/all/input/namd_inputs.txt"

echo "Command: $cmd"
{ time eval $cmd ; } > ../gem5_out/namd_run.log 2>&1
echo "NAMD benchmark completed. Logs in ../gem5_out/namd_run.log"

# === SPHINX ===
cd ~/Documents/EE_748/CPU2006/482.sphinx3/build/build_base_gcc44-64bit.0000 || exit 1

echo "Running SPHINX benchmark..."
cmd="~/Documents/gem5/build/X86/gem5.opt -d ~/Documents/gem5_out/baseline \
--stats-file=sphinx_stats.log \
~/Documents/gem5/configs/my_configs/se_kvm.py \
--warmup-insts 200_000_000 \
--detailed-insts 50_000_000 \
--binary ../../exe/sphinx_livepretend_base.gcc44-64bit \
--inputs ./ctlfile . ./args.an4"

echo "Command: $cmd"
{ time eval $cmd ; } > ../gem5_out/sphinx_run.log 2>&1
echo "SPHINX benchmark completed. Logs in ../gem5_out/sphinx_run.log"
cd ~/Documents/gem5/ || exit 1
