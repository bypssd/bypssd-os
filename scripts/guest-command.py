#!/usr/bin/env python3
import socket,sys,time
from pathlib import Path
s=socket.socket(socket.AF_UNIX);s.settimeout(1);s.connect(str(Path(__file__).resolve().parents[1]/'out/qemu-test/serial.sock'))
s.sendall(('\n'+sys.argv[1]+"\nprintf '\\n__DONE__\\n'\n").encode());data=b'';end=time.time()+120
while time.time()<end:
 try:p=s.recv(65536)
 except socket.timeout:continue
 if not p:break
 data+=p
 if b'\r\n__DONE__\r\n' in data:break
print(data.decode(errors='replace'))
