"""Classic border preservation, wrapper enum guards and panel reload fixtures."""
from pathlib import Path
import configparser,sys,xml.etree.ElementTree as ET
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import desktop_update


def main():
    for old,new in [('ScarletProtocolGlobal8','ScarletProtocolGlobal81'),('ScarletProtocolNight8','ScarletProtocolNight81')]:
        source=ROOT/'aurorae'/old;target=ROOT/'aurorae'/new
        assert (source/(old+'rc')).read_bytes()==(target/(new+'rc')).read_bytes()
        for button in ('close','minimize','maximize','restore','alldesktops','keepabove','keepbelow','shade','help','appmenu'):
            assert (source/(button+'.svg')).read_bytes()==(target/(button+'.svg')).read_bytes()
        before={e.get('id'):e for e in ET.parse(source/'decoration.svg').getroot() if e.get('id')}
        after={e.get('id'):e for e in ET.parse(target/'decoration.svg').getroot() if e.get('id')}
        for name,group in after.items():
            if not name.startswith('decoration-'):continue
            previous=before[name]
            if 'maximized' in name or name.endswith('-center'):
                assert ET.tostring(group)==ET.tostring(previous);continue
            # Outline/halo/face geometry is retained; only the detail overlay changes.
            assert all(ET.tostring(a)==ET.tostring(b) for a,b in zip(list(group)[1][:8],list(previous)[1][:8]))
            part=name.rsplit('-',1)[-1]
            if part in ('top','bottom','left','right'):
                slits=[n for n in group.iter() if n.get('data-pitch')=='32']
                assert len(slits)==(6 if part=='top' else 3)
        assert 'l-2.3' not in (target/'decoration.svg').read_text()
    for widget in ('launcher','clock'):
        source=(ROOT/'plasmoids'/('org.scarletprotocol.'+widget)/'contents/ui/main.qml').read_text()
        assert 'import org.kde.plasma.core as PlasmaCore' in source
        assert 'Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground' in source
        assert 'Plasmoid.backgroundHints: 0' not in source
    # A service that is not active is never started or restarted by this updater.
    native=desktop_update.native;calls=[]
    with patch.object(desktop_update.shutil,'which',return_value=None):
        assert 'sign out' in desktop_update.reload_panels()
    def inactive(argv):calls.append(argv);return 'inactive'
    with patch.object(desktop_update.shutil,'which',return_value='systemctl-fixture'),patch.object(native,'run',side_effect=inactive):
        assert 'sign out' in desktop_update.reload_panels()
        assert len(calls)==1 and 'restart' not in calls[0]
    calls=[]
    def active(argv):calls.append(argv);return 'active' if 'is-active' in argv else ''
    with patch.object(desktop_update.shutil,'which',return_value='systemctl-fixture'),patch.object(native,'run',side_effect=active):
        assert 'reloaded' in desktop_update.reload_panels()
        assert calls==[['systemctl-fixture','--user','is-active','plasma-plasmashell.service'],['systemctl-fixture','--user','restart','plasma-plasmashell.service'],['systemctl-fixture','--user','is-active','plasma-plasmashell.service']]
    print('PASS: straight 32px cuts; rounded outline, dimensions, buttons and maximized art preserved; launcher/clock enum guards; active-service-only panel reload')


if __name__=='__main__':main()
