import argparse
import shlex
from pathlib import Path

from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy,
)
from gem5.components.memory.single_channel import SingleChannelDDR3_1600
from gem5.components.processors.cpu_types import (
    CPUTypes,
    get_mem_mode,
)
from gem5.components.processors.simple_core import SimpleCore
from gem5.components.processors.switchable_processor import (
    SwitchableProcessor,
)
from gem5.isas import ISA
from gem5.resources.resource import (
    BinaryResource,
    FileResource,
)
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires

# Parse Command Line Arguments
# --------------------------------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(
    description="Custom SE simulation script with fast-forward and warmup functionality and uses kvm for the initial fast-forwarding"
)

# Instruction limits
parser.add_argument(
    "--fastforward-insts",
    type=int,
    default=0,
    help="Fast-forward (KVM + ATOMIC) instructions",
)
parser.add_argument(
    "--warmup-insts",
    type=int,
    required=True,
    help="Warmup (TIMING) instructions",
)
parser.add_argument(
    "--detailed-insts",
    type=int,
    required=True,
    help="Detailed (O3) instructions",
)

# Workload
parser.add_argument("--binary", type=str, required=True, help="Path to binary")
parser.add_argument(
    "--inputs", type=str, nargs="*", default=[], help="Binary input arguments"
)
parser.add_argument(
    "--input-file",
    type=str,
    default=None,
    help="Path to a file containing the full set of input arguments (one line).",
)

# Processor and Memory
parser.add_argument(
    "--num-cores", type=int, default=1, help="Number of CPU cores"
)
parser.add_argument(
    "--clk-freq",
    type=str,
    default="3GHz",
    help="Clk freq of the board. Same as CPU freq in this case.",
)
parser.add_argument(
    "--mem-size", type=str, default="8GiB", help="Size of DRAM"
)

# Cache hierarchy
parser.add_argument("--l1i-size", type=str, default="32KiB")
parser.add_argument("--l1d-size", type=str, default="32KiB")
parser.add_argument("--l2-size", type=str, default="256KiB")
# Course cache extensions (defaults preserve the original hierarchy).
parser.add_argument("--l1i-assoc", type=int, default=8)
parser.add_argument("--l1i-tag-latency", type=int, default=1)
parser.add_argument("--l1i-data-latency", type=int, default=1)
parser.add_argument("--l1i-response-latency", type=int, default=1)
parser.add_argument("--l1d-assoc", type=int, default=8)
parser.add_argument("--l1d-tag-latency", type=int, default=1)
parser.add_argument("--l1d-data-latency", type=int, default=1)
parser.add_argument("--l1d-response-latency", type=int, default=1)
parser.add_argument("--l2-assoc", type=int, default=4)
parser.add_argument("--l2-tag-latency", type=int, default=10)
parser.add_argument("--l2-data-latency", type=int, default=10)
parser.add_argument("--l2-response-latency", type=int, default=1)
parser.add_argument("--stdin-file", help="File supplied to benchmark stdin")
parser.add_argument(
    "--library-path", help="Library path for the simulated binary"
)
args = parser.parse_args()
if 0 < args.fastforward_insts <= 10_000_000:
    parser.error(
        "KVM fast-forward must exceed 10,000,000 instructions; use se.py for short runs"
    )
if (
    args.fastforward_insts < 0
    or min(args.warmup_insts, args.detailed_insts) <= 0
):
    parser.error(
        "Fast-forward must be nonnegative; warmup/detail must be positive"
    )
if args.num_cores < 1:
    parser.error("--num-cores must be positive")
if args.input_file and args.inputs:
    parser.error("Use either --inputs or --input-file")
# --------------------------------------------------------------------------------------------------------------------
# Color codes for terminal output
BOLD_YELLOW = "\033[1;93m"
BOLD_BLUE = "\033[1;96m"
BOLD_RED = "\033[1;91m"
BOLD_GREEN = "\033[1;92m"
RESET = "\033[0m"
# --------------------------------------------------

