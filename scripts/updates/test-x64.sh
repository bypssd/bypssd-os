#!/bin/bash
# This entire test runs in a disposable container. Its test-only repository is unsigned.
set -euo pipefail
zypper -n refresh
zypper -n install --no-recommends rpm-build createrepo_c
root=/tmp/qa-platform
mkdir -p "$root"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
cat > "$root/SPECS/platform.spec" <<'SPEC'
Name: bypssd-qa-platform
Version: 1
Release: 1
Summary: Test-only installed-kernel architecture capability
License: MIT
BuildArch: noarch
Provides: kernel-default(x86-64)
%description
Resolver fixture only. Never published or shipped in BYPSSD.
%files
SPEC
rpmbuild --define "_topdir $root" -bb "$root/SPECS/platform.spec"
rpm -i "$root"/RPMS/noarch/*.rpm
mkdir /tmp/bypssd-test-rpms
cp out/update-qa/bypssd-branding-1.1-17.noarch.rpm out/update-qa/bypssd-nextwindow-0.7.0.1-2.x86_64.rpm /tmp/bypssd-test-rpms/
createrepo_c /tmp/bypssd-test-rpms
cat > /etc/zypp/repos.d/bypssd-qa.repo <<'REPO'
[bypssd-qa]
name=Disposable unsigned integration test only
baseurl=dir:/tmp/bypssd-test-rpms
enabled=1
gpgcheck=0
pkg_gpgcheck=0
REPO
zypper -n refresh bypssd-qa
# Only request the pre-existing distribution package: its rich dependency must pull the driver.
zypper -n install --no-recommends --from bypssd-qa bypssd-branding
rpm -q bypssd-branding bypssd-nextwindow
for version in 7.3.3-1-default 7.3.4-1-default; do
 test -s "/usr/lib/bypssd-nextwindow/modules/$version/nw-fermi.ko"
 modinfo -F vermagic "/usr/lib/bypssd-nextwindow/modules/$version/nw-fermi.ko" | grep -q "^$version "
done
printf '\nX64 UPDATE DEPENDENCY INSTALL PASSED. No hardware activation attempted.\n'
