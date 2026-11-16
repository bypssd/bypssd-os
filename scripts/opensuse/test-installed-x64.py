#!/usr/bin/env python3
"""Black-box Calamares install into a new disposable QEMU disk on CI."""
from pathlib import Path
import subprocess,os,json,time,socket,threading,http.server,functools,shutil,sys
r=Path.cwd();run=r/'out/installed-x64';run.mkdir(parents=True,exist_ok=True)
iso=next((r/'incoming').rglob('BYPSSD-OS-Renacer-1.1-x86_64.iso'))
share=run/'http';share.mkdir(exist_ok=True)
shutil.copy('opensuse/dracut/91bypssd-live/remove-media.sh',share/'remove-media.sh');shutil.copy('scripts/opensuse/qa-bootstrap.sh',share/'qa.sh');shutil.copy('scripts/opensuse/check-installed.py',share/'check.py')
server=http.server.ThreadingHTTPServer(('127.0.0.1',8765),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(share)))
threading.Thread(target=server.serve_forever,daemon=True).start()
shutil.copy('/usr/share/OVMF/OVMF_VARS_4M.fd',run/'vars.fd')
subprocess.run(['qemu-img','create','-f','qcow2',str(run/'disk.qcow2'),'32G'],check=True)
accel=['-accel','kvm','-cpu','host'] if Path('/dev/kvm').exists() else ['-accel','tcg','-cpu','max']
args=['qemu-system-x86_64','-machine','q35',*accel,'-smp','4','-m','4096','-drive','if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE_4M.fd','-drive',f'if=pflash,format=raw,file={run}/vars.fd','-drive',f'if=none,id=livecd,media=cdrom,readonly=on,format=raw,file={iso}','-device','ide-cd,drive=livecd,bootindex=0','-drive',f'if=virtio,format=qcow2,file={run}/disk.qcow2','-device','virtio-vga','-device','qemu-xhci','-device','usb-kbd','-device','usb-tablet','-netdev','user,id=n0','-device','virtio-net-pci,netdev=n0','-audiodev',f'wav,id=qa,path={run}/audio.wav','-device','ich9-intel-hda','-device','hda-output,audiodev=qa','-display','none','-serial',f'unix:{run}/serial.sock,server=on,wait=off','-qmp',f'unix:{run}/qmp.sock,server=on,wait=off']
vm=subprocess.Popen(args,stdout=(run/'qemu.log').open('w'),stderr=subprocess.STDOUT)
os.environ['BYPSSD_QMP_SOCKET']=str(run/'qmp.sock')
def qmp(cmd,arguments=None):
 out=subprocess.check_output([sys.executable,'scripts/qmp.py',cmd]+([json.dumps(arguments)] if arguments else []),text=True);data=json.loads(out)
 if 'error' in data:raise RuntimeError(data)
 return data['return']
def key(k):subprocess.run([sys.executable,'scripts/qmp-type.py','--key',k],check=True)
def text(t,encoded=False):subprocess.run([sys.executable,'scripts/qmp-type.py']+(['--encoded'] if encoded else [])+[t],check=True)
def click(x,y,double=False):subprocess.run([sys.executable,'scripts/qmp-click.py',str(x),str(y),'--width','1000','--height','625']+(['--double'] if double else []),check=True)
def screenshot(name):
 p=run/(name+'.ppm');qmp('screendump',{'filename':str(p)})
 from PIL import Image
 Image.open(p).save(run/(name+'.png'));p.unlink()
