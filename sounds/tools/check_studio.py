"""Real Qt event wiring with native-command and audio-decoder fixtures."""
from pathlib import Path
import importlib.util,json,os,sys,tempfile
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from PySide6.QtCore import Qt,QEventLoop,QTimer,QProcess
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication


def main():
    spec=importlib.util.spec_from_file_location('sound_gui',ROOT/'desktop/sound_studio.py');gui=importlib.util.module_from_spec(spec);spec.loader.exec_module(gui)
    app=QApplication([]);temporary,root=gui.load_payload()
    with tempfile.TemporaryDirectory(prefix='scarlet-sound-gui-') as directory:
        work=Path(directory);data=work/'data';config=work/'config';state=work/'state';gui.homes=lambda:(data,config,state)
        backend=gui.backend;settings={};backend.program=lambda name:name
        def native(argv):
            key=argv[argv.index('--key')+1]
            if argv[0]=='kreadconfig6':return settings.get(key,argv[-1])
            if argv[-1]=='--delete':settings.pop(key,None)
            else:settings[key]=argv[-1]
            return ''
        backend.run=native;actual_launcher=gui.install_launcher;gui.install_launcher=lambda *args:None
        window=gui.Studio(root);window.show()
        def wait(predicate):
            loop=QEventLoop();poll=QTimer();poll.setInterval(20);poll.timeout.connect(lambda:loop.quit() if predicate() else None)
            timeout=QTimer();timeout.setSingleShot(True);timeout.timeout.connect(loop.quit);poll.start();timeout.start(20000);loop.exec();poll.stop();timeout.stop();assert predicate(),'GUI worker timed out'
        def click(button):QTest.mouseClick(button,Qt.LeftButton);wait(lambda:window.active_task is None)
        assert window.tree.topLevelItemCount()==39
        window.search.setText('Window open');assert window.tree.currentItem().text(0)=='Window open'
        window.profile.setCurrentIndex(2)
        played=[]
        def decoder(path):
            played.append(path);return ['/usr/bin/ffmpeg','-v','error','-i',str(path),'-f','null','-']
        backend.player_command=decoder;QTest.mouseClick(window.preview,Qt.LeftButton)
        wait(lambda:window.player.state()==QProcess.NotRunning)
        assert window.tree.geometry().bottom()<window.detail.geometry().top()
        assert not window.preview.icon().pixmap(24,24).isNull()
        assert played[0]==root/'WAV/overdrive/window-open.wav' and window.status.text().startswith('Preview finished'),window.status.text()
        window.search.clear();window.family.setCurrentText('Alerts')
        assert all(window.tree.topLevelItem(i).isHidden() or window.tree.topLevelItem(i).text(1)=='Alerts' for i in range(39))
        click(window.apply_button);assert settings['Theme']=='scarlet-protocol-cyber2-overdrive'
        assert window.restore_button.isEnabled();click(window.restore_button)
        assert settings=={} and window.status.text()=='Previous sounds restored.'
        # Copying the actual launcher is verified separately from the test install.
        executable=work/'download/Scarlet-Sound-Studio';executable.parent.mkdir();executable.write_bytes(b'\x7fELF-test')
        old_executable=sys.executable;old_which=gui.shutil.which
        try:
            sys.frozen=True;sys.executable=str(executable);gui.shutil.which=lambda name:None
            actual_launcher(data,root)
            target=data/'ScarletProtocol/SoundStudio/Scarlet-Sound-Studio'
            assert target.read_bytes()==executable.read_bytes() and target.stat().st_mode&0o111
            assert 'Terminal=false' in (data/'applications/org.scarletprotocol.soundstudio.desktop').read_text()
            os.environ['LD_LIBRARY_PATH']='/bundled';os.environ['LD_LIBRARY_PATH_ORIG']='/system';os.environ['QT_PLUGIN_PATH']='/bundled/plugins'
            environment=backend.native_environment();assert environment['LD_LIBRARY_PATH']=='/system' and 'QT_PLUGIN_PATH' not in environment
        finally:
            sys.executable=old_executable;del sys.frozen;gui.shutil.which=old_which
            for key in ('LD_LIBRARY_PATH','LD_LIBRARY_PATH_ORIG','QT_PLUGIN_PATH'):os.environ.pop(key,None)
        window.close()
    temporary.cleanup()
    print('PASS: actual graphical search/group/edition selection, preview decoder routing, Apply/Restore, executable launcher and frozen child-library isolation')


if __name__=='__main__':main()
