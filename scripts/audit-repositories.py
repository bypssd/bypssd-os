#!/usr/bin/env python3
"""Validate the effective shipped DNF repository IDs and download URLs."""
import configparser,fnmatch,json,sys
from pathlib import Path
from urllib.parse import urlparse
root=Path(sys.argv[1]);repos={}
for p in sorted((root/'etc/yum.repos.d').glob('*.repo')):
 c=configparser.RawConfigParser(strict=False);c.read(p)
 for name in c: 
  if name!='DEFAULT':repos[name]=dict(c[name])
for directory in ['usr/share/dnf5/repos.override.d','etc/dnf/repos.override.d']:
 for p in sorted((root/directory).glob('*.repo')):
  c=configparser.RawConfigParser(strict=False);c.read(p)
  for pattern in c.sections():
   for name in repos:
    if fnmatch.fnmatchcase(name,pattern):repos[name].update(dict(c[pattern]))
active={n:r for n,r in repos.items() if r.get('enabled','1').lower() in ('1','true','yes')}
errors=[]
if set(active)!={'bypssd-base','bypssd-updates'}:errors.append('Unexpected enabled repository IDs: '+','.join(active))
for name,r in active.items():
 if r.get('metalink') or r.get('mirrorlist'):errors.append(name+': external mirror discovery')
 for url in r.get('baseurl','').split():
  u=urlparse(url)
  if u.scheme!='https' or u.netloc!='bypssd.github.io' or not u.path.startswith('/bypssd-os/45/'):errors.append(name+': unexpected URL '+url)
 if not r.get('baseurl'):errors.append(name+': missing baseurl')
 if r.get('gpgcheck')!='1':errors.append(name+': RPM signature checking disabled')
print(json.dumps({'enabled':active,'errors':errors},indent=2))
if errors:raise SystemExit(1)
