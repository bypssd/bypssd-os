#!/bin/bash
# Integration check in an isolated privileged CI container, never a user disk.
set -euxo pipefail
zypper -n install --no-recommends grub2 dosfstools e2fsprogs sddm-qt6 xorg-x11-server-Xvfb ImageMagick qt6-declarative-imports
qa=$(mktemp -d /var/tmp/bypssd-check.XXXXXX)
truncate -s 128M "$qa/boot.img"
truncate -s 64M "$qa/efi.img"
mkfs.ext4 -F "$qa/boot.img"
mkfs.vfat "$qa/efi.img"
mkdir -p /boot
mount -o loop "$qa/boot.img" /boot
mkdir -p /boot/grub2 /boot/efi
mount -o loop "$qa/efi.img" /boot/efi
cleanup() { umount /boot/efi || true; umount /boot || true; }
trap cleanup EXIT
printf 'set timeout=3\n' > /boot/grub2/grub.cfg
BYPSSD_EFI_TEST=1 sh opensuse/bypssd-efi-config
expected=$(grub2-probe --target=fs_uuid /boot/grub2)
grep -F "$expected" /boot/efi/EFI/BYPSSD/grub.cfg
grep -F '/grub2/grub.cfg' /boot/efi/EFI/BYPSSD/grub.cfg
cmp /boot/efi/EFI/BYPSSD/grub.cfg /boot/efi/EFI/BOOT/grub.cfg
printf '# Configuración nativa que debe conservarse\n' > /boot/efi/EFI/BYPSSD/grub.cfg
BYPSSD_EFI_TEST=1 sh opensuse/bypssd-efi-config
cmp /boot/efi/EFI/BYPSSD/grub.cfg /boot/efi/EFI/BOOT/grub.cfg
grep -F 'debe conservarse' /boot/efi/EFI/BYPSSD/grub.cfg
cleanup
trap - EXIT
mkdir -p /usr/share/bypssd
cp assets/logo-256.png assets/wallpaper.png /usr/share/bypssd/
mkdir -p "$qa/runtime"
chmod 700 "$qa/runtime"
Xvfb :99 -screen 0 1280x800x24 -ac >out/logs/sddm-xvfb.log 2>&1 &
xpid=$!
sleep 2
greeter=$(command -v sddm-greeter-qt6 || command -v sddm-greeter)
DISPLAY=:99 XDG_RUNTIME_DIR="$qa/runtime" QT_QUICK_BACKEND=software "$greeter" --test-mode --theme /workspace/branding/sddm >out/logs/sddm-preview.log 2>&1 &
gpid=$!
sleep 6
kill -0 "$gpid"
if grep -Ei 'Type .* unavailable|Cannot assign|is not a type|Expected token|Cannot load.*Main.qml|failed to load' out/logs/sddm-preview.log; then exit 1; fi
DISPLAY=:99 import -window root out/logs/sddm-preview.png
kill "$gpid" "$xpid"
echo 'BYPSSD_INSTALL_AND_LOGIN_CHECK_OK'
