"""Same-scale comparison of shipped Aurorae artwork; no live desktop implied."""
from pathlib import Path
import os,tempfile
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtCore import QRectF,Qt
from PySide6.QtGui import QGuiApplication,QImage,QPainter,QColor,QFont
from PySide6.QtSvg import QSvgRenderer
from render_preview import render_frame,ROOT


def main():
    app=QGuiApplication([]);out=QImage(1480,680,QImage.Format_ARGB32_Premultiplied);out.fill(QColor('#090b10'))
    p=QPainter(out);p.setRenderHint(QPainter.Antialiasing)
    def text(x,y,w,h,value,size,color='#f6dce6',bold=False):
        p.setPen(QColor(color));p.setFont(QFont('DejaVu Sans',size,QFont.Bold if bold else QFont.Normal));p.drawText(QRectF(x,y,w,h),Qt.AlignVCenter,value)
    text(40,20,1400,30,'SCARLET / PROTOCOL',11,'#ff315b',True)
    text(40,59,1400,50,'Classic Slits. The finer pattern returns.',28,bold=True)
    with tempfile.TemporaryDirectory() as directory:
        for x,new in [(26,False),(762,True)]:
            decor=ROOT/'aurorae'/('ScarletProtocolGlobal81' if new else 'ScarletProtocolGlobal8')
            text(x+13,124,660,32,'CLASSIC SLITS 8.1' if new else 'OBSIDIAN 8',12,'#ff628b' if new else '#ae7d94',True)
            target=Path(directory)/('new.png' if new else 'old.png');render_frame(decor/'decoration.svg',target,(690,450))
            p.drawImage(x,168,QImage(str(target)))
            inset=24;top=62
            p.fillRect(QRectF(x+inset,168+top,690-2*inset,450-top-inset),QColor('#11141b'))
            # Identical example contents make the frame difference easy to judge.
            text(x+inset+22,168+top+20,570,28,'SCARLET WORKSPACE',11,'#a7748e',True)
            for i,name in enumerate(('Documents','Downloads','Pictures')):
                gx=x+inset+24+i*190;gy=168+top+81
                p.setPen(QColor('#583045'));p.setBrush(QColor('#1a1721'));p.drawRoundedRect(QRectF(gx,gy,166,150),16,16)
                svg=QSvgRenderer(str(ROOT/'icons/ScarletProtocolIcons/places/scalable'/('folder-'+name.lower()+'.svg')))
                svg.render(p,QRectF(gx+56,gy+22,54,54));text(gx+12,gy+93,142,27,name,11)
            for i,name in enumerate(('close','minimize','maximize')):
                svg=QSvgRenderer(str(decor/(name+'.svg')))
                svg.render(p,'active-center',QRectF(x+24+i*42,168+16,38,34))
            text(x+170,188,450,25,'Scarlet Protocol — Workspace',11,'#f0c8db' if new else '#c795ae')
            text(x+23,627,655,24,'Fine straight cuts · rounded glow · same controls' if new else 'Larger diagonal vent pockets',10,'#d799b3' if new else '#91677b')
    p.end();path=ROOT.parent/'Scarlet-Protocol-Classic-Slits-Preview.png';assert out.save(str(path));print(path)

if __name__=='__main__':main()
