#!/usr/bin/env python3
"""Resume temporary GitHub Actions artifacts with parallel HTTP ranges; verify ISO."""
import argparse,concurrent.futures,hashlib,json,os,pathlib,subprocess,threading,time,urllib.request,urllib.error,zipfile,shutil
p=argparse.ArgumentParser();p.add_argument('run',type=int);p.add_argument('arch',choices=['aarch64','x86_64']);a=p.parse_args()
r=pathlib.Path(__file__).resolve().parents[1];directory=r/'out/actions-transfer'/str(a.run)/a.arch;directory.mkdir(parents=True,exist_ok=True)
name=f'BYPSSD-OS-Renacer-1.1-{a.arch}.iso';target=r/'out'/name
if target.exists():raise SystemExit('El destino ya existe: '+str(target))
meta=json.loads(subprocess.check_output(['gh','api',f'repos/bypssd/bypssd-os/actions/runs/{a.run}/artifacts'],text=True))
artifact=next(x for x in meta['artifacts'] if x['name']=='opensuse-delivery-'+a.arch)
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args):return None
url_lock=threading.Lock();url='';renew_at=0
def signed_url(force=False):
 global url,renew_at
 with url_lock:
  if force or time.monotonic()>=renew_at:
   token=subprocess.check_output(['gh','auth','token'],text=True).strip()
   endpoint=artifact['archive_download_url']+'?check='+str(time.time_ns())
   request=urllib.request.Request(endpoint,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','Cache-Control':'no-cache'})
   try:urllib.request.build_opener(NoRedirect).open(request,timeout=30)
   except urllib.error.HTTPError as error:
    if error.code!=302:raise
    url=error.headers['Location']
   else:raise RuntimeError('Falta la redirección autorizada de descarga')
   renew_at=time.monotonic()+60
  return url
url=signed_url()
with urllib.request.urlopen(urllib.request.Request(url,headers={'Range':'bytes=0-0'}),timeout=30) as response:
 if response.status!=206:raise RuntimeError('El servidor no admite rangos')
 total=int(response.headers['Content-Range'].split('/')[-1]);response.read()
archive=directory/'archive.zip.partial';checkpoint=directory/'archive.ranges.json';chunk=32*1024**2
if checkpoint.exists():state=json.loads(checkpoint.read_text());assert state['total']==total
else:
 prefix=archive.stat().st_size if archive.exists() else 0
 assert prefix<=total
 state={'total':total,'prefix':prefix,'complete':[]};checkpoint.write_text(json.dumps(state))
lock=threading.Lock();active={};completed=set(state['complete']);fd=os.open(archive,os.O_RDWR|os.O_CREAT,0o600);os.ftruncate(fd,total)
ranges=[(start,min(start+chunk,total)) for start in range(state['prefix'],total,chunk)]
def download(segment):
 start,end=segment
 if start in completed:return
 for attempt in range(4):
  try:
   request=urllib.request.Request(signed_url(),headers={'Range':f'bytes={start}-{end-1}'})
   with urllib.request.urlopen(request,timeout=180) as response:
    if response.status!=206 or response.headers.get('Content-Range')!=f'bytes {start}-{end-1}/{total}':raise RuntimeError('Respuesta de rango incorrecta')
    position=start
    while True:
     block=response.read(min(1024**2,end-position)) if position<end else b''
     if not block:break
     written=os.pwrite(fd,block,position)
     if written!=len(block):raise RuntimeError('Escritura parcial inesperada')
     position+=written
     with lock:active[start]=position-start
    if position!=end:raise RuntimeError('Rango incompleto')
   with lock:
    completed.add(start);active.pop(start,None);state['complete']=sorted(completed)
    temporary=checkpoint.with_suffix('.tmp');temporary.write_text(json.dumps(state));temporary.replace(checkpoint)
   return
  except Exception as error:
   if isinstance(error,urllib.error.HTTPError) and error.code in (401,403):signed_url(force=True)
   if attempt==3:raise
   time.sleep(attempt+1)
def progress():
 with lock:done=state['prefix']+sum(end-start for start,end in ranges if start in completed)+sum(active.values())
 return done
print('Reanudando',a.arch,state['prefix'],'de',total,'bytes con 8 conexiones',flush=True)
try:
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
  pending={executor.submit(download,s) for s in ranges if s[0] not in completed}
  while pending:
   ready,pending=concurrent.futures.wait(pending,timeout=10,return_when=concurrent.futures.FIRST_EXCEPTION)
   for future in ready:future.result()
   done=progress();print(f'{a.arch}: {done}/{total} bytes ({done/total:.1%})',flush=True)
finally:os.close(fd)
if artifact.get('digest'):
 h=hashlib.sha256()
 with archive.open('rb') as stream:
  for block in iter(lambda:stream.read(8*1024**2),b''):h.update(block)
 if 'sha256:'+h.hexdigest()!=artifact['digest']:raise RuntimeError('SHA256 del artefacto incorrecto')
partial=target.with_name(target.name+'.partial');h=hashlib.sha256()
with zipfile.ZipFile(archive) as package:
 members=package.namelist();iso=next(x for x in members if pathlib.PurePosixPath(x).name==name)
 checksum=next(x for x in members if pathlib.PurePosixPath(x).name==name+'.sha256');expected=package.read(checksum).decode().split()[0]
 with package.open(iso) as src,partial.open('xb') as dest:
  for block in iter(lambda:src.read(8*1024**2),b''):dest.write(block);h.update(block)
 if h.hexdigest()!=expected:raise RuntimeError('SHA256 de ISO incorrecto')
 for prefix in ['audit-opensuse-'+a.arch,'package-manifest-opensuse-'+a.arch]:
  for member in members:
   base=pathlib.PurePosixPath(member).name
   if base.startswith(prefix):
    path=pathlib.Path(base);(r/'out'/(path.stem+'-r8'+path.suffix)).write_bytes(package.read(member))
partial.replace(target);target.with_suffix('.iso.sha256').write_text(expected+'  '+name+'\n')
(r/'out'/f'delivery-r8-{a.arch}.json').write_text(json.dumps({'run':a.run,'artifact':artifact['id'],'arch':a.arch,'iso':name,'bytes':target.stat().st_size,'sha256':expected},indent=2)+'\n')
archive.unlink();checkpoint.unlink();print('VERIFIED',a.arch,target,flush=True)
