#!/bin/bash
set -euo pipefail
zypper -n refresh
zypper -n install --no-recommends rpm-build gcc make kernel-default-devel kernel-devel glibc-32bit libudev1-32bit gzip tar findutils binutils systemd
root=/workspace/out/nextwindow
mkdir -p "$root"/{SOURCES,SPECS,BUILD,BUILDROOT,RPMS,SRPMS}
tar -czf "$root/SOURCES/bypssd-nextwindow-0.7.0.1.tar.gz" --transform='s,^nextwindow,bypssd-nextwindow-0.7.0.1,' -C opensuse nextwindow
cp opensuse/nextwindow/bypssd-nextwindow.spec "$root/SPECS/"
rpmbuild --define "_topdir $root" --define 'debug_package %{nil}' -ba "$root/SPECS/bypssd-nextwindow.spec"
find "$root/RPMS" "$root/SRPMS" -name '*.rpm' -exec cp '{}' "$root/" \;
rpm -qp --requires "$root"/*.x86_64.rpm
rpm -qp --scripts "$root"/*.x86_64.rpm
zypper -n install --allow-unsigned-rpm "$root"/*.x86_64.rpm
systemd-analyze verify /usr/lib/systemd/system/bypssd-nextwindow.service /usr/lib/systemd/system/nwfermi@1.service /usr/lib/systemd/system/fwprod-*.service
cd "$root"
sha256sum ./*.rpm SOURCES/*.tar.gz > SHA256SUMS
printf '\nBUILD PASSED: module compiled, both ELF32 dependencies resolved. Physical touchscreen NOT tested.\n'
