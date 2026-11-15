#!/bin/bash
# Native, privileged openSUSE container on a disposable GitHub runner.
set -euxo pipefail
cd /workspace
export BYPSSD_ARCH=$(uname -m)
mkdir -p out/logs out/opensuse/rpms out/opensuse/srpms
zypper --non-interactive refresh
zypper --non-interactive install --no-recommends python3-kiwi kiwi-systemdeps-iso-media kiwi-systemdeps-bootloaders kiwi-systemdeps-filesystems rpm-build createrepo_c rsvg-convert curl python3-lxml
python3 scripts/opensuse/prepare.py
for n in spinner track fill; do rsvg-convert "branding/plymouth/$n.svg" -o "out/opensuse/payload/usr/share/plymouth/themes/bypssd/$n.png"; done
top=/var/tmp/bypssd-opensuse-rpmbuild
mkdir -p "$top"/{SOURCES,SPECS,BUILD,BUILDROOT,RPMS,SRPMS}
tar -czf "$top/SOURCES/bypssd-branding-1.1.tar.gz" --transform='s,^,bypssd-branding-1.1/,' -C out/opensuse/payload usr
rpmbuild -ba --define "_topdir $top" opensuse/bypssd-branding.spec
find "$top/RPMS" -name '*.rpm' -exec cp -t out/opensuse/rpms {} +
find "$top/SRPMS" -name '*.rpm' -exec cp -t out/opensuse/srpms {} +
createrepo_c out/opensuse/rpms
for n in $(seq 0 31); do [ -b "/dev/loop$n" ] || mknod "/dev/loop$n" b 7 "$n"; done
kiwi-ng --debug system build --description out/opensuse/description --target-dir /workspace/out/opensuse/result 2>&1 | tee out/logs/opensuse-kiwi.log
root=/workspace/out/opensuse/result/build/image-root
rpm --root "$root" -qa --qf '%{NAME}\t%{VERSION}-%{RELEASE}.%{ARCH}\n' | sort > "out/package-manifest-opensuse-$BYPSSD_ARCH.txt"
python3 scripts/opensuse/audit.py "$root" > "out/audit-opensuse-$BYPSSD_ARCH.json"
iso=$(find out/opensuse/result -maxdepth 1 -name '*.iso' -print -quit)
test -s "$iso"
cp "$iso" "out/BYPSSD-OS-Renacer-1.1-$BYPSSD_ARCH.iso"
(cd out && sha256sum "BYPSSD-OS-Renacer-1.1-$BYPSSD_ARCH.iso" > "BYPSSD-OS-Renacer-1.1-$BYPSSD_ARCH.iso.sha256")
