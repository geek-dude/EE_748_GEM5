import m5

from gem5.components.boards.x86_board import X86Board
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy,
)
from gem5.components.memory.single_channel import SingleChannelDDR3_1600
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.resources.resource import BinaryResource
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator

# === Memory Heirarchy ===
cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
    l1i_size="32KiB",
    l1d_size="32KiB",
    l2_size="256KiB",
    l1d_assoc=8,
    l1i_assoc=8,
    l2_assoc=16,
)

memory = SingleChannelDDR3_1600(size="2GiB")

# Processor setup
processor = SimpleProcessor(
    cpu_type=CPUTypes.O3,
    isa=ISA.X86,
    num_cores=1,
)

# Board setup
board = X86Board(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

# Binary and inputs
binary = BinaryResource("../benchmarks/gcc/gcc_base.gcc41-64bit")
inputs = ["../benchmarks/gcc/166.in"]
board.set_se_binary_workload(binary, arguments=inputs)

# === Setting the instruction limit ===
max_insts = 4_000_000
cpu = board.get_processor().get_cores()[0]
# cpu.get_simobject().scheduleInstStopAnyThread(params() = max_insts
cpu.get_simobject().scheduleInstStopAnyThread(max_insts)


def exit_event_handler():
    print(f"Simulated {max_insts} instructions on O3 core")
    yield True


# Simulator setup
simulator = Simulator(
    board=board,
    checkpoint_path="../gem5_out/gcc/warmup_checkpoint",
    on_exit_event={
        ExitEvent.MAX_INSTS: exit_event_handler(),
    },
)

# Actual simulation starts
print("Starting warmup simulation on O3 cpu")
simulator.run()
print("Simulation Done")
