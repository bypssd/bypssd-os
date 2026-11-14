# BYPSSD OS Renacer: derived from the last official fedora-live-kde.ks,
# fedora-live-kde-base.ks and fedora-live-base.ks in spin-kickstarts d93b2ac.
# Adapted for Fedora 45 / aarch64; explicit office packages, no games.
lang es_ES.UTF-8
keyboard es
timezone Europe/Madrid --utc
selinux --enforcing
firewall --enabled --service=mdns
xconfig --startxonboot
network --bootproto=dhcp --device=link --activate --hostname=bypssd
rootpw --lock
services --enabled=NetworkManager,sddm,livesys,livesys-late --disabled=sshd
zerombr
clearpart --all
part / --size=20000 --fstype=ext4
shutdown

url --url=https://download.fedoraproject.org/pub/fedora/linux/releases/45/Everything/aarch64/os/
repo --name=bypssd-fedora-updates --baseurl=https://download.fedoraproject.org/pub/fedora/linux/updates/45/Everything/aarch64/
repo --name=bypssd --baseurl=http://127.0.0.1:8765/ --cost=1

%packages --exclude-weakdeps
@core
@base-x
kernel
kernel-modules
kernel-modules-extra
linux-firmware
dracut-live
grub2-efi-aa64
shim-aa64
efibootmgr
anaconda-live
anaconda-gui
anaconda-install-env-deps
livesys-scripts
NetworkManager
NetworkManager-wifi
NetworkManager-bluetooth
bluez
firewalld
plasma-desktop
plasma-workspace
plasma-breeze
plasma-nm
plasma-pa
plasma-print-manager
plasma-systemmonitor
plasma-discover
plasma-discover-notifier
kscreen
kscreenlocker
kwin
polkit-kde
kinfocenter
systemsettings
dolphin
konsole
ark
spectacle
gwenview
okular
libreoffice-writer
libreoffice-calc
libreoffice-impress
libreoffice-draw
libreoffice-langpack-es
chromium
kate
kcalc
kde-connect
elisa-player
haruna
filelight
skanpage
kde-partitionmanager
kfind
krdc
gimp
inkscape
libreoffice-math
hunspell-es
langpacks-es
glibc-langpack-es
glibc-langpack-en
google-noto-sans-vf-fonts
google-noto-sans-mono-vf-fonts
dejavu-sans-fonts
qemu-guest-agent
spice-vdagent
pipewire
pipewire-pulseaudio
wireplumber
xdg-desktop-portal-kde
xdg-user-dirs
cups
sddm
sddm-wayland-plasma
plymouth
plymouth-plugin-script
generic-logos
bypssd-release-identity
bypssd-breeze-style
bypssd-branding
-plasma-lookandfeel-fedora
-f45-backgrounds-*
-desktop-backgrounds-kde
-desktop-backgrounds-compat
-fedora-bookmarks
-fedora-release-identity-*
-fedora-logos
-fedora-logos-httpd
-fedora-logos-sshd
-plasma-welcome
-plasma-welcome-fedora
-plasma-login-manager
-kde-settings-plasmalogin
%end

%post --erroronfail --log=/root/bypssd-post.log
set -eu
systemctl set-default graphical.target
systemctl enable sddm.service livesys.service livesys-late.service NetworkManager.service bypssd-live.service
systemctl disable sshd.service
echo bypssd > /etc/hostname
# livesys creates the live user and removes its autologin settings after install.
sed -i 's/^livesys_session=.*/livesys_session="kde"/' /etc/sysconfig/livesys
/usr/libexec/bypssd-configure
plymouth-set-default-theme bypssd
mkdir -p /etc/systemd/system/getty@.service.d
cat > /etc/systemd/system/getty@.service.d/bypssd.conf <<'EOF'
[Service]
ExecStart=
ExecStart=-/sbin/agetty -o '-p -- \\u' --noclear --noissue - $TERM
EOF
cat > /etc/locale.conf <<'EOF'
LANG=es_ES.UTF-8
EOF
cat > /etc/vconsole.conf <<'EOF'
KEYMAP=es
EOF
cat > /etc/sysconfig/desktop <<'EOF'
DESKTOP="KDE"
DISPLAYMANAGER="SDDM"
EOF
cat >> /etc/default/grub <<'EOF'
GRUB_DISTRIBUTOR="BYPSSD OS"
EOF
# The build repository is loopback-only and must never ship as a configured repo.
rm -f /etc/yum.repos.d/bypssd.repo
# First boot must generate its own random seed and machine identifier.
rm -f /var/lib/systemd/random-seed
truncate -s 0 /etc/machine-id
%end
