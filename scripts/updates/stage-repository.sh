#!/bin/bash
# Prepare metadata only in a NEW staging directory, never overwrite the live repo.
set -euo pipefail
incoming=${1:?RPM directory required}
staging=${2:?New staging directory required}
asset_base=${3:?HTTPS release asset base URL required}
[[ $asset_base == https://github.com/bypssd/bypssd-os/releases/download/* ]] || exit 2
[[ ! -e $staging ]] || { echo 'El staging ya existe; usa un directorio nuevo.' >&2; exit 2; }
mkdir -p "$staging"/{aarch64,x86_64}
branding=$incoming/bypssd-branding-1.1-17.noarch.rpm
touch=$incoming/bypssd-nextwindow-0.7.0.1-2.x86_64.rpm
test -s "$branding";test -s "$touch"
for arch in aarch64 x86_64; do cp "$branding" "$staging/$arch/";done
cp "$touch" "$staging/x86_64/"
for arch in aarch64 x86_64; do
    createrepo_c --no-database --baseurl "$asset_base/" "$staging/$arch"
done
printf 'STAGED ONLY: requiere firma de RPM y metadatos antes de publicar en el canal.\n'
