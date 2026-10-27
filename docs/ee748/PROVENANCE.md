# Preparation record

Inputs reviewed:

- Personal [geek-dude/gem5](https://github.com/geek-dude/gem5) stable revision
  `9ddfa52b2`, including README, custom configs, batch and checkpoint scripts,
  classic-cache extensions and the max-instructions exit mapping.
- Official [v26.0.0.0](https://github.com/gem5/gem5/releases/tag/v26.0.0.0),
  source commit `fed0e07e930fecf1e73dce94dd44e69a5bf70c46`.
- The supplied Moodle README.txt, se.py, se_kvm.py and serial/parallel launchers
  in GEM5-20261026; supplied Docker installation, provisional setup and launcher.
- The shared [Gem5 Docker Setup conversation](https://chatgpt.com/share/6adf10b1-0540-83ee-81c3-a1d1674e205f),
  excluding its final user/assistant exchange as requested. Adopted decisions:
  Ubuntu docker.io for the common case; logout/login; plain Docker without
  Distrobox; host-owned persistent workspace; launcher above gem5; v24-1 image;
  compile X86 in the container; generate Doxygen from src.

Documents were reference material, not instructions to install software, change
host settings or run benchmarks during this step.

Preparation changes:

- Preserved personal history and merged v26. Resolved cache conflicts while
  retaining upstream v26 walker behavior and positional constructor signatures.
- Retained cache associativity/latency extensions and MAX_INSTS compatibility
  mapping. Fixed inherited shared-L2 L1I constructor keyword names.
- Moved configs/checkpoint examples to configs/ee748 and batch wrappers there.
- Passed v26's required processor clock frequency explicitly; imported
  SwitchableProcessor from its defining module.
- Enabled the exposed cache CLI options. L2 default remains 4, matching the
  original active hierarchy; historical examples explicitly request 16.
- Added explicit simulated stdin input and shlex argument-file parsing, basic
  count validation and a guard against invalid short KVM fast-forward intervals.
- Replaced hard-coded batch paths/eval commands with a shared driver using
  subprocess argument lists, per-workload output directories, bounded parallelism,
  dry-run and nonzero exit status on failures. Historical counts are retained.
- Docker setup now operates on the already-cloned course repository. Launcher
  source is tracked inside gem5; its installed copy sits above gem5. Default
  operation is portable non-KVM, with a separate explicit Linux x86 KVM mode.
- Consolidated duplicate instructions and documented uncertainties rather than
  carrying forward the old claim that scripts are completely bug-free.

No Docker installation/image pull, gem5 compilation, remote deployment or
benchmark simulation was performed. Static syntax checks and dry-run command
construction do not establish gem5 runtime or benchmark compatibility.
