import m5

from gem5.components.boards.x86_board import X86Board
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.components.memory.single_channel import SingleChannelDDR3_1600
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.resources.resource import BinaryResource
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator

# === Memory Heirarchy ===
cache_hierarchy = NoCache()

memory = SingleChannelDDR3_1600(size="2GiB")

# Processor setup
processor = SimpleProcessor(
    cpu_type=CPUTypes.ATOMIC,
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
ffwd_insts = 1_000_000
cpu = board.get_processor().get_cores()[0]
cpu.get_simobject().max_insts_all_threads = ffwd_insts


def exit_event_handler():
    print(f"Simulated {ffwd_insts} instructions on ATOMIC core")
    simulator.save_checkpoint("../gem5_out/gcc/ff_checkpoint")
    print("Saved checkpoint")
    yield True


# Simulator setup
simulator = Simulator(
    board=board,
    on_exit_event={
        ExitEvent.MAX_INSTS: exit_event_handler(),
    },
)

# Actual simulation starts
print("Starting fast forward simulation on ATOMIC cpu")
simulator.run()
print("Simulation Done")
