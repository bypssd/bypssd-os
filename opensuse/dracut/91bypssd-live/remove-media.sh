#!/bin/sh
# Executed in the shutdown initramfs, after the Live filesystems are released.
case " $(cat /proc/cmdline) " in *' rd.live.image '*) ;; *) return 0 ;; esac
[ "${ACTION:-}" = reboot ] || return 0
message='Please remove the installation media, and then press enter'
# Never let an unresponsive optical drive or splash daemon block the prompt.
for dev in /dev/sr*; do [ ! -b "$dev" ] || timeout 3 eject "$dev" 2>/dev/null || :; done
if command -v plymouth >/dev/null 2>&1; then timeout 5 plymouth quit 2>/dev/null || :; fi
# tty0 can still refer to the compositor's inactive VT during graphical shutdown.
if [ -c /dev/tty1 ]; then
 console=/dev/tty1
 chvt 1 2>/dev/null || :
else
 console=/dev/console
fi
stty sane < "$console" 2>/dev/null || :
printf '\033c\033[?25h\n%s\n\n' "$message" > "$console"
read -r answer < "$console"
return 0
