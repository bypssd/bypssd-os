#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess

root = Path(__file__).resolve().parents[1]
def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024*1024), b''):
            result.update(block)
    return result.hexdigest()
def commit(path):
    return subprocess.check_output(['git','-C',str(root/path),'rev-parse','HEAD'],text=True).strip()
iso = root/'out/BYPSSD-OS-Renacer-1.0-aarch64.iso'
if not iso.is_file():
    raise SystemExit('No final ISO exists yet')
data = {
    'product':'BYPSSD OS Renacer', 'version':'1.0', 'architecture':'aarch64',
    'base':'Fedora 45', 'desktop':'Plasma 6.8.2', 'builder':'KIWI 11.1.1',
    'recorded_at_utc':datetime.now(timezone.utc).isoformat(),
    'iso':{'filename':iso.name,'bytes':iso.stat().st_size,'sha256':digest(iso)},
    'sources':{repo:commit('src/'+repo) for repo in ('breeze','plasma-workspace')},
    'fedora_kiwi_descriptions_commit':commit('kickstart/kiwi-upstream'),
    'files':{},
    'publication_status':'development candidate; see README for remaining verification and branding review',
}
for directory in ['assets','branding','scripts','docs']:
    for path in sorted((root/directory).rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts:
            data['files'][str(path.relative_to(root))]=digest(path)
for relative in ['build.sh','README.md','kickstart/bypssd.ks','kickstart/kiwi/BYPSSD.kiwi','out/package-manifest.txt']:
    path=root/relative
    if path.is_file():data['files'][relative]=digest(path)
(root/'out/build-manifest.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(data['iso'],indent=2))
