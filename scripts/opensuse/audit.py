#!/usr/bin/env python3
import configparser,json,sys,subprocess
from pathlib import Path
root=Path(sys.argv[1]);repos={};errors=[]
for p in (root/'etc/zypp/repos.d').glob('*.repo'):
 c=configparser.RawConfigParser();c.read(p)
 for name in c.sections():
  if c[name].get('enabled','1')=='1':repos[name]=dict(c[name])
if set(repos)!={'opensuse-oss','bypssd-updates'}:errors.append('Unexpected active repositories')
for n,r in repos.items():
 if 'fedora' in str(r).lower():errors.append('Fedora repository remains')
if not (root/'etc/os-release').is_file() or 'ID=bypssd' not in (root/'etc/os-release').read_text():errors.append('Missing BYPSSD identity')
required=['discover6','discover6-backend-packagekit','PackageKit-backend-zypp','AppStream','calamares','bypssd-branding','pkexec','xf86-input-libinput','ocean-sound-theme6','oxygen6-sounds','plasma6-pa','pipewire-pulseaudio','qt6-translations','kf6-kcmutils-lang','libKF6KCMUtils6-lang','libKF6ConfigWidgets6-lang','libKF6WidgetsAddons6-lang','libKF6XmlGui6-lang']
for n in required:
 if subprocess.run(['rpm','--root',str(root),'-q',n],stdout=subprocess.DEVNULL).returncode:errors.append('Missing '+n)
grub=(root/'etc/calamares/modules/grubcfg.conf').read_text()
if 'overwrite: true' not in grub or '/usr/share/grub2/themes/bypssd/theme.txt' not in grub:errors.append('Installed GRUB would retain Live parameters or broken theme')
boot=(root/'etc/calamares/modules/bootloader.conf').read_text()
for key in ['grubInstall:', 'grubMkconfig:', 'grubCfg:', 'grubProbe:', 'efiBootMgr:']:
 if key not in boot:errors.append('Missing installer bootloader key '+key)
for rel in ['usr/libexec/bypssd-calamares','usr/share/polkit-1/actions/com.bypssd.install.policy','usr/share/calamares/branding/bypssd/show.qml','usr/share/calamares/branding/bypssd/stylesheet.qss']:
 if not (root/rel).is_file():errors.append('Missing installer branding '+rel)
if 'Defaults:%wheel !targetpw' not in (root/'etc/sudoers.d/91-bypssd-admin').read_text():errors.append('Administrator sudo would request root password')
if '/usr/libexec/bypssd-installed-cleanup' not in (root/'etc/calamares/modules/shellprocess-bypssd-cleanup.conf').read_text():errors.append('Missing installed-system cleanup job')
for rel in ['usr/libexec/bypssd-installed-cleanup','usr/lib/dracut/modules.d/91bypssd-live/remove-media.sh','usr/share/sounds/ocean/index.theme','usr/share/sounds/oxygen/index.theme']:
 if not (root/rel).is_file():errors.append('Missing '+rel)
if not (root/'usr/libexec/bypssd-efi-config').is_file():errors.append('Missing UEFI fallback config helper')
if 'shellprocess@bypssd-efi' not in (root/'etc/calamares/settings.conf').read_text():errors.append('Missing UEFI fallback installer job')
import re
for desktop in (root/'usr/share/applications').glob('*.desktop'):
 if desktop.name=='bypssd-install.desktop':continue
 if re.search(r'^(Exec|TryExec)=.*calamares',desktop.read_text(),re.M):
  override=root/'usr/local/share/applications'/desktop.name
  if not override.exists() or 'NoDisplay=true' not in override.read_text():errors.append('Upstream installer remains visible: '+desktop.name)
admin=json.loads((root/'var/lib/bypssd/hidden-admin-launchers.json').read_text())
for item in admin:
 p=root/'usr/local/share/applications'/item['desktop']
 if not p.is_file() or 'NoDisplay=true' not in p.read_text():errors.append('Admin launcher visible: '+item['desktop'])
 seed=root/'etc/skel/.local/share/applications'/item['desktop']
 if not seed.is_file() or 'NoDisplay=true' not in seed.read_text():errors.append('Missing per-user menu override: '+item['desktop'])
if not {'file-manager','terminal'}.issubset({a['kind'] for a in admin}):errors.append('Expected superuser menu launchers were not hidden')
print(json.dumps({'repositories':repos,'required_packages':required,'hidden_admin_launchers':admin,'errors':errors},indent=2))
if errors:raise SystemExit(1)
