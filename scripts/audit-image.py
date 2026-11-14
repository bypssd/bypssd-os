#!/usr/bin/env python3
"""Audit vendor references in user-facing theme/browser defaults, not legal credits."""
from pathlib import Path
import json,sys
root=Path(sys.argv[1]);hits=[]
for relative in ['usr/share/plasma/look-and-feel','usr/share/wallpapers','usr/share/color-schemes']:
 for p in (root/relative).rglob('*'):
  if p.is_file() and p.suffix in ('.json','.desktop','.colors'):
   t=p.read_text(errors='replace')
   if 'fedora' in t.lower():hits.append(str(p.relative_to(root)))
p=root/'etc/chromium/master_preferences'
if not p.exists() or 'fedora' in p.read_text().lower():hits.append('etc/chromium/master_preferences')
print(json.dumps({'scope':'theme metadata, wallpaper metadata, color schemes, Chromium initial preferences','vendor_references':hits,'homepage':json.loads(p.read_text()).get('homepage') if p.exists() else None},indent=2))
if hits:raise SystemExit('User-facing vendor branding remains')
