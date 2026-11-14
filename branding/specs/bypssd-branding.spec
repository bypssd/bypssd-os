Name:           bypssd-branding
Version:        1.0
Release:        5%{?dist}
Summary:        Identidad visual de BYPSSD OS Renacer
License:        GPL-2.0-or-later AND LGPL-2.0-or-later AND LicenseRef-BYPSSD-Artwork
URL:            https://bypssd.com
Source0:        bypssd-branding-%{version}.tar.gz
BuildArch:      noarch
BuildRequires:  librsvg2-tools
Provides:       plasma-lookandfeel-fedora = 6.8.2-1%{?dist}
Obsoletes:      plasma-lookandfeel-fedora < 6.8.3
Provides:       system-backgrounds-kde = 1.0
Provides:       desktop-backgrounds-compat = 45.0.0-3%{?dist}
Obsoletes:      desktop-backgrounds-compat < 46
Requires:       bypssd-breeze-style = 6.8.2
Requires:       plasma-workspace >= 6.8.2
Requires:       sddm, plymouth-plugin-script, qt6-qtdeclarative

%description
Tema global com.bypssd.desktop, SDDM, Plymouth, colores, logos y fondo.
La pantalla de bienvenida deriva de Plasma Workspace v6.8.2.

%prep
%autosetup

%build
# QML, colores y arte: componentes interpretados, no requieren recompilar Plasma.

