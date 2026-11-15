// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include "motion.h"
#include <QColor>
#include <QImage>
namespace Scarlet {
QImage sprite(Design design, const QColor &color, int glow, int stroke);
}
