#!/usr/bin/env python3
from pathlib import Path
import subprocess
packages, excluded = [], []
inside = False
for raw in Path('/workspace/kickstart/bypssd.ks').read_text().splitlines():
    line = raw.split('#', 1)[0].strip()
    if line.startswith('%packages'):
        inside = True
        continue
    if line == '%end':
        inside = False
    if inside and line:
        (excluded if line.startswith('-') else packages).append(line.lstrip('-'))
cmd = ['dnf', '--installroot=/var/tmp/bypssd-solve', '--releasever=45',
       '--use-host-config', '--repofrompath=bypssd,file:///workspace/out/rpms',
       '--setopt=bypssd.gpgcheck=0', '--setopt=install_weak_deps=False',
       '--exclude=' + ','.join(excluded), '--assumeno', 'install', *packages]
print(' '.join(cmd), flush=True)
raise SystemExit(subprocess.call(cmd))
