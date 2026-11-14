#!/usr/bin/env python3
"""Enter only the disposable laboratory credentials in the QEMU guest."""
import json,socket,time,sys
from pathlib import Path
s=socket.socket(socket.AF_UNIX);s.connect(str(Path(__file__).resolve().parents[1]/'out/qemu-test/qmp.sock'));f=s.makefile('rwb',buffering=0)
def request(name,arguments=None):
 d={'execute':name}
 if arguments:d['arguments']=arguments
 f.write(json.dumps(d).encode()+b'\n')
 while True:
  r=json.loads(f.readline())
  if 'return' in r:return r
  if 'error' in r:raise RuntimeError(r)
f.readline();request('qmp_capabilities')
for char in ('bypssd-test-only\n' if '--password-only' in sys.argv else 'bypssdtest\tbypssd-test-only\n'):
 key={'\t':'tab','\n':'ret','-':'slash'}.get(char,char)
 request('send-key',{'keys':[{'type':'qcode','data':key}],'hold-time':40});time.sleep(.10)
print('Laboratory credentials submitted to SDDM.')
