#!/usr/bin/env python3
"""Boot the candidate and open the real desktop installer, without installing."""
from pathlib import Path
import os,socket,subprocess,time
r=Path(__file__).resolve().parents[1]
browser=os.environ.get('BYPSSD_TEST_BROWSER')=='1'
log=(r/('out/logs/browser-r6-serial.log' if browser else 'out/logs/anaconda-graphical-serial.log')).open('ab',buffering=0)
proc=subprocess.Popen(['bash',str(r/'scripts/test-qemu.sh')],cwd=r,env=dict(os.environ,BYPSSD_TEST_SERIAL_SOCKET='1'),stdout=log,stderr=log)
s=socket.socket(socket.AF_UNIX);s.settimeout(1)
for _ in range(120):
 try:s.connect(str(r/'out/qemu-test/serial.sock'));break
 except (ConnectionRefusedError,FileNotFoundError):time.sleep(.5)
buffer=b''
def until(marker,timeout=180):
 global buffer
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  if marker in buffer:
   a,buffer=buffer.split(marker,1);return a
  try:data=s.recv(65536)
  except socket.timeout:continue
  if not data:raise EOFError
  log.write(data);buffer+=data
 raise TimeoutError(marker)
def command(t):
 global buffer
 buffer=b'';s.sendall((t+"\nprintf '\\n__DONE__\\n'\n").encode());return until(b'\r\n__DONE__\r\n')
until(b'login: ');s.sendall(b'root\n');until(b']# ')
command('stty -echo; for n in $(seq 1 60); do pgrep -u liveuser -x plasmashell >/dev/null && break; sleep 1; done; sleep 5; rpm -q bypssd-branding; dnf repo list')
if browser:
    print('New live image booted; launching Chromium with its real first-run defaults.',flush=True)
    command('runuser -u liveuser -- env XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus systemd-run --user --collect chromium-browser')
    time.sleep(20)
    print(command('chromium-browser --version; find /usr/share/plasma/look-and-feel -maxdepth 1 -type d; getenforce').decode(errors='replace'),flush=True)
else:
    print('New live image booted; launching the actual installer as liveuser.',flush=True)
    command('runuser -u liveuser -- env XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus /usr/libexec/bypssd-liveinst > /tmp/bypssd-gui-installer.log 2>&1 &')
    time.sleep(25)
    print(command('cat /tmp/bypssd-gui-installer.log; pgrep -af anaconda; getenforce').decode(errors='replace'),flush=True)
print('GUI ready for screenshot. QEMU remains running for inspection.',flush=True)

s.close()
proc.wait()
