#!/bin/bash
# Disposable guest only: runtime root console for automated installation QA.
set -eu
case "$(systemd-detect-virt --vm)" in qemu|kvm) ;; *) echo "QA requiere QEMU" >&2; exit 1 ;; esac
console=${1:-ttyS0}
mkdir -p "/run/systemd/system/serial-getty@$console.service.d"
cat > "/run/systemd/system/serial-getty@$console.service.d/qa.conf" <<'CFG'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin root --noclear %I 115200 vt100
CFG
systemctl daemon-reload
systemctl restart "serial-getty@$console.service"
