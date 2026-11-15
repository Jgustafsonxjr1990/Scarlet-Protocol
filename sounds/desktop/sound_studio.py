#!/usr/bin/env python3
"""Scarlet Protocol Sound Studio — portable graphical audition and installer."""
from pathlib import Path
import hashlib,json,os,shutil,sys,tempfile,zipfile
from PySide6.QtCore import Qt,QObject,QRunnable,QThreadPool,Signal,QTimer,QProcess,QProcessEnvironment,QUrl
from PySide6.QtGui import QIcon,QDesktopServices
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QLineEdit,QTreeWidget,QTreeWidgetItem,QPushButton,QPlainTextEdit,QProgressBar
import sound_backend as backend


def homes():
    home=Path.home()
    return Path(os.environ.get('XDG_DATA_HOME') or home/'.local/share'),Path(os.environ.get('XDG_CONFIG_HOME') or home/'.config'),Path(os.environ.get('XDG_STATE_HOME') or home/'.local/state')/'ScarletProtocol'


def load_payload():
    bundle=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))
    source=bundle/'sound-payload.zip'
    if hashlib.sha256(source.read_bytes()).hexdigest()!=(bundle/'payload.sha256').read_text().strip():raise ValueError('Sound files failed their integrity check. Download a fresh copy.')
    temporary=tempfile.TemporaryDirectory(prefix='scarlet-sound-studio-');root=Path(temporary.name)
    with zipfile.ZipFile(source) as archive:
        if any(Path(p.filename).is_absolute() or '..' in Path(p.filename).parts for p in archive.infolist()):raise ValueError('Invalid sound package path')
        archive.extractall(root)
    backend.HERE=root
    return temporary,root


def install_launcher(data_home,root):
    if not getattr(sys,'frozen',False):return
    folder=data_home/'ScarletProtocol/SoundStudio';folder.mkdir(parents=True,exist_ok=True)
    source=Path(sys.executable).resolve();target=folder/'Scarlet-Sound-Studio'
    if source!=target.resolve():
        stage=folder/'.Sound-Studio.new';shutil.copy2(source,stage);stage.chmod(0o755);stage.replace(target)
    icons=data_home/'icons/hicolor/scalable/apps';icons.mkdir(parents=True,exist_ok=True)
    shutil.copy2(root/'desktop/sound-studio.svg',icons/'org.scarletprotocol.soundstudio.svg')
    applications=data_home/'applications';applications.mkdir(parents=True,exist_ok=True)
    quoted='"'+str(target).replace('\\','\\\\').replace('"','\\"').replace('`','\\`').replace('$','\\$').replace('%','%%')+'"'
    (applications/'org.scarletprotocol.soundstudio.desktop').write_text('[Desktop Entry]\nType=Application\nName=Scarlet Protocol Sound Studio\nComment=Preview and apply cyberpunk desktop sounds\nIcon=org.scarletprotocol.soundstudio\nTerminal=false\nCategories=Settings;Audio;\nExec='+quoted+'\n')
    if exe:=shutil.which('kbuildsycoca6'):backend.run([exe,'--noincremental'])


class Signals(QObject):
    done=Signal(object)
    failed=Signal(str)


class Task(QRunnable):
    def __init__(self,action,profile,backup,root):
        super().__init__();self.action=action;self.profile=profile;self.backup=backup;self.root=root;self.signals=Signals()
    def run(self):
        try:
            data,config,state=homes()
            if self.action=='apply':
                result=backend.apply(data,config,state,self.profile);result['action']='apply'
                try:install_launcher(data,self.root)
                except Exception as error:result['launcher_error']=str(error)
            else:result={'action':'restore','previous':backend.restore(data,config,self.backup)}
            self.signals.done.emit(result)
        except Exception as error:
            self.signals.failed.emit(getattr(error,'stderr',None) or str(error))


