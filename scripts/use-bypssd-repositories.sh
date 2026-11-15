#!/bin/bash
# Run inside BYPSSD Linux, after the complete mirror is published and verified.
set -euo pipefail
[[ $(uname -s) == Linux && $EUID == 0 ]] || { echo 'Solo BYPSSD Linux, como root.' >&2; exit 1; }
. /etc/os-release
[[ $ID == bypssd ]] || { echo 'No es un sistema BYPSSD.' >&2; exit 1; }
cd "$(dirname "$0")/.."
# Fail before changing repositories if either architecture mirror is incomplete.
python3 - <<'PY'
import json, urllib.request, platform
arch=platform.machine()
base='https://bypssd.github.io/bypssd-os/'
with urllib.request.urlopen(base+'catalog-summary.json') as r: summary=json.load(r)
if summary.get('status')!='complete':raise SystemExit('El catálogo no está completo; no se cambia nada')
for channel in ('base','updates'):
 with urllib.request.urlopen(base+'45/'+arch+'/'+channel+'/repodata/repomd.xml') as r:
  if r.status!=200:raise SystemExit('Metadatos no disponibles')
print('Catálogo completo:',summary['unique_packages'],'RPM')
PY
stamp=$(date -u +%Y%m%dT%H%M%SZ)
backup="/var/lib/bypssd/repository-backups/$stamp"
mkdir -p "$backup"
cp -a /etc/yum.repos.d "$backup/"
if [[ -d /etc/dnf/repos.override.d ]]; then cp -a /etc/dnf/repos.override.d "$backup/"; fi
install -Dm644 branding/config/bypssd-github.repo /etc/yum.repos.d/bypssd-github.repo
mkdir -p /etc/dnf/repos.override.d
python3 - <<'PY'
import configparser,pathlib
ids=set()
for path in pathlib.Path('/etc/yum.repos.d').glob('*.repo'):
 c=configparser.RawConfigParser(strict=False);c.read(path);ids.update(c.sections())
c=configparser.RawConfigParser()
for name in sorted(ids):c[name]={'enabled':'1' if name in ('bypssd-base','bypssd-updates') else '0'}
with open('/etc/dnf/repos.override.d/99-bypssd-exclusive.repo','w') as f:c.write(f)
PY
if ! dnf5 makecache --refresh; then
  echo "Error al validar. Copia de seguridad: $backup. Revisa la configuración antes de instalar paquetes." >&2
  exit 1
fi
dnf5 repo list --enabled
printf 'Repositorio BYPSSD activado. Historial y firmas originales conservados. Backup: %s\n' "$backup"
