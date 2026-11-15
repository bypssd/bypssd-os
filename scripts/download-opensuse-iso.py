#!/usr/bin/env python3
"""Download and assemble a BYPSSD ISO, verifying each part and the full image."""
import argparse,hashlib,json,pathlib,urllib.request,time
p=argparse.ArgumentParser();p.add_argument('arch',choices=['aarch64','x86_64']);p.add_argument('--tag',default='renacer-1.1-opensuse-r7');p.add_argument('--out',default='out');a=p.parse_args()
base=f'https://github.com/bypssd/bypssd-os/releases/download/{a.tag}/'
with urllib.request.urlopen(base+f'iso-parts-{a.arch}.json?check={time.time_ns()}',timeout=180) as response:m=json.load(response)
assert m['architecture']==a.arch and m['iso']==f'BYPSSD-OS-Renacer-1.1-{a.arch}.iso'
out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True);target=out/m['iso'];temp=target.with_name(target.name+'.partial')
if target.exists():
 digest=hashlib.sha256()
 with target.open('rb') as existing:
  for block in iter(lambda:existing.read(8*1024**2),b''):digest.update(block)
 if target.stat().st_size==m['bytes'] and digest.hexdigest()==m['sha256']:
  print('ISO ya descargada y SHA256 verificado:',target);raise SystemExit(0)
 raise SystemExit('El archivo existente corresponde a otra imagen. Consérvalo y utiliza --out con otra carpeta: '+str(target))
whole=hashlib.sha256();total=0
with temp.open('xb') as dest:
 for part in m['parts']:
  if pathlib.Path(part['name']).name!=part['name']:raise SystemExit('Nombre de parte inválido')
  print('Descargando',part['name'],flush=True);digest=hashlib.sha256();size=0
  with urllib.request.urlopen(base+part['name'],timeout=180) as response:
   while True:
    block=response.read(8*1024**2)
    if not block:break
    dest.write(block);digest.update(block);whole.update(block);size+=len(block);total+=len(block)
  if size!=part['bytes'] or digest.hexdigest()!=part['sha256']:raise SystemExit('Parte incorrecta; se conserva .partial para revisión')
if total!=m['bytes'] or whole.hexdigest()!=m['sha256']:raise SystemExit('ISO incorrecta; se conserva .partial para revisión')
temp.rename(target);target.with_suffix('.iso.sha256').write_text(m['sha256']+'  '+target.name+'\n');print('ISO completa y SHA256 verificado:',target)
