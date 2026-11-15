"""Render the actual Plasma SVG states with FrameSvg-compatible tiling."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
from PySide6.QtCore import QRectF,Qt
from PySide6.QtGui import QGuiApplication,QImage,QPixmap,QPainter,QColor,QFont,QPen
from PySide6.QtSvg import QSvgRenderer

ROOT=Path(__file__).resolve().parents[1]
STYLE=ROOT/'plasma-style/ScarletProtocolPlasma8'


def frame(path,prefix,size):
    svg=QSvgRenderer(str(path));assert svg.isValid()
    name=lambda part:(prefix+'-' if prefix else '')+part
    m=round(svg.boundsOnElement(name('topleft')).width());w,h=size
    image=QImage(w,h,QImage.Format_ARGB32_Premultiplied);image.fill(QColor('transparent'));p=QPainter(image)
    pieces={'topleft':(0,0,m,m),'top':(m,0,w-2*m,m),'topright':(w-m,0,m,m),
        'left':(0,m,m,h-2*m),'center':(m,m,w-2*m,h-2*m),'right':(w-m,m,m,h-2*m),
        'bottomleft':(0,h-m,m,m),'bottom':(m,h-m,w-2*m,m),'bottomright':(w-m,h-m,m,m)}
    for part,rect in pieces.items():
        if part in ('left','right','top','bottom') or part=='center' and svg.elementExists(prefix+'-hint-tile-center'):
            tile=QPixmap(m,m);tile.fill(QColor('transparent'));tp=QPainter(tile);svg.render(tp,name(part),QRectF(0,0,m,m));tp.end()
            p.save();p.translate(rect[0],rect[1]);p.drawTiledPixmap(0,0,rect[2],rect[3],tile);p.restore()
        else:svg.render(p,name(part),QRectF(*rect))
    p.end();return image


def main():
    app=QGuiApplication([]);out=QImage(1440,1020,QImage.Format_ARGB32_Premultiplied);out.fill(QColor('#090b10'))
    p=QPainter(out);p.setRenderHint(QPainter.Antialiasing)
    def text(x,y,w,h,value,size=12,color='#e4b9cb',bold=False):
        p.setPen(QColor(color));p.setFont(QFont('DejaVu Sans',size,QFont.Bold if bold else QFont.Normal));p.drawText(QRectF(x,y,w,h),Qt.AlignVCenter,value)
    def draw(file,prefix,x,y,w,h):p.drawImage(x,y,frame(STYLE/file,prefix,(w,h)))
    text(53,28,1300,25,'S C A R L E T   /   O B S I D I A N   /   0 8',10,'#ff315b',True)
    text(52,69,1300,55,'Deeper metal. Brighter contacts.',29,'#ffe2ed',True)
    text(54,132,1300,28,'Rounded popups  ·  Illuminated controls  ·  Keyboard focus  ·  Segmented meters',12,'#a97b90')
    draw('dialogs/background.svg','',40,191,830,365)
    text(73,220,740,32,'POPUPS & NOTIFICATIONS',12,'#ff688c',True)
    text(73,266,730,40,'Carbon faces with recessed corner contacts.',21,'#f5d5e3',True)
    text(73,314,735,38,'The same edge language now follows menus, notifications and desktop surfaces.',11,'#bc8cA3')
    draw('widgets/bar_meter_horizontal.svg','background',74,383,730,23)
    draw('widgets/bar_meter_horizontal.svg','bar-active',74,383,501,23)
    text(74,416,700,26,'SEGMENTED PROGRESS',9,'#a16c83')
    draw('widgets/button.svg','normal',74,468,222,49);text(94,474,190,34,'Normal',12)
    draw('widgets/button.svg','hover',316,468,222,49);text(336,474,190,34,'Hover',12,'#ffe4ef')
    draw('widgets/button.svg','pressed',558,468,222,49);text(578,474,190,34,'Pressed',12,'#ffe4ef')
    draw('widgets/tooltip.svg','',910,193,482,122)
    text(941,224,420,35,'Sharper hover feedback',16,'#ffe0ed',True)
    text(941,265,420,23,'Detailed edge contacts, consistent contrast.',10,'#ba879f')
    draw('widgets/background.svg','',910,346,482,210)
    text(941,372,420,27,'FOCUS & INPUT',12,'#ff688c',True)
    draw('widgets/lineedit.svg','base',941,419,420,45);text(961,425,380,31,'Text input',12,'#aa8397')
    draw('widgets/lineedit.svg','focus',941,481,420,45);text(961,487,380,31,'Keyboard focus stays visible',12,'#ffe5ef')
    draw('widgets/background.svg','',40,594,1352,331)
    text(74,620,1240,35,'TASKS, MENUS & SELECTION',14,'#ff688c',True)
    for i,(prefix,label) in enumerate([('normal','Idle'),('hover','Hover'),('focus','Active'),('attention','Attention'),('minimized','Minimized')]):
        x=74+i*252;draw('widgets/tasks.svg',prefix,x,681,230,58);text(x+18,690,200,38,label,12)
    for i,(prefix,label) in enumerate([('normal','Normal item'),('hover','Hovered item'),('selected','Selected item'),('selected+hover','Selected + hover')]):
        x=74+i*315;draw('widgets/viewitem.svg',prefix,x,785,290,58);text(x+18,794,260,38,label,12)
    text(74,868,1240,30,'Wider slotted Obsidian window frames carry the same sculpted metal and scarlet lighting.',11,'#b5819a')
    text(54,958,1300,27,'Rendered from the shipped Plasma SVGs; interaction states are shown side by side.',10,'#93677e')
    p.end();path=ROOT.parent/'Scarlet-Protocol-Surface-Details.png';assert out.save(str(path));print(path)


if __name__=='__main__':main()
