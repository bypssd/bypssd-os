#!/bin/bash
set -euo pipefail
zypper -n refresh
zypper -n install --no-recommends rpm-build rsvg-convert python3 tar gzip desktop-file-utils
export BYPSSD_ARCH=x86_64
python3 scripts/opensuse/prepare.py
for n in spinner track fill; do rsvg-convert "branding/plymouth/$n.svg" -o "out/opensuse/payload/usr/share/plymouth/themes/bypssd/$n.png"; done
desktop-file-validate opensuse/graphics/chromium-browser.desktop
python3 -m unittest discover -s tests -p test_graphics.py -v
root=/workspace/out/branding-update
mkdir -p "$root"/{SOURCES,SPECS,BUILD,BUILDROOT,RPMS,SRPMS}
tar -czf "$root/SOURCES/bypssd-branding-1.1.tar.gz" --transform='s,^,bypssd-branding-1.1/,' -C out/opensuse/payload usr
rpmbuild --define "_topdir $root" --define 'debug_package %{nil}' -ba opensuse/bypssd-branding.spec
find "$root/RPMS" "$root/SRPMS" -name '*.rpm' -exec cp '{}' out/nextwindow/ \;
printf '\nBranding r17 built without building or publishing any ISO.\n'
