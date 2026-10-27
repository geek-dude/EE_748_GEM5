#!/usr/bin/env bash
# EE 748 container launcher. Distributed under the repository LICENSE.
set -euo pipefail
WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# The tracked copy is a template; setup installs it beside gem5/.
if [[ ! -f "$WORKSPACE_DIR/gem5/util/ee748/container.env" ]]; then
    echo 'Run gem5/util/ee748/step_2_setup-gem5-container.sh first.' >&2
    exit 1
fi
source "$WORKSPACE_DIR/gem5/util/ee748/container.env"
command -v docker >/dev/null || { echo 'Install Docker first.' >&2; exit 1; }
docker info >/dev/null 2>&1 || { echo 'Start Docker and verify user access.' >&2; exit 1; }
options=(--rm -i --user "$(id -u):$(id -g)"
    --volume "$WORKSPACE_DIR:/EE_748_gem5"
    --workdir /EE_748_gem5 --env HOME=/EE_748_gem5
    --env XDG_CACHE_HOME=/EE_748_gem5/.cache)
if [[ -t 0 && -t 1 ]]; then options+=(-t); fi
if [[ "${1:-}" == --kvm ]]; then
    shift
    [[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 && -r /dev/kvm && -w /dev/kvm ]] || {
        echo 'KVM mode requires an x86 Linux host with read/write access to /dev/kvm.' >&2
        exit 1
    }
    # perf_event_open is blocked by Docker's default seccomp profile.
    options+=(--device /dev/kvm --group-add "$(stat -c %g /dev/kvm)"
        --cap-add PERFMON --security-opt seccomp=unconfined)
fi
if (( $# == 0 )); then set -- bash; fi
exec docker run "${options[@]}" "$GEM5_IMAGE" "$@"
