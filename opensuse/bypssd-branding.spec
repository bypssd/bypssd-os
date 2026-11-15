Name: bypssd-branding
Version: 1.1
Release: 1
Summary: Escritorio BYPSSD OS Renacer
License: GPL-2.0-or-later AND LGPL-2.0-or-later AND LicenseRef-BYPSSD-Artwork
URL: https://bypssd.com
Source0: bypssd-branding-1.1.tar.gz
BuildArch: noarch
Provides: plasma6-branding = 6.8.2
Provides: sddm-branding = 0.21.0
Provides: sddm-qt6-branding = 0.21.0
Provides: calamares-branding = 3.4.2
Conflicts: plasma6-branding-openSUSE
Conflicts: sddm-branding-openSUSE
Conflicts: sddm-qt6-branding-openSUSE
Conflicts: calamares-branding-upstream
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
/usr/share/metainfo/org.bypssd.bypssd.metainfo.xml
/usr/share/icons/hicolor/48x48/apps/bypssd-logo.png
/usr/share/icons/hicolor/256x256/apps/bypssd-logo.png
