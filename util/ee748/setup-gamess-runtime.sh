#!/usr/bin/env bash
# Optional x86 GAMESS runtime. Distributed under repository LICENSE.
set -euo pipefail
[[ "$(uname -m)" == x86_64 ]] || { echo 'Requires an x86_64 container.' >&2; exit 1; }
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNTIME_DIR="$(dirname "$REPO_DIR")/legacy-runtime"
mkdir -p "$RUNTIME_DIR"
cd "$RUNTIME_DIR"
curl --fail --location --retry 3 -o libgfortran3.deb https://archive.ubuntu.com/ubuntu/pool/universe/g/gcc-6/libgfortran3_6.4.0-17ubuntu1_amd64.deb
echo 'a82368f16a9e4ff0cde8269a6c26d7727367b61b4586d51694641c0b156327fa  libgfortran3.deb' | sha256sum -c -
dpkg-deb --extract libgfortran3.deb .
echo 'GAMESS runtime prepared outside the repository; no system packages changed.'
