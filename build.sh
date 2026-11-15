#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
case "${1:-help}" in
 github) gh workflow run build-opensuse.yml --repo bypssd/bypssd-os ;;
 prepare) python3 scripts/opensuse/prepare.py ;;
 linux-container) [[ $(uname -s) == Linux ]] || { echo 'Este modo requiere el contenedor Linux aislado.' >&2; exit 1; }; exec bash scripts/opensuse/build.sh ;;
 *) printf 'Uso: ./build.sh github | prepare | linux-container\nLa versión actual usa openSUSE; las recetas Fedora son históricas.\n' ;;
esac