%install
mkdir -p %{buildroot}%{_datadir}/bypssd
cp assets/*.png %{buildroot}%{_datadir}/bypssd/
cp -a branding/start branding/browser %{buildroot}%{_datadir}/bypssd/
install -Dm755 branding/config/bypssd-configure %{buildroot}%{_libexecdir}/bypssd-configure
mkdir -p %{buildroot}/etc/skel/.kde/share/apps/konqueror
cat > %{buildroot}/etc/skel/.kde/share/apps/konqueror/bookmarks.xml <<'BOOKMARKS'
<?xml version="1.0" encoding="UTF-8"?><xbel><bookmark href="https://bypssd.com"><title>BYPSSD Informática Retro</title></bookmark></xbel>
BOOKMARKS
install -Dm644 branding/BYPSSDRenacer.colors %{buildroot}%{_datadir}/color-schemes/BYPSSDRenacer.colors
mkdir -p %{buildroot}%{_datadir}/plasma/look-and-feel/com.bypssd.desktop
cp -a branding/look-and-feel/. %{buildroot}%{_datadir}/plasma/look-and-feel/com.bypssd.desktop/
mkdir -p %{buildroot}%{_datadir}/sddm/themes/bypssd
cp -a branding/sddm/. %{buildroot}%{_datadir}/sddm/themes/bypssd/
mkdir -p %{buildroot}%{_datadir}/plymouth/themes/bypssd
cp branding/plymouth/* %{buildroot}%{_datadir}/plymouth/themes/bypssd/
for name in spinner track fill; do
  rsvg-convert branding/plymouth/$name.svg -o %{buildroot}%{_datadir}/plymouth/themes/bypssd/$name.png
done
cp assets/logo-256.png %{buildroot}%{_datadir}/plymouth/themes/bypssd/logo.png
mkdir -p %{buildroot}%{_datadir}/wallpapers/com.bypssd.wallpaper/contents/images
cp assets/wallpaper.png %{buildroot}%{_datadir}/wallpapers/com.bypssd.wallpaper/contents/images/1920x1080.png
cp branding/wallpaper-metadata.json %{buildroot}%{_datadir}/wallpapers/com.bypssd.wallpaper/metadata.json
ln -s com.bypssd.wallpaper %{buildroot}%{_datadir}/wallpapers/Default
install -Dm644 branding/config/kdeglobals %{buildroot}/etc/xdg/kdeglobals
install -Dm644 branding/config/kcm-about-distrorc %{buildroot}/etc/skel/.config/kcm-about-distrorc
install -Dm644 branding/config/ksplashrc %{buildroot}/etc/xdg/ksplashrc
install -Dm644 branding/config/kscreenlockerrc %{buildroot}/etc/xdg/kscreenlockerrc
install -Dm644 branding/config/sddm.conf %{buildroot}/etc/sddm.conf.d/90-bypssd.conf
install -Dm644 branding/config/bypssd-anaconda.conf %{buildroot}/etc/anaconda/profile.d/bypssd.conf
install -Dm644 branding/config/anaconda.css %{buildroot}%{_datadir}/bypssd/anaconda.css
install -Dm644 branding/config/bypssd-instalar.desktop %{buildroot}%{_datadir}/bypssd/bypssd-instalar.desktop
install -Dm755 branding/config/bypssd-live %{buildroot}%{_libexecdir}/bypssd-live
install -Dm755 branding/config/bypssd-liveinst %{buildroot}%{_libexecdir}/bypssd-liveinst
install -Dm755 branding/config/bypssd-anaconda %{buildroot}%{_libexecdir}/bypssd-anaconda
install -Dm644 branding/config/bypssd-live.service %{buildroot}%{_unitdir}/bypssd-live.service
install -Dm644 assets/logo-48.png %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/bypssd-logo.png
install -Dm644 assets/logo-256.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/bypssd-logo.png
mkdir -p %{buildroot}/etc/skel/.config
cp branding/config/kdeglobals %{buildroot}/etc/skel/.config/kdeglobals
cp branding/config/mimeapps.list %{buildroot}/etc/skel/.config/mimeapps.list

mkdir -p %{buildroot}%{_datadir}/cockpit/branding/bypssd
cp branding/cockpit/bypssd/branding.css %{buildroot}%{_datadir}/cockpit/branding/bypssd/
cp assets/logo-256.png %{buildroot}%{_datadir}/cockpit/branding/bypssd/logo.png
cp assets/logo-48.png %{buildroot}%{_datadir}/cockpit/branding/bypssd/favicon.ico
cp assets/logo-256.png %{buildroot}%{_datadir}/cockpit/branding/bypssd/apple-touch-icon.png
install -Dm644 branding/config/anaconda-cockpit.conf %{buildroot}/etc/anaconda/cockpit/conf.d/90-bypssd.conf
install -Dm644 branding/config/bypssd-repositories.repo %{buildroot}%{_datadir}/dnf5/repos.override.d/90-bypssd.repo

%posttrans
%{_libexecdir}/bypssd-configure

%transfiletriggerin -- /etc/chromium
%{_libexecdir}/bypssd-configure

%files
%license branding/licenses/* assets/LICENSE.txt
%{_datadir}/bypssd
%{_datadir}/cockpit/branding/bypssd
%{_datadir}/dnf5/repos.override.d/90-bypssd.repo
%config(noreplace) /etc/anaconda/cockpit/conf.d/90-bypssd.conf
%{_datadir}/color-schemes/BYPSSDRenacer.colors
%{_datadir}/plasma/look-and-feel/com.bypssd.desktop
%{_datadir}/sddm/themes/bypssd
%{_datadir}/plymouth/themes/bypssd
%{_datadir}/wallpapers/com.bypssd.wallpaper
%{_datadir}/wallpapers/Default
%{_datadir}/icons/hicolor/48x48/apps/bypssd-logo.png
%{_datadir}/icons/hicolor/256x256/apps/bypssd-logo.png
%config(noreplace) /etc/xdg/kdeglobals
%config(noreplace) /etc/skel/.config/kcm-about-distrorc
%config(noreplace) /etc/xdg/ksplashrc
%config(noreplace) /etc/xdg/kscreenlockerrc
%config(noreplace) /etc/sddm.conf.d/90-bypssd.conf
%config(noreplace) /etc/anaconda/profile.d/bypssd.conf
%config(noreplace) /etc/skel/.config/kdeglobals
%config(noreplace) /etc/skel/.config/mimeapps.list
%{_libexecdir}/bypssd-live
%{_libexecdir}/bypssd-configure
%config(noreplace) /etc/skel/.kde/share/apps/konqueror/bookmarks.xml
%{_libexecdir}/bypssd-liveinst
%{_libexecdir}/bypssd-anaconda
%{_unitdir}/bypssd-live.service

%changelog
* Sat Nov 14 2026 BYPSSD Informática Retro <info@bypssd.com> - 1.0-5
- Sustituir temas/fondos del proveedor; navegador BYPSSD y animaciones Renacer.
* Sat Nov 14 2026 BYPSSD Informática Retro <info@bypssd.com> - 1.0-4
- Branding de Anaconda GTK/Cockpit y nombres de repositorios BYPSSD.
* Sat Nov 14 2026 BYPSSD Informática Retro <info@bypssd.com> - 1.0-3
- Fondo sin recorte, Chromium por defecto y lanzador de instalación con identidad propia.
* Sat Nov 14 2026 BYPSSD Informática Retro <info@bypssd.com> - 1.0-1
- Tema Renacer inicial.
