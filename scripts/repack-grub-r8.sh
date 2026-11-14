#!/bin/bash
# Change only the x64 GRUB text configuration; preserve all RPM/EFI/kernel payloads.
set -euo pipefail
cd /workspace
dnf -y --setopt=install_weak_deps=False install xorriso isomd5sum grub2-tools python3
mkdir -p out/publish-r8 out/repack-tmp out/logs
(cd out/original-r7 && sha256sum -c BYPSSD-OS-Renacer-1.0-aarch64.iso.sha256 && sha256sum -c BYPSSD-OS-Renacer-1.0-x86_64.iso.sha256)
xorriso -osirrox on -indev out/original-r7/BYPSSD-OS-Renacer-1.0-x86_64.iso \
 -extract /boot/grub2/grub.cfg out/repack-tmp/grub-original.cfg
python3 scripts/fix-grub-video.py out/repack-tmp/grub-original.cfg out/repack-tmp/grub-fixed.cfg
grub2-script-check out/repack-tmp/grub-fixed.cfg
xorriso -indev out/original-r7/BYPSSD-OS-Renacer-1.0-x86_64.iso \
 -outdev out/publish-r8/BYPSSD-OS-Renacer-1.0-x86_64.iso \
 -boot_image any replay -map out/repack-tmp/grub-fixed.cfg /boot/grub2/grub.cfg -commit -end
implantisomd5 --force --supported-iso out/publish-r8/BYPSSD-OS-Renacer-1.0-x86_64.iso
checkisomd5 out/publish-r8/BYPSSD-OS-Renacer-1.0-x86_64.iso
cp --reflink=auto out/original-r7/BYPSSD-OS-Renacer-1.0-aarch64.iso out/publish-r8/
cp out/original-r7/package-manifest-*.txt out/original-r7/branding-audit-*.json out/publish-r8/
python3 - <<'PY'
from pathlib import Path
import hashlib,json
p=Path('out/repack-tmp')
report={'source_release':'renacer-1.0-r7','change':'x86_64: flatten invalid nested GRUB video function declarations','unchanged':'aarch64 ISO bytes; all kernel, EFI binaries, initrd and LiveOS payloads','original_grub_sha256':hashlib.sha256((p/'grub-original.cfg').read_bytes()).hexdigest(),'fixed_grub_sha256':hashlib.sha256((p/'grub-fixed.cfg').read_bytes()).hexdigest(),'grub_script_check':'passed','media_md5_check':'passed'}
Path('out/publish-r8/grub-fix-report.json').write_text(json.dumps(report,indent=2)+'\n')
PY
(cd out/publish-r8 && for file in *.iso; do sha256sum "$file" > "$file.sha256"; done)
