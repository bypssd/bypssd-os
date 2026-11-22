#!/bin/bash
set -euo pipefail
dnf -y install gcc make rpm-build cpio curl tar gzip kmod elfutils-libelf-devel openssl-devel glibc.i686 systemd-libs.i686 python3 mokutil libinput-utils usbutils systemd
root=/workspace/out/fedora45
mkdir -p "$root"/{headers,rpmbuild/SOURCES,rpmbuild/SPECS,downloads,delivery}
python3 - <<'PY'
import json,subprocess,hashlib
from pathlib import Path
root=Path('/workspace/out/fedora45');items=json.loads(Path('fedora/nextwindow/kernels.json').read_text())
for item in items:
 p=root/'downloads'/item['url'].rsplit('/',1)[-1]
 subprocess.run(['curl','-fL','--retry','3',item['url'],'-o',str(p)],check=True)
 item['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
 subprocess.run(['bash','-o','pipefail','-c','rpm2cpio "$1" | cpio -idm --quiet --no-absolute-filenames','extract',str(p)],cwd=root/'headers',check=True)
assert all((root/'headers/usr/src/kernels'/i['uname']/'Makefile').is_file() for i in items)
(root/'delivery/kernels.json').write_text(json.dumps(items,indent=2)+'\n')
PY
cp -a opensuse/nextwindow "$root/payload"
cp "$root/delivery/kernels.json" "$root/payload/kernels.json"
cp fedora/nextwindow/README.md "$root/payload/README.md"
tar -czf "$root/rpmbuild/SOURCES/bypssd-nextwindow-0.7.0.1.tar.gz" --transform='s,^payload,bypssd-nextwindow-0.7.0.1,' -C "$root" payload
tar -czf "$root/rpmbuild/SOURCES/nextwindow-fedora45-headers.tar.gz" -C "$root/headers/usr/src/kernels" .
rpmbuild --define "_topdir $root/rpmbuild" --define 'debug_package %{nil}' --define 'dist .fc45' -ba fedora/nextwindow/bypssd-nextwindow.spec
find "$root/rpmbuild/RPMS" "$root/rpmbuild/SRPMS" -name '*.rpm' -exec cp '{}' "$root/delivery/" \;
dnf -y install "$root/delivery/"*.x86_64.rpm
python3 - <<'PY'
import json,subprocess
from pathlib import Path
items=json.loads(Path('/workspace/out/fedora45/delivery/kernels.json').read_text())
for item in items:
 p=Path('/usr/lib/bypssd-nextwindow/modules')/item['uname']/'nw-fermi.ko'
 vermagic=subprocess.check_output(['modinfo','-F','vermagic',str(p)],text=True)
 assert vermagic.startswith(item['uname']+' '),vermagic
 print('VERIFIED',item['uname'],vermagic.strip())
PY
systemd-analyze verify /usr/lib/systemd/system/bypssd-nextwindow.service /usr/lib/systemd/system/bypssd-nextwindow-auto.service /usr/lib/systemd/system/nwfermi@1.service /usr/lib/systemd/system/fwprod-*.service
cd "$root/delivery"
sha256sum *.rpm kernels.json > SHA256SUMS
printf '\nFEDORA45 BUILD AND INSTALL PASSED: three exact kernels; hardware/Secure Boot not tested.\n'
