#!/usr/bin/env bash
# EE 748 Ubuntu Docker setup. Distributed under the repository LICENSE.
set -euo pipefail
if (( EUID == 0 )); then
    echo 'Run as your normal user, without sudo; sudo will prompt when needed.' >&2
    exit 1
fi
if command -v docker >/dev/null && docker info >/dev/null 2>&1; then
    echo 'Docker is already available to this user.'
    exit 0
fi
source /etc/os-release
if [[ "$ID" != ubuntu || ! -d /run/systemd/system ]]; then
    echo 'Automatic installation requires native Ubuntu with systemd.' >&2
    echo 'For other systems, follow the Docker instructions in README.md.' >&2
    exit 1
fi
sudo -v
if ! command -v docker >/dev/null; then
    sudo apt update
    sudo apt install -y docker.io
fi
sudo systemctl enable --now docker
sudo groupadd -f docker
sudo usermod -aG docker "$(id -un)"
echo 'Log out of the desktop session and log back in before container setup.'
echo 'Then verify: docker run --rm hello-world'
