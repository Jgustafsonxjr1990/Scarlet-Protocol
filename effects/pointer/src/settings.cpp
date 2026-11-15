// SPDX-License-Identifier: GPL-2.0-or-later
#include "settings.h"
#include <algorithm>
namespace Scarlet {
Settings Settings::read(const KConfigGroup &g)
{
    Settings s;
    auto number=[&g](const char *key, int fallback, int low, int high) {
        return std::clamp(g.readEntry(key, fallback), low, high);
    };
    auto color=[&g](const QString &key, const QColor &fallback) {
        const QColor c(g.readEntry(key,fallback.name()));
        return c.isValid() ? c : fallback;
    };
    for (int i=0;i<3;++i) {
        const QString suffix=QString::number(i);
        s.buttons[i]=Design(std::clamp(g.readEntry("Button"+suffix,int(s.buttons[i])),0,4));
        s.colors[i]=color("Color"+suffix,s.colors[i]);
    }
    s.trigger=number("Trigger",s.trigger,0,2);
    s.clickSize=number("ClickSize",s.clickSize,16,160);
    s.clickLife=number("ClickLife",s.clickLife,80,1800);
    s.clickOpacity=number("ClickOpacity",s.clickOpacity,0,100);
    s.clickGlow=number("ClickGlow",s.clickGlow,0,100);
    s.stroke=number("Stroke",s.stroke,40,220);
    const int trail=g.readEntry("Trail",int(s.trail));
    s.trail=trail==0 || (trail>=5 && trail<=7) ? Design(trail) : Design::Ribbon;
    s.trailColor=color("TrailColor",s.trailColor);
    s.dragOnly=g.readEntry("DragOnly",s.dragOnly);
    s.trailWidth=number("TrailWidth",s.trailWidth,3,42);
    s.trailLife=number("TrailLife",s.trailLife,50,1600);
    s.trailOpacity=number("TrailOpacity",s.trailOpacity,0,100);
    s.trailGlow=number("TrailGlow",s.trailGlow,0,100);
    s.spacing=number("Spacing",s.spacing,3,48);
    return s;
}
void Settings::write(KConfigGroup g) const
{
    for (int i=0;i<3;++i) {
        const QString suffix=QString::number(i);
        g.writeEntry("Button"+suffix,int(buttons[i]));
        g.writeEntry("Color"+suffix,colors[i].name());
    }
    g.writeEntry("Trigger",trigger);
    g.writeEntry("ClickSize",clickSize); g.writeEntry("ClickLife",clickLife);
    g.writeEntry("ClickOpacity",clickOpacity); g.writeEntry("ClickGlow",clickGlow); g.writeEntry("Stroke",stroke);
    g.writeEntry("Trail",int(trail)); g.writeEntry("TrailColor",trailColor.name());
    g.writeEntry("DragOnly",dragOnly); g.writeEntry("TrailWidth",trailWidth); g.writeEntry("TrailLife",trailLife);
    g.writeEntry("TrailOpacity",trailOpacity); g.writeEntry("TrailGlow",trailGlow); g.writeEntry("Spacing",spacing);
    g.sync();
}
}
