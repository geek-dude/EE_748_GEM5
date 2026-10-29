#!/usr/bin/env bash
# Distributed under the repository LICENSE.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Respect CPU affinity when choosing the number of concurrent simulations.
DEFAULT_JOBS="$(python3 -c 'import os; n = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else (os.cpu_count() or 1); print(max(1, n - 1))')"
echo "Parallel simulations may make your PC sluggish; lower MAX_JOBS if needed." >&2
exec python3 "$SCRIPT_DIR/run_benchmarks.py" --mode kvm --jobs "${MAX_JOBS:-$DEFAULT_JOBS}" "$@"
