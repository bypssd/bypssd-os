#!/bin/zsh
export PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin
export CONTAINERS_MACHINE_PROVIDER=applehv
set -e
if ! podman machine inspect bypssd-build >/dev/null 2>&1; then
  podman machine init --provider applehv --cpus 6 --memory 8192 --disk-size 60 \
    --rootful --volume /Users/andy/BYPSSD-OS:/Users/andy/BYPSSD-OS bypssd-build
fi
if ! podman --connection bypssd-build-root info >/dev/null 2>&1; then
  podman machine start bypssd-build
fi
while podman --connection bypssd-build-root info >/dev/null 2>&1; do
  sleep 30
done
