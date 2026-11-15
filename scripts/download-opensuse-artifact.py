#!/usr/bin/env python3
"""Transfer a temporary CI-built ISO to out/ and verify its SHA256."""
import argparse,hashlib,pathlib,subprocess,shutil,json
p=argparse.ArgumentParser();p.add_argument('run');p.add_argument('arch',choices=['aarch64','x86_64']);a=p.parse_args()
r=pathlib.Path(__file__).resolve().parents[1];stage=r/'out/actions-transfer'/a.run/a.arch;stage.mkdir(parents=True,exist_ok=True)
subprocess.run(['gh','run','download',a.run,'--repo','bypssd/bypssd-os','--name','opensuse-delivery-'+a.arch,'--dir',str(stage)],check=True)
name=f'BYPSSD-OS-Renacer-1.1-{a.arch}.iso';images=list(stage.rglob(name));assert len(images)==1
src=images[0];checksum=src.with_suffix('.iso.sha256');expected=checksum.read_text().split()[0];digest=hashlib.sha256()
with src.open('rb') as f:
 for block in iter(lambda:f.read(8*1024**2),b''):digest.update(block)
if digest.hexdigest()!=expected:raise SystemExit('SHA256 incorrecto; se conserva el archivo para revisión')
target=r/'out'/name
if target.exists():raise SystemExit('Ya existe el destino: '+str(target))
size=src.stat().st_size;src.rename(target);shutil.copy2(checksum,target.with_suffix('.iso.sha256'))
for prefix in ['audit-opensuse','package-manifest-opensuse']:
 for path in stage.rglob(prefix+'-*'):
  shutil.copy2(path,r/'out'/(path.stem+'-r8'+path.suffix))
(r/'out'/f'delivery-r8-{a.arch}.json').write_text(json.dumps({'run':a.run,'arch':a.arch,'iso':name,'bytes':size,'sha256':expected},indent=2)+'\n')
print('ISO completa y SHA256 verificado:',target,flush=True)
