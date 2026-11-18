#!/bin/bash
set -euo pipefail
zypper -n refresh
zypper -n install --no-recommends rpm-build gcc make curl glibc-32bit libudev1-32bit gzip tar findutils binutils systemd
if [[ ${NEXTWINDOW_TARGET:-latest} == live-r16 ]]; then
    zypper -n install --no-recommends \
      https://download.opensuse.org/tumbleweed/repo/oss/noarch/kernel-devel-7.3.3-1.1.noarch.rpm \
      https://download.opensuse.org/tumbleweed/repo/oss/x86_64/kernel-default-devel-7.3.3-1.1.x86_64.rpm
else
    zypper -n install --no-recommends kernel-default-devel kernel-devel
fi
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
if [[ ${NEXTWINDOW_TARGET:-latest} == live-r16 ]]; then
    module="$root/nw-fermi-built.ko"
    test -f "$module"
    cp "$module" "$root/nw-fermi-7.3.3-1-default.ko"
    modinfo "$root/nw-fermi-7.3.3-1-default.ko" | tee "$root/module-info.txt"
    modinfo -F vermagic "$module" | grep -q '^7.3.3-1-default '
fi
cd "$root"
sha256sum ./*.rpm SOURCES/*.tar.gz > SHA256SUMS
printf '\nBUILD PASSED: module compiled, both ELF32 dependencies resolved. Physical touchscreen NOT tested.\n'
