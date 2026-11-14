#!/bin/bash
set -euo pipefail
case "$(uname -m)" in aarch64|x86_64) ;; *) exit 1;; esac
dnf -y --setopt=install_weak_deps=False install \
  librsvg2-tools git rpm-build rpm-sign gnupg2 python3-rpm rpmdevtools cmake ninja-build gcc-c++ extra-cmake-modules \
  python3 python3-pip python3-pillow createrepo_c dnf5-plugins \
  lorax-lmc-novirt pykickstart kiwi-cli kiwi-systemdeps-bootloaders kiwi-systemdeps-iso-media \
  qt6-qtbase-devel qt6-qtsvg-devel qt6-qtdeclarative-devel \
  kf6-kcoreaddons-devel kf6-kcolorscheme-devel kf6-kconfig-devel \
  kf6-kguiaddons-devel kf6-ki18n-devel kf6-kiconthemes-devel \
  kf6-kwindowsystem-devel kf6-kcmutils-devel kf6-frameworkintegration-devel
