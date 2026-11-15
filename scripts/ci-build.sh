#!/bin/bash
# Native Linux phases in a persistent, isolated GitHub runner container.
set -euo pipefail
cd /workspace
export BYPSSD_ARCH=$(uname -m)
phase=${1:?Usage: ci-build.sh rpms|iso|common}
mkdir -p src out/logs
case "$phase" in
rpms)
  bash scripts/container-setup.sh
  for repo in breeze plasma-workspace; do
    git clone --depth 1 --branch v6.8.2 "https://invent.kde.org/plasma/$repo.git" "src/$repo"
    test "$(git -C "src/$repo" rev-parse HEAD)" = "$(cat "branding/$repo-upstream.commit")"
  done
  git clone https://pagure.io/fedora-kiwi-descriptions.git kickstart/kiwi-upstream
  git -C kickstart/kiwi-upstream checkout "$(cat branding/kiwi-upstream.commit)"
  mkdir -p out/rpms out/srpms
  for revision in 7 5; do
    base="https://github.com/bypssd/bypssd-os/releases/download/packages-1.0-$revision-$BYPSSD_ARCH"
    if curl -fL "$base/bypssd-breeze-style-6.8.2-1.fc45.$BYPSSD_ARCH.rpm" -o /var/tmp/bypssd-style.rpm && \
       curl -fL "$base/bypssd-breeze-style-6.8.2-1.fc45.src.rpm" -o /var/tmp/bypssd-style.src.rpm; then
      cp /var/tmp/bypssd-style.rpm "out/rpms/bypssd-breeze-style-6.8.2-1.fc45.$BYPSSD_ARCH.rpm"
      cp /var/tmp/bypssd-style.src.rpm out/srpms/bypssd-breeze-style-6.8.2-1.fc45.src.rpm
      export BYPSSD_REUSE_STYLE=1
      break
    fi
  done
  bash scripts/build-rpms.sh 2>&1 | tee out/logs/ci-rpmbuild.log
  test -f "out/rpms/bypssd-breeze-style-6.8.2-1.fc45.$BYPSSD_ARCH.rpm"
  test -f out/rpms/bypssd-branding-1.0-8.fc45.noarch.rpm
  test -f out/rpms/bypssd-release-identity-1.0-1.fc45.noarch.rpm
  ;;
iso)
  bash scripts/build-kiwi.sh 2>&1 | tee out/logs/ci-iso.log
  root=$(cat out/logs/latest-kiwi-run.txt)/result/build/image-root
  rpm --root "$root" -qa --qf '%{NAME}\t%{EPOCHNUM}:%{VERSION}-%{RELEASE}.%{ARCH}\n' | sort > "out/package-manifest-$BYPSSD_ARCH.txt"
  python3 scripts/audit-image.py "$root" > "out/branding-audit-$BYPSSD_ARCH.json"
  python3 scripts/audit-repositories.py "$root" > "out/repository-audit-$BYPSSD_ARCH.json"
  ;;
common)
  mkdir -p "out/common-packages/$BYPSSD_ARCH"
  mapfile -t packages < branding/common-packages.txt
  dnf -y --setopt=install_weak_deps=False download --destdir "out/common-packages/$BYPSSD_ARCH" "${packages[@]}"
  ;;
*) exit 2;;
esac
