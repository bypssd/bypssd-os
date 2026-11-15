#!/usr/bin/env python3
"""Immutable full binary-catalog mirror; never changes RPM headers/signatures."""
import sys,re
import argparse, bz2, concurrent.futures, gzip, hashlib, json, lzma, os, pathlib, subprocess, time, urllib.request, urllib.parse, xml.etree.ElementTree as E
P=pathlib.Path
R='http://linux.duke.edu/metadata/repo'; C='http://linux.duke.edu/metadata/common'
def asset_name(p):return re.sub('[^A-Za-z0-9._-]','.',p['name'])
def validate_asset_names(packages):
    seen={}
    for p in packages:
        key=(p['tag'],asset_name(p))
        if key in seen and seen[key]!=p['checksum']:raise ValueError('Normalized asset name collision: '+str(key))
        seen[key]=p['checksum']
def get(url):
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url,timeout=180) as r:return r.read()
        except Exception:
            if attempt==4:raise
            time.sleep(2**attempt)
def gh(*args):
    for attempt in range(8):
        result=subprocess.run(['gh',*args],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if result.returncode==0:return result.stdout.strip()
        message=result.stderr.lower()
        if not any(x in message for x in ('rate limit','http 429','http 502','http 503','http 504','connection reset','timeout')):
            raise RuntimeError(result.stderr)
        if attempt==7:raise RuntimeError(result.stderr)
        time.sleep(min(60*2**attempt,900))
def unpack(data,name):
    if name.endswith('.gz'):return gzip.decompress(data)
    if name.endswith('.xz'):return lzma.decompress(data)
    if name.endswith('.bz2'):return bz2.decompress(data)
    if name.endswith('.zst'):return subprocess.check_output(['zstd','-dc'],input=data)
    return data
def inventory(a):
    root=P(a.directory);root.mkdir(parents=True,exist_ok=True); packages=[]; repos=[]
    for arch in ('aarch64','x86_64'):
        for channel,repo in [('base','fedora-45'),('updates','updates-released-f45')]:
            metalink=E.fromstring(get('https://mirrors.fedoraproject.org/metalink?'+urllib.parse.urlencode({'repo':repo,'arch':arch})))
            urls=[x.text for x in metalink.iter() if x.tag.endswith('}url') and x.text and x.text.startswith('https://') and x.text.endswith('/repodata/repomd.xml')]
            expected=[x.text for x in metalink.iter() if x.tag.endswith('}hash') and x.get('type')=='sha256']
            last=None
            for url in urls:
                try:
                    data=get(url)
                    if expected and hashlib.sha256(data).hexdigest() not in expected:raise ValueError('repomd checksum mismatch')
                    tree=E.fromstring(data);base=url.rsplit('repodata/',1)[0];break
                except Exception as ex:last=ex
            else:raise RuntimeError(f'No verified mirror for {arch}/{channel}: {last}')
            target=root/'metadata'/arch/channel/'repodata';target.mkdir(parents=True)
            (target/'repomd.xml').write_bytes(data)
            entries={}
            for item in tree.findall('{'+R+'}data'):
                kind=item.get('type')
                if kind not in ('primary','filelists','other','group','group_gz','updateinfo'):continue
                loc=item.find('{'+R+'}location').get('href');blob=get(urllib.parse.urljoin(base,loc)); check=item.find('{'+R+'}checksum')
                if hashlib.new(check.get('type'),blob).hexdigest()!=check.text:raise ValueError('metadata checksum mismatch')
                (target/P(loc).name).write_bytes(blob);entries[kind]=P(loc).name
            primary=E.fromstring(unpack((target/entries['primary']).read_bytes(),entries['primary']))
            for pkg in primary.findall('{'+C+'}package'):
                href=pkg.find('{'+C+'}location').get('href');checksum=pkg.find('{'+C+'}checksum')
                packages.append({'repo':f'{arch}/{channel}','name':P(href).name,'url':urllib.parse.urljoin(base,href),'checksum_type':checksum.get('type'),'checksum':checksum.text,'size':int(pkg.find('{'+C+'}size').get('package'))})
            repos.append({'id':f'{arch}/{channel}','entries':entries})
    # One immutable asset per name+checksum, shared across architecture repositories.
    unique={}
    for pkg in packages:
        key=(pkg['name'],pkg['checksum']);unique.setdefault(key,pkg.copy())
    items=list(unique.values());chunks=[]
    for i in range(0,len(items),900):
        chunk=len(chunks);tag=f'catalog-45-{a.snapshot}-{chunk:04d}'
        for pkg in items[i:i+900]:pkg['tag']=tag
        (root/f'chunk-{chunk:04d}.json').write_text(json.dumps(items[i:i+900]));chunks.append(f'{chunk:04d}')
    if len(chunks)>256:raise RuntimeError('Catalog exceeds one GitHub matrix; split runs before uploading')
    mapping={(p['name'],p['checksum']):p['tag'] for p in items}
    for p in packages:p['tag']=mapping[p['name'],p['checksum']]
    validate_asset_names(items)
    plan={'snapshot':a.snapshot,'repository':a.repository,'repos':repos,'packages':packages,'chunks':chunks,'unique_packages':len(items),'bytes':sum(x['size'] for x in items)}
    (root/'plan.json').write_text(json.dumps(plan))
    print(f"Inventory: {len(items)} unique RPMs; {plan['bytes']} bytes; {len(chunks)} release shards", file=sys.stderr,flush=True)
    print(json.dumps({k:plan[k] for k in ('snapshot','unique_packages','bytes','chunks')}))
    if os.getenv('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('chunks='+json.dumps(chunks)+'\n')
def upload(a):
    entries=json.loads((P(a.directory)/f'chunk-{a.chunk}.json').read_text());validate_asset_names(entries);tag=entries[0]['tag']
    try:gh('release','view',tag,'--repo',a.repository)
    except RuntimeError as ex:
        if not any(x in str(ex).lower() for x in ('not found','http 404')):raise
        gh('release','create',tag,'--repo',a.repository,'--prerelease','--title',f'BYPSSD OS · catálogo {tag}','--notes','Repositorio BYPSSD. RPM redistribuidos sin alterar firmas, licencias ni atribuciones de origen.')
    rid=gh('api',f'repos/{a.repository}/releases/tags/{tag}','--jq','.id')
    pages=json.loads(gh('api',f'repos/{a.repository}/releases/{rid}/assets?per_page=100','--paginate','--slurp'))
    existing={x['name']:x for page in pages for x in page}
    def one(p):
        old=existing.get(asset_name(p))
        if old:
            if old['size']!=p['size'] or (old.get('digest') and old['digest']!='sha256:'+p['checksum']):raise ValueError('Existing asset mismatch: '+p['name'])
            return
        if p['size']>=2*1024**3:raise ValueError('GitHub asset exceeds 2 GiB: '+p['name'])
        path=P(a.directory)/asset_name(p);path.write_bytes(get(p['url']))
        if path.stat().st_size!=p['size'] or hashlib.new(p['checksum_type'],path.read_bytes()).hexdigest()!=p['checksum']:raise ValueError('RPM checksum mismatch: '+p['name'])
        # Upload only verified bytes. Delete only this disposable downloaded file.
        gh('release','upload',tag,str(path),'--repo',a.repository);path.unlink()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(one,entries))
    print(json.dumps({'chunk':a.chunk,'verified_and_uploaded':len(entries)}))
def finalize(a):
    root=P(a.directory);plan=json.loads((root/'plan.json').read_text());out=P(a.site);out.mkdir(parents=True,exist_ok=True)
    for chunk in plan['chunks']:
        entries=json.loads((root/f'chunk-{chunk}.json').read_text());tag=entries[0]['tag'];assets={x['name']:x for x in json.loads(gh('api',f'repos/{a.repository}/releases/tags/{tag}'))['assets']}
        # REST release response may paginate assets separately; fetch every page.
        rid=gh('api',f'repos/{a.repository}/releases/tags/{tag}','--jq','.id')
        pages=json.loads(gh('api',f'repos/{a.repository}/releases/{rid}/assets?per_page=100','--paginate','--slurp'));assets={x['name']:x for page in pages for x in page}
        for p in entries:
            x=assets.get(asset_name(p))
            if not x or x['state']!='uploaded' or x['size']!=p['size'] or x.get('digest')!='sha256:'+p['checksum']:raise ValueError('Incomplete mirror: '+p['name'])
    validate_asset_names(plan['packages'])
    mapping={(p['repo'],p['name'],p['checksum']):(p['tag'],asset_name(p)) for p in plan['packages']}
    for repo in plan['repos']:
        src=root/'metadata'/repo['id']/'repodata';dest=out/'45'/repo['id']/'repodata';dest.mkdir(parents=True)
        repomd=E.fromstring((src/'repomd.xml').read_bytes())
        for entry in list(repomd):
            if entry.tag!='{'+R+'}data':continue
            kind=entry.get('type')
            if kind not in repo['entries']:repomd.remove(entry);continue
            name=repo['entries'][kind];data=(src/name).read_bytes()
            if kind=='primary':
                primary=E.fromstring(unpack(data,name))
                for p in primary.findall('{'+C+'}package'):
                    loc=p.find('{'+C+'}location');filename=P(loc.get('href')).name;digest=p.find('{'+C+'}checksum').text;tag,asset=mapping[repo['id'],filename,digest]
                    loc.attrib.clear();loc.set('href',f'https://github.com/{a.repository}/releases/download/{tag}/{asset}')
                raw=E.tostring(primary,encoding='utf-8',xml_declaration=True);data=gzip.compress(raw,mtime=0);name=hashlib.sha256(data).hexdigest()+'-primary.xml.gz'
                for key,blob in [('checksum',data),('open-checksum',raw)]:
                    el=entry.find('{'+R+'}'+key);el.set('type','sha256');el.text=hashlib.sha256(blob).hexdigest()
                entry.find('{'+R+'}size').text=str(len(data));entry.find('{'+R+'}open-size').text=str(len(raw))
                for el in list(entry):
                    if el.tag in ('{'+R+'}header-checksum','{'+R+'}header-size'):entry.remove(el)
            entry.find('{'+R+'}location').set('href','repodata/'+name);(dest/name).write_bytes(data)
        (dest/'repomd.xml').write_bytes(E.tostring(repomd,encoding='utf-8',xml_declaration=True))
    (out/'catalog-summary.json').write_text(json.dumps(dict(status='complete', **{k:plan[k] for k in ('snapshot','unique_packages','bytes','chunks')}),indent=2))
    (out/'bypssd.repo').write_bytes(P('branding/config/bypssd-github.repo').read_bytes())
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>BYPSSD OS · Repositorio</title><h1>BYPSSD OS</h1><p>Catálogo binario completo para ARM64 y x64, servido desde GitHub.</p><p><a href="bypssd.repo">Configuración DNF</a> · <a href="catalog-summary.json">Inventario verificado</a></p>')
    (out/'.nojekyll').touch();print('COMPLETE: all package assets verified; metadata ready')
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('mode',choices=['inventory','upload','finalize']);a.add_argument('--directory',default='out/catalog');a.add_argument('--repository',default='bypssd/bypssd-os');a.add_argument('--snapshot',default=time.strftime('%Y%m%d'));a.add_argument('--chunk');a.add_argument('--site',default='site');args=a.parse_args();globals()[args.mode](args)