# === Memory Heirarchy ===
# --------------------------------------------------
cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
    l1i_size=args.l1i_size,
    l1d_size=args.l1d_size,
    l2_size=args.l2_size,
    l1i_assoc=args.l1i_assoc,
    l1d_assoc=args.l1d_assoc,
    l2_assoc=args.l2_assoc,
    l1i_tag_latency=args.l1i_tag_latency,
    l1i_data_latency=args.l1i_data_latency,
    l1i_response_latency=args.l1i_response_latency,
    l1d_tag_latency=args.l1d_tag_latency,
    l1d_data_latency=args.l1d_data_latency,
    l1d_response_latency=args.l1d_response_latency,
    l2_tag_latency=args.l2_tag_latency,
    l2_data_latency=args.l2_data_latency,
    l2_response_latency=args.l2_response_latency,
)
memory = SingleChannelDDR3_1600(size=args.mem_size)
# --------------------------------------------------

# Processor setup
# ---------------------------------------------------------------------------------
requires(
    isa_required=ISA.X86,  # Ensures that the gem5 binary is built with X86 ISA
    kvm_required=True,  # Ensures that the host machine has KVM support
)
# SwitchableProcessor expects a dictonary, mapping string keys -> lists of SimpleCore
switchable_cores = {
    "kvm": [
        SimpleCore(cpu_type=CPUTypes.KVM, core_id=i, isa=ISA.X86)
        for i in range(args.num_cores)
    ],
    "atomic": [
        SimpleCore(cpu_type=CPUTypes.ATOMIC, core_id=i, isa=ISA.X86)
        for i in range(args.num_cores)
    ],
    "timing": [
        SimpleCore(cpu_type=CPUTypes.TIMING, core_id=i, isa=ISA.X86)
        for i in range(args.num_cores)
    ],
    "o3": [
        SimpleCore(cpu_type=CPUTypes.O3, core_id=i, isa=ISA.X86)
        for i in range(args.num_cores)
    ],
}

if args.fastforward_insts > 0:
    starting_cores = "kvm"
else:
    starting_cores = "timing"
processor = SwitchableProcessor(
    switchable_cores=switchable_cores,
    starting_cores=starting_cores,
    clk_freq=args.clk_freq,
)
# ---------------------------------------------------------------------------------

