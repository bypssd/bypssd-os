#!/usr/bin/env python3
import argparse,json,os,socket,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('x',type=int);p.add_argument('y',type=int);p.add_argument('--double',action='store_true');p.add_argument('--width',type=int,default=1280);p.add_argument('--height',type=int,default=800);a=p.parse_args()
s=socket.socket(socket.AF_UNIX);s.connect(os.environ.get('BYPSSD_QMP_SOCKET',str(Path(__file__).resolve().parents[1]/'out/qemu-opensuse-direct/qmp.sock')));f=s.makefile('rwb');json.loads(f.readline())
def call(cmd,args):
 f.write((json.dumps({'execute':cmd,'arguments':args})+'\n').encode());f.flush()
 while True:
  r=json.loads(f.readline())
  if 'error' in r:raise RuntimeError(r['error'])
  if 'return' in r:return
call('qmp_capabilities',{})
call('input-send-event',{'events':[{'type':'abs','data':{'axis':'x','value':int(a.x*32767/a.width)}},{'type':'abs','data':{'axis':'y','value':int(a.y*32767/a.height)}}]})
for i in range(2 if a.double else 1):
 for down in (True,False):
  call('input-send-event',{'events':[{'type':'btn','data':{'down':down,'button':'left'}}]});time.sleep(.08)
time.sleep(.7)
f.close();s.close()
