#!/usr/bin/env bash
# Prepare an already-cloned course repo. Distributed under repository LICENSE.
set -euo pipefail
if (( EUID == 0 )); then echo 'Run without sudo.' >&2; exit 1; fi
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
WORKSPACE_DIR="$(dirname "$REPO_DIR")"
[[ "$(basename "$REPO_DIR")" == gem5 ]] || {
    echo 'Clone the course repository into EE_748_gem5/gem5 first.' >&2; exit 1;
}
command -v docker >/dev/null || { echo 'Install Docker first.' >&2; exit 1; }
docker info >/dev/null 2>&1 || {
    echo 'Start Docker; if newly installed, log out and back in.' >&2; exit 1;
}
source "$SCRIPT_DIR/container.env"
docker pull "$GEM5_IMAGE"
mkdir -p "$WORKSPACE_DIR/benchmarks" "$WORKSPACE_DIR/gem5_out"
LAUNCHER="$WORKSPACE_DIR/run-gem5-container.sh"
if [[ -e "$LAUNCHER" ]] && ! cmp -s "$SCRIPT_DIR/run-gem5-container.sh" "$LAUNCHER"; then
    echo "Existing launcher differs; preserving it at $LAUNCHER" >&2
    echo 'Compare it with util/ee748/run-gem5-container.sh before replacing it.' >&2
    exit 1
fi
cp "$SCRIPT_DIR/run-gem5-container.sh" "$LAUNCHER"
chmod +x "$LAUNCHER"
echo "Container environment prepared in $WORKSPACE_DIR"
echo 'Enter with ./run-gem5-container.sh from that directory.'
echo 'Then: cd gem5 && scons build/X86/gem5.opt -j2'
