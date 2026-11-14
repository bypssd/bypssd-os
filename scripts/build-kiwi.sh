#!/bin/bash
set -euo pipefail
cd /workspace
exec 9>/var/tmp/bypssd-iso.lock
flock -n 9 || { echo 'Another BYPSSD ISO build is running.' >&2; exit 1; }
arch=${BYPSSD_ARCH:-$(uname -m)}
test "$(uname -m)" = "$arch"
export BYPSSD_ARCH="$arch"
python3 scripts/prepare-kiwi.py
for number in $(seq 0 15); do
  [ -b "/dev/loop$number" ] || mknod -m 660 "/dev/loop$number" b 7 "$number"
done
volume=/var/tmp/bypssd-kiwi-work.ext4
work=/var/tmp/bypssd-kiwi-work
mkdir -p "$work"
if [ ! -f "$volume" ]; then
  truncate -s 24G "$volume"
  mkfs.ext4 -F "$volume"
fi
mountpoint -q "$work" || mount -o loop "$volume" "$work"
if [[ "${BYPSSD_KIWI_RESUME:-}" == "$work/"* ]]; then
  run=$(dirname "$BYPSSD_KIWI_RESUME")
else
  run="$work/kiwi-$(date -u +%Y%m%dT%H%M%SZ)"
fi
mkdir -p "$run" /workspace/out/logs
printf '%s\n' "$run" > /workspace/out/logs/latest-kiwi-run.txt
mkdir -p "$run/description"
cp -r "/workspace/kickstart/kiwi/$arch/." "$run/description/"
resume=()
if [ -n "${BYPSSD_KIWI_RESUME:-}" ]; then
  if [ "$BYPSSD_KIWI_RESUME" != "$run/result" ]; then
    cp -a "$BYPSSD_KIWI_RESUME" "$run/result"
  fi
  resume=(--allow-existing-root)
fi
mkdir -p "$work/tmp"
kiwi-ng --temp-dir "$work/tmp" --logfile "$run/kiwi.log" --target-arch "$arch" system build \
  --description "$run/description" --target-dir "$run/result" "${resume[@]}"
cp "$run"/result/*.iso /workspace/out/BYPSSD-OS-Renacer-1.0-$arch.iso
cp "$run/kiwi.log" "/workspace/out/logs/${run##*/}.log"
cp "$run"/result/*.packages /workspace/out/ 2>/dev/null || true
cd /workspace/out
sha256sum BYPSSD-OS-Renacer-1.0-$arch.iso > BYPSSD-OS-Renacer-1.0-$arch.iso.sha256
