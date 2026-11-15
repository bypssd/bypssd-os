#!/usr/bin/env python3
"""Publish complete images as verified parts below the GitHub asset size limit."""
import argparse,hashlib,json,pathlib,subprocess
p=argparse.ArgumentParser();p.add_argument('directory');p.add_argument('arch',choices=['aarch64','x86_64']);p.add_argument('--tag',default='renacer-1.1-opensuse-r1');a=p.parse_args();root=pathlib.Path(a.directory)
iso=next(root.rglob(f'BYPSSD-OS-Renacer-1.1-{a.arch}.iso'));manifest=iso.with_suffix('.iso.sha256');expected=manifest.read_text().split()[0]
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
if sha(iso)!=expected:raise SystemExit('ISO checksum mismatch')
def gh(*x):return subprocess.check_output(['gh',*x,'--repo','bypssd/bypssd-os'],text=True)
assets={x['name']:x for x in json.loads(gh('release','view',a.tag,'--json','assets'))['assets']}
def upload(path):
 old=assets.get(path.name)
 if old:
  if old['size']!=path.stat().st_size:raise SystemExit('Published asset mismatch: '+path.name)
  return
 gh('release','upload',a.tag,str(path))
parts=[]
if iso.stat().st_size<2*1024**3:
 upload(iso);parts=[{'name':iso.name,'bytes':iso.stat().st_size,'sha256':expected}]
else:
 with iso.open('rb') as src:
  number=0
  while True:
   first=src.read(8*1024**2)
   if not first:break
   number+=1;part=iso.with_name(iso.name+f'.part{number:03d}');left=1900*1024**2-len(first)
   with part.open('wb') as out:
    out.write(first)
    while left:
     blob=src.read(min(left,8*1024**2))
     if not blob:break
     out.write(blob);left-=len(blob)
   parts.append({'name':part.name,'bytes':part.stat().st_size,'sha256':sha(part)});upload(part)
record={'architecture':a.arch,'iso':iso.name,'bytes':iso.stat().st_size,'sha256':expected,'parts':parts}
record_path=iso.parent/f'iso-parts-{a.arch}.json';record_path.write_text(json.dumps(record,indent=2)+'\n');upload(record_path);upload(manifest)
for pattern in (f'package-manifest-opensuse-{a.arch}.txt',f'audit-opensuse-{a.arch}.json'):
 for path in root.rglob(pattern):upload(path)
pkg=f'bypssd-opensuse-1.1-{a.arch}'
try:gh('release','view',pkg)
except subprocess.CalledProcessError:gh('release','create',pkg,'--prerelease','--title',f'BYPSSD branding y fuentes · openSUSE {a.arch}','--notes','Branding BYPSSD nativo de openSUSE; RPM propio y fuente, sin firma de producción.')
old={x['name'] for x in json.loads(gh('release','view',pkg,'--json','assets'))['assets']}
for path in root.rglob('*.rpm'):
 if path.name not in old:gh('release','upload',pkg,str(path));old.add(path.name)
print(json.dumps(record,indent=2))
