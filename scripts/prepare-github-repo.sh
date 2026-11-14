#!/bin/bash
# Run inside the dedicated Fedora container. Creates local files only.
set -euo pipefail
cd /workspace
repository=${1:?Usage: prepare-github-repo.sh OWNER/REPOSITORY TAG}
tag=${2:?Missing immutable release tag}
[[ "$repository" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || exit 2
[[ "$tag" =~ ^[A-Za-z0-9_.-]+$ ]] || exit 2
stage="out/github-repository/$tag"
[ ! -e "$stage" ] || { echo "Output already exists: $stage. Use a new tag." >&2; exit 1; }
mkdir -p "$stage/assets" "$stage/pages/45/aarch64"
# Select latest versions using RPM's own version comparison, not filename sort.
python3 - "$stage" <<'PY'
from pathlib import Path
import rpm,shutil,sys
stage=Path(sys.argv[1]); ts=rpm.TransactionSet();ts.setVSFlags(rpm._RPMVSF_NOSIGNATURES)
best={}
for p in Path('out/rpms').glob('bypssd-*.rpm'):
 with p.open('rb') as f:h=ts.hdrFromFdno(f)
 n=h['name']
 if n not in {'bypssd-branding','bypssd-breeze-style','bypssd-release-identity'}:continue
 v=(str(h['epoch'] or 0),h['version'],h['release'])
 if n not in best or rpm.labelCompare(v,best[n][0])>0:best[n]=(v,p)
if len(best)!=3:raise SystemExit('Expected exactly three BYPSSD package names')
for _,p in best.values():shutil.copy2(p,stage/'assets'/p.name)
PY
key=${BYPSSD_SIGNING_KEY:-}
if [ -n "$key" ]; then
  for package in "$stage"/assets/*.rpm; do rpmsign --addsign --define "_openpgp_sign gpg" --define "_openpgp_sign_id $key" "$package"; done
  gpg --armor --export "$key" > "$stage/pages/RPM-GPG-KEY-BYPSSD"
  test -s "$stage/pages/RPM-GPG-KEY-BYPSSD"
fi
createrepo_c --baseurl "https://github.com/$repository/releases/download/$tag/" "$stage/assets"
cp -r "$stage/assets/repodata" "$stage/pages/45/aarch64/"
# Only RPMs are release assets; metadata is published atomically through Pages.
if [ -n "$key" ]; then
  gpg --batch --yes --armor --detach-sign --local-user "$key" "$stage/pages/45/aarch64/repodata/repomd.xml"
fi
owner=${repository%%/*};repo=${repository#*/}
cat > "$stage/pages/bypssd.repo" <<REPO
[bypssd]
name=BYPSSD OS - Paquetes propios
baseurl=https://$owner.github.io/$repo/45/\$basearch/
enabled=$([ -n "$key" ] && echo 1 || echo 0)
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://$owner.github.io/$repo/RPM-GPG-KEY-BYPSSD
metadata_expire=6h
REPO
printf '%s\n' '<!doctype html><meta charset="utf-8"><title>Repositorio BYPSSD OS</title><h1>Repositorio BYPSSD OS</h1><p>Paquetes propios para ARM64. Instalación: <a href="bypssd.repo">bypssd.repo</a>.</p>' > "$stage/pages/index.html"
touch "$stage/pages/.nojekyll"
python3 - "$stage" <<'PYCODE'
import rpm,shutil,sys
from pathlib import Path
s=Path(sys.argv[1]);ts=rpm.TransactionSet();ts.setVSFlags(rpm._RPMVSF_NOSIGNATURES)
for p in list((s/'assets').glob('*.rpm')):
 with p.open('rb') as f:h=ts.hdrFromFdno(f)
 source=Path('out/srpms')/h['sourcerpm']
 if not source.is_file():raise SystemExit('Missing matching source RPM: '+str(source))
 shutil.copy2(source,s/'assets'/source.name)
PYCODE
if [ -z "$key" ]; then
  echo 'DEVELOPMENT ONLY: unsigned packages and metadata; bypssd.repo is disabled.' | tee "$stage/STATUS.txt"
else
  echo 'SIGNED: verify the public key fingerprint out of band before installation.' | tee "$stage/STATUS.txt"
fi
printf 'Prepared %s. No GitHub upload has been performed.\n' "$stage"
