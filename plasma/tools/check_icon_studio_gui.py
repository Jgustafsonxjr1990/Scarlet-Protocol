"""Exercise the graphical install/restore buttons in an isolated desktop fixture."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time

os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tools')]
from PySide6.QtCore import Qt,QEventLoop,QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication


def main():
    spec=importlib.util.spec_from_file_location('scarlet_icon_gui',ROOT/'desktop/icon_studio_gui.py')
    gui=importlib.util.module_from_spec(spec);spec.loader.exec_module(gui)
    app=QApplication([]);bundle,root=gui.load_payload()
    with tempfile.TemporaryDirectory(prefix='scarlet-gui-check-') as directory:
        work=Path(directory);data=work/'data';config=work/'config';state=work/'state'
        gui.homes=lambda:(data,config,state)
        backend=gui.backend
        originals={'Icons/Theme':'BeforeScarlet'};settings=dict(originals)
        backend.program=lambda name:name
        def setting(home,group,key,value=backend.READ):
            if value is backend.READ:return settings.get(group+'/'+key)
            if value is None:settings.pop(group+'/'+key,None)
            else:settings[group+'/'+key]=value
        backend.setting=setting;backend.notify=lambda:None
        backend.data_roots=lambda data:[data]
        actual_launcher=gui.install_launcher;gui.install_launcher=lambda data:None
        window=gui.Studio(root);window.show()
        def click(button):
            QTest.mouseClick(button,Qt.LeftButton);wait()
        def wait():
            loop=QEventLoop();poll=QTimer();poll.setInterval(20)
            poll.timeout.connect(lambda:loop.quit() if window.active_task is None else None)
            timeout=QTimer();timeout.setSingleShot(True);timeout.timeout.connect(loop.quit)
            poll.start();timeout.start(90000);loop.exec();poll.stop();timeout.stop()
            assert window.active_task is None,'GUI worker timed out'
        click(window.install)
        assert window.status.text().startswith('Installed.'),window.log.toPlainText()
        assert settings['Icons/Theme'].startswith('ScarletProtocolIcons62_')
        assert window.restore.isEnabled() and window.backup
        window.restore_menu.actions()[1].trigger();wait()
        assert window.status.text()=='Previous icons restored.'
        assert settings==originals
        gui.desktop_update.reload_panels=lambda:'Fixture panels reloaded'
        styles={'name':'ScarletProtocolPlasma6'}
        gui.desktop_update.current_style=lambda cfg:styles['name']
        def apply_style(name):styles['name']=name;return 'Selected '+name
        gui.desktop_update.apply_style=apply_style
        window.use_widgets.setChecked(False)
        previous_decor={'library':None,'theme':None};deco=dict(previous_decor)
        gui.desktop_update.decoration=lambda cfg:dict(deco)
        def set_decor(cfg,values):deco.clear();deco.update(values)
        gui.desktop_update.set_decoration=set_decor
        gui.desktop_update.kwin_command=lambda method:['fixture',method]
        gui.desktop_update.appearance=lambda cfg:{'plasma_style':styles['name'],'decoration':dict(deco),'icons':settings.get('Icons/Theme'),'application_style':'Breeze','kwin_confirmed':True}
        assert window.use_frame.isChecked()
        click(window.desktop)
        assert window.status.text().startswith('Classic Slits 8.1 applied.'),window.log.toPlainText()
        assert 'Fixture panels reloaded' in window.log.toPlainText()
        assert window.reload_panels.isChecked()
        assert styles['name']=='ScarletProtocolPlasma8'
        assert (data/'plasma/desktoptheme/ScarletProtocolPlasma8/metadata.json').is_file()
        assert deco['theme']=='__aurorae__svg__ScarletProtocolGlobal81'
        click(window.verify)
        assert 'confirmed' in window.log.toPlainText()
        window.restore_menu.actions()[0].trigger();wait()
        assert deco==previous_decor
        assert styles['name']=='ScarletProtocolPlasma6'
        assert window.status.text()=='Previous appearance restored.'
        # Verify the launcher install uses the executable and preserves launchability.
        native=work/'download/Scarlet-Desktop-Studio';native.parent.mkdir();native.write_bytes(b'\x7fELF-test-launcher')
        original_executable=sys.executable
        original_which=gui.shutil.which
        try:
            sys.frozen=True;sys.executable=str(native);gui.shutil.which=lambda name:None
            installed=actual_launcher(data)
            assert installed.read_bytes()==native.read_bytes() and installed.stat().st_mode&0o111
            desktop=(data/'applications/org.scarletprotocol.desktopstudio.desktop').read_text()
            assert 'Terminal=false' in desktop and str(installed) in desktop
        finally:
            sys.executable=original_executable;del sys.frozen;gui.shutil.which=original_which
        # The frozen parent must not make system KDE tools load bundled Qt libraries.
        try:
            sys.frozen=True
            os.environ['LD_LIBRARY_PATH']='/temporary/bundled-qt'
            os.environ['LD_LIBRARY_PATH_ORIG']='/original/system-libraries'
            os.environ['QT_PLUGIN_PATH']='/temporary/bundled-qt/plugins'
            output=backend.run(['/usr/bin/python3','-c','import os,json;print(json.dumps({k:os.environ.get(k) for k in ("LD_LIBRARY_PATH","QT_PLUGIN_PATH")}))'])
            child=json.loads(output)
            assert child=={'LD_LIBRARY_PATH':'/original/system-libraries','QT_PLUGIN_PATH':None}
        finally:
            del sys.frozen
            for key in ('LD_LIBRARY_PATH','LD_LIBRARY_PATH_ORIG','QT_PLUGIN_PATH'):os.environ.pop(key,None)
        window.close()
    bundle.cleanup()
    print('PASS: actual GUI desktop/icon Install/Restore actions, isolated native-command fixture, missing-setting restoration, executable launcher copy, and frozen child-library isolation')


if __name__=='__main__':main()
