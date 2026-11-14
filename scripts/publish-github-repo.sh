#!/bin/bash
# Explicit publication command. Not called by build.sh.
set -euo pipefail
cd "$(dirname "$0")/.."
repository=${1:?Usage: publish-github-repo.sh OWNER/REPO TAG}
tag=${2:?Missing tag}
stage="out/github-repository/$tag"
test -f "$stage/pages/RPM-GPG-KEY-BYPSSD"
test -f "$stage/pages/45/aarch64/repodata/repomd.xml.asc"
grep -q '^SIGNED:' "$stage/STATUS.txt"
command -v gh >/dev/null
# Never clobber existing release assets: metadata points at immutable RPM URLs.
gh release create "$tag" "$stage"/assets/*.rpm --repo "$repository" \
 --title "BYPSSD OS: paquetes $tag" --notes-file docs/github-release-notes.md
printf '\nRPM uploaded. Publish the matching pages/ directory using the documented Pages workflow.\n'
