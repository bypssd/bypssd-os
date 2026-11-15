import gzip, hashlib, importlib.util, json, tempfile, unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import xml.etree.ElementTree as ET
spec=importlib.util.spec_from_file_location('mirror',Path(__file__).parents[1]/'scripts/mirror-catalog.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class MirrorTests(unittest.TestCase):
 def test_normalized_names_and_collisions(self):
  p={'name':'app-0.7^2026+git.noarch.rpm','tag':'one','checksum':'a'}
  self.assertEqual(m.asset_name(p),'app-0.7.2026.git.noarch.rpm')
  with self.assertRaisesRegex(ValueError,'collision'):m.validate_asset_names([p,dict(p,name='app-0.7.2026.git.noarch.rpm',checksum='b')])
 def test_verified_assets_and_rewritten_metadata(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);src=root/'metadata/aarch64/base/repodata';src.mkdir(parents=True)
   checksum='a'*64;pkg={'repo':'aarch64/base','name':'test.rpm','checksum':checksum,'size':123,'tag':'catalog-test'}
   primary=f'<metadata xmlns="{m.C}"><package><checksum type="sha256">{checksum}</checksum><location href="Packages/t/test.rpm"/></package></metadata>'.encode()
   blob=gzip.compress(primary);(src/'primary.xml.gz').write_bytes(blob)
   repomd=f'<repomd xmlns="{m.R}"><data type="primary"><checksum type="sha256">old</checksum><open-checksum type="sha256">old</open-checksum><size>1</size><open-size>1</open-size><location href="repodata/primary.xml.gz"/></data><data type="primary_zck"/></repomd>'
   (src/'repomd.xml').write_text(repomd)
   (root/'chunk-0000.json').write_text(json.dumps([pkg]));(root/'plan.json').write_text(json.dumps({'snapshot':'test','repos':[{'id':'aarch64/base','entries':{'primary':'primary.xml.gz'}}],'packages':[pkg],'chunks':['0000'],'unique_packages':1,'bytes':123}))
   a=SimpleNamespace(directory=str(root),repository='bypssd/bypssd-os',site=str(root/'site'))
   asset={'name':'test.rpm','state':'uploaded','size':123,'digest':'sha256:'+checksum}
   def gh(*args):
    if '--jq' in args:return '1'
    if '--slurp' in args:return json.dumps([[asset]])
    return json.dumps({'assets':[asset]})
   with patch.object(m,'gh',gh):m.finalize(a)
   dest=root/'site/45/aarch64/base/repodata';tree=ET.parse(dest/'repomd.xml');entry=tree.find('{'+m.R+'}data');data=(dest/entry.find('{'+m.R+'}location').get('href').split('/')[-1]).read_bytes()
   self.assertEqual(hashlib.sha256(data).hexdigest(),entry.find('{'+m.R+'}checksum').text)
   text=gzip.decompress(data).decode();self.assertIn('https://github.com/bypssd/bypssd-os/releases/download/catalog-test/test.rpm',text);self.assertNotIn('primary_zck',ET.tostring(tree.getroot()).decode())
   asset['digest']='sha256:wrong'
   with patch.object(m,'gh',gh),self.assertRaisesRegex(ValueError,'Incomplete mirror'):m.finalize(a)
if __name__=='__main__':unittest.main()
