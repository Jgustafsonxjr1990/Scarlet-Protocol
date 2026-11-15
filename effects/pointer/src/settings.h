// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include "motion.h"
#include <KConfigGroup>
#include <QColor>
#include <array>

namespace Scarlet {
struct Settings {
    // Binding order is left, right, middle.
    std::array<Design,3> buttons{Design::SplitRing, Design::Reticle, Design::ArcSparks};
    std::array<QColor,3> colors{QColor("#ff265a"), QColor("#e41951"), QColor("#ff6384")};
    int trigger=0;  // press, release, both
    int clickSize=64, clickLife=420, clickOpacity=90, clickGlow=65, stroke=100;
    Design trail=Design::Ribbon;
    QColor trailColor{"#f12157"};
    bool dragOnly=false;
    int trailWidth=11, trailLife=210, trailOpacity=68, trailGlow=48, spacing=8;
    static Settings read(const KConfigGroup &group);
    void write(KConfigGroup group) const;
    bool operator==(const Settings &) const = default;
};
}
