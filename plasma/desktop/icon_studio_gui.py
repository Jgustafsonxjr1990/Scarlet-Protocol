#!/usr/bin/env python3
"""Scarlet Icon Studio — graphical, self-contained Linux application."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

from PySide6.QtCore import QObject,QRunnable,QThreadPool,Signal,Qt,QTimer,QSize
from PySide6.QtGui import QIcon,QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,
    QLabel,QPushButton,QProgressBar,QPlainTextEdit,QFrame,QGridLayout,QCheckBox,QComboBox,QMenu)
import icon_studio as backend
import desktop_update


def homes():
    home=Path.home()
    return (Path(os.environ.get('XDG_DATA_HOME') or home/'.local/share'),
            Path(os.environ.get('XDG_CONFIG_HOME') or home/'.config'),
            Path(os.environ.get('XDG_STATE_HOME') or home/'.local/state')/'ScarletProtocol')


def load_payload():
    bundle=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))
    archive=bundle/'desktop-studio-payload.zip'
    checksum=(bundle/'payload.sha256').read_text().strip()
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=checksum:
        raise ValueError('The bundled icon files failed their integrity check. Download a fresh copy.')
    temporary=tempfile.TemporaryDirectory(prefix='scarlet-icon-studio-')
    root=Path(temporary.name)
    with zipfile.ZipFile(archive) as z:
        for item in z.infolist():
            path=Path(item.filename)
            if path.is_absolute() or '..' in path.parts:raise ValueError('Invalid bundled file path')
        z.extractall(root)
    backend.HERE=root;backend.SOURCE=root/'icons/ScarletProtocolIcons';desktop_update.HERE=root;desktop_update.upgrade.HERE=root
    return temporary,root


def install_launcher(data_home):
    if not getattr(sys,'frozen',False):return None
    source=Path(sys.executable).resolve()
    folder=data_home/'ScarletProtocol/DesktopStudio';folder.mkdir(parents=True,exist_ok=True)
    target=folder/'Scarlet-Desktop-Studio'
    if source!=target.resolve():
        staged=folder/'.Scarlet-Icon-Studio.new'
        shutil.copy2(source,staged);staged.chmod(0o755);staged.replace(target)
    def quote(value):
        return '"'+str(value).replace('\\','\\\\').replace('"','\\"').replace('`','\\`').replace('$','\\$').replace('%','%%')+'"'
    applications=data_home/'applications';applications.mkdir(parents=True,exist_ok=True)
    (applications/'org.scarletprotocol.desktopstudio.desktop').write_text(
        '[Desktop Entry]\nType=Application\nName=Scarlet Protocol Desktop Studio\n'
        'Comment=Upgrade Scarlet desktop surfaces, launcher, calendar and icons\n'
        'Icon=org.scarletprotocol.iconstudio\nTerminal=false\n'
        'Categories=Settings;DesktopSettings;\nExec='+quote(target)+'\n')
    old=applications/'org.scarletprotocol.iconstudio.desktop'
    if old.is_file() and not old.is_symlink() and 'Icon=org.scarletprotocol.iconstudio' in old.read_text():
        old.write_text(old.read_text().replace(next(line for line in old.read_text().splitlines() if line.startswith('Exec=')),'Exec='+quote(target)))
    if executable:=shutil.which('kbuildsycoca6'):backend.run([executable,'--noincremental'])
    return target


class Signals(QObject):
    progress=Signal(str)
    done=Signal(object)
    failed=Signal(str)


class Task(QRunnable):
    def __init__(self,action,backup=None,night=False,widgets=True,window_frame=True,reload_panels=True):
        super().__init__();self.action=action;self.backup=backup;self.night=night;self.widgets=widgets;self.window_frame=window_frame;self.reload_panels=reload_panels;self.signals=Signals()

    def run(self):
        try:
            data,config,state=homes()
            if self.action=='verify':
                self.signals.done.emit({'action':'verify','appearance':desktop_update.appearance(config)});return
            if self.action=='desktop':
                self.signals.progress.emit('Updating native desktop surfaces, launcher and calendar…')
                result=desktop_update.apply(data,config,state,self.night,self.widgets,self.window_frame)
                result['action']='desktop'
                try:install_launcher(data)
                except Exception as error:result['launcher_error']=str(error)
                if self.reload_panels:
                    try:result['panel_reload']=desktop_update.reload_panels()
                    except Exception as error:result['panel_reload']='Panel reload: '+str(error)
                self.signals.done.emit(result);return
            if self.action=='restore-desktop':
                desktop_update.restore(config,self.backup)
                self.signals.done.emit({'action':'restore-desktop'});return
            if self.action=='restore':
                self.signals.progress.emit('Restoring the previous icon settings…')
                backend.restore(config,self.backup)
                self.signals.done.emit({'action':'restore'});return
            self.signals.progress.emit('Checking this computer’s applications and widgets…')
            report=backend.audit(backend.data_roots(data))
            derived,overrides=backend.plan(report,backend.data_roots(data))
            report['generated_names']=len(derived);report['desktop_overrides']=len(overrides)
            result={'action':self.action,'report':report}
            if self.action=='install':
                if hasattr(os,'geteuid') and os.geteuid()==0:
                    raise RuntimeError('Open Icon Studio as your normal desktop user, without sudo.')
                self.signals.progress.emit('Installing and applying Scarlet icons…')
                identity,backup=backend.apply(data,config,state,report,derived,overrides)
                result['backup']=str(backup)
                try:
                    install_launcher(data);result['launcher']=True
                except OSError as error:result['launcher_error']=str(error)
            self.signals.done.emit(result)
        except Exception as error:
            if hasattr(error,'stderr') and error.stderr:error=error.stderr
            self.signals.failed.emit(str(error))


class Studio(QMainWindow):
    def __init__(self,root):
        super().__init__();self.root=root;self.active_task=None
        self.setWindowTitle('Scarlet Protocol · Desktop Studio');self.resize(930,900)
        self.setMinimumSize(780,840)
        theme=root/'icons/ScarletProtocolIcons'
        self.setWindowIcon(QIcon(str(theme/'apps/scalable/org.scarletprotocol.iconstudio.svg')))
        panel=QWidget();self.setCentralWidget(panel);layout=QVBoxLayout(panel)
        layout.setContentsMargins(30,24,30,24);layout.setSpacing(15)
        eyebrow=QLabel('S C A R L E T   /   P R O T O C O L');eyebrow.setObjectName('eyebrow');layout.addWidget(eyebrow)
        title=QLabel('Desktop Studio');title.setObjectName('title');layout.addWidget(title)
        intro=QLabel('Classic Slits 8.1: straight segmented rails restored, with launcher repairs included.');intro.setWordWrap(True);intro.setObjectName('muted');layout.addWidget(intro)
        manifest=json.loads((theme/'coverage.json').read_text())
        count=QLabel(f"{manifest['unique_names']:,} icon names  ·  12 categories  ·  Complete artwork included")
        count.setObjectName('count');layout.addWidget(count)
        frame=QFrame();frame.setObjectName('preview');grid=QGridLayout(frame);grid.setContentsMargins(16,13,16,13)
        samples=[('Dolphin','apps','org.kde.dolphin'),('Konsole','apps','org.kde.konsole'),
            ('Firefox','apps','firefox'),('Settings','apps','systemsettings'),
            ('Downloads','places','folder-download'),('Pictures','places','folder-pictures'),
            ('Code','places','folder-code'),('Nanook','places','folder-nanook')]
        for i,(name,category,icon) in enumerate(samples):
            column=QWidget();box=QVBoxLayout(column);box.setContentsMargins(0,0,0,0);box.setSpacing(7)
            picture=QLabel();picture.setAlignment(Qt.AlignCenter)
            picture.setPixmap(QIcon(str(theme/category/'scalable'/(icon+'.svg'))).pixmap(42,42));box.addWidget(picture)
            caption=QLabel(name);caption.setAlignment(Qt.AlignCenter);caption.setObjectName('caption');box.addWidget(caption)
            grid.addWidget(column,0,i)
        layout.addWidget(frame)
        options=QHBoxLayout();options.addWidget(QLabel('Desktop edition'))
        self.edition=QComboBox();self.edition.addItems(['Blackout','Night Shift']);options.addWidget(self.edition);options.addStretch();layout.addLayout(options)
        self.use_frame=QCheckBox('Apply the restored Classic Slits window frame');self.use_frame.setChecked(True);layout.addWidget(self.use_frame)
        self.verify=QPushButton('Check Active Theme');self.verify.setIcon(QIcon(str(theme/'actions/scalable/edit-find.svg')));self.verify.clicked.connect(lambda:self.start('verify'));options.addWidget(self.verify)
        self.use_widgets=QCheckBox('Use Scarlet launcher and calendar on existing panels');self.use_widgets.setChecked(True);layout.addWidget(self.use_widgets)
        self.reload_panels=QCheckBox('Reload Plasma panels after applying (keeps application windows open)');self.reload_panels.setChecked(True);layout.addWidget(self.reload_panels)
        self.desktop=QPushButton('Upgrade && Apply Desktop');self.desktop.setObjectName('installButton');self.desktop.setMinimumHeight(48)
        self.desktop.setIcon(self.windowIcon());self.desktop.clicked.connect(lambda:self.start('desktop'));layout.addWidget(self.desktop)
        self.install=QPushButton('Install / Refresh Icons');self.install.setObjectName('iconButton');self.install.setMinimumHeight(38)
        self.install.setIcon(QIcon(str(theme/'actions/scalable/dialog-ok-apply.svg')))
        self.install.clicked.connect(lambda:self.start('install'))
        row=QHBoxLayout();row.addWidget(self.install);self.audit=QPushButton('Check Icon Coverage');self.audit.setObjectName('auditButton')
        self.audit.setIcon(QIcon(str(theme/'actions/scalable/edit-find.svg')));self.audit.clicked.connect(lambda:self.start('audit'));row.addWidget(self.audit)
        self.restore=QPushButton('Restore…');self.restore.setObjectName('restoreButton')
        self.restore.setIcon(QIcon(str(theme/'actions/scalable/edit-undo.svg')));self.restore_menu=QMenu(self.restore);self.restore.setMenu(self.restore_menu);row.addWidget(self.restore);layout.addLayout(row)
        self.progress=QProgressBar();self.progress.setTextVisible(False);self.progress.setMaximumHeight(5)
        self.progress.setRange(0,1);self.progress.setValue(0);layout.addWidget(self.progress)
        self.status=QLabel('Ready. Click Upgrade & Apply Desktop to begin.');self.status.setWordWrap(True);layout.addWidget(self.status)
        self.log=QPlainTextEdit();self.log.setReadOnly(True);self.log.setObjectName('activityLog');self.log.setMaximumBlockCount(500)
        self.log.setPlaceholderText('Coverage, backup location and installation results appear here.');layout.addWidget(self.log,1)
        footer=QLabel('Classic Slits restores the straight-cut border pattern. Existing wallpaper, icons and effects stay selected.');footer.setObjectName('muted');footer.setWordWrap(True);layout.addWidget(footer)
        self.refresh_restore()
        self.setStyleSheet('''
            QMenu { background:#1c1520; border:1px solid #8c2e4d; } QMenu::item:selected { background:#5e1c36; }
            QComboBox { padding:7px; border:1px solid #713047; border-radius:9px; }
            QMainWindow,QWidget { background:#101116; color:#f7d6e3; font-family:DejaVu Sans; font-size:13px; }
            QLabel#eyebrow { color:#ff315b; font-size:11px; font-weight:600; }
            QLabel#title { font-size:34px; font-weight:600; }
            QLabel#muted { color:#aa8093; font-size:12px; }
            QLabel#count { color:#ff7397; padding:8px 0; }
            QLabel#caption { color:#d0a2b7; font-size:11px; }
            QFrame#preview { border:1px solid #6a263f; border-radius:17px; background:#15131b; }
            QPushButton { border:1px solid #693047; border-radius:12px; padding:10px 15px; background:#20151f; color:#f6d5e2; }
            QPushButton:hover,QPushButton:focus { border:1px solid #ff315b; background:#401b2d; }
            QPushButton:pressed { background:#651d38; }
            QPushButton:disabled { color:#816272; border-color:#34242e; background:#17151b; }
            QPushButton#installButton { border:1px solid #ff315b; background:#4b1730; font-size:15px; font-weight:600; }
            QPushButton#installButton:hover { background:#74203e; }
            QPlainTextEdit { border:1px solid #422532; border-radius:12px; background:#0c0e13; padding:10px; color:#cda6b9; }
            QProgressBar { border:0; border-radius:2px; background:#2a1b26; }
            QProgressBar::chunk { background:#ff315b; border-radius:2px; }
        ''')

    def refresh_restore(self):
        state=homes()[2]
        backups=[p for p in state.glob('before-icons-*') if (p/'restore.json').is_file()]
        self.backup=max(backups,key=lambda p:p.stat().st_mtime) if backups else None
        styles=[p for p in state.glob('before-desktop-update-*') if (p/'desktop-style.json').is_file()]
        self.style_backup=max(styles,key=lambda p:p.stat().st_mtime) if styles else None
        self.restore_menu.clear()
        action=self.restore_menu.addAction('Restore previous appearance');action.setEnabled(self.style_backup is not None);action.triggered.connect(lambda:self.start('restore-desktop'))
        action=self.restore_menu.addAction('Restore previous icons');action.setEnabled(self.backup is not None);action.triggered.connect(lambda:self.start('restore'))
        self.restore.setEnabled(self.backup is not None or self.style_backup is not None)

    def busy(self,value):
        self.desktop.setEnabled(not value);self.edition.setEnabled(not value);self.use_widgets.setEnabled(not value);self.use_frame.setEnabled(not value);self.verify.setEnabled(not value);self.reload_panels.setEnabled(not value)
        self.install.setEnabled(not value);self.audit.setEnabled(not value)
        self.restore.setEnabled(not value and (self.backup is not None or self.style_backup is not None))
        self.progress.setRange(0,0 if value else 1)
        if not value:self.progress.setValue(1)

    def start(self,action):
        if self.active_task:return
        if action=='restore' and not self.backup:return
        if action=='restore-desktop' and not self.style_backup:return
        self.busy(True);self.log.clear()
        task=Task(action,self.style_backup if action=='restore-desktop' else self.backup,self.edition.currentIndex()==1,self.use_widgets.isChecked(),self.use_frame.isChecked(),self.reload_panels.isChecked());self.active_task=task
        task.signals.progress.connect(self.status.setText)
        task.signals.done.connect(self.completed);task.signals.failed.connect(self.failed)
        QThreadPool.globalInstance().start(task)

    def completed(self,result):
        self.active_task=None;self.refresh_restore();self.busy(False)
        if result['action']=='verify':
            self.status.setText('Active appearance check complete.');self.show_appearance(result['appearance']);return
        if result['action']=='desktop':
            self.status.setText('Classic Slits 8.1 applied. '+('Open or refocus a KDE window to see its new frame.' if result['window_frame'] else 'Your existing window frame is still selected.'))
            self.log.appendPlainText(f"Components updated: {result['changed']}\nAlready current: {result['same']}\nBackup: {result['backup']}")
            self.show_appearance(result['appearance'])
            self.log.appendPlainText('Icon selection, wallpaper and existing effects were retained.')
            self.log.appendPlainText(result.get('panel_reload','Sign out and back in once to load the repaired widget QML.'))
            if result.get('launcher_error'):self.log.appendPlainText(result['launcher_error'])
            return
        if result['action']=='restore-desktop':
            self.status.setText('Previous appearance restored.');return
        if result['action']=='restore':
            self.status.setText('Previous icons restored.');self.log.appendPlainText('Restored the backed-up icon preferences and launcher/widget files.');return
        report=result['report']
        self.log.appendPlainText(f"Visible application entries: {len(report['apps'])}\nWidget records: {len(report['widgets'])}\nAdditional icon names prepared: {report['generated_names']}\nPer-user launcher icon overrides: {report['desktop_overrides']}")
        exceptions=[w for w in report['widgets'] if w['coverage']=='external' or not w['icon']]
        if exceptions:self.log.appendPlainText(f'Widgets with embedded or unspecified icons: {len(exceptions)}')
        if result['action']=='install':
            self.status.setText('Installed. Reopen your apps to see their Scarlet icons.')
            self.log.appendPlainText('\nBackup: '+result['backup'])
            self.log.appendPlainText('Already-loaded widgets refresh at the next Plasma login.')
            if result.get('launcher'):self.log.appendPlainText('Desktop Studio is now available in your application launcher.')
            if result.get('launcher_error'):self.log.appendPlainText('Icons applied; launcher shortcut could not be installed: '+result['launcher_error'])
        else:self.status.setText('Coverage check complete. No desktop settings changed.')

    def show_appearance(self,report):
        self.log.appendPlainText('Plasma style: '+str(report['plasma_style']))
        self.log.appendPlainText('Window decoration: '+str(report['decoration']['theme']))
        self.log.appendPlainText('KWin reports this decoration: '+('confirmed' if report['kwin_confirmed'] else 'not confirmed — reopen a window or log in again'))
        self.log.appendPlainText('Icon theme: '+str(report['icons']))
        self.log.appendPlainText('Application control style: '+str(report['application_style']))

    def failed(self,error):
        self.active_task=None;self.refresh_restore();self.busy(False)
        self.status.setText('The update stopped. Details are shown below.');self.log.appendPlainText(error)

    def closeEvent(self,event):
        if self.active_task:
            self.status.setText('Please wait for the current operation to finish.');event.ignore()
        else:event.accept()


def main():
    app=QApplication(sys.argv);app.setApplicationName('Scarlet Protocol Desktop Studio')
    temporary,root=load_payload();window=Studio(root);window.show()
    if '--self-test' in sys.argv:
        from PySide6.QtTest import QTest
        assert window.install.isEnabled() and window.audit.isEnabled()
        # Exercise the real graphical event wiring with a read-only audit.
        QTest.mouseClick(window.audit,Qt.LeftButton)
        def done():
            if window.active_task:QTimer.singleShot(100,done);return
            assert window.status.text()=='Coverage check complete. No desktop settings changed.',window.log.toPlainText()
            output=Path(os.environ.get('SCARLET_STUDIO_SCREENSHOT','/tmp/Scarlet-Icon-Studio.png'))
            assert window.grab().save(str(output));print('PASS: native GUI loaded; actual Check Icon Coverage click completed; '+str(output),flush=True)
            app.quit()
        QTimer.singleShot(100,done)
        QTimer.singleShot(45000,lambda:app.exit(2))
    result=app.exec();temporary.cleanup();return result


if __name__=='__main__':raise SystemExit(main())
