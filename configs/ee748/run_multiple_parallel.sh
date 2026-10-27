#!/usr/bin/env bash
# Distributed under the repository LICENSE.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/run_benchmarks.py" --jobs "${MAX_JOBS:-2}" "$@"
