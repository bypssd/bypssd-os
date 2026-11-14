#!/bin/bash
set -euo pipefail
cd /workspace
top=/var/tmp/bypssd-rpmbuild
mkdir -p "$top"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS} out/rpms out/srpms
python3 scripts/prepare-branding.py
if [ "${BYPSSD_REUSE_STYLE:-0}" != 1 ]; then
tar --exclude=.git -czf "$top/SOURCES/breeze-bypssd-6.8.2.tar.gz" --transform='s,^breeze,breeze-bypssd-6.8.2,' -C src breeze
rpmbuild -ba --define "_topdir $top" branding/specs/bypssd-breeze-style.spec
else
  test -f "out/rpms/bypssd-breeze-style-6.8.2-1.fc45.$(uname -m).rpm"
  test -f out/srpms/bypssd-breeze-style-6.8.2-1.fc45.src.rpm
fi
tar -czf "$top/SOURCES/bypssd-branding-1.0.tar.gz" --transform='s,^,bypssd-branding-1.0/,' branding assets
rpmbuild -ba --define "_topdir $top" branding/specs/bypssd-branding.spec
identity=$(dnf -q repoquery --latest-limit 1 --queryformat '%{version} %{release}' fedora-release-common)
read -r identity_version identity_release <<< "$identity"
rpmbuild -ba --define "_topdir $top" \
  --define "fedora_identity_version $identity_version" \
  --define "fedora_identity_release $identity_release" \
  branding/specs/bypssd-release-identity.spec
find "$top/RPMS" -name '*.rpm' -exec cp -t out/rpms {} +
find "$top/SRPMS" -name '*.rpm' -exec cp -t out/srpms {} +
createrepo_c out/rpms
