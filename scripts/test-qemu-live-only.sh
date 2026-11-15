#!/bin/bash
# Read-only ISO boot: no hard disk, no host directories, no installation target.
set -euo pipefail
cd "$(dirname "$0")/.."
project=$(pwd -P)
run="$project/out/qemu-r8-live-only"
iso="$project/out/BYPSSD-OS-Renacer-1.1-aarch64.iso"
test -f "$iso"
mkdir -p "$run"
[ -f "$run/vars.fd" ] || cp /opt/homebrew/share/qemu/edk2-arm-vars.fd "$run/vars.fd"
exec qemu-system-aarch64 -name BYPSSD-R8-Live-Only -machine virt -accel hvf -cpu host -smp 4 -m 4096 \
 -drive if=pflash,format=raw,readonly=on,file=/opt/homebrew/share/qemu/edk2-aarch64-code.fd \
 -drive "if=pflash,format=raw,file=$run/vars.fd" \
 -device virtio-scsi-pci,id=scsi0 \
 -drive "if=none,id=livecd,format=raw,media=cdrom,readonly=on,file=$iso" \
 -device scsi-cd,drive=livecd,bus=scsi0.0,bootindex=0 \
 -device virtio-gpu-pci -device qemu-xhci -device usb-kbd -device usb-tablet \
 -netdev user,id=net0 -device virtio-net-pci,netdev=net0 \
 -display none -serial "file:$run/serial.log" -monitor none \
 -qmp "unix:$run/qmp.sock,server=on,wait=off"
