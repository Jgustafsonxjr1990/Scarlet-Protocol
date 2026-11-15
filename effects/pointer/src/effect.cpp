// SPDX-License-Identifier: GPL-2.0-or-later
#include "art.h"
#include "settings.h"
#include <effect/effect.h>
#include <effect/effecthandler.h>
#include <scene/imageitem.h>
#include <scene/workspacescene.h>
#ifdef SCARLET_RENDERER_FACTORY
#include <scene/itemrenderer.h>
#endif
#include <QElapsedTimer>
#include <QTimer>
#include <QTransform>
#include <algorithm>
#include <cmath>
#include <deque>
#include <memory>
#include <optional>

namespace KWin {
using namespace Scarlet;
class ScarletPointer final : public Effect
{
    Q_OBJECT
public:
    ScarletPointer()
    {
        clock.start();
        timer.setInterval(16);
        timer.setTimerType(Qt::PreciseTimer);
        connect(&timer,&QTimer::timeout,this,&ScarletPointer::tick);
        connect(effects,&EffectsHandler::mouseChanged,this,&ScarletPointer::mouse);
        connect(effects,&EffectsHandler::screenLockingChanged,this,[this](bool){clear();});
        reconfigure(ReconfigureAll);
    }
    void reconfigure(ReconfigureFlags) override
    {
        clear();
        options=Settings::read(KConfigGroup(effects->config(),QStringLiteral("Effect-scarletpointer")));
        for (int i=0;i<3;++i) clickArt[i]=sprite(options.buttons[i],options.colors[i],options.clickGlow,options.stroke);
        trailArt=sprite(options.trail,options.trailColor,options.trailGlow,100);
    }
    bool isActive() const override {return !clicks.empty() || !trail.empty();}

private:
    struct Mark {
        std::unique_ptr<ImageItem> item;
        Design design;
        QPointF center;
        double width,height,angle,opacity;
        qint64 born;
        int life;
    };
    std::deque<Mark> clicks,trail;
    Settings options;
    std::array<QImage,3> clickArt;
    QImage trailArt;
    QElapsedTimer clock;
    QTimer timer;
    std::optional<Point> anchor;

    void clear()
    {
        timer.stop();
        clicks.clear();
        trail.clear();
        anchor.reset();
    }
    static void place(Mark &m,double t)
    {
        const auto p=pose(m.design,t);
        // Ribbon segments keep their length so adjacent samples meet while the width fades.
        const bool line=m.design==Design::Ribbon || m.design==Design::TwinTrace;
        const double w=m.width*(line ? 1. : p.scale), h=m.height*p.scale;
        m.item->setSize(QSizeF(w,h));
        m.item->setPosition(m.center-QPointF(w/2,h/2));
        QTransform transform;
        transform.translate(w/2,h/2).rotate(m.angle+p.rotation).translate(-w/2,-h/2);
        m.item->setTransform(transform);
        m.item->setOpacity(m.opacity*p.opacity);
    }
    void append(std::deque<Mark> &list, int limit, const QImage &image, Design design,
                const QPointF &center, double width, double height, double angle, int life, double opacity)
    {
        if (int(list.size())>=limit) list.pop_front();
        auto *layer=effects->scene()->overlayItem();
#ifdef SCARLET_RENDERER_FACTORY
        auto node=effects->scene()->renderer()->createImageItem(layer);
#else
        auto node=std::make_unique<ImageItem>(layer);
#endif
        const bool clickLayer = &list == &clicks;
        node->setZ(clickLayer ? 2 : 1);
        node->setImage(image);
        list.push_back({std::move(node),design,center,width,height,angle,opacity,clock.elapsed(),life});
        place(list.back(),0);
        if (!timer.isActive()) timer.start();
    }
    void tick()
    {
        const auto now=clock.elapsed();
        auto animate=[now](std::deque<Mark> &list) {
            while (!list.empty() && now-list.front().born>=list.front().life) list.pop_front();
            for (auto &mark:list) place(mark,double(now-mark.born)/mark.life);
        };
        animate(trail);
        animate(clicks);
        if (!isActive()) timer.stop();
    }
    void mouse(const QPointF &position,const QPointF &old,Qt::MouseButtons buttons,
               Qt::MouseButtons previous,Qt::KeyboardModifiers,Qt::KeyboardModifiers)
    {
        if (effects->isScreenLocked()) return;
        constexpr std::array<Qt::MouseButton,3> keys{Qt::LeftButton,Qt::RightButton,Qt::MiddleButton};
        for (int i=0;i<3;++i) {
            const bool down=buttons.testFlag(keys[i]), wasDown=previous.testFlag(keys[i]);
            if (down==wasDown || options.buttons[i]==Design::Off || options.clickOpacity==0) continue;
            if ((down && options.trigger==1) || (!down && options.trigger==0)) continue;
            append(clicks,24,clickArt[i],options.buttons[i],position,options.clickSize,
                   options.clickSize,0,options.clickLife,options.clickOpacity/100.);
        }
        if (options.trail==Design::Off || !options.trailOpacity || (options.dragOnly && !buttons)) {
            anchor.reset();
            return;
        }
        if (!anchor) anchor=Point{old.x(),old.y()};
        if (position==old) return;
        const auto samples=samplePath(*anchor,{position.x(),position.y()},options.spacing);
        for (const auto &s:samples) {
            const bool ember=options.trail==Design::Embers;
            const QPointF center((s.from.x+s.to.x)/2,(s.from.y+s.to.y)/2);
            const double angle=std::atan2(s.to.y-s.from.y,s.to.x-s.from.x)*180./3.141592653589793;
            append(trail,128,trailArt,options.trail,center,ember ? options.trailWidth : s.distance+.65,
                   options.trailWidth,angle,options.trailLife,options.trailOpacity/100.);
        }
    }
};
KWIN_EFFECT_FACTORY(ScarletPointer, "metadata.json")
} // namespace KWin
#include "effect.moc"
