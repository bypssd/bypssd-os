#!/usr/bin/env python3
"""Generate native openSUSE branding payload and architecture-specific KIWI recipe."""
from pathlib import Path
import os,shutil,json,xml.etree.ElementTree as E
r=Path(__file__).resolve().parents[2];arch=os.environ.get('BYPSSD_ARCH','aarch64');assert arch in ('aarch64','x86_64')
stage=r/'out/opensuse';payload=stage/'payload';share=payload/'usr/share';desc=stage/'description';desc.mkdir(parents=True,exist_ok=True)
def copy(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True)
 if src.is_dir():shutil.copytree(src,dst,dirs_exist_ok=True)
 else:shutil.copy2(src,dst)
def write(dst,text):
 dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():dst.chmod(dst.stat().st_mode | 0o200)
 dst.write_text(text)
copy(r/'opensuse/bypssd-efi-config',payload/'usr/libexec/bypssd-efi-config');(payload/'usr/libexec/bypssd-efi-config').chmod(0o755)
copy(r/'assets',share/'bypssd');copy(r/'branding/start',share/'bypssd/start');copy(r/'branding/browser',share/'bypssd/browser')
copy(r/'branding/look-and-feel',share/'plasma/look-and-feel/com.bypssd.desktop')
p=share/'plasma/look-and-feel/com.bypssd.desktop/contents/defaults';p.write_text(p.read_text().replace('widgetStyle=BYPSSD','widgetStyle=Breeze'))
# The native openSUSE Chromium desktop ID is chromium-browser.desktop.
copy(r/'branding/BYPSSDRenacer.colors',share/'color-schemes/BYPSSDRenacer.colors')
copy(r/'branding/sddm',share/'sddm/themes/bypssd');copy(r/'branding/plymouth',share/'plymouth/themes/bypssd');copy(r/'assets/logo-256.png',share/'plymouth/themes/bypssd/logo.png')
copy(r/'assets/wallpaper.png',share/'wallpapers/com.bypssd.wallpaper/contents/images/1920x1080.png');copy(r/'branding/wallpaper-metadata.json',share/'wallpapers/com.bypssd.wallpaper/metadata.json')
copy(r/'assets/logo-48.png',share/'icons/hicolor/48x48/apps/bypssd-logo.png');copy(r/'assets/logo-256.png',share/'icons/hicolor/256x256/apps/bypssd-logo.png')
copy(r/'opensuse/calamares/branding',share/'calamares/branding/bypssd');copy(r/'assets/logo-256.png',share/'calamares/branding/bypssd/logo.png');copy(r/'assets/wallpaper.png',share/'calamares/branding/bypssd/wallpaper.png')
copy(r/'assets/wallpaper.png',share/'grub2/themes/bypssd/wallpaper.png')
write(share/'grub2/themes/bypssd/theme.txt',"""desktop-image: "wallpaper.png"
title-text: "BYPSSD OS Renacer"
title-color: "#FFB800"
title-font: "Unifont Regular 16"
message-color: "#FFFFFF"
terminal-font: "Unifont Regular 16"
+ boot_menu {
 left = 10%
 top = 35%
 width = 80%
 height = 40%
 item_color = "#FFFFFF"
 selected_item_color = "#FFB800"
 item_font = "Unifont Regular 16"
 selected_item_font = "Unifont Regular 16"
 item_height = 36
 item_padding = 12
 item_spacing = 8
}
""")
copy(r/'branding/licenses',share/'bypssd/licenses');copy(r/'assets/LICENSE.txt',share/'bypssd/licenses/ASSETS.txt')
write(share/'bypssd/README.txt','BYPSSD OS Renacer 1.1\nDistribución independiente basada en openSUSE Tumbleweed.\nNo es un producto oficial de openSUSE ni de SUSE.\nSe conservan las licencias, firmas y atribuciones originales.\n')
write(share/'metainfo/com.bypssd.bypssd.metainfo.xml','''<?xml version="1.0"?><component type="operating-system"><id>com.bypssd.bypssd</id><name>BYPSSD OS Renacer</name><summary>Sistema para oficina y educación</summary><metadata_license>CC0-1.0</metadata_license><project_license>LicenseRef-mixed</project_license><url type="homepage">https://bypssd.com</url><developer id="com.bypssd"><name>BYPSSD Informática Retro</name></developer></component>''')
meta=E.parse(share/'metainfo/com.bypssd.bypssd.metainfo.xml').getroot()
collection=E.Element('components',version='1.0',origin='bypssd');collection.append(meta)
write(share/'swcatalog/xml/bypssd-os.xml',E.tostring(collection,encoding='unicode'))
root=desc/'root';copy(r/'opensuse/calamares',root/'etc/calamares');copy(r/'opensuse/bypssd-updates.repo',root/'etc/zypp/repos.d/bypssd-updates.repo')
for n in ('kdeglobals','ksplashrc','kscreenlockerrc'):
 text=(r/'branding/config'/n).read_text().replace('widgetStyle=BYPSSD','widgetStyle=Breeze');write(root/'etc/xdg'/n,text);write(root/'etc/skel/.config'/n,text)
