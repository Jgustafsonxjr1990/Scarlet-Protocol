"""Exercise install/rollback in isolated data trees with a fake KWin service."""
import importlib.util,os,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('installer',ROOT/'install.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class InstallerChecks(unittest.TestCase):
 def scenario(self,preferred=False,fail=False):
  with tempfile.TemporaryDirectory() as temp:
   home=Path(temp);data=home/'data';state=home/'state';state.mkdir()
   target=data/('kwin-wayland/effects' if preferred else 'kwin/effects')/m.PLUGIN
   target.mkdir(parents=True);(target/'old.txt').write_text('old version')
   untouched=data/'kwin/effects/kwin6_effect_scarlet_phase_relay';untouched.mkdir(parents=True);(untouched/'sentinel').write_text('preserve')
   calls=[];loaded={m.PLUGIN:True,'wobblywindows':True};failed=False
   class FakeKWin:
    def loaded(self,p):return loaded.get(p,False)
    def call(self,method,p):
     nonlocal failed
     calls.append((method,p))
     if method=='unloadEffect':loaded[p]=False
     elif method=='loadEffect':
      if fail and p==m.PLUGIN and not failed:failed=True;loaded[p]=False
      else:loaded[p]=True
     return 'true'
   def run(args,check=True):
    calls.append(args)
    if '--upgrade' in args:
     (target/'old.txt').unlink();(target/'new.txt').write_text('new version')
    return SimpleNamespace(stdout='',stderr='',returncode=0)
   with patch.object(m,'STATE',state),patch.object(m,'LOG',state/'log'),patch.object(m.os,'geteuid',return_value=1000),patch.dict(os.environ,{'XDG_DATA_HOME':str(data)}),patch.object(m.shutil,'which',side_effect=lambda n:'/usr/bin/'+n),patch.object(m,'KWin',FakeKWin),patch.object(m,'run',run):
    if fail:
     with self.assertRaisesRegex(RuntimeError,'did not load'):m.install()
     assert (target/'old.txt').read_text()=='old version';assert not (target/'new.txt').exists()
     assert loaded['wobblywindows'] and loaded[m.PLUGIN]
     assert not any(isinstance(c,list) and 'kwriteconfig6' in c[0] for c in calls)
    else:
     m.install();assert loaded[m.PLUGIN] and not loaded['wobblywindows']
     write=next(c for c in calls if isinstance(c,list) and '--upgrade' in c)
     assert write[write.index('--packageroot')+1]==str(target.parent)
     assert (state/next(p.name for p in state.iterdir() if p.is_dir())/'old.txt').exists()
    assert (untouched/'sentinel').read_text()=='preserve'
    assert all('phase_relay' not in str(c) for c in calls)
 def test_legacy_install(self):self.scenario()
 def test_preferred_shadow_install(self):self.scenario(preferred=True)
 def test_failed_load_rollback(self):self.scenario(fail=True)
if __name__=='__main__':unittest.main()
