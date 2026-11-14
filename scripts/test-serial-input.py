#!/usr/bin/env python3
import socket,sys,time,select
from pathlib import Path
r=Path(__file__).resolve().parents[1]
s=socket.socket(socket.AF_UNIX);s.connect(str(r/'out/qemu-test/serial.sock'))
s.sendall((sys.argv[1]+'\n').encode());end=time.time()+float(sys.argv[2] if len(sys.argv)>2 else 8)
with (r/'out/logs/qemu-install-interactive.log').open('ab') as f:
 while time.time()<end:
  if select.select([s],[],[],.5)[0]:
   b=s.recv(65536)
   if not b:break
   f.write(b);f.flush();sys.stdout.buffer.write(b);sys.stdout.buffer.flush()
