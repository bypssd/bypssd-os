#!/bin/sh
# Executed in the shutdown initramfs, after the Live filesystems are unmounted.
case " $(cat /proc/cmdline) " in *' rd.live.image '*) ;; *) return 0 ;; esac
[ "${ACTION:-}" = reboot ] || return 0
message='Please remove the installation media, and then press enter'
# This hook is reached only after the root filesystem has been released.
for dev in /dev/sr*; do [ ! -b "$dev" ] || eject "$dev" 2>/dev/null || :; done
if command -v plymouth >/dev/null 2>&1; then plymouth quit 2>/dev/null || :; fi
if [ -c /dev/tty0 ]; then console=/dev/tty0; else console=/dev/console; fi
printf '\n%s\n\n' "$message" > "$console"
read -r answer < "$console"
return 0
