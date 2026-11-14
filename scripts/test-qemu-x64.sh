#!/bin/bash
# Isolated x86_64 UEFI boot test using TCG on the ARM Mac; no host disks/shared folders.
set -euo pipefail
cd "$(dirname "$0")/.."
project=$(pwd -P)
run="$project/out/qemu-x64-test"
mkdir -p "$run"
[ -f "$run/vars.fd" ] || cp /opt/homebrew/share/qemu/edk2-i386-vars.fd "$run/vars.fd"
exec qemu-system-x86_64 -name BYPSSD-x64-Test -machine q35 -accel tcg,thread=multi \
 -cpu max -smp 2 -m 4096 \
 -drive if=pflash,format=raw,readonly=on,file=/opt/homebrew/share/qemu/edk2-x86_64-code.fd \
 -drive "if=pflash,format=raw,file=$run/vars.fd" \
 -drive "file=$project/out/BYPSSD-OS-Renacer-1.0-x86_64.iso,media=cdrom,readonly=on,format=raw" \
 -device virtio-vga -device qemu-xhci -device usb-kbd -device usb-tablet \
 -netdev user,id=net0 -device virtio-net-pci,netdev=net0 \
 -display none -serial stdio -monitor none -qmp "unix:$run/qmp.sock,server=on,wait=off"