copy(r/'branding/config/kcm-about-distrorc',root/'etc/skel/.config/kcm-about-distrorc')
p=root/'etc/skel/.config/kcm-about-distrorc';p.write_text(p.read_text().replace('Renacer 1.0','Renacer 1.1').replace('/usr/share/bypssd/logo-256.png','/usr/share/bypssd/logo-256.png'))
copy(r/'branding/config/sddm.conf',root/'etc/sddm.conf.d/90-bypssd.conf')
p=root/'etc/sddm.conf.d/90-bypssd.conf';p.write_text(p.read_text().replace('[General]','[General]\nInputMethod='))
copy(r/'branding/config/mimeapps.list',root/'etc/skel/.config/mimeapps.list')
copy(r/'branding/config/mimeapps.list',root/'etc/xdg/mimeapps.list')
write(root/'usr/share/bypssd/os-release','''NAME="BYPSSD OS"
PRETTY_NAME="BYPSSD OS Renacer 1.1"
ID=bypssd
ID_LIKE="opensuse suse"
VERSION="1.1 (Renacer)"
VERSION_ID="1.1"
VERSION_CODENAME=renacer
LOGO=bypssd-logo
HOME_URL="https://bypssd.com"
SUPPORT_URL="https://bypssd.com"
BUG_REPORT_URL="https://github.com/bypssd/bypssd-os/issues"
''')
write(root/'etc/sudoers.d/90-bypssd-live','linux ALL=(ALL) NOPASSWD: ALL\n');(root/'etc/sudoers.d/90-bypssd-live').chmod(0o440)
write(root/'etc/sudoers.d/91-bypssd-admin','Defaults:%wheel !targetpw\n%wheel ALL=(ALL:ALL) ALL\n');(root/'etc/sudoers.d/91-bypssd-admin').chmod(0o440)
write(root/'etc/polkit-1/rules.d/49-bypssd-live.rules','''polkit.addRule(function(action, subject) {
 if (subject.user !== "linux" || !subject.local || !subject.active) return;
 if (action.id === "io.calamares.calamares.pkexec.run" || action.id === "com.bypssd.install") return polkit.Result.YES;
 if (action.id === "org.freedesktop.policykit.exec" && (action.lookup("program") === "/usr/bin/calamares" || action.lookup("program") === "/usr/libexec/bypssd-calamares")) return polkit.Result.YES;
 var allowed = ["package-install", "package-reinstall", "package-remove", "system-sources-refresh", "system-update"];
 for (var i=0; i<allowed.length; i++) if (action.id === "org.freedesktop.packagekit." + allowed[i]) return polkit.Result.YES;
});
''')
write(root/'etc/polkit-1/rules.d/50-bypssd-admin.rules','polkit.addAdminRule(function(action, subject) { return ["unix-group:wheel"]; });\n')
write(share/'polkit-1/actions/com.bypssd.install.policy','''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policyconfig PUBLIC "-//freedesktop//DTD PolicyKit Policy Configuration 1.0//EN" "http://www.freedesktop.org/standards/PolicyKit/1.0/policyconfig.dtd">
<policyconfig>
 <vendor>BYPSSD Informática Retro</vendor><vendor_url>https://bypssd.com</vendor_url>
 <action id="com.bypssd.install">
  <description>Instalar BYPSSD OS</description>
  <message>Se necesita autorización para instalar BYPSSD OS en el equipo.</message>
  <icon_name>bypssd-logo</icon_name>
  <defaults><allow_any>no</allow_any><allow_inactive>auth_admin</allow_inactive><allow_active>auth_admin</allow_active></defaults>
  <annotate key="org.freedesktop.policykit.exec.path">/usr/libexec/bypssd-calamares</annotate>
  <annotate key="org.freedesktop.policykit.exec.allow_gui">true</annotate>
 </action>
</policyconfig>
''')
write(payload/'usr/libexec/bypssd-calamares','''#!/bin/sh
# Keep the installer readable on virtual GPUs and systems without accelerated Qt Quick.
export QT_QUICK_BACKEND=software
exec /usr/bin/calamares "$@"
''');(payload/'usr/libexec/bypssd-calamares').chmod(0o755)
write(root/'usr/share/applications/bypssd-install.desktop','''[Desktop Entry]
Type=Application
Name=Instalar BYPSSD OS
Comment=Instalar BYPSSD OS Renacer en este equipo
Exec=pkexec /usr/libexec/bypssd-calamares
Icon=bypssd-logo
Terminal=false
Categories=System;
''')
copy(root/'usr/share/applications/bypssd-install.desktop',root/'etc/skel/Desktop/bypssd-install.desktop')
write(root/'etc/systemd/system/bypssd-live.service','''[Unit]
Description=Preparar sesión Live BYPSSD
Before=display-manager.service
ConditionKernelCommandLine=rd.live.image
[Service]
Type=oneshot
ExecStart=/usr/libexec/bypssd-live-setup
[Install]
WantedBy=graphical.target
''')
write(root/'usr/libexec/bypssd-live-setup','''#!/bin/bash
set -eu
id linux >/dev/null 2>&1 || useradd -m -c 'Sesión Live BYPSSD' -G users,video,audio linux
passwd -d linux
session=$(basename "$(find /usr/share/wayland-sessions -name '*plasma*.desktop' | head -1)")
mkdir -p /etc/sddm.conf.d
printf '\\nDISPLAYMANAGER_AUTOLOGIN="linux"\\n' >> /etc/sysconfig/displaymanager
printf '[Autologin]\\nUser=linux\\nSession=%s\\nRelogin=false\\n' "$session" > /etc/sddm.conf.d/10-bypssd-live.conf
install -d -o linux -g users /home/linux/Desktop
install -o linux -g users -m755 /usr/share/applications/bypssd-install.desktop /home/linux/Desktop/
''');(root/'usr/libexec/bypssd-live-setup').chmod(0o755)
# Browser configuration is supported admin policy, not a patched browser binary.
copy(r/'branding/browser/master_preferences',root/'etc/chromium/master_preferences')
copy(r/'branding/browser/firefox-policies.json',root/'etc/firefox/policies/policies.json')
write(root/'etc/chromium/policies/managed/bypssd.json',json.dumps({'HomepageLocation':'file:///usr/share/bypssd/start/index.html','HomepageIsNewTabPage':False,'RestoreOnStartup':4,'RestoreOnStartupURLs':['file:///usr/share/bypssd/start/index.html'],'ShowHomeButton':True,'BookmarkBarEnabled':False},indent=2))
# native architecture repos and bootstrap (no Fedora RPM URLs or packages)
base='https://download.opensuse.org/'+('ports/aarch64/' if arch=='aarch64' else '')+'tumbleweed/repo/oss/'
image=E.Element('image',schemaversion='7.6',name='BYPSSD-OS-Renacer',displayname='BYPSSD OS Renacer')
d=E.SubElement(image,'description',type='system')
for k,v in [('author','BYPSSD Informática Retro'),('contact','https://bypssd.com'),('specification','BYPSSD OS Renacer 1.1 · KDE · base openSUSE Tumbleweed')]:E.SubElement(d,k).text=v
prefs=E.SubElement(image,'preferences');t=E.SubElement(prefs,'type',image='iso',primary='true',flags='overlay',firmware='uefi',mediacheck='true',volid='BYPSSD',squashfscompression='zstd',kernelcmdline='quiet splash=silent rd.live.image')
E.SubElement(t,'bootloader',name='grub2',timeout='5')
for k,v in [('version','1.1.0'),('packagemanager','zypper'),('locale','es_ES'),('keytable','es'),('timezone','Europe/Madrid'),('rpm-excludedocs','true'),('bootsplash-theme','bypssd'),('bootloader-theme','bypssd')]:E.SubElement(prefs,k).text=v
for alias,url,priority,check in [('bypssd-build','dir:///workspace/out/opensuse/rpms','1','false'),('opensuse-oss',base,'99','true')]:
 repo=E.SubElement(image,'repository',type='rpm-md',alias=alias,priority=priority,package_gpgcheck=check);E.SubElement(repo,'source',path=url)
