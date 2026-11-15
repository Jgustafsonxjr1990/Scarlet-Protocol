"""Record the actual release 6 QML views with sample model data."""
from pathlib import Path
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
os.environ.setdefault('QT_QUICK_BACKEND','software')
import subprocess
import tempfile
from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtTest import QTest
from render_preview import ROOT,assets,create_view

def main():
    app=QGuiApplication([]);assets();view=create_view();view.requestActivate();QTest.qWait(200)
    stage=view.rootObject()
    def item(name):
        pending=[stage,view.contentItem()]
        while pending:
            current=pending.pop()
            if current.objectName()==name:return current
            pending.extend(current.childItems())
        raise AssertionError(name)
    def point(name):
        target=item(name)
        return target.mapToScene(QPointF(target.width()/2,target.height()/2)).toPoint()
    def click(name):QTest.mouseClick(view,Qt.LeftButton,Qt.NoModifier,point(name))
    with tempfile.TemporaryDirectory(prefix='scarlet-release6-frames-') as temp:
        for frame in range(220):
            if frame==0:QTest.mouseMove(view,QPoint(74,158))
            if frame==20:click('toolsTab')
            if frame==48:click('recentTab')
            if frame==72:click('applicationsTab')
            if frame==90:click('chooseMonthButton')
            if frame==114:click('nextPickerYear')
            if frame==138:click('monthChoice6')
            if frame==158:click('todayButton')
            if frame==180:click('browseNotesButton')
            if frame==204:QTest.mouseMove(view,point('indexedNote0'))
            QTest.qWait(50)
            assert view.grabWindow().save(str(Path(temp)/f'{frame:04d}.png'))
        output=ROOT.parent/'Scarlet-Protocol-Desktop-7-Preview.mp4'
        subprocess.run(['ffmpeg','-v','error','-y','-framerate','20','-i',str(Path(temp)/'%04d.png'),'-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(output)],check=True)
        print(output)
    view.close()

if __name__=='__main__':main()
