# Calamares supplies this private QML module at runtime; it is not an RPM capability.
%global __requires_exclude ^qt6qmlimport[(]calamares[.]slideshow[.]1[)]$
Name: bypssd-branding
Version: 1.1
Release: 14
Summary: Escritorio BYPSSD OS Renacer
License: GPL-2.0-or-later AND GPL-3.0-or-later AND LGPL-2.0-or-later AND LicenseRef-BYPSSD-Artwork
URL: https://bypssd.com
Vendor: BYPSSD Informática Retro
Distribution: BYPSSD OS Renacer
Source0: bypssd-branding-1.1.tar.gz
BuildArch: noarch
Provides: plasma6-branding = 6.8.2
Provides: sddm-branding = 0.21.0
Provides: sddm-qt6-branding = 0.21.0
Conflicts: plasma6-branding-openSUSE
Conflicts: sddm-branding-openSUSE
Conflicts: sddm-qt6-branding-openSUSE
%description
Identidad visual propia. Base openSUSE; no es un producto oficial de openSUSE ni SUSE.
%prep
%setup -q
%build
%install
mkdir -p %{buildroot}
cp -a usr %{buildroot}/
%files
/usr/share/bypssd
/usr/share/plasma/look-and-feel/com.bypssd.desktop
/usr/share/color-schemes/BYPSSDRenacer.colors
/usr/share/sddm/themes/bypssd
/usr/share/plymouth/themes/bypssd
/usr/share/wallpapers/com.bypssd.wallpaper
/usr/share/calamares/branding/bypssd
/usr/share/metainfo/com.bypssd.bypssd.metainfo.xml
/usr/share/icons/hicolor/48x48/apps/bypssd-logo.png
/usr/share/icons/hicolor/256x256/apps/bypssd-logo.png

/usr/share/grub2/themes/bypssd

/usr/share/swcatalog/xml/bypssd-os.xml

/usr/share/polkit-1/actions/com.bypssd.install.policy

/usr/libexec/bypssd-calamares

/usr/libexec/bypssd-efi-config

/usr/libexec/bypssd-installed-cleanup

/usr/libexec/bypssd-hide-admin-launchers
