// SPDX-License-Identifier: GPL-2.0-or-later
#include "art.h"
#include "settings.h"
#include <KCModule>
#include <KPluginFactory>
#include <KSharedConfig>
#include <QCheckBox>
#include <QColorDialog>
#include <QComboBox>
#include <QDBusConnection>
#include <QDBusMessage>
#include <QElapsedTimer>
#include <QEnterEvent>
#include <QIcon>
#include <QPixmap>
#include <QFormLayout>
#include <QLabel>
#include <QMouseEvent>
#include <QPainter>
#include <QPushButton>
#include <QSpinBox>
#include <QTabWidget>
#include <QTimer>
#include <QVBoxLayout>
#include <array>
#include <cmath>
#include <deque>
#include <functional>
#include <optional>
#include <utility>

namespace Scarlet {
namespace {
const std::array<QString,8> names{QStringLiteral("Off"),QStringLiteral("Split Ring"),QStringLiteral("Reticle"),
    QStringLiteral("Arc Sparks"),QStringLiteral("Nanook’s Paw"),QStringLiteral("Ribbon"),
    QStringLiteral("Twin Trace"),QStringLiteral("Embers")};

class Preview final : public QWidget {
public:
    explicit Preview(QWidget *parent): QWidget(parent) {
        setMouseTracking(true);
        setMinimumHeight(126);
        clock.start();
        timer.setInterval(16);
        connect(&timer,&QTimer::timeout,this,[this] {
            const auto now=clock.elapsed();
            std::erase_if(marks,[now](const Mark &m){return now-m.start>=m.life;});
            update();
            if (marks.empty()) timer.stop();
        });
    }
    void apply(const Settings &value) {
        settings=value; marks.clear(); anchor.reset(); timer.stop();
        for (int i=0;i<3;++i) clicks[i]=sprite(value.buttons[i],value.colors[i],value.clickGlow,value.stroke);
        trail=sprite(value.trail,value.trailColor,value.trailGlow,100);
        update();
    }
protected:
    void enterEvent(QEnterEvent *event) override { anchor.reset(); QWidget::enterEvent(event); }
    void leaveEvent(QEvent *event) override { anchor.reset(); QWidget::leaveEvent(event); }
    void mousePressEvent(QMouseEvent *e) override { if (settings.trigger!=1) hit(e); }
    void mouseReleaseEvent(QMouseEvent *e) override { if (settings.trigger!=0) hit(e); }
    void mouseDoubleClickEvent(QMouseEvent *e) override { mousePressEvent(e); }
    void mouseMoveEvent(QMouseEvent *e) override {
        Point p{e->position().x(),e->position().y()};
        if (settings.trail==Design::Off || (settings.dragOnly && !e->buttons()) || !settings.trailOpacity) {anchor.reset(); return;}
        if (!anchor) anchor=p;
        for (const auto &s:samplePath(*anchor,p,settings.spacing)) {
            const double angle=std::atan2(s.to.y-s.from.y,s.to.x-s.from.x)*180./3.141592653589793;
            add(trail, settings.trail, QPointF((s.to.x+s.from.x)/2,(s.to.y+s.from.y)/2),
                QSizeF(settings.trail==Design::Embers ? settings.trailWidth : s.distance+.65, settings.trailWidth),
                angle,settings.trailLife,settings.trailOpacity);
        }
    }
    void paintEvent(QPaintEvent *) override {
        QPainter p(this);
        p.setRenderHints(QPainter::Antialiasing|QPainter::SmoothPixmapTransform);
        p.setPen(QColor("#51313f")); p.setBrush(QColor("#101116"));
        p.drawRoundedRect(QRectF(rect()).adjusted(1,1,-1,-1),12,12);
        p.setPen(QColor("#c295a7")); p.drawText(rect().adjusted(12,8,-12,-7),Qt::AlignTop|Qt::AlignLeft,tr("Click or move here to preview"));
        for (bool clickLayer:{false,true}) for (const auto &m:marks) {
            const bool click=m.design<=Design::Paw;
            if (click!=clickLayer) continue;
            const Pose a=pose(m.design,double(clock.elapsed()-m.start)/m.life);
            const bool line=m.design==Design::Ribbon || m.design==Design::TwinTrace;
            const double w=m.size.width()*(line ? 1. : a.scale),h=m.size.height()*a.scale;
            p.save(); p.translate(m.pos); p.rotate(m.angle+a.rotation); p.setOpacity(a.opacity*m.opacity);
            p.drawImage(QRectF(-w/2,-h/2,w,h),m.image); p.restore();
        }
    }
private:
    struct Mark {QImage image; Design design; QPointF pos; QSizeF size; double angle; int life; double opacity; qint64 start;};
    Settings settings;
    std::array<QImage,3> clicks;
    QImage trail;
    std::deque<Mark> marks;
    std::optional<Point> anchor;
    QElapsedTimer clock;
    QTimer timer;
    void add(const QImage &img,Design design,QPointF pt,QSizeF size,double angle,int life,int opacity) {
        if (marks.size()>=152) marks.pop_front();
        marks.push_back({img,design,pt,size,angle,life,opacity/100.,clock.elapsed()});
        if (!timer.isActive()) timer.start();
        update();
    }
    void hit(QMouseEvent *e) {
        constexpr std::array<Qt::MouseButton,3> map{Qt::LeftButton,Qt::RightButton,Qt::MiddleButton};
        for (int i=0;i<3;++i) {
            if (map[i]==e->button() && settings.buttons[i]!=Design::Off && settings.clickOpacity)
                add(clicks[i],settings.buttons[i],e->position(),QSizeF(settings.clickSize,settings.clickSize),0,settings.clickLife,settings.clickOpacity);
        }
    }
};
}

class PointerConfig final : public KCModule {
    Q_OBJECT
public:
    PointerConfig(QObject *parent,const KPluginMetaData &data):KCModule(parent,data) {
        auto *layout=new QVBoxLayout(widget());
        preview=new Preview(widget()); layout->addWidget(preview);
        auto *tabs=new QTabWidget(widget()); layout->addWidget(tabs);
        auto page=[tabs](const QString &name) {
            auto *w=new QWidget(tabs); tabs->addTab(w,name);
            return new QFormLayout(w);
        };
        auto *bindings=page(tr("Buttons"));
        const std::array<QString,3> labels{tr("Left"),tr("Right"),tr("Middle")};
        for (int i=0;i<3;++i) {
            bindDesign(bindings,labels[i],{Design::Off,Design::SplitRing,Design::Reticle,Design::ArcSparks,Design::Paw},&values.buttons[i]);
            bindColor(bindings,labels[i]+tr(" color"),&values.colors[i]);
        }
        auto *motion=page(tr("Click animation"));
        auto *when=new QComboBox(widget());
        when->addItems({tr("Press"),tr("Release"),tr("Press and release")}); motion->addRow(tr("Trigger"),when);
        connect(when,&QComboBox::currentIndexChanged,this,[this](int i){values.trigger=i; changed();});
        refreshers.push_back([this,when]{when->setCurrentIndex(values.trigger);});
        number(motion,tr("Size"),&values.clickSize,16,160," px");
        number(motion,tr("Duration"),&values.clickLife,80,1800," ms");
        number(motion,tr("Opacity"),&values.clickOpacity,0,100," %");
        number(motion,tr("Glow"),&values.clickGlow,0,100," %");
        number(motion,tr("Stroke weight"),&values.stroke,40,220," %");
        auto *trail=page(tr("Trail"));
        bindDesign(trail,tr("Style"),{Design::Off,Design::Ribbon,Design::TwinTrace,Design::Embers},&values.trail);
        bindColor(trail,tr("Color"),&values.trailColor);
        auto *drag=new QCheckBox(tr("Only while dragging"),widget()); trail->addRow(drag);
        connect(drag,&QCheckBox::toggled,this,[this](bool on){values.dragOnly=on; changed();});
        refreshers.push_back([this,drag]{drag->setChecked(values.dragOnly);});
        number(trail,tr("Width"),&values.trailWidth,3,42," px");
        number(trail,tr("Fade time"),&values.trailLife,50,1600," ms");
        number(trail,tr("Spacing"),&values.spacing,3,48," px");
        number(trail,tr("Opacity"),&values.trailOpacity,0,100," %");
        number(trail,tr("Glow"),&values.trailGlow,0,100," %");
        load();
    }
    void load() override {
        auto config=KSharedConfig::openConfig(QStringLiteral("kwinrc"));
        config->reparseConfiguration();
        saved=Settings::read(KConfigGroup(config,QStringLiteral("Effect-scarletpointer")));
        values=saved; refresh();
    }
    void defaults() override { values=Settings{}; refresh(); }
    void save() override {
        auto config=KSharedConfig::openConfig(QStringLiteral("kwinrc"));
        values.write(KConfigGroup(config,QStringLiteral("Effect-scarletpointer")));
        saved=values; changed();
        auto message=QDBusMessage::createMethodCall(QStringLiteral("org.kde.KWin"),QStringLiteral("/Effects"),
                QStringLiteral("org.kde.kwin.Effects"),QStringLiteral("reconfigureEffect"));
        message<<QStringLiteral("scarletpointer");
        QDBusConnection::sessionBus().send(message);
    }
private:
    Settings values,saved;
    Preview *preview=nullptr;
    bool updating=false;
    std::vector<std::function<void()>> refreshers;
    void changed() {
        if (updating) return;
        preview->apply(values);
        setNeedsSave(values!=saved);
        setRepresentsDefaults(values==Settings{});
    }
    void refresh() {
        updating=true;
        for (const auto &fn:refreshers) fn();
        updating=false; changed();
    }
    void number(QFormLayout *form,const QString &label,int *field,int low,int high,const QString &suffix) {
        auto *box=new QSpinBox(widget()); box->setRange(low,high); box->setSuffix(suffix);
        form->addRow(label,box);
        connect(box,&QSpinBox::valueChanged,this,[this,field](int v){*field=v; changed();});
        refreshers.push_back([field,box]{box->setValue(*field);});
    }
    void bindDesign(QFormLayout *form,const QString &label,std::initializer_list<Design> choices,Design *field) {
        auto *box=new QComboBox(widget());
        for (Design d:choices) box->addItem(names[int(d)],int(d));
        form->addRow(label,box);
        connect(box,&QComboBox::currentIndexChanged,this,[this,field,box](int){*field=Design(box->currentData().toInt()); changed();});
        refreshers.push_back([field,box]{box->setCurrentIndex(box->findData(int(*field)));});
    }
    void bindColor(QFormLayout *form,const QString &label,QColor *field) {
        auto *button=new QPushButton(widget()); form->addRow(label,button);
        auto swatch=[field,button]{
            QPixmap pix(20,14); pix.fill(*field); button->setIcon(QIcon(pix));
            button->setText(field->name().toUpper());
        };
        connect(button,&QPushButton::clicked,this,[this,field,label,swatch] {
            const QColor picked=QColorDialog::getColor(*field,widget(),label);
            if (picked.isValid()) { *field=picked; swatch(); changed(); }
        });
        refreshers.push_back(swatch);
    }
};
}
K_PLUGIN_CLASS(Scarlet::PointerConfig)
#include "config.moc"