# Board setup
# ---------------------------
board = SimpleBoard(
    clk_freq=args.clk_freq,
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

# Binary & inputs
# -----------------------------------------------------------------
binary = BinaryResource(args.binary)
if args.input_file:
    # Read everything from the file and split into arguments
    with open(args.input_file) as f:
        file_args = shlex.split(f.read())
    print(file_args)
    inputs = file_args
else:
    inputs = args.inputs
board.set_se_binary_workload(
    binary,
    arguments=inputs,
    env_list=(
        [f"LD_LIBRARY_PATH={Path(args.library_path).resolve()}"]
        if args.library_path
        else None
    ),
    stdin_file=(
        FileResource(str(Path(args.stdin_file).resolve()))
        if args.stdin_file
        else None
    ),
)
# -----------------------------------------------------------------


# Simulator flow setup
# ----------------------------------------------------------------------------------------------------
def exit_event_handler():  # This function must be defined before defining the simulator as the simulator will call this function on exit events to decide what to do next
    """
    Generator used by Simulator.on_exit_event for ExitEvent.MAX_INSTS.
    Each yield False continues the simulation; yield True stops the simulator.
    The order is:
    1) KVM (fast-forward-Stage-1)    -> switch to ATOMIC
    2) ATOMIC (fast-forward-Stage-2) -> switch to O3
    3) TIMING (warmup)               -> switch to O3
    4) O3 (detailed)                 -> stop
    """
    # 1) Stage-1 Fast-forward completed (KVM)
    core_type = processor.get_cores()[0].get_type()
    if args.fastforward_insts > 0:
        actual_sim_insts = simulator.get_instruction_count()
        overshoot_insts = actual_sim_insts - kvm_fastforward_insts
        print(
            f"{BOLD_YELLOW}Simulated {actual_sim_insts} instructions on {core_type} (fast-forward-1)."
        )
        print(
            f"Overshoot after stage-1 fast-forward = {overshoot_insts} instructions{RESET}"
        )
        processor.switch_to_processor("atomic")
        core_type = processor.get_cores()[0].get_type()
        print(f"{BOLD_BLUE}Switched to {core_type} (fast-forward-2){RESET}")
        board.set_mem_mode(get_mem_mode(core_type))
        if overshoot_insts >= atomic_fastforward_insts:
            print(
                f"{BOLD_RED}Warning: Not enough instructions left for atomic fastforward phase."
            )
            print("Increase atomic_fastforward_insts as needed.")
            print(f"Exiting simulation.{RESET}")
            yield True  # exit simulation
        adjusted_atomic_fastforward_limit = (
            atomic_fastforward_insts - overshoot_insts
        )
        print(
            f"{BOLD_YELLOW}Adjusted atomic fastforward limit = {adjusted_atomic_fastforward_limit} instructions{RESET}"
        )
        simulator.schedule_max_insts(adjusted_atomic_fastforward_limit)
        yield False  # continue simulation

    # 2) Stage-2 Fast-forward completed (ATOMIC)
    if args.fastforward_insts > 0:
        actual_sim_insts = simulator.get_instruction_count()
        overshoot_insts = actual_sim_insts - adjusted_atomic_fastforward_limit
        print(
            f"{BOLD_YELLOW}Simulated {actual_sim_insts} instructions on {core_type} (fast-forward-2)."
        )
        print(
            f"Overshoot after stage-2 fast-forward = {overshoot_insts} instructions{RESET}"
        )
        processor.switch_to_processor("timing")
        core_type = processor.get_cores()[0].get_type()
        print(f"{BOLD_BLUE}Switched to {core_type} (warmup){RESET}")
        board.set_mem_mode(get_mem_mode(core_type))
        if overshoot_insts >= args.warmup_insts:
            print(
                f"{BOLD_RED}Warning: Not enough instructions left for warmup phase."
            )
            print(
                "Decrease --fastforward-insts and/or atomic_fast_forward_insts as needed."
            )
            print(f"Exiting simulation.{RESET}")
            yield True  # exit simulation
        adjusted_warmup_limit = args.warmup_insts - overshoot_insts
        print(
            f"{BOLD_YELLOW}Adjusted warmup limit = {adjusted_warmup_limit} instructions{RESET}"
        )
        simulator.schedule_max_insts(adjusted_warmup_limit)
        yield False  # continue simulation

    # 3) Warmup completed (TIMING)
    actual_sim_insts = simulator.get_instruction_count()
    print(
        f"{BOLD_YELLOW}Simulated {actual_sim_insts} instructions on {core_type} (warmup)."
    )
    if args.fastforward_insts > 0:
        overshoot_insts = actual_sim_insts - adjusted_warmup_limit
        print(
            f"Overshoot after warmup = {overshoot_insts} instructions{RESET}"
        )
        if overshoot_insts >= args.detailed_insts:
            print(
                f"{BOLD_RED}Warning: Not enough instructions left for detailed phase."
            )
            print("Decrease ----warmup-insts as needed.")
            print(f"Exiting simulation.{RESET}")
            yield True  # exit simulation
    processor.switch_to_processor("o3")
    core_type = processor.get_cores()[0].get_type()
    print(f"{BOLD_BLUE}Switched to {core_type} (detailed){RESET}")
    board.set_mem_mode(get_mem_mode(core_type))
    simulator.schedule_max_insts(args.detailed_insts)
    yield False  # continue simulation

    # 4) Detailed completed (O3) -> stop simulation
    actual_sim_insts = simulator.get_instruction_count()
    print(
        f"{BOLD_YELLOW}Simulated {actual_sim_insts} instructions on {core_type} (detailed)."
    )
    print(
        f"{BOLD_GREEN}Success: All three-phases of simulation completed!{RESET}"
    )
    yield True  # exit simulation)


# ----------------------------------------------------------------------------------------------------

# Actual Simulator setup
# --------------------------------------------------
simulator = Simulator(
    board=board,
    on_exit_event={
        ExitEvent.MAX_INSTS: exit_event_handler(),
    },
)
# --------------------------------------------------

# Actual simulation starts
# --------------------------------------------------
core_type = processor.get_cores()[0].get_type()
board.set_mem_mode(get_mem_mode(core_type))
if args.fastforward_insts > 0:
    atomic_fastforward_insts = 10_000_000
    kvm_fastforward_insts = args.fastforward_insts - atomic_fastforward_insts
    simulator.schedule_max_insts(kvm_fastforward_insts)
else:
    simulator.schedule_max_insts(args.warmup_insts)
print(f"{BOLD_BLUE}Starting the simulation!{RESET}")
simulator.run()
# --------------------------------------------------
