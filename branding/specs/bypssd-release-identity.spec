%{!?fedora_identity_version:%global fedora_identity_version 45}
%{!?fedora_identity_release:%global fedora_identity_release 14}
Name:           bypssd-release-identity
Version:        1.0
Release:        1%{?dist}
Summary:        Identidad del sistema BYPSSD OS Renacer
License:        MIT
URL:            https://bypssd.com
BuildArch:      noarch
Provides:       fedora-release-identity = %{fedora_identity_version}-%{fedora_identity_release}
Provides:       fedora-release-variant = %{fedora_identity_version}-%{fedora_identity_release}
Conflicts:      fedora-release-identity-basic
Conflicts:      fedora-release-identity-kde
Conflicts:      fedora-release-identity-workstation
Requires:       fedora-release-common = %{fedora_identity_version}-%{fedora_identity_release}

%description
Identidad propia que satisface las dependencias de Fedora 45 conservando
fedora-release-common sin modificar sus archivos. No es un paquete oficial.

%install
mkdir -p %{buildroot}/usr/lib
cat > %{buildroot}/usr/lib/os-release <<'EOF'
NAME="BYPSSD OS"
PRETTY_NAME="BYPSSD OS Renacer 1.0"
ID=bypssd
ID_LIKE=fedora
PLATFORM_ID=platform:f45
VERSION="1.0 (Renacer)"
VERSION_ID=1.0
VERSION_CODENAME=renacer
ANSI_COLOR="0;33"
LOGO=bypssd-logo
HOME_URL="https://bypssd.com"
SUPPORT_URL="https://bypssd.com"
DEFAULT_HOSTNAME=bypssd
EOF
mkdir -p %{buildroot}/etc/dnf/vars
echo 45 > %{buildroot}/etc/dnf/vars/releasever

%files
/usr/lib/os-release
%config(noreplace) /etc/dnf/vars/releasever

%changelog
* Sat Nov 14 2026 BYPSSD Informática Retro <info@bypssd.com> - 1.0-1
- Identidad separada sin editar fedora-release-common.
