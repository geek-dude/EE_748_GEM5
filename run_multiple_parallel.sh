#!/bin/bash
#
# Parallel GEM5 benchmark launcher
# Runs multiple benchmarks concurrently with a configurable number of threads.
# Uses wait -n (requires Bash 5+).
#

# === CONFIGURATION ===
MAX_JOBS=7   # Number of parallel jobs (set to 7 for your 8-core system)

sudo sysctl kernel/perf_event_paranoid=1

# === HELPER FUNCTION ===
run_benchmark() {
    name=$1
    shift
    log="../gem5_out/baseline/${name}_run.log"

    echo "[$(date +'%F %T')] Starting $name benchmark..."
    echo "Command: $*" | tee -a "$log"

    { time eval "$@" ; } > "$log" 2>&1
    echo "[$(date +'%F %T')] $name benchmark completed. Logs in $log"
}

# === JOB LIST ===
jobs=(
    # ASTAR
    "astar|cd ~/Documents/EE_748/CPU2006/473.astar/data/ref/input/ && \
     ~/Documents/gem5/build/X86/gem5.opt -d ~/Documents/gem5_out/baseline \
     --stats-file=astar_stats.log \
     ~/Documents/gem5/configs/my_configs/se_kvm.py \
     --fastforward-insts 180_800_000_000 \
     --warmup-insts 200_000_000 \
     --detailed-insts 50_000_000 \
     --binary ../../../exe/astar_base.gcc44-64bit \
     --inputs ./BigLakes2048.cfg"

    # BZIP2
     "bzip|cd ~/Documents/gem5 && \
     ./build/X86/gem5.opt -d ../gem5_out/baseline \
     --stats-file=bzip_stats.log \
     ./configs/my_configs/se_kvm.py \
     --fastforward-insts 54_800_000_000 \
     --warmup-insts 200_000_000 \
     --detailed-insts 50_000_000 \
     --binary ../EE_748/CPU2006/401.bzip2/exe/bzip2_base.gcc44-64bit \
     --inputs ../EE_748/CPU2006/401.bzip2/data/ref/input/input.source"

    # HMMER
     "hmmer|cd ~/Documents/gem5 && \
     ./build/X86/gem5.opt -d ../gem5_out/baseline \
     --stats-file=hmmer_stats.log \
     ./configs/my_configs/se_kvm.py \
     --fastforward-insts 15_800_000_000 \
     --warmup-insts 200_000_000 \
     --detailed-insts 50_000_000 \
     --binary ../EE_748/CPU2006/456.hmmer/exe/hmmer_base.gcc44-64bit \
     --inputs ../EE_748/CPU2006/456.hmmer/data/ref/input/nph3.hmm ../EE_748/CPU2006/456.hmmer/data/ref/input/swiss41"

    # LBM
     "lbm|cd ~/Documents/gem5 && \
     ./build/X86/gem5.opt -d ../gem5_out/baseline \
     --stats-file=lbm_stats.log \
     ./configs/my_configs/se_kvm.py \
     --fastforward-insts 92_800_000_000 \
     --warmup-insts 200_000_000 \
     --detailed-insts 50_000_000 \
     --binary ../EE_748/CPU2006/470.lbm/exe/lbm_base.gcc44-64bit \
     --inputs 3000 reference.dat 0 0 ../EE_748/CPU2006/470.lbm/data/ref/input/100_100_130_ldc.of"

    # MCF
     "mcf|cd ~/Documents/gem5 && \
     ./build/X86/gem5.opt -d ../gem5_out/baseline \
     --stats-file=mcf_stats.log \
     ./configs/my_configs/se_kvm.py \
     --fastforward-insts 305_800_000_000 \
     --warmup-insts 200_000_000 \
     --detailed-insts 50_000_000 \
     --binary ../EE_748/CPU2006/429.mcf/exe/mcf_base.gcc44-64bit \
     --inputs ../EE_748/CPU2006/429.mcf/data/ref/input/inp.in"

    # MILC (needs stdin redirection)
     "milc|cd ~/Documents/gem5 && \
     ./build/X86/gem5.opt -d ../gem5_out/baseline \
     --stats-file=milc_stats.log \
     ./configs/my_configs/se_kvm.py \
     --fastforward-insts 6_800_000_000 \
     --warmup-insts 200_000_000 \
     --detailed-insts 50_000_000 \
     --binary ../EE_748/CPU2006/433.milc/exe/milc_base.gcc44-64bit \
     < ../EE_748/CPU2006/433.milc/data/ref/input/su3imp.in"

    # NAMD (input file)
     "namd|cd ~/Documents/gem5 && \
     ./build/X86/gem5.opt -d ../gem5_out/baseline \
     --stats-file=namd_stats.log \
     ./configs/my_configs/se_kvm.py \
     --fastforward-insts 1645_800_000_000 \
     --warmup-insts 200_000_000 \
     --detailed-insts 50_000_000 \
     --binary ../EE_748/CPU2006/444.namd/exe/namd_base.gcc44-64bit \
     --input-file ../EE_748/CPU2006/444.namd/data/all/input/namd_inputs.txt"

    # SPHINX
    "sphinx|cd ~/Documents/EE_748/CPU2006/482.sphinx3/build/build_base_gcc44-64bit.0000 && \
     ~/Documents/gem5/build/X86/gem5.opt -d ~/Documents/gem5_out/baseline \
     --stats-file=sphinx_stats.log \
     ~/Documents/gem5/configs/my_configs/se_kvm.py \
     --warmup-insts 200_000_000 \
     --detailed-insts 50_000_000 \
     --binary ../../exe/sphinx_livepretend_base.gcc44-64bit \
     --inputs ./ctlfile . ./args.an4"
)

# === PARALLEL EXECUTION ===
running=0
for entry in "${jobs[@]}"; do
    name="${entry%%|*}"      # left side of "|"
    cmd="${entry#*|}"        # right side of "|"

    run_benchmark "$name" "$cmd" &

    ((running++))
    if (( running >= MAX_JOBS )); then
        wait -n   # wait for any job to finish before launching a new one
        ((running--))
    fi
done

# Wait for all remaining jobs
wait
echo "[$(date +'%F %T')] All benchmarks completed!"
