#!/usr/bin/env python3
"""Type into the isolated Spanish-layout BYPSSD QEMU guest, not the host UI."""
import argparse,base64,json,os,socket,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('text',nargs='?',default='');p.add_argument('--encoded',action='store_true');p.add_argument('--key');p.add_argument('--layout',choices=['es','us'],default='es');a=p.parse_args()
path=os.environ.get('BYPSSD_QMP_SOCKET',str(Path(__file__).resolve().parents[1]/'out/qemu-opensuse-test/qmp.sock'))
s=socket.socket(socket.AF_UNIX);s.settimeout(30);s.connect(path);f=s.makefile('rwb');json.loads(f.readline())
def call(cmd,args=None):
 f.write((json.dumps(dict(execute=cmd,arguments=args or {}))+'\n').encode());f.flush()
 while True:
  result=json.loads(f.readline())
  if 'error' in result:raise RuntimeError(result['error'])
  if 'return' in result:return result['return']
call('qmp_capabilities')
def keys(codes):
 call('input-send-event',{'events':[{'type':'key','data':{'down':True,'key':{'type':'qcode','data':c}}} for c in codes]});time.sleep(.12)
 call('input-send-event',{'events':[{'type':'key','data':{'down':False,'key':{'type':'qcode','data':c}}} for c in reversed(codes)]});time.sleep(.12)
if a.key:keys(a.key.split('-'))
text='echo '+base64.b64encode(a.text.encode()).decode()+' | base64 -d | bash\n' if a.encoded else a.text
mapping={'\t':['tab'],' ':['spc'],'\n':['ret'],'-':['slash'],'+':['bracket_right'],'/':['shift','7'],'=':['shift','0'],'|':['alt_r','1'],'.':['dot'],':':['shift','dot'],'@':['alt_r','2'],'_':['shift','slash']}
if a.layout=='us':
 mapping.update({'-':['minus'],'/':['slash'],'=':['equal'],'+':['shift','equal'],'|':['shift','backslash'],':':['shift','semicolon'],'@':['shift','2'],'_':['shift','minus'],'(':['shift','9'],')':['shift','0'],',':['comma'],'$':['shift','4']})
for c in text:
 if c.isascii() and c.isalnum():keys((['shift',c.lower()] if c.isupper() else [c]))
 elif c in mapping:keys(mapping[c])
 else:raise ValueError('Unsupported Spanish-layout character: '+repr(c))
f.close();s.close()
