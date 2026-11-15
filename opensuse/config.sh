#!/bin/bash
set -euxo pipefail
# Admin identity override, original upstream release file remains untouched.
if [ -L /etc/os-release ]; then unlink /etc/os-release; fi
cp /usr/share/bypssd/os-release /etc/os-release
printf 'bypssd\n' > /etc/hostname
printf 'LANG=es_ES.UTF-8\n' > /etc/locale.conf
printf 'KEYMAP=es\n' > /etc/vconsole.conf
printf 'DISPLAYMANAGER="sddm"\n' > /etc/sysconfig/displaymanager
systemctl enable NetworkManager display-manager bypssd-live.service
systemctl disable sshd.service 2>/dev/null || true
systemctl set-default graphical.target
passwd -l root
plymouth-set-default-theme bypssd
# Replace only local repository configuration, preserve package signatures.
for f in /etc/zypp/repos.d/*.repo; do
 [ "${f##*/}" = bypssd-updates.repo ] || mv "$f" "$f.disabled"
done
arch=$(uname -m)
base=https://download.opensuse.org/tumbleweed/repo/oss/
[ "$arch" != aarch64 ] || base=https://download.opensuse.org/ports/aarch64/tumbleweed/repo/oss/
cat > /etc/zypp/repos.d/opensuse-oss.repo <<EOF
[opensuse-oss]
name=openSUSE Tumbleweed - Paquetes oficiales
baseurl=$base
enabled=1
autorefresh=1
gpgcheck=1
EOF
cat >> /etc/default/grub <<'EOF'
GRUB_DISTRIBUTOR="BYPSSD OS"
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash=silent"
EOF
# PackageKit uses the native ZYpp backend; no dnf/Fedora plugin is installed.
mkdir -p /etc/PackageKit
printf '[Daemon]\nDefaultBackend=zypp\n' > /etc/PackageKit/PackageKit.conf
# The live account is created only when rd.live.image is present.
# Calamares removes its autologin/polkit/sudo policy from the target disk.
if [ -f /etc/calamares/modules/shellprocess-bypssd-cleanup.conf ]; then
 sed -i '/script:/a\  - "rm -f /etc/sudoers.d/90-bypssd-live /etc/polkit-1/rules.d/49-bypssd-live.rules"' /etc/calamares/modules/shellprocess-bypssd-cleanup.conf
fi
# Keep systemd first-boot identity unique.
truncate -s 0 /etc/machine-id
