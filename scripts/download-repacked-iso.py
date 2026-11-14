#!/usr/bin/env python3
"""Reuse an identical-layout local ISO, accepting it only on an exact GitHub SHA256 match."""
from pathlib import Path
import hashlib,json,subprocess,sys
metadata=Path(sys.argv[1]);source=Path(sys.argv[2]);target=Path(sys.argv[3])
asset=next(x for x in json.loads(metadata.read_text())['assets'] if x['name']==target.name)
if source.stat().st_size!=asset['size']:raise SystemExit('Layouts differ; use a full download.')
expected=asset.get('digest','').removeprefix('sha256:')
if len(expected)!=64:raise SystemExit('No authoritative SHA256 digest supplied')
target.parent.mkdir(parents=True,exist_ok=True)
subprocess.run(['cp','-c',str(source),str(target)],check=True)
window=64*1024*1024
for label,start,end in [('head',0,window-1),('tail',asset['size']-window,asset['size']-1)]:
 chunk=target.with_suffix('.'+label+'.range')
 print(f'Downloading {label}: {start}-{end}',flush=True)
 subprocess.run(['curl','--fail','--location','--silent','--show-error','--retry','2','--max-filesize',str(window),'--range',f'{start}-{end}','--output',str(chunk),asset['browser_download_url']],check=True)
 if chunk.stat().st_size!=end-start+1:raise SystemExit('Range length mismatch; use a full download.')
 with target.open('r+b') as out,chunk.open('rb') as data:
  out.seek(start)
  while block:=data.read(1024*1024):out.write(block)
with target.open('rb') as data:actual=hashlib.file_digest(data,'sha256').hexdigest()
print(json.dumps({'file':target.name,'expected':expected,'actual':actual,'exact_match':actual==expected}),flush=True)
if actual!=expected:raise SystemExit('Full verification failed; use a full download.')