class Studio(QMainWindow):
    def __init__(self,root):
        super().__init__();self.root=root;self.active_task=None;self.playing_title='';self.stopping=False
        self.catalog=json.loads((root/'catalog.json').read_text());self.profiles=json.loads((root/'profiles.json').read_text())
        self.setWindowTitle('Scarlet Protocol · Sound Studio');self.resize(940,850);self.setMinimumSize(780,730)
        self.setWindowIcon(QIcon(str(root/'desktop/sound-studio.svg')))
        panel=QWidget();self.setCentralWidget(panel);layout=QVBoxLayout(panel);layout.setContentsMargins(28,20,28,20);layout.setSpacing(10)
        label=QLabel('S C A R L E T  /  P R O T O C O L');label.setObjectName('eyebrow');layout.addWidget(label)
        title=QLabel('Cyber Circuit · Sound Studio');title.setObjectName('title');layout.addWidget(title)
        label=QLabel('39 original cues · FM pulses · circuit glitches · filtered power sweeps');label.setObjectName('muted');layout.addWidget(label)
        row=QHBoxLayout();row.addWidget(QLabel('Sound edition'))
        self.profile=QComboBox()
        for key,entry in self.profiles.items():self.profile.addItem(entry['title'],key)
        row.addWidget(self.profile);row.addStretch();self.browser=QPushButton('Open Sound Browser');self.browser.clicked.connect(lambda:QDesktopServices.openUrl(QUrl.fromLocalFile(str(root/'preview.html'))));row.addWidget(self.browser);layout.addLayout(row)
        self.edition_note=QLabel();self.edition_note.setObjectName('muted');self.edition_note.setWordWrap(True);layout.addWidget(self.edition_note)
        self.profile.currentIndexChanged.connect(self.edition_changed)
        filters=QHBoxLayout();self.search=QLineEdit();self.search.setPlaceholderText('Find a sound…');self.search.setClearButtonEnabled(True);filters.addWidget(self.search)
        self.family=QComboBox();self.family.addItem('All events');self.family.addItems(['Session','Messages','System','Alerts','Interface','Windows']);filters.addWidget(self.family);layout.addLayout(filters)
        self.tree=QTreeWidget();self.tree.setHeaderLabels(['Sound','Event group','Length']);self.tree.setRootIsDecorated(False);self.tree.setAlternatingRowColors(True);self.tree.setColumnWidth(0,420);self.tree.setColumnWidth(1,150)
        self.tree.setAccessibleName('Sound collection');self.tree.setMinimumHeight(180)
        for item in self.catalog:
            row=QTreeWidgetItem([item['title'],item['family'],str(item['duration'])+' s']);row.setData(0,Qt.UserRole,item);self.tree.addTopLevelItem(row)
        layout.addWidget(self.tree,1);self.search.textChanged.connect(self.filter);self.family.currentIndexChanged.connect(self.filter)
        self.detail=QLabel();self.detail.setWordWrap(True);self.detail.setMinimumHeight(40);self.detail.setObjectName('muted');layout.addWidget(self.detail)
        self.tree.currentItemChanged.connect(self.describe);self.tree.itemDoubleClicked.connect(lambda *args:self.play());self.tree.setCurrentItem(self.tree.topLevelItem(0))
        row=QHBoxLayout();self.preview=QPushButton('Preview Selected');self.preview.clicked.connect(self.play);row.addWidget(self.preview)
        self.stop=QPushButton('Stop');self.stop.clicked.connect(self.stop_audio);row.addWidget(self.stop);layout.addLayout(row)
        self.apply_button=QPushButton('Install && Apply Sounds');self.apply_button.setObjectName('primary');self.apply_button.setMinimumHeight(47);self.apply_button.clicked.connect(lambda:self.start('apply'));layout.addWidget(self.apply_button)
        self.restore_button=QPushButton('Restore Previous Sounds');self.restore_button.clicked.connect(lambda:self.start('restore'));layout.addWidget(self.restore_button)
        self.progress=QProgressBar();self.progress.setRange(0,1);self.progress.setTextVisible(False);self.progress.setMaximumHeight(4);layout.addWidget(self.progress)
        self.status=QLabel('Choose an edition and preview a sound.');self.status.setWordWrap(True);layout.addWidget(self.status)
        self.log=QPlainTextEdit();self.log.setReadOnly(True);self.log.setFixedHeight(70);self.log.setPlaceholderText('Installation details and backup location appear here.');layout.addWidget(self.log)
        footer=QLabel('Playback follows each app’s notification settings. Window and click cues are included for apps that request them.');footer.setWordWrap(True);footer.setObjectName('muted');layout.addWidget(footer)
        self.player=QProcess(self);self.player.finished.connect(self.audio_finished);self.player.errorOccurred.connect(self.audio_error)
        self.setStyleSheet('''QWidget { background:#101116; color:#efd3e1; font-size:13px; } QLabel#title { font-size:29px; font-weight:700; } QLabel#eyebrow { color:#ff315b; font-size:12px; } QLabel#muted { color:#b17e96; } QPushButton,QComboBox,QLineEdit { border:1px solid #653048; border-radius:12px; padding:9px 14px; background:#211721; } QPushButton:hover,QComboBox:hover { border-color:#ff315b; background:#3d1e30; } QPushButton:focus,QLineEdit:focus,QComboBox:focus { border:1px solid #ff7fa5; } QPushButton:disabled { color:#725361; border-color:#36202c; } QPushButton#primary { background:#48172f; border-color:#ff315b; font-weight:700; } QTreeWidget,QPlainTextEdit { background:#0c0e13; alternate-background-color:#17131c; border:1px solid #54263b; border-radius:12px; padding:7px; } QTreeWidget::item { padding:6px; } QTreeWidget::item:selected { background:#58233d; color:#ffe9f1; } QHeaderView::section { background:#211721; color:#ce8da9; padding:8px; border:0; } QProgressBar { border:0; background:#311b2a; } QProgressBar::chunk { background:#ff315b; }''')
        for button,name in [(self.preview,'play'),(self.stop,'stop'),(self.apply_button,'apply'),(self.restore_button,'restore')]:button.setIcon(QIcon(str(root/'desktop/icons'/(name+'.svg'))))
        self.edition_changed();self.refresh_restore()

    def edition_changed(self):
        self.edition_note.setText({'protocol':'Cyber Circuit: sharp packet tones, gritty bass and controlled glitch detail.','night':'Night Shift: darker filtering and roughly half-amplitude cues for a quieter desktop.','overdrive':'Overdrive: stronger saturation and digital grain, with nearly the same peak level as Cyber Circuit.'}[self.profile.currentData()])
        if hasattr(self,'player'):self.stop_audio()

    def describe(self,*args):
        row=self.tree.currentItem();self.detail.setText(row.data(0,Qt.UserRole)['description'] if row else '')

    def filter(self,*args):
        query=self.search.text().casefold();group=self.family.currentText()
        first=None
        for index in range(self.tree.topLevelItemCount()):
            row=self.tree.topLevelItem(index);item=row.data(0,Qt.UserRole)
            hidden=not (query in (item['title']+' '+item['name']+' '+item['description']).casefold() and (group=='All events' or group==item['family']))
            row.setHidden(hidden)
            if not hidden and first is None:first=row
        self.tree.setCurrentItem(first);self.preview.setEnabled(first is not None)

    def stop_audio(self):
        if self.player.state()!=QProcess.NotRunning:
            self.stopping=True;self.player.kill();self.player.waitForFinished(500)
        self.stopping=False

    def play(self):
        row=self.tree.currentItem()
        if row is None:return
        self.stop_audio();item=row.data(0,Qt.UserRole)
        try:command=backend.player_command(self.root/'WAV'/self.profile.currentData()/(item['name']+'.wav'))
        except RuntimeError as error:self.status.setText(str(error));return
        environment=QProcessEnvironment()
        for key,value in backend.native_environment().items():environment.insert(key,value)
        self.player.setProcessEnvironment(environment);self.playing_title=item['title'];self.status.setText('Playing: '+self.playing_title)
        self.player.start(command[0],command[1:])

    def audio_finished(self,code,*args):
        if self.stopping:return
        self.status.setText('Preview finished: '+self.playing_title if code==0 else 'Audio playback stopped. '+bytes(self.player.readAllStandardError()).decode(errors='replace').strip())

    def audio_error(self,*args):
        if not self.stopping:self.status.setText('Audio player could not start. Use Open Sound Browser to listen.')

    def refresh_restore(self):
        state=homes()[2];backups=[p for p in state.glob('before-sound-selection-*') if (p/'selection.json').is_file()]
        self.backup=max(backups,key=lambda p:p.stat().st_mtime) if backups else None
        self.restore_button.setEnabled(self.backup is not None and self.active_task is None)

    def start(self,action):
        if self.active_task or action=='restore' and not self.backup:return
        self.stop_audio();self.log.clear();self.status.setText('Applying sound theme…' if action=='apply' else 'Restoring previous sounds…')
        task=Task(action,self.profile.currentData(),self.backup,self.root);self.active_task=task
        self.apply_button.setEnabled(False);self.restore_button.setEnabled(False);self.profile.setEnabled(False);self.progress.setRange(0,0)
        task.signals.done.connect(self.completed);task.signals.failed.connect(self.failed);QThreadPool.globalInstance().start(task)

    def finish(self):
        self.active_task=None;self.apply_button.setEnabled(True);self.profile.setEnabled(True);self.progress.setRange(0,1);self.progress.setValue(1);self.refresh_restore()

    def completed(self,result):
        self.finish()
        if result['action']=='restore':self.status.setText('Previous sounds restored.');return
        self.status.setText('Sounds are already current.' if result['current'] else 'Cyber Circuit sounds installed and selected.')
        self.log.appendPlainText('Selected sound theme: '+result['theme']+'\nSound settings verified.\nEditions updated: '+str(result['changed']))
        if result['backup']:self.log.appendPlainText('Backup: '+result['backup'])
        if result.get('launcher_error'):self.log.appendPlainText('Launcher shortcut: '+result['launcher_error'])
        self.log.appendPlainText('Reopen Sound Theme settings or sign in again if an application retains cached audio.')

    def failed(self,error):
        self.finish();self.status.setText('Sound update stopped.');self.log.appendPlainText(error)

    def closeEvent(self,event):
        if self.active_task:self.status.setText('Please wait for the sound update to finish.');event.ignore()
        else:self.stop_audio();event.accept()


def main():
    app=QApplication(sys.argv);app.setApplicationName('Scarlet Protocol Sound Studio')
    temporary,root=load_payload();window=Studio(root);window.show()
    if '--self-test' in sys.argv:
        def check():
            window.profile.setCurrentIndex(2);window.search.setText('Window open')
            assert sum(not window.tree.topLevelItem(i).isHidden() for i in range(window.tree.topLevelItemCount()))==1
            assert window.preview.isEnabled() and window.apply_button.isEnabled()
            window.search.clear();window.profile.setCurrentIndex(0)
            output=os.environ.get('SCARLET_SOUND_SCREENSHOT','/tmp/Scarlet-Sound-Studio.png');assert window.grab().save(output)
            print('PASS: packaged native Sound Studio, 39 cues, edition change, search and preview routing ready; '+output,flush=True);app.quit()
        QTimer.singleShot(300,check)
    result=app.exec();temporary.cleanup();return result


if __name__=='__main__':raise SystemExit(main())
