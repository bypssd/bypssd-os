#!/usr/bin/env python3
"""Use absolute RPM URLs: libzypp does not apply location xml:base here."""
from pathlib import Path
import gzip,hashlib,subprocess,sys,xml.etree.ElementTree as E
from urllib.parse import urljoin
repo=Path(sys.argv[1]);ns={'r':'http://linux.duke.edu/metadata/repo','c':'http://linux.duke.edu/metadata/common'}
manifest=repo/'repodata/repomd.xml';tree=E.parse(manifest)
data=next(d for d in tree.findall('r:data',ns) if d.get('type')=='primary')
old=repo/data.find('r:location',ns).get('href')
raw=subprocess.check_output(['zstd','-dc',str(old)]) if old.suffix=='.zst' else gzip.decompress(old.read_bytes())
primary=E.fromstring(raw)
for loc in primary.findall('c:package/c:location',ns):
 base=loc.attrib.pop('{http://www.w3.org/XML/1998/namespace}base','')
 loc.set('href',urljoin(base,loc.get('href')))
 assert loc.get('href').startswith('https://github.com/bypssd/bypssd-os/releases/download/')
E.register_namespace('','http://linux.duke.edu/metadata/common');E.register_namespace('rpm','http://linux.duke.edu/metadata/rpm')
raw=E.tostring(primary,encoding='utf-8',xml_declaration=True);compressed=gzip.compress(raw,mtime=0)
digest=hashlib.sha256(compressed).hexdigest();dest=repo/'repodata'/(digest+'-primary.xml.gz');dest.write_bytes(compressed)
data.find('r:location',ns).set('href','repodata/'+dest.name)
for name,content in [('checksum',compressed),('open-checksum',raw)]:
 field=data.find('r:'+name,ns);field.set('type','sha256');field.text=hashlib.sha256(content).hexdigest()
for name,size in [('size',len(compressed)),('open-size',len(raw))]:data.find('r:'+name,ns).text=str(size)
E.register_namespace('','http://linux.duke.edu/metadata/repo');tree.write(manifest,encoding='utf-8',xml_declaration=True)
print('Absolute RPM URLs:',len(primary.findall('c:package',ns)))
