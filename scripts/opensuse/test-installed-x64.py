#!/usr/bin/env python3
"""Black-box Calamares install into a new disposable QEMU disk on CI."""
from pathlib import Path
import subprocess,os,json,time,socket,threading,http.server,functools,shutil,sys
r=Path.cwd();run=r/'out/installed-x64';run.mkdir(parents=True,exist_ok=True)
iso=next((r/'incoming').rglob('BYPSSD-OS-Renacer-1.1-x86_64.iso'))
share=run/'http';share.mkdir(exist_ok=True)
shutil.copy('scripts/opensuse/qa-bootstrap.sh',share/'qa.sh');shutil.copy('scripts/opensuse/check-installed.py',share/'check.py')
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
 click(52,45,True);time.sleep(5);key('meta_l-pgup');time.sleep(2);screenshot('02-welcome')
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
 key('ctrl-alt-t');time.sleep(4);text(bootstrap,True);time.sleep(3);text('BypssdQA42');key('ret');time.sleep(4)
 serial=Serial();serial.read(2);serial.command('stty -echo; id; cat /proc/cmdline')
 result=serial.command('curl -fsS http://10.0.2.2:8765/check.py -o /tmp/bypssd-check.py; python3 /tmp/bypssd-check.py')
 if '"installed_checks": "passed"' not in result:raise RuntimeError('Installed audit failed')
 audio=serial.command('runuser -u qa -- env XDG_RUNTIME_DIR=/run/user/1000 systemctl --user is-active pipewire wireplumber pipewire-pulse')
 if sum(line.strip()=='active' for line in audio.splitlines())!=3:raise RuntimeError('Audio services not active')
 serial.command('runuser -u qa -- env XDG_RUNTIME_DIR=/run/user/1000 pw-play /usr/share/sounds/ocean/stereo/desktop-login.oga; echo AUDIO_PLAYED')
 text('kcmshell6 kcm_soundtheme\n');time.sleep(5);screenshot('10-sound-themes')
 words=subprocess.check_output(['tesseract',str(run/'10-sound-themes.png'),'stdout'],stderr=subprocess.DEVNULL,text=True).lower()
 if 'ocean' not in words or 'oxygen' not in words:raise RuntimeError('Sound themes missing in Settings')
 serial.command('systemctl --no-block reboot');serial.close();serial=None;bootwait(70);screenshot('11-second-boot')
 (run/'result.json').write_text(json.dumps({'installed':'passed','media_removal_prompt':'passed','installed_audit':'passed','sound_services':'passed','sound_themes_in_settings':'passed','second_boot_without_iso':'captured'},indent=2)+'\n')
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
