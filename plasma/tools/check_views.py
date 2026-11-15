"""Exercise actual shipped Qt Quick views, date math and upgrade behavior."""
from pathlib import Path
import json
import os
import tempfile
import importlib.util
import sys

os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
os.environ.setdefault('QT_QUICK_BACKEND','software')
from PySide6.QtCore import QPoint, QPointF, Qt, QUrl, qInstallMessageHandler
from PySide6.QtGui import QGuiApplication, QInputMethodEvent
from PySide6.QtQml import QJSEngine, QQmlEngine, QQmlComponent
from PySide6.QtQuick import QQuickItem
from PySide6.QtTest import QTest
from render_preview import ROOT,assets,create_view

def load_module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def main():
    messages=[]
    qInstallMessageHandler(lambda kind,context,message: messages.append(message))
    app=QGuiApplication([]);assets();view=create_view();view.requestActivate();QTest.qWait(300)
    stage=view.rootObject()
    def item(name):
        pending=[stage,view.contentItem()]
        while pending:
            found=pending.pop()
            if found.objectName()==name:return found
            pending.extend(found.childItems())
        raise AssertionError(name+'\n'+'\n'.join(messages))
    def click(name):
        control=item(name);point=control.mapToScene(QPointF(control.width()/2,control.height()/2)).toPoint()
        QTest.mouseClick(view,Qt.LeftButton,Qt.NoModifier,point);QTest.qWait(70)
    def value(name):
        v=stage.property(name)
        return v.toVariant() if hasattr(v,'toVariant') else v
    def type_text(text):
        event=QInputMethodEvent();event.setCommitString(text)
        QGuiApplication.sendEvent(view,event);QTest.qWait(20)
    launcher=item('launcher');calendar=item('calendar')
    click('favoritesTab');assert launcher.property('section')==0
    click('applicationsTab');assert launcher.property('section')==1
    click('appPin0');assert value('pinEvents')==['dolphin']
    click('appTile1');assert value('launches')==[1]
    click('launcherSearch');type_text('dolphin');assert launcher.property('query')=='dolphin'
    QTest.keyClick(view,Qt.Key_Escape);assert launcher.property('query')==''
    click('nextMonth');assert calendar.property('displayMonth')==11
    click('previousMonth');assert calendar.property('displayMonth')==10
    click('dateCell13');assert calendar.property('selectedKey')=='2026-11-14'
    click('dateNote');QTest.keyClick(view,Qt.Key_A,Qt.ControlModifier);type_text('Review window detail')
    assert calendar.property('noteDirty') is True
    click('saveNoteButton');assert value('savedNotes')['2026-11-14']=='Review window detail',value('savedNotes')
    assert calendar.property('noteDirty') is False
    click('dateCell12');click('dateCell13');assert item('dateNote').property('text')=='Review window detail'
    click('todayButton');assert calendar.property('selectedKey')=='2026-11-13'
    click('launcherSearch');QTest.keyClick(view,Qt.Key_Down);QTest.keyClick(view,Qt.Key_Right);QTest.keyClick(view,Qt.Key_Return)
    assert value('launches')[-1]==1,value('launches')
    click('dateCell13');QTest.keyClick(view,Qt.Key_Right);QTest.keyClick(view,Qt.Key_Return)
    assert calendar.property('selectedKey')=='2026-11-15',calendar.property('selectedKey')
    launcher.setWidth(520);calendar.setWidth(410);QTest.qWait(50)
    assert item('applicationGrid').width()>400 and item('calendarGrid').width()>300
    engine=QJSEngine()
    code=(ROOT/'plasmoids/org.scarletprotocol.clock/contents/ui/DateMath.js').read_text().replace('.pragma library','')
    assert not engine.evaluate(code).isError()
    for year,month,day,expected in [(2021,1,1,53),(2021,1,4,1),(2024,12,30,1),(2026,11,13,46)]:
        result=engine.evaluate(f'isoWeek(new Date({year},{month-1},{day},12))').toInt()
        assert result==expected,(year,month,day,result)
    assert engine.evaluate('monthCells(2024,1,false).filter(d=>d.inMonth).length').toInt()==29
    assert engine.evaluate('key(monthCells(2024,1,false)[0].date)').toString()=='2024-01-28'
    assert engine.evaluate('key(monthCells(2024,1,true)[0].date)').toString()=='2024-01-29'
    click('toolsTab');assert launcher.property('section')==2 and item('applicationGrid').property('count')==2
    click('appTile0');assert value('launches')[-1]==2
    click('recentTab');assert launcher.property('section')==3 and item('applicationGrid').property('count')==2
    click('clearRecentButton');assert item('applicationGrid').property('count')==0
    QTest.keyClick(view,Qt.Key_3,Qt.ControlModifier);assert launcher.property('section')==2
    QTest.keyClick(view,Qt.Key_2,Qt.ControlModifier);assert launcher.property('section')==1
    click('chooseMonthButton');QTest.qWait(80)
    assert item('monthChoice0').property('text')=='Jan'
    click('nextPickerYear');click('monthChoice6')
    assert calendar.property('displayYear')==2027 and calendar.property('displayMonth')==6
    click('todayButton')
    click('browseNotesButton');assert calendar.property('notesIndexOpen') is True
    click('notesSearch');type_text('Review window')
    assert item('notesList').property('count')==1
    click('indexedNote0');assert calendar.property('selectedKey')=='2026-11-14' and calendar.property('notesIndexOpen') is False
    assert item('dateNote').property('text')=='Review window detail'
    assert engine.evaluate('fromKey("2026-02-31")===null').toBool()
    assert engine.evaluate('daysBetween(new Date(2026,2,7,12),new Date(2026,2,9,12))').toInt()==2
    history=(ROOT/'plasmoids/org.scarletprotocol.launcher/contents/ui/AppHistory.js').read_text().replace('.pragma library','')
    assert not engine.evaluate(history).isError()
    assert engine.evaluate('JSON.stringify(remember(["a","b","a"],"b",2))').toString()=='["b","a"]'
    host=(ROOT/'plasmoids/org.scarletprotocol.launcher/contents/ui/main.qml').read_text()
    assert 'root.favorites.favorites' not in host and 'favoritesModel.favorites' not in host.replace('systemFavoritesModel.favorites','systemFavorites')
    print('PASS: Tools/Recent source-row launch routing, clear history, section shortcuts, month/year picker, saved-note search/navigation, DST-safe date distance and native favorites API contract')
    config_engine=QQmlEngine()
    component=QQmlComponent(config_engine,QUrl.fromLocalFile(str(ROOT/'plasmoids/org.scarletprotocol.systemcore/contents/ui/CoreButton.qml')))
    control=component.createWithInitialProperties({'text':'START','iconName':'media-playback-start'})
    assert control is not None,[e.toString() for e in component.errors()]
    for name in ['launcher','clock']:
        component=QQmlComponent(config_engine,QUrl.fromLocalFile(str(ROOT/f'plasmoids/org.scarletprotocol.{name}/contents/ui/configGeneral.qml')))
        config=component.create()
        assert config is not None,[e.toString() for e in component.errors()]
        assert config.metaObject().indexOfProperty('cfg_accentColor')>=0
        assert config.metaObject().indexOfProperty('cfg_glowStrength')>=0
    assert not messages,'\n'.join(messages)
    print('PASS: Qt 6 loads without warnings; tabs, pinning, launch signals, search input, keyboard, month navigation, leap dates, ISO weeks and persisted date-note callbacks')
    sys.path.insert(0,str(ROOT))
    if not (ROOT.parent/'v5-plasma-source/install.py').exists():
        print('SKIP: archived release 5 source is not present for the development-only migration rehearsal')
        view.close();return
    previous=load_module(ROOT.parent/'v5-plasma-source/install.py','old_install')
    current=load_module(ROOT/'upgrade.py','new_upgrade')
    with tempfile.TemporaryDirectory(prefix='scarlet-v6-upgrade-') as directory:
        data=Path(directory)/'data';state=Path(directory)/'state'
        previous.install(data)
        old_frame=(data/'aurorae/themes/ScarletProtocolGlobal/decoration.svg').read_bytes()
        changed,same,backup=current.upgrade(data,state)
        assert changed>0 and backup
        assert (data/'aurorae/themes/ScarletProtocolGlobal81/decoration.svg').is_file()
        assert (data/'aurorae/themes/ScarletProtocolGlobal/decoration.svg').read_bytes()==old_frame
        assert (data/'plasma/plasmoids/org.scarletprotocol.launcher/contents/ui/main.qml').is_file()
        assert (data/'plasma/plasmoids/org.scarletprotocol.clock/contents/ui/main.qml').is_file()
        assert current.upgrade(data,state)==(0,len(current.COMPONENTS),None)
        assert '__aurorae__svg__ScarletProtocolGlobal81' in (data/'plasma/look-and-feel/ScarletProtocolGlobal/contents/defaults').read_text()
    print('PASS: v5 upgrade keeps prior frames, installs v8 components, backs up changed components and repeats without changes')
    view.close()

if __name__=='__main__':main()
