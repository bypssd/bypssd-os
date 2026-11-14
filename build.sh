#!/bin/bash
# All Linux commands run in the dedicated Podman VM. Never use Parallels.
set -euo pipefail
cd "$(dirname "$0")"
project=$(pwd -P)
machine=bypssd-build
container=bypssd-build-f45
connection=${machine}-root
export CONTAINERS_MACHINE_PROVIDER=applehv
mkdir -p out/logs
stamp=$(date -u +%Y%m%dT%H%M%SZ)
phase=${1:-all}

run_logged() {
  local name=$1
  shift
  "$@" 2>&1 | tee "out/logs/${stamp}-${name}.log"
}
remote() { podman --connection "$connection" exec "$container" "$@"; }

prepare_sources() {
  local repo expected actual
  for repo in breeze plasma-workspace; do
    if [ ! -d "src/$repo/.git" ]; then
      git clone --depth 1 --branch v6.8.2 "https://invent.kde.org/plasma/$repo.git" "src/$repo"
    fi
    expected=$(cat "branding/$repo-upstream.commit")
    actual=$(git -C "src/$repo" rev-parse HEAD)
    if [ "$actual" != "$expected" ]; then
      echo "Unexpected source commit for $repo: $actual (expected $expected)" >&2
      exit 1
    fi
  done
  python3 scripts/prepare-branding.py
  test -f assets/logo.png
  test -f assets/wallpaper.png
}

prepare_environment() {
  for tool in podman git python3 launchctl; do
    command -v "$tool" >/dev/null || { echo "Missing prerequisite: $tool" >&2; exit 1; }
  done
  command -v vfkit >/dev/null || { echo 'Install vfkit with: brew install vfkit' >&2; exit 1; }
  if ! podman --connection "$connection" info >/dev/null 2>&1; then
    if ! launchctl print "gui/$(id -u)/com.bypssd.builder" >/dev/null 2>&1; then
      launchctl bootstrap "gui/$(id -u)" "$project/scripts/com.bypssd.builder.plist"
    else
      launchctl kickstart "gui/$(id -u)/com.bypssd.builder"
    fi
    local attempts=0
    until podman --connection "$connection" info >/dev/null 2>&1; do
      attempts=$((attempts + 1))
      if [ "$attempts" -ge 120 ]; then
        echo 'Podman did not become ready. See out/logs/podman-service*.log.' >&2
        exit 1
      fi
      sleep 1
    done
  fi
  if ! podman --connection "$connection" container exists "$container"; then
    podman --connection "$connection" run --detach --privileged --name "$container" \
      --platform linux/arm64 --volume "$project:/workspace" --workdir /workspace \
      registry.fedoraproject.org/fedora:45 sleep infinity
  else
    podman --connection "$connection" start "$container" >/dev/null
  fi
  run_logged container-setup remote bash scripts/container-setup.sh
}

build_packages() {
  prepare_sources
  run_logged rpmbuild remote bash scripts/build-rpms.sh
}

build_iso() (
  mode=$(podman machine ssh --username root "$machine" getenforce | tr -d '\r')
  if [ "$mode" = Enforcing ]; then
    podman machine ssh --username root "$machine" setenforce 0
    trap 'podman machine ssh --username root "$machine" setenforce 1' EXIT
  fi
  run_logged iso remote env "BYPSSD_KIWI_RESUME=${BYPSSD_KIWI_RESUME:-}" bash scripts/build-kiwi.sh
)

case "$phase" in
  env) prepare_environment ;;
  rpms) prepare_environment; build_packages ;;
  iso) build_iso ;;
  all) prepare_environment; build_packages; build_iso ;;
  *) echo "Usage: $0 [env|rpms|iso|all]" >&2; exit 2 ;;
esac
