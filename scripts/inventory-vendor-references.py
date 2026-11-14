#!/usr/bin/env python3
"""Inventory textual vendor mentions without reading binary payloads or key files."""
from pathlib import Path
import json,sys
root=Path(sys.argv[1]);found=[];scanned=0;binary=0
for top in ['etc','usr/share','usr/libexec']:
 for p in (root/top).rglob('*'):
  if not p.is_file() or p.is_symlink():continue
  rel=str(p.relative_to(root))
  if '/ssh/' in rel or 'gnupg' in rel or p.name in ('shadow','gshadow'):continue
  try:
   with p.open('rb') as f:
    head=f.read(8192)
    if b'\0' in head:binary+=1;continue
    text=(head+f.read()).decode('utf-8',errors='replace')
   scanned+=1
   n=text.lower().count('fedora')
   if n:
    category='technical-or-documentation'
    if rel.startswith(('usr/share/licenses/','usr/share/doc/')):category='license-or-documentation'
    if rel.startswith(('usr/share/plasma/look-and-feel/','usr/share/wallpapers/','usr/share/color-schemes/')):category='appearance'
    found.append({'path':rel,'mentions':n,'category':category})
  except (OSError,ValueError):continue
print(json.dumps({'text_files_scanned':scanned,'binary_files_skipped':binary,'files_with_mentions':found},indent=2))
