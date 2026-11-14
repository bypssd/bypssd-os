#!/usr/bin/env python3
from pathlib import Path
import xml.etree.ElementTree as ET
import os
root = Path(__file__).resolve().parents[1]
arch = os.environ.get('BYPSSD_ARCH','aarch64')
if arch not in ('aarch64','x86_64'):raise SystemExit('Unsupported architecture: '+arch)
out = root/'kickstart/kiwi'/arch
out.mkdir(parents=True,exist_ok=True)
efi = 'aa64' if arch == 'aarch64' else 'x64'
template = 'grub-arm.cfg.iso-template' if arch == 'aarch64' else 'grub-x86.cfg.iso-template'
ks = (root/'kickstart/bypssd.ks').read_text()
if arch == 'x86_64':ks = ks.replace('aarch64','x86_64').replace('grub2-efi-aa64','grub2-efi-x64').replace('shim-aa64','shim-x64')
image = ET.Element('image', schemaversion='7.4', name='BYPSSD-OS-Renacer', displayname='BYPSSD OS Renacer')
desc = ET.SubElement(image, 'description', type='system')
for key, value in [('author','BYPSSD Informática Retro'),('contact','https://bypssd.com'),('specification','Sistema para oficina y educación')]:
    ET.SubElement(desc,key).text=value
prefs = ET.SubElement(image,'preferences')
ET.SubElement(prefs,'type',image='iso',primary='true',flags='dmsquash',filesystem='erofs',erofscompression='lzma,level=6',mediacheck='true',firmware='uefi',efiparttable='gpt',efifatimagesize='30',kernelcmdline='quiet rhgb rd.live.image',publisher='BYPSSD INFORMATICA RETRO',volid='BYPSSD',application_id='BYPSSD_OS',fscreateoptions='-Efragments -C 1048576')
ET.SubElement(prefs.find('type'),'bootloader',name='grub2',grub_template=template,console='console',timeout='5')
for key,value in [('version','1.0.0'),('packagemanager','dnf5'),('locale','es_ES'),('keytable','es'),('timezone','Europe/Madrid'),('release-version','45')]:
    ET.SubElement(prefs,key).text=value
for alias,path,priority in [('bypssd','dir:///workspace/out/rpms','1'),('base',f'https://download.fedoraproject.org/pub/fedora/linux/releases/45/Everything/{arch}/os/','99'),('updates',f'https://download.fedoraproject.org/pub/fedora/linux/updates/45/Everything/{arch}/','99')]:
    repo=ET.SubElement(image,'repository',type='rpm-md',alias=alias,priority=priority,package_gpgcheck='false')
    ET.SubElement(repo,'source',path=path)
bootstrap=ET.SubElement(image,'packages',type='bootstrap')
for name in ['filesystem','dnf5','bypssd-release-identity']:
    ET.SubElement(bootstrap,'package',name=name)
packages=ET.SubElement(image,'packages',type='image',patternType='onlyRequired')
inside=False
for raw in ks.splitlines():
    line=raw.split('#',1)[0].strip()
    if line.startswith('%packages'):
        inside=True
        continue
    if line=='%end': inside=False
    if not inside or not line: continue
    if line.startswith('-'): ET.SubElement(packages,'ignore',name=line[1:])
    elif line.startswith('@'): ET.SubElement(packages,'namedCollection',name=line[1:])
    else: ET.SubElement(packages,'package',name=line)
for name in [f'grub2-efi-{efi}-modules','grubby','isomd5sum','btrfs-progs','udisks2-btrfs']:
    ET.SubElement(packages,'package',name=name)
if arch == 'x86_64':
    for name in ['grub2-pc','grub2-pc-modules']:
        ET.SubElement(packages,'package',name=name)
iso=ET.SubElement(image,'packages',type='iso')
ET.SubElement(iso,'package',name=f'grub2-efi-{efi}-cdboot')
ET.SubElement(iso,'file',name='iso-esp-excludes.yaml',target='image/exclude_files_efifatimage.yaml')
ET.indent(image,space='  ')
ET.ElementTree(image).write(out/'BYPSSD.kiwi',encoding='utf-8',xml_declaration=True)
post=ks.split('%post --erroronfail --log=/root/bypssd-post.log\n',1)[1].rsplit('%end',1)[0]
(out/'config.sh').write_text('#!/bin/bash\n# BYPSSD configuration, shared with the kickstart.\n'+post)
(out/'config.sh').chmod(0o755)
text=(root/'kickstart/kiwi-upstream'/template).read_text()
text=text.replace('set default="1"','set default="0"').replace('--class fedora','--class bypssd').replace('Test this media & start ${title}','Comprobar el medio e iniciar ${title}').replace('Start ${title} in basic graphics mode','Iniciar ${title} con gráficos básicos').replace('Start ${title}','Iniciar ${title}').replace('Troubleshooting -->','Solución de problemas -->')
(out/template).write_text(text)
(out/'iso-esp-excludes.yaml').write_bytes((root/'kickstart/kiwi-upstream/iso-esp-excludes.yaml').read_bytes())
(out/'COPYING').write_bytes((root/'kickstart/kiwi-upstream/COPYING').read_bytes())
