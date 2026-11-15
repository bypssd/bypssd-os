#!/bin/bash
# Test only a new project-owned ARM virtual disk. Never accesses Parallels.
set -euo pipefail
cd "$(dirname "$0")/.."
export BYPSSD_QEMU_RUN_DIR="$PWD/out/qemu-opensuse-test"
export BYPSSD_TEST_ISO="$PWD/out/BYPSSD-OS-Renacer-1.1-aarch64.iso"
export BYPSSD_TEST_SERIAL_SOCKET=1
exec bash scripts/test-qemu.sh
