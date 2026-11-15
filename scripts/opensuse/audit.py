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
required=['discover6','discover6-backend-packagekit','PackageKit-backend-zypp','AppStream','calamares','bypssd-branding','pkexec','xf86-input-libinput']
for n in required:
 if subprocess.run(['rpm','--root',str(root),'-q',n],stdout=subprocess.DEVNULL).returncode:errors.append('Missing '+n)
boot=(root/'etc/calamares/modules/bootloader.conf').read_text()
for key in ['grubInstall:', 'grubMkconfig:', 'grubCfg:', 'grubProbe:', 'efiBootMgr:']:
 if key not in boot:errors.append('Missing installer bootloader key '+key)
for rel in ['usr/libexec/bypssd-calamares','usr/share/polkit-1/actions/com.bypssd.install.policy','usr/share/calamares/branding/bypssd/show.qml','usr/share/calamares/branding/bypssd/stylesheet.qss']:
 if not (root/rel).is_file():errors.append('Missing installer branding '+rel)
if 'Defaults:%wheel !targetpw' not in (root/'etc/sudoers.d/91-bypssd-admin').read_text():errors.append('Administrator sudo would request root password')
if '/home/*/Desktop/bypssd-install.desktop' not in (root/'etc/calamares/modules/shellprocess-bypssd-cleanup.conf').read_text():errors.append('Installed desktop keeps Live installer shortcut')
if not (root/'usr/libexec/bypssd-efi-config').is_file():errors.append('Missing UEFI fallback config helper')
if 'shellprocess@bypssd-efi' not in (root/'etc/calamares/settings.conf').read_text():errors.append('Missing UEFI fallback installer job')
import re
for desktop in (root/'usr/share/applications').glob('*.desktop'):
 if desktop.name=='bypssd-install.desktop':continue
 if re.search(r'^(Exec|TryExec)=.*calamares',desktop.read_text(),re.M):
  override=root/'usr/local/share/applications'/desktop.name
  if not override.exists() or 'Hidden=true' not in override.read_text():errors.append('Upstream installer remains visible: '+desktop.name)
print(json.dumps({'repositories':repos,'required_packages':required,'errors':errors},indent=2))
if errors:raise SystemExit(1)
