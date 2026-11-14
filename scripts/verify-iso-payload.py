#!/usr/bin/env python3
"""Compare immutable x64 boot/system payloads through libarchive's tar reader."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
reader=shutil.which('bsdtar') or '/usr/bin/tar'
files=['boot/x86_64/loader/linux','boot/x86_64/loader/initrd','EFI/BOOT/BOOTX64.EFI','EFI/BOOT/grubx64.efi','LiveOS/squashfs.img']
def digest(iso,path):
 p=subprocess.Popen([reader,'-xOf',iso,path],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 h=hashlib.sha256()
 while data:=p.stdout.read(1024*1024):h.update(data)
 error=p.stderr.read();status=p.wait()
 if status:raise RuntimeError(error.decode(errors='replace'))
 return h.hexdigest()
results=[]
for path in files:
 a=digest(sys.argv[1],path);b=digest(sys.argv[2],path)
 results.append({'path':path,'sha256':a,'unchanged':a==b})
print(json.dumps(results,indent=2))
if not all(x['unchanged'] for x in results):raise SystemExit(1)
