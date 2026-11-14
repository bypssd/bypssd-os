#!/bin/bash
set -euo pipefail
cd /workspace
exec 9>/var/tmp/bypssd-iso.lock
flock -n 9 || { echo 'Another BYPSSD ISO build is running.' >&2; exit 1; }
if pgrep -f '^/usr/bin/python3 /usr/bin/anaconda' >/dev/null; then
  echo 'Anaconda from an earlier build is still running; restart this build container first.' >&2
  exit 1
fi
# A container restart preserves /run; Anaconda reads this error file on startup.
rm -f /run/anaconda.pid /run/anaconda/installation-error-msg /run/anaconda/bus.address /run/anaconda/anaconda.conf
mkdir -p /run/dbus
dbus-uuidgen --ensure
if ! dbus-send --system --type=method_call --print-reply --dest=org.freedesktop.DBus / org.freedesktop.DBus.ListNames >/dev/null 2>&1; then
  rm -f /run/dbus/pid
  dbus-daemon --system --fork --nopidfile
fi
test "$(uname -m)" = aarch64
ksvalidator -v F45 kickstart/bypssd.ks
test -f out/rpms/repodata/repomd.xml
for number in $(seq 0 15); do
  if [ ! -b "/dev/loop$number" ]; then
    mknod -m 660 "/dev/loop$number" b 7 "$number"
  fi
done
run=/var/tmp/bypssd-lmc-$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$run/tmp" /workspace/out/logs
printf '%s\n' "$run" > /workspace/out/logs/latest-lmc-run.txt
python3 -m http.server 8765 --bind 127.0.0.1 --directory /workspace/out/rpms > "$run/repo-http.log" 2>&1 &
repo_pid=$!
trap 'kill "$repo_pid" 2>/dev/null || true; mkdir -p "/workspace/out/logs/${run##*/}"; cp -a "$run"/*.log "/workspace/out/logs/${run##*/}/" 2>/dev/null || true; cp /tmp/packaging.log "/workspace/out/logs/${run##*/}/anaconda-packaging.log" 2>/dev/null || true' EXIT
python3 - <<'PY'
import time, urllib.request
for attempt in range(20):
    try:
        urllib.request.urlopen('http://127.0.0.1:8765/repodata/repomd.xml').read()
        break
    except OSError:
        time.sleep(0.2)
else:
    raise SystemExit('Local RPM repository did not start')
PY
livemedia-creator --no-virt --make-iso --ks /workspace/kickstart/bypssd.ks \
  --project "BYPSSD OS" --volid BYPSSD --releasever 45 --arch aarch64 \
  --nomacboot --iso-only --iso-name BYPSSD-OS-Renacer-1.0-aarch64.iso \
  --compression xz --compress-arg=-processors --compress-arg=4 \
  --compress-arg=-mem --compress-arg=1G \
  --resultdir "$run/result" --tmp "$run/tmp" --logfile "$run/livemedia.log"
cp "$run/result/BYPSSD-OS-Renacer-1.0-aarch64.iso" /workspace/out/
cd /workspace/out
sha256sum BYPSSD-OS-Renacer-1.0-aarch64.iso > BYPSSD-OS-Renacer-1.0-aarch64.iso.sha256
