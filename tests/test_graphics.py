import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest
loader=importlib.machinery.SourceFileLoader('graphics',str(Path(__file__).resolve().parents[1]/'opensuse/graphics/chromium'))
spec=importlib.util.spec_from_loader(loader.name,loader);graphics=importlib.util.module_from_spec(spec);loader.exec_module(graphics)
class GraphicsTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def card(self,driver,primary=True,connected=False):
        device=self.root/'card0/device';device.mkdir(parents=True)
        target=self.root/'drivers'/driver;target.mkdir(parents=True)
        (device/'driver').symlink_to(target,target_is_directory=True)
        (device/'boot_vga').write_text('1' if primary else '0')
        if connected:
            p=self.root/'card0-HDMI-A-1/enabled';p.parent.mkdir();p.write_text('enabled')
    def test_legacy_radeon_software(self):
        self.card('radeon');self.assertEqual(graphics.arguments(['https://example.org'],self.root),['https://example.org','--ozone-platform=x11','--disable-gpu'])
    def test_amdgpu_keeps_acceleration(self):
        self.card('amdgpu');self.assertEqual(graphics.arguments(['--new-window','https://example.org'],self.root),['--new-window','https://example.org'])
    def test_intel_unchanged(self):
        self.card('i915');self.assertEqual(graphics.arguments([],self.root),[])
    def test_disconnected_secondary_radeon_unchanged(self):
        self.card('radeon',False);self.assertEqual(graphics.arguments([],self.root),[])
    def test_active_secondary_radeon_fallback(self):
        self.card('radeon',False,True);self.assertTrue(graphics.legacy_radeon(self.root))
    def test_no_gpu_unchanged(self):self.assertEqual(graphics.arguments([],self.root),[])
    def test_manual_native(self):
        self.card('radeon');self.assertEqual(graphics.arguments([],self.root,'native'),[])
    def test_manual_software(self):self.assertIn('--disable-gpu',graphics.arguments([],self.root,'software'))
    def test_never_disables_sandbox(self):
        self.card('radeon');self.assertNotIn('--no-sandbox',graphics.arguments([],self.root))
if __name__=='__main__':unittest.main()
