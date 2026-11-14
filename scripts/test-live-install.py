#!/usr/bin/env python3
"""Install to the disposable QEMU disk only; never accesses host block devices."""
from pathlib import Path
import base64
import os
import socket
import subprocess
import sys
import json
import time

root=Path(__file__).resolve().parents[1]
run=root/'out/qemu-test'
run.mkdir(parents=True,exist_ok=True)
env=dict(os.environ,BYPSSD_TEST_SERIAL_SOCKET='1')
log=(root/'out/logs/qemu-install-serial.log').open('ab',buffering=0)
qlog=(root/'out/logs/qemu-install-process.log').open('ab',buffering=0)
attach=os.environ.get('BYPSSD_TEST_ATTACH')=='1'
guest=None if attach else subprocess.Popen(['bash',str(root/'scripts/test-qemu.sh')],cwd=root,env=env,stdout=qlog,stderr=qlog)
sock=socket.socket(socket.AF_UNIX)
sock.settimeout(1)
for attempt in range(120):
    try:
        sock.connect(str(run/'serial.sock'))
        break
    except (FileNotFoundError,ConnectionRefusedError):
        if guest is not None and guest.poll() is not None:raise SystemExit('QEMU failed to start; see qemu-install-process.log')
        time.sleep(0.5)
else:raise SystemExit('QEMU serial socket not ready')
pending=b''
def read_until(marker,timeout):
    global pending
    end=time.monotonic()+timeout
    while time.monotonic()<end:
        if marker in pending:
            before,pending=pending.split(marker,1)
            return before+marker
        try:data=sock.recv(65536)
        except socket.timeout:continue
        if not data:raise EOFError('Guest console closed')
        log.write(data)
        pending+=data
    raise TimeoutError('Guest did not reach '+repr(marker))
def command(text):
    global pending
    pending=b''
    sock.sendall((text+"\nprintf '\\n__BYPSSD_COMMAND_DONE__\\n'\n").encode())
    return read_until(b'\r\n__BYPSSD_COMMAND_DONE__\r\n',180)

if attach:
    sock.sendall(b'\nroot\n')
else:
    read_until(b'login: ',240)
    sock.sendall(b'root\n')
read_until(b']# ',60)
command('stty -echo; export SYSTEMD_PAGER=cat PAGER=cat; getenforce; systemctl is-active sddm bypssd-live')
print('Live boot and root console reached.',flush=True)
command('for attempt in $(seq 1 60); do pgrep -u liveuser -x plasmashell >/dev/null && break; sleep 1; done; sleep 5')
picture=run/'final-live-desktop.ppm'
subprocess.run([sys.executable,str(root/'scripts/qmp.py'),'screendump',json.dumps({'filename':str(picture)})],check=True)
subprocess.run(['sips','-s','format','png',str(picture),'--out',str(run/'final-live-desktop.png')],check=True)
ks=(run/'install-test.ks').read_bytes()
encoded=base64.b64encode(ks).decode()
command("printf '%s' '"+encoded+"' | base64 -d > /usr/share/anaconda/interactive-defaults.ks")
command('anaconda-cleanup; rm -f /run/anaconda/installation-error-msg /run/anaconda.pid; while IFS= read -r bypssd_variable; do export "$bypssd_variable"; done < <(runuser -u liveuser -- env XDG_RUNTIME_DIR=/run/user/1000 systemctl --user show-environment)')
# --liveinst deliberately ignores an explicit kickstart. Feed its documented
# interactive defaults only in this disposable VM, retaining the live payload.
command("setenforce 0; export PKEXEC_UID=1000 ANACONDA_PRODUCTNAME='BYPSSD OS' ANACONDA_PRODUCTVERSION='Renacer 1.0'")
# Live mode remains interactive even with defaults; select and commit the only
# attached disposable disk through Anaconda's text UI, rather than --cmdline.
sock.sendall(b'anaconda --liveinst --text\n')
read_until(b"actualizar]: ",120)
for answer in ('3','c','c','c'):
    sock.sendall((answer+'\n').encode())
    read_until(b"actualizar]: ",120)
sock.sendall(b'b\n')
print('Anaconda disk installation started.',flush=True)
end=time.monotonic()+1800
try:
    while time.monotonic()<end:
        try:data=sock.recv(65536)
        except socket.timeout:continue
        if not data:break
        log.write(data)
        text=data.decode(errors='replace')
        print(text,flush=True)
        if 'Traceback' in text or 'El instalador terminará ahora' in text:
            raise RuntimeError('Anaconda failed; see qemu-install-serial.log')
    else:raise TimeoutError('Installation exceeded 30 minutes')
except EOFError:
    pass
if guest is not None:
    guest.wait(timeout=90)
    if guest.returncode:raise SystemExit(guest.returncode)
print('Guest powered off. Installed disk must now be boot-tested.',flush=True)