def bootwait(seconds):
 for _ in range(seconds//10):
  if vm.poll() is not None:raise RuntimeError('QEMU exited')
  time.sleep(10)
class Serial:
 def __init__(self):
  self.s=socket.socket(socket.AF_UNIX);self.s.settimeout(1);self.s.connect(str(run/'serial.sock'));self.log=(run/'serial.log').open('ab',buffering=0)
 def read(self,seconds):
  data=b'';end=time.time()+seconds
  while time.time()<end:
   try:
    b=self.s.recv(65536)
    if not b:break
    self.log.write(b);data+=b
   except socket.timeout:pass
  return data.decode(errors='replace')
 def command(self,cmd):
  marker='BYPSSD_QA_END';self.s.sendall((cmd+"; printf '\\n%s%s\\n' BYPSSD_QA_ END\n").encode());out='';end=time.time()+100
  while marker not in out and time.time()<end:out+=self.read(1)
  if marker not in out:raise TimeoutError(cmd)
  print(out,flush=True);return out
 def close(self):self.s.close();self.log.close()
bootstrap='curl -fsS http://10.0.2.2:8765/qa.sh | sudo bash'
serial=None
try:
 bootwait(100);screenshot('01-live');key('ctrl-alt-t');time.sleep(4);text(bootstrap,True);time.sleep(4)
 serial=Serial();serial.read(2);serial.command('stty -echo; id; lsblk -o NAME,SIZE,TYPE')
 click(26,605);text('super');time.sleep(1);screenshot('01b-live-no-superuser-entries');key('esc')
 if 'LIVE_SHUTDOWN_IMAGE_OK' not in serial.command('test -s /boot/initrd && echo LIVE_SHUTDOWN_IMAGE_OK'):raise RuntimeError('Live shutdown initramfs missing')
 if os.environ.get('BYPSSD_QA_REBOOT_ONLY')=='1':
  setup=serial.command('/usr/lib/dracut/dracut-initramfs-restore; /usr/lib/dracut/dracut-install -D /run/initramfs -a /usr/bin/chvt /usr/bin/stty /usr/bin/timeout; curl -fsS http://10.0.2.2:8765/remove-media.sh -o /run/initramfs/var/lib/dracut/hooks/shutdown/99-remove-media.sh; sed -i "2i exec 2>/dev/ttyS0; set -x" /run/initramfs/var/lib/dracut/hooks/shutdown/99-remove-media.sh; test -x /run/initramfs/usr/bin/chvt && echo CONSOLE_SETUP_OK')
  if 'CONSOLE_SETUP_OK' not in setup:raise RuntimeError('Console tool installation failed')
  serial.command('systemctl --no-block reboot');seen=False
  for _ in range(30):
   time.sleep(3);serial.read(1);screenshot('reboot-only-prompt')
   words=subprocess.check_output(['tesseract',str(run/'reboot-only-prompt.png'),'stdout'],stderr=subprocess.DEVNULL,text=True).lower()
   if 'installation media' in words and 'enter' in words:seen=True;break
  if not seen:raise RuntimeError('Reboot-only console prompt not visible')
  (run/'reboot-only-result.json').write_text(json.dumps({'scope':'Live reboot prompt only','prompt_visible':True},indent=2)+'\n')
  print('BYPSSD_REBOOT_CONSOLE_QA_OK',flush=True);sys.exit(0)

 click(52,45,True);time.sleep(5);key('meta_l-pgup');time.sleep(2);screenshot('02-welcome')
 live=serial.command('cat /home/linux/.config/kscreenlockerrc; cat /var/lib/bypssd/hidden-admin-launchers.json; systemd-inhibit --list --no-pager')
 if 'Autolock=false' not in live or 'LockOnResume=false' not in live or 'RequirePassword=false' not in live:raise RuntimeError('Live lock protection missing')
 # Reproduce inactivity past KDE's default five-minute automatic lock timeout.
 print('BYPSSD_LIVE_IDLE_TEST_START',flush=True);bootwait(330);screenshot('02b-live-after-idle')
 active=serial.command('runuser -u linux -- env XDG_RUNTIME_DIR=/run/user/1000 busctl --user call org.freedesktop.ScreenSaver /ScreenSaver org.freedesktop.ScreenSaver GetActive')
 if 'b false' not in active:raise RuntimeError('Live session locked during installer inactivity')
 print('BYPSSD_LIVE_IDLE_TEST_OK',flush=True)

 for _ in range(3):click(887,575);time.sleep(1)
 screenshot('03-partition');click(161,77);click(887,575);time.sleep(1)
 for x,y,value in [(233,60,'BYPSSD QA'),(233,108,'qa'),(233,155,'bypssd-qa'),(233,202,'BypssdQA42'),(390,202,'BypssdQA42')]:
  click(x,y);key('ctrl-a');text(value);time.sleep(.5)
 screenshot('04-users');click(887,575);time.sleep(1);screenshot('05-summary');click(887,575)
 deadline=time.time()+600
 while time.time()<deadline:
  out=serial.command("grep 'completion: succeeded' /root/.cache/calamares/session.log || true")
  if 'completion: succeeded' in out:break
  if 'Installation Failed' in serial.command("tail -n 10 /root/.cache/calamares/session.log"):raise RuntimeError('Calamares failed')
  time.sleep(10)
 else:raise TimeoutError('Installation did not complete')
 serial.command('cat /root/.cache/calamares/session.log');screenshot('06-finished');serial.close();serial=None;click(963,575)
 # The initramfs must show the actual media-removal prompt before reboot.
 prompt=False
 for _ in range(24):
  time.sleep(5);screenshot('07-remove-media')
  words=subprocess.check_output(['tesseract',str(run/'07-remove-media.png'),'stdout'],stderr=subprocess.DEVNULL,text=True).lower()
  if 'installation media' in words and 'enter' in words:prompt=True;break
 if not prompt:raise RuntimeError('Media-removal prompt was not displayed')
 qmp('eject',{'device':'livecd','force':False});key('ret');bootwait(60);screenshot('08-installed-login');text('BypssdQA42');key('ret');bootwait(30);screenshot('09-installed-desktop')
 click(26,605);text('super');time.sleep(1);screenshot('09b-installed-no-superuser-entries');key('esc')
 key('ctrl-alt-t');time.sleep(4);text(bootstrap,True);time.sleep(3);text('BypssdQA42');key('ret');time.sleep(4)
 serial=Serial();serial.read(2);serial.command('stty -echo; id; cat /proc/cmdline')
 result=serial.command('curl -fsS http://10.0.2.2:8765/check.py -o /tmp/bypssd-check.py; python3 /tmp/bypssd-check.py')
 if '"installed_checks": "passed"' not in result:raise RuntimeError('Installed audit failed')
 audio=serial.command('runuser -u qa -- env XDG_RUNTIME_DIR=/run/user/1000 systemctl --user is-active pipewire wireplumber pipewire-pulse')
 if sum(line.strip()=='active' for line in audio.splitlines())!=3:raise RuntimeError('Audio services not active')
 serial.command('runuser -u qa -- env XDG_RUNTIME_DIR=/run/user/1000 pw-play /usr/share/sounds/ocean/stereo/desktop-login.oga && echo AUDIO_PLAYED')
 text('kcmshell6 kcm_soundtheme\n');time.sleep(5);screenshot('10-sound-themes')
 words=subprocess.check_output(['tesseract',str(run/'10-sound-themes.png'),'stdout'],stderr=subprocess.DEVNULL,text=True).lower()
 if not any(t in words for t in ['ocean','océano','oceano']) or not any(t in words for t in ['oxygen','oxígeno','oxigeno']):raise RuntimeError('Sound themes missing in Settings')
 serial.command('systemctl --no-block reboot');serial.close();serial=None;bootwait(70);screenshot('11-second-boot')
 (run/'result.json').write_text(json.dumps({'installed':'passed','live_idle_after_330_seconds':'passed','privileged_launchers_hidden_both_modes':'passed','media_removal_prompt':'passed','installed_audit':'passed','sound_services':'passed','sound_themes_in_settings':'passed','second_boot_without_iso':'captured'},indent=2)+'\n')
 print('BYPSSD_INSTALLED_X64_QA_OK',flush=True)
except Exception:
 try:screenshot('failure')
 except Exception:pass
 raise
finally:
 if serial:serial.close()
 try:qmp('quit')
 except Exception:vm.terminate()
 vm.wait(timeout=30);server.shutdown()

# Some QEMU versions leave zero length placeholders; validate actual PCM bytes.
import array,struct
raw=(run/'audio.wav').read_bytes()
if raw[:4]!=b'RIFF' or raw[8:12]!=b'WAVE' or raw[36:40]!=b'data':raise RuntimeError('Unexpected audio container')
if struct.unpack_from('<H',raw,34)[0]!=16:raise RuntimeError('Unexpected audio sample width')
peak=max(map(abs,array.array('h',raw[44:])),default=0)
if peak<=64:raise RuntimeError('The virtual audio output was silent')
print('BYPSSD_AUDIO_PCM_OK',peak,flush=True)
result=json.loads((run/'result.json').read_text());result['audio_peak_pcm_s16']=peak;(run/'result.json').write_text(json.dumps(result,indent=2)+'\n')
