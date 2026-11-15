"""Window artwork, resize, customization and rollback regression checks."""
import configparser
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import customize_windows as studio
from window_art import make_decoration, PRESETS


def main():
    with tempfile.TemporaryDirectory(prefix='scarlet-slots-') as directory:
        work = Path(directory)
        # Every edge repeats actual slots; inactive windows retain the hardware detail.
        for night in (False,True):
            for density,count in (('off',0),('sparse',1),('normal',2),('dense',3)):
                path = work/'frame.svg'; make_decoration(path,night,density,75,8)
                tree = ET.parse(path)
                elements = {node.get('id'):node for node in tree.iter() if node.get('id')}
                assert 'hint-stretch-borders' not in elements
                for prefix in ('decoration','decoration-inactive'):
                    for edge in ('left','right','top','bottom'):
                        group = elements[prefix+'-'+edge]
                        assert sum(node.get('data-slot')=='true' for node in group.iter()) == count
        # Content-addressed outputs are stable and customization preserves approved controls.
        ids = set()
        for name,options in PRESETS.items():
            identity,target = studio.stage(work/'data',options)
            ids.add(identity)
            assert studio.stage(work/'data',options) == (identity,target)
            cfg = configparser.ConfigParser(); cfg.read(target/(identity+'rc'))
            assert cfg.getint('Layout','BorderLeft')==options['frame_width']
            assert cfg.getint('Layout','TitleHeight')==options['title_height']
            assert (target/'close.svg').read_bytes()==(ROOT/'aurorae/ScarletProtocolGlobal6/close.svg').read_bytes()
            assert json.loads((target/'appearance.json').read_text())['slots']==options['slots']
        assert len(ids)==3
        altered = dict(PRESETS['signature'],glow=0)
        assert studio.stage(work/'data',altered)[0] not in ids
        assert studio.stage(work/'data',PRESETS['signature'],True)[0] not in ids
        studio.install_studio(work/'data')
        desktop = (work/'data/applications/org.scarletprotocol.windowstudio.desktop').read_text()
        assert '--configure' in desktop and 'Terminal=false' in desktop
        saved_studio = work/'data/ScarletProtocol/window-studio'
        assert (saved_studio/'tools/window_art.py').is_file()
        # Exercise apply/rollback separately from the unavailable native Plasma session.
        state = {'library':'old-library','theme':'old-theme'}
        prior = dict(state)
        unrelated = '[Plugins]\nscarlet_vectorwakeEnabled=true\n'
        config = work/'config'; config.mkdir(); (config/'kwinrc').write_text(unrelated)
        studio.current_settings = lambda _:dict(state)
        studio.write_setting = lambda _,key,value:state.update({key:value})
        refreshes=[]; studio.refresh=lambda:refreshes.append(True)
        target,backup=studio.apply(work/'data',config,work/'state',PRESETS['signature'])
        assert backup and json.loads((backup/'previous.json').read_text())==prior
        assert studio.apply(work/'data',config,work/'state',PRESETS['signature'])[1] is None
        assert (config/'kwinrc').read_text()==unrelated
        studio.restore(config,backup); assert state==prior
        def fail_once():
            studio.refresh=lambda:None
            raise RuntimeError('simulated compositor refresh failure')
        studio.refresh=fail_once
        try: studio.apply(work/'data',config,work/'state',PRESETS['overdrive'])
        except RuntimeError: pass
        else: raise AssertionError('Expected failure')
        assert state==prior
    print('PASS: four-edge slots, both editions, density/glow identities, preserved buttons, saved Studio, repeat apply and rollback (Plasma command fixture)')


if __name__=='__main__': main()
