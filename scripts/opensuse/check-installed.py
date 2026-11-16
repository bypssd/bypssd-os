#!/usr/bin/env python3
"""Run as root in an installed BYPSSD guest; exits nonzero on inconsistencies."""
from pathlib import Path
import configparser,json,subprocess,re
errors=[]
def check(ok,message):
 if not ok:errors.append(message)
check(Path('/var/lib/bypssd/installed').is_file(),'Missing installed-state marker')
check('rd.live.image' not in Path('/proc/cmdline').read_text(),'Live kernel parameters remain in installed boot')
check(not Path('/etc/sddm.conf.d/10-bypssd-live.conf').exists(),'Live autologin remains')
check(not Path('/etc/sudoers.d/90-bypssd-live').exists(),'Live passwordless sudo remains')
check(not Path('/etc/polkit-1/rules.d/49-bypssd-live.rules').exists(),'Live authorization remains')
for p in Path('/usr/share/applications').glob('*.desktop'):
 try:text=p.read_text()
 except (OSError,UnicodeError):continue
 if re.search(r'^(Exec|TryExec)=.*(calamares|bypssd-install)',text,re.M):
  override=Path('/usr/local/share/applications')/p.name
  check(override.is_file() and 'Hidden=true' in override.read_text(),'Installer visible: '+p.name)
for base in [Path('/home'),Path('/etc/skel')]:
 check(not list(base.rglob('bypssd-install.desktop')),'Installer shortcut remains under '+str(base))
for theme in ['ocean','oxygen']:
 check(Path('/usr/share/sounds',theme,'index.theme').is_file(),'Missing sound theme '+theme)
check(Path('/boot/initrd').is_file(),'Missing installed initramfs')
theme=subprocess.check_output(['bash','-c','. /etc/default/grub; printf "%s" "$GRUB_THEME"'],text=True)
check(Path(theme).is_file(),'Configured GRUB theme does not exist')
check(Path('/boot/grub2/grub.cfg').is_file(),'Missing GRUB configuration')
for path in ['EFI/BYPSSD/grub.cfg','EFI/BOOT/grub.cfg']:
 check(Path('/boot/efi',path).is_file(),'Missing '+path)
failed=subprocess.check_output(['systemctl','--failed','--no-legend','--plain'],text=True)
check(not failed.strip(),'Failed system units: '+failed)
print(json.dumps({'installed_checks':'passed' if not errors else 'failed','errors':errors},indent=2))
raise SystemExit(bool(errors))
