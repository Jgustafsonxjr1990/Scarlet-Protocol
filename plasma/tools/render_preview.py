"""Render the shipped QML views and native SVG parts using Qt 6."""
from pathlib import Path
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
os.environ.setdefault('QT_QUICK_BACKEND','software')
from PySide6.QtCore import QRectF, QUrl, QTimer
from PySide6.QtGui import QGuiApplication, QImage, QPainter, QColor, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtQuick import QQuickView

ROOT=Path(__file__).resolve().parents[1]

def render_part(path,element,target,size):
    svg=QSvgRenderer(str(path));assert svg.isValid(),path
    image=QImage(*size,QImage.Format_ARGB32_Premultiplied);image.fill(QColor('transparent'))
    painter=QPainter(image);svg.render(painter,element,QRectF(0,0,*size));painter.end()
    image.save(str(target))

def render_frame(path,target,size,prefix="decoration",dpr=1):
    w,h=size
    svg=QSvgRenderer(str(path));assert svg.isValid()
    bounds=lambda part:svg.boundsOnElement(prefix+'-'+part)
    left=round(bounds('topleft').width());right=round(bounds('topright').width())
    top=round(bounds('topleft').height());bottom=round(bounds('bottomleft').height())
    image=QImage(w*dpr,h*dpr,QImage.Format_ARGB32_Premultiplied);image.setDevicePixelRatio(dpr);image.fill(QColor('transparent'))
    painter=QPainter(image)
    for name,rect in {
        'topleft':(0,0,left,top),'top':(left,0,w-left-right,top),'topright':(w-right,0,right,top),
        'left':(0,top,left,h-top-bottom),'center':(left,top,w-left-right,h-top-bottom),'right':(w-right,top,right,h-top-bottom),
        'bottomleft':(0,h-bottom,left,bottom),'bottom':(left,h-bottom,w-left-right,bottom),'bottomright':(w-right,h-bottom,right,bottom)}.items():
        element=prefix+'-'+name
        if name in ('left','right','top','bottom'):
            tw,th=round(bounds(name).width()),round(bounds(name).height())
            tile=QPixmap(tw*dpr,th*dpr);tile.setDevicePixelRatio(dpr);tile.fill(QColor('transparent'))
            tile_painter=QPainter(tile);svg.render(tile_painter,element,QRectF(0,0,tw,th));tile_painter.end()
            painter.save();painter.translate(rect[0],rect[1])
            painter.drawTiledPixmap(0,0,rect[2],rect[3],tile);painter.restore()
        else:
            svg.render(painter,element,QRectF(*rect))
    painter.end();image.save(str(target))

def create_view():
    view=QQuickView();view.setResizeMode(QQuickView.SizeViewToRootObject)
    view.setSource(QUrl.fromLocalFile(str(ROOT/'tools/preview.qml')))
    assert view.status()!=QQuickView.Error,[e.toString() for e in view.errors()]
    view.show();return view

def assets(night=False):
    decor=ROOT/'aurorae'/('ScarletProtocolNight81' if night else 'ScarletProtocolGlobal81')
    render_frame(decor/'decoration.svg',ROOT/'tools/rendered-frame.png',(1368,844))
    for name in ['close','minimize','maximize']:
        render_part(decor/(name+'.svg'),'hover-center',ROOT/'tools'/('rendered-'+name+'.png'),(66,58))
        render_part(decor/(name+'.svg'),'active-center',ROOT/'tools'/('rendered-'+name+'-active.png'),(66,58))
    style=ROOT/'plasma-style'/('ScarletProtocolNightPlasma8' if night else 'ScarletProtocolPlasma8')/'widgets/clock.svg'
    svg=QSvgRenderer(str(style))
    image=QImage(256,256,QImage.Format_ARGB32_Premultiplied);image.fill(QColor('transparent'))
    painter=QPainter(image);painter.scale(2,2)
    svg.render(painter,'ClockFace',QRectF(0,0,128,128))
    for part,angle,width,length in [('HourHand',350.5,6,21),('MinuteHand',246,4,28),('SecondHand',162,2,36)]:
        painter.save();painter.translate(64,64);painter.rotate(angle)
        svg.render(painter,part,QRectF(-width/2,-length,width,length));painter.restore()
    svg.render(painter,'HandCenterScrew',QRectF(60,60,8,8))
    painter.end();image.save(str(ROOT/'tools/rendered-analog.png'))

if __name__=='__main__':
    import sys
    night='--night-shift' in sys.argv
    app=QGuiApplication([]);assets(night);view=create_view();view.rootObject().setProperty('nightShift',night)
    def save():
        path=Path('/tmp/scarlet-night-preview.png') if night else ROOT.parent/'Scarlet-Protocol-Plasma-Preview.png'
        assert view.grabWindow().save(str(path));print(path);app.quit()
    QTimer.singleShot(1200,save);app.exec()
