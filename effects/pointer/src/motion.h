// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <vector>

namespace Scarlet {
enum class Design { Off, SplitRing, Reticle, ArcSparks, Paw, Ribbon, TwinTrace, Embers };
struct Point { double x, y; };
struct Shape {
    std::vector<Point> points;
    double width;
    bool filled;
    double brightness;
};
using Art = std::vector<Shape>;

struct Pose { double scale, rotation, opacity; };
Art artwork(Design design);
Pose pose(Design design, double progress);
struct Sample { Point from, to; double distance; };
// Each segment has equal length, even when pointer event rates vary.
std::vector<Sample> samplePath(Point &anchor, Point target, double spacing);
}