pkgs=E.SubElement(image,'packages',type='bootstrap')
for n in ('filesystem','glibc-locale','ca-certificates','ca-certificates-mozilla','zypper','openSUSE-release','shadow','gawk','grep','gzip','xz','udev') :E.SubElement(pkgs,'package',name=n)
pkgs=E.SubElement(image,'packages',type='image')
for line in (r/'opensuse/packages.txt').read_text().splitlines():
 if line and not line.startswith('#'):E.SubElement(pkgs,'package',name=line)
for n in (['grub2-arm64-efi'] if arch=='aarch64' else ['grub2-x86_64-efi','grub2-i386-pc']):E.SubElement(pkgs,'package',name=n)
for n in ('plasma6-branding-openSUSE','sddm-branding-openSUSE','sddm-qt6-branding-openSUSE','plymouth-branding-openSUSE','grub2-branding-openSUSE'):E.SubElement(pkgs,'ignore',name=n)
pkgs=E.SubElement(image,'packages',type='iso');E.SubElement(pkgs,'package',name='dracut-kiwi-live')
E.indent(image,space='  ');E.ElementTree(image).write(desc/'BYPSSD.kiwi',encoding='utf-8',xml_declaration=True)
copy(r/'opensuse/config.sh',desc/'config.sh');(desc/'config.sh').chmod(0o755)
print('Prepared',arch,base)
