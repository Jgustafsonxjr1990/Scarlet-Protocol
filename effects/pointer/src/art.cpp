// SPDX-License-Identifier: GPL-2.0-or-later
#include "art.h"
#include <algorithm>
#include <QPainter>
#include <QPainterPath>

namespace Scarlet {
QImage sprite(Design design, const QColor &color, int glow, int stroke)
{
    constexpr int resolution=256;
    QImage image(resolution,resolution,QImage::Format_ARGB32_Premultiplied);
    image.fill(Qt::transparent);
    QPainter painter(&image);
    painter.setRenderHint(QPainter::Antialiasing);
    painter.translate(resolution/2,resolution/2);
    painter.scale(resolution/2,resolution/2);
    for (const auto &shape: artwork(design)) {
        QPainterPath path;
        path.moveTo(shape.points.front().x,shape.points.front().y);
        for (size_t i=1;i<shape.points.size();++i) path.lineTo(shape.points[i].x,shape.points[i].y);
        if (shape.filled) path.closeSubpath();
        auto line=[&](QColor ink, double width, double alpha) {
            ink.setAlphaF(std::clamp(alpha*shape.brightness,0.,1.));
            painter.strokePath(path,QPen(ink,width,Qt::SolidLine,Qt::RoundCap,Qt::RoundJoin));
        };
        const double width=shape.width*stroke/100.;
        if (glow) {
            for (int band=4;band>0;--band)
                line(color,width*(1+band*1.30),(.08+(4-band)*.035)*glow/100.);
        }
        if (shape.filled) {
            QColor fill=color;
            fill.setAlphaF(.66);
            painter.fillPath(path,fill);
        }
        line(color,width,.97);
        QColor filament=QColor::fromRgbF(.63+color.redF()*.37,.63+color.greenF()*.37,.63+color.blueF()*.37);
        line(filament,width*.28,.92);
    }
    return image;
}
}
