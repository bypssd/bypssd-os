Name:           bypssd-nextwindow
Version:        0.7.0.1
Release:        2
Summary:        Experimental NextWindow Fermi touchscreen support for BYPSSD OS
License:        GPL-2.0-only AND MIT
URL:            https://github.com/bypssd/bypssd-os
Source0:        %{name}-%{version}.tar.gz
ExclusiveArch:  x86_64
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  kernel-default-devel
BuildRequires:  kernel-devel
BuildRequires:  glibc-32bit
BuildRequires:  libudev1-32bit
Requires:       gcc
Requires:       make
Requires:       kernel-default-devel
Requires:       kernel-devel
Requires:       glibc-32bit
Requires:       libudev1-32bit
Requires:       kmod
Requires:       mokutil
Requires:       usbutils
Requires:       libinput-tools
Requires:       systemd
%define _build_id_links none
%define __requires_exclude ^libudev\\.so\\.0.*$

%description
Optional experimental support for USB IDs in the NextWindow Fermi driver.
Includes original Intel 32-bit decoders and GPL module sources adapted to
standard Linux direct-touch events. Activation is explicit; no session change,
no HID blacklist, no Secure Boot changes. Automatic activation is limited to the physically validated USB 1926:0DBE.

%prep
%setup -q

%build
# Build against the installed development kernel, never the CI host kernel.
mkdir -p bundled
for headers in /usr/src/linux-*-obj/x86_64/default; do
    test -d "$headers" || continue
    make -C "$headers" M="$PWD/source" clean
    make -C "$headers" M="$PWD/source" -j2 modules
    kernel=$(cat "$headers/include/config/kernel.release")
    mkdir -p "bundled/$kernel"
    cp source/nw-fermi.ko "bundled/$kernel/"
done
test -n "$(find bundled -name nw-fermi.ko -print -quit)"
cp -a bundled %{_topdir}/compiled-modules
/lib/ld-linux.so.2 --list ./nwfermi_daemon
ln -s /usr/lib/libudev.so.1 libudev.so.0
/lib/ld-linux.so.2 --library-path "$PWD" --list ./fwprod

%install
install -d %{buildroot}/usr/src/bypssd-nextwindow %{buildroot}/usr/libexec/bypssd-nextwindow
install -m 0644 source/nw-fermi.c source/nwfermi_public.h source/Makefile %{buildroot}/usr/src/bypssd-nextwindow/
install -m 0755 nwfermi_daemon fwprod %{buildroot}/usr/libexec/bypssd-nextwindow/
# fwprod expects libudev.so.0. Scope the compatibility name to this decoder.
ln -s /usr/lib/libudev.so.1 %{buildroot}/usr/libexec/bypssd-nextwindow/libudev.so.0
install -D -m 0755 build-module %{buildroot}/usr/libexec/bypssd-nextwindow-build
install -D -m 0755 auto-enable %{buildroot}/usr/libexec/bypssd-nextwindow-auto
install -d %{buildroot}/usr/lib/bypssd-nextwindow
cp -a bundled %{buildroot}/usr/lib/bypssd-nextwindow/modules
install -D -m 0755 enable %{buildroot}/usr/sbin/bypssd-nextwindow-enable
install -D -m 0755 diagnose %{buildroot}/usr/sbin/bypssd-nextwindow-diagnose
install -d %{buildroot}/usr/lib/systemd/system %{buildroot}/usr/lib/udev/rules.d
install -m 0644 systemd/*.service %{buildroot}/usr/lib/systemd/system/
install -m 0644 udev/*.rules %{buildroot}/usr/lib/udev/rules.d/

%post
if [ -d /run/systemd/system ]; then
    systemctl daemon-reload || :
    udevadm control --reload-rules || :
    if [ ! -e /etc/bypssd-nextwindow/disable-auto ]; then
        systemctl enable bypssd-nextwindow-auto.service || :
        systemctl start --no-block bypssd-nextwindow-auto.service || :
    fi
fi

%preun
if [ "$1" = 0 ] && [ -d /run/systemd/system ]; then
    systemctl disable --now bypssd-nextwindow-auto.service bypssd-nextwindow.service || :
    systemctl stop 'nwfermi@*.service' 'fwprod-*.service' || :
fi

%files
%license LICENSE-NW
%doc README.md UPSTREAM
/usr/src/bypssd-nextwindow
/usr/libexec/bypssd-nextwindow
/usr/libexec/bypssd-nextwindow-build
/usr/sbin/bypssd-nextwindow-enable
/usr/sbin/bypssd-nextwindow-diagnose
/usr/lib/systemd/system/bypssd-nextwindow.service
/usr/lib/systemd/system/nwfermi@.service
/usr/lib/systemd/system/fwprod-*.service
/usr/lib/udev/rules.d/70-bypssd-nextwindow.rules

/usr/libexec/bypssd-nextwindow-auto
/usr/lib/bypssd-nextwindow
/usr/lib/systemd/system/bypssd-nextwindow-auto.service
