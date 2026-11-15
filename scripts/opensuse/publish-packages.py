#!/usr/bin/env python3
"""Publish only BYPSSD's native branding RPM and SRPM, never ISO images."""
import argparse,hashlib,json,pathlib,subprocess
p=argparse.ArgumentParser();p.add_argument('directory');p.add_argument('arch',choices=['aarch64','x86_64']);p.add_argument('--tag',required=True);a=p.parse_args()
root=pathlib.Path(a.directory);tag=f'{a.tag}-branding-{a.arch}'
def gh(*args):return subprocess.check_output(['gh',*args,'--repo','bypssd/bypssd-os'],text=True)
try:gh('release','view',tag)
except subprocess.CalledProcessError:gh('release','create',tag,'--prerelease','--title',f'BYPSSD · paquetes y fuentes · {a.arch}','--notes','Solo RPM propios BYPSSD y sus fuentes. Las ISO se distribuyen por separado. Paquetes de desarrollo sin firma de producción.')
assets={x['name']:x for x in json.loads(gh('release','view',tag,'--json','assets'))['assets']}
paths=list((root/'opensuse/rpms').glob('bypssd-branding-1.1-*.rpm'))+list((root/'opensuse/srpms').glob('bypssd-branding-1.1-*.src.rpm'))
if len(paths)!=2:raise SystemExit('Se esperaba exactamente un RPM propio y un SRPM')
for path in paths:
 digest=hashlib.sha256(path.read_bytes()).hexdigest();old=assets.get(path.name)
 if old:
  if old['size']!=path.stat().st_size or old.get('digest')!='sha256:'+digest:raise SystemExit('Paquete existente distinto: '+path.name)
 else:gh('release','upload',tag,str(path))
 print('Paquete publicado:',path.name)
