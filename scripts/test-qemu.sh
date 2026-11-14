#!/bin/bash
# Disposable ARM64 test VM. Does not use or inspect Parallels.
set -euo pipefail
cd "$(dirname "$0")/.."
project=$(pwd -P)
test -f out/BYPSSD-OS-Renacer-1.0-aarch64.iso
command -v qemu-system-aarch64 >/dev/null
run="$project/out/qemu-test"
mkdir -p "$run"
if [ ! -f "$run/vars.fd" ]; then
  cp /opt/homebrew/share/qemu/edk2-arm-vars.fd "$run/vars.fd"
fi
if [ ! -f "$run/install.qcow2" ]; then
  qemu-img create -f qcow2 "$run/install.qcow2" 24G
fi
serial=(-chardev stdio,id=serial0,signal=off -serial chardev:serial0)
if [ "${BYPSSD_TEST_SERIAL_SOCKET:-0}" = 1 ]; then
  serial=(-chardev "socket,id=serial0,path=$run/serial.sock,server=on,wait=off" -serial chardev:serial0)
fi
cdrom=()
if [ "${BYPSSD_TEST_INSTALLED:-0}" != 1 ]; then
  cdrom=(-drive "if=none,id=livecd,format=raw,media=cdrom,readonly=on,file=$project/out/BYPSSD-OS-Renacer-1.0-aarch64.iso" -device scsi-cd,drive=livecd,bus=scsi0.0,bootindex=0)
fi
exec qemu-system-aarch64 \
  -name BYPSSD-ISO-Test -machine virt -accel hvf -cpu host -smp 4 -m 4096 \
  -drive if=pflash,format=raw,readonly=on,file=/opt/homebrew/share/qemu/edk2-aarch64-code.fd \
  -drive "if=pflash,format=raw,file=$run/vars.fd" \
  -device virtio-scsi-pci,id=scsi0 \
  ${cdrom[@]+"${cdrom[@]}"} \
  -drive "if=none,id=testdisk,format=qcow2,file=$run/install.qcow2" \
  -device virtio-blk-pci,drive=testdisk,bootindex=1 \
  -device virtio-gpu-pci -device qemu-xhci -device usb-kbd -device usb-tablet \
  -netdev user,id=net0 -device virtio-net-pci,netdev=net0 \
  -display none "${serial[@]}" -monitor none \
  -qmp "unix:$run/qmp.sock,server=on,wait=off"
