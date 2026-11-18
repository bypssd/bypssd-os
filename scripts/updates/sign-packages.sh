#!/bin/bash
# Requires an EXISTING, authorized local signing key; never creates/exports a private key.
set -euo pipefail
incoming=${1:?RPM directory required}
staging=${2:?New staging directory required}
asset_base=${3:?Release asset base URL required}
fingerprint=${4:?Full trusted signing fingerprint required}
: "${GNUPGHOME:?Set a dedicated existing local GnuPG directory}"
[[ $fingerprint =~ ^[A-Fa-f0-9]{40}$ ]] || exit 2
gpg --batch --homedir "$GNUPGHOME" --list-secret-keys "$fingerprint" >/dev/null
for package in "$incoming"/*.rpm; do
    rpmsign --define "_gpg_path $GNUPGHOME" --define "_gpg_name $fingerprint" --define '__gpg /usr/bin/gpg' --addsign "$package"
done
pub=$incoming/BYPSSD-OS-RPM.asc
gpg --batch --homedir "$GNUPGHOME" --armor --export "$fingerprint" > "$pub"
rpmkeys --import "$pub"
rpmkeys --checksig "$incoming"/*.rpm
bash scripts/updates/stage-repository.sh "$incoming" "$staging" "$asset_base"
for arch in aarch64 x86_64; do
    gpg --batch --homedir "$GNUPGHOME" --local-user "$fingerprint" --armor --detach-sign "$staging/$arch/repodata/repomd.xml"
    cp "$pub" "$staging/$arch/repodata/repomd.xml.key"
    gpg --batch --homedir "$GNUPGHOME" --verify "$staging/$arch/repodata/repomd.xml.asc" "$staging/$arch/repodata/repomd.xml"
done
printf '%s\n' "$fingerprint" > "$staging/SIGNING-FINGERPRINT"
