#!/bin/bash
# Native Linux build for the architecture of the isolated GitHub runner.
set -euo pipefail
cd /workspace
export BYPSSD_ARCH=$(uname -m)
mkdir -p src out/logs
bash scripts/container-setup.sh
for repo in breeze plasma-workspace; do
  git clone --depth 1 --branch v6.8.2 "https://invent.kde.org/plasma/$repo.git" "src/$repo"
  test "$(git -C "src/$repo" rev-parse HEAD)" = "$(cat "branding/$repo-upstream.commit")"
done
git clone https://pagure.io/fedora-kiwi-descriptions.git kickstart/kiwi-upstream
git -C kickstart/kiwi-upstream checkout "$(cat branding/kiwi-upstream.commit)"
bash scripts/build-rpms.sh 2>&1 | tee out/logs/ci-rpmbuild.log
bash scripts/build-kiwi.sh 2>&1 | tee out/logs/ci-iso.log
root=$(cat out/logs/latest-kiwi-run.txt)/result/build/image-root
rpm --root "$root" -qa --qf '%{NAME}\t%{EPOCHNUM}:%{VERSION}-%{RELEASE}.%{ARCH}\n' | sort > "out/package-manifest-$BYPSSD_ARCH.txt"
python3 scripts/audit-image.py "$root" > "out/branding-audit-$BYPSSD_ARCH.json"
mkdir -p "out/common-packages/$BYPSSD_ARCH"
mapfile -t packages < branding/common-packages.txt
dnf -y --setopt=install_weak_deps=False download --destdir "out/common-packages/$BYPSSD_ARCH" "${packages[@]}"
cp out/rpms/bypssd-branding-1.0-5*.rpm "out/common-packages/$BYPSSD_ARCH/"
cp out/rpms/bypssd-release-identity-*.rpm "out/common-packages/$BYPSSD_ARCH/"
cp out/rpms/bypssd-breeze-style-6.8.2-1.$BYPSSD_ARCH.rpm "out/common-packages/$BYPSSD_ARCH/"
