Name:           bypssd-breeze-style
Version:        6.8.2
Release:        1%{?dist}
Summary:        Estilo Qt de BYPSSD derivado de Breeze
License:        GPL-2.0-or-later
URL:            https://bypssd.com
Source0:        breeze-bypssd-%{version}.tar.gz
BuildRequires:  gcc-c++, cmake, ninja-build, extra-cmake-modules
BuildRequires:  qt6-qtbase-devel, qt6-qtsvg-devel, qt6-qtdeclarative-devel
BuildRequires:  kf6-kcoreaddons-devel, kf6-kcolorscheme-devel, kf6-kconfig-devel
BuildRequires:  kf6-kguiaddons-devel, kf6-ki18n-devel, kf6-kiconthemes-devel
BuildRequires:  kf6-kwindowsystem-devel, kf6-kcmutils-devel, kf6-frameworkintegration-devel

%description
Plugin seleccionable como BYPSSD. No sustituye archivos de plasma-breeze.

%prep
%autosetup -n breeze-bypssd-%{version}

%build
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=%{_prefix} -DKDE_INSTALL_LIBDIR=lib64 \
  -DBUILD_QT5=OFF -DBUILD_QT6=ON -DBUILD_CURSOR=OFF \
  -DWITH_DECORATIONS=OFF -DWITH_WALLPAPERS=OFF -DBUILD_TESTING=OFF
cmake --build build --target breeze6 --parallel 4

%install
install -Dm755 build/bin/bypssdstyle6.so %{buildroot}%{_libdir}/qt6/plugins/styles/bypssdstyle6.so

%files
%license LICENSES/GPL-2.0-or-later.txt
%{_libdir}/qt6/plugins/styles/bypssdstyle6.so

%changelog
* Sat Nov 14 2026 BYPSSD Informática Retro <info@bypssd.com> - 6.8.2-1
- Plugin separado BYPSSD, basado en etiqueta estable v6.8.2.
