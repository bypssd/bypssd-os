#!/bin/bash
# Download only: cross-architecture packages are never executed.
set -euo pipefail
cd /workspace
dnf -y --setopt=install_weak_deps=False install dnf5-plugins
mkdir -p out/logs
mapfile -t packages < branding/extra-hosted-packages.txt
for arch in aarch64 x86_64; do
  mkdir -p "out/hosted-extras/$arch"
  dnf -y --setopt=install_weak_deps=False download --forcearch="$arch" \
    --destdir "out/hosted-extras/$arch" "${packages[@]}"
  rpm --import "/etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-45-$arch"
  rpmkeys --checksig "out/hosted-extras/$arch/"*.rpm > "out/logs/hosted-signatures-$arch.txt"
done
