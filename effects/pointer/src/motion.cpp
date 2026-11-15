// SPDX-License-Identifier: GPL-2.0-or-later
#include "motion.h"
#include <algorithm>
#include <cmath>
#include <utility>

namespace Scarlet {
namespace {
constexpr double pi = 3.14159265358979323846;
Point polar(double radius, double angle)
{
    const double a = angle * pi / 180;
    return {radius * std::cos(a), radius * std::sin(a)};
}
std::vector<Point> arc(double radius, double start, double span)
{
    const int count = std::max(3, int(std::ceil(std::abs(span) / 5)));
    std::vector<Point> points;
    for (int i = 0; i <= count; ++i) points.push_back(polar(radius, start + span * i / count));
    return points;
}
std::vector<Point> rotate(std::vector<Point> points, double angle)
{
    const Point axis = polar(1, angle);
    for (Point &p : points) p = {p.x * axis.x - p.y * axis.y, p.x * axis.y + p.y * axis.x};
    return points;
}
void ellipse(Art &art, Point center, double rx, double ry, double tilt)
{
    auto points = arc(1, 0, 360);
    for (Point &p : points) { p.x *= rx; p.y *= ry; }
    points = rotate(std::move(points), tilt);
    for (Point &p : points) { p.x += center.x; p.y += center.y; }
    art.push_back({std::move(points), .020, true, 1});
}
void cubic(std::vector<Point> &out, Point a, Point b, Point end)
{
    const Point start = out.back();
    for (int i = 1; i <= 12; ++i) {
        const double t = i / 12., u = 1 - t;
        out.push_back({u*u*u*start.x + 3*u*u*t*a.x + 3*u*t*t*b.x + t*t*t*end.x,
                       u*u*u*start.y + 3*u*u*t*a.y + 3*u*t*t*b.y + t*t*t*end.y});
    }
}
double easeOut(double t) { return 1 - std::pow(1 - t, 3); }
}

Art artwork(Design d)
{
    Art result;
    if (d == Design::SplitRing) {
        for (int n = 0; n < 2; ++n) {
            result.push_back({arc(.70, -73+n*180, 132), .066, false, 1});
            result.push_back({arc(.54, -49+n*180, 46), .023, false, .72});
            result.push_back({{polar(.64, 75+n*180), polar(.81, 75+n*180)}, .036, false, .92});
        }
    } else if (d == Design::Reticle) {
        for (int n = 0; n < 4; ++n) {
            result.push_back({rotate({{.24,-.60},{.49,-.60},{.60,-.49},{.60,-.24}}, n*90), .065, false, 1});
            result.push_back({rotate({{.61,0},{.76,0}}, n*90), .035, false, .64});
        }
        result.push_back({arc(.11, 0, 360), .028, false, .8});
    } else if (d == Design::ArcSparks) {
        for (int n = 0; n < 4; ++n) {
            const double angle = 18+n*90;
            result.push_back({rotate({{.22,0},{.50,-.12},{.80,-.085},{.51,.03},{.58,.06}},angle), .035, true, 1});
            result.push_back({rotate({{.52,.14},{.72,.15}},angle), .029, false, .80});
        }
    } else if (d == Design::Paw) {
        std::vector<Point> pad{{0,-.09}};
        cubic(pad,{.15,-.09},{.25,.09},{.37,.23});
        cubic(pad,{.55,.48},{.30,.64},{.11,.54});
        cubic(pad,{.02,.49},{-.02,.49},{-.11,.54});
        cubic(pad,{-.30,.64},{-.55,.48},{-.37,.23});
        cubic(pad,{-.25,.09},{-.15,-.09},{0,-.09});
        result.push_back({std::move(pad), .027, true, 1});
        ellipse(result,{-.47,-.11},.115,.19,-31);
        ellipse(result,{-.18,-.41},.13,.225,-14);
        ellipse(result,{.18,-.41},.13,.225,14);
        ellipse(result,{.47,-.11},.115,.19,31);
        result.push_back({arc(.77, 23, 42), .026, false, .60});
        result.push_back({arc(.77, 203, 42), .026, false, .60});
    } else if (d == Design::Ribbon) {
        result.push_back({{{-1,0},{1,0}}, .28, false, 1});
    } else if (d == Design::TwinTrace) {
        for (double y : {-.34,.34}) result.push_back({{{-1,y},{1,y}}, .14, false, y<0 ? 1. : .75});
    } else if (d == Design::Embers) {
        result.push_back({{{-.76,0},{0,-.36},{.76,0},{0,.36}}, .050, true, 1});
    }
    return result;
}

Pose pose(Design d, double progress)
{
    const double t = std::clamp(progress, 0., 1.);
    const double e = easeOut(t);
    double opacity = 1 - std::pow(t, 1.8);
    if (d == Design::SplitRing) return {.30+.84*e, 55*e, opacity};
    if (d == Design::Reticle) return {1.18-.66*e, -12*(1-e), opacity};
    if (d == Design::ArcSparks) return {.23+.97*e, 39*e, opacity};
    if (d == Design::Paw) {
        const double stamp = t < .23 ? .64+.41*easeOut(t/.23) : 1.05-.12*easeOut((t-.23)/.77);
        return {stamp, -10+5*e, 1-std::pow(t, 3.)};
    }
    if (d == Design::Off) return {0,0,0};
    return {1-.55*t, 0, std::pow(1-t,1.35)};
}

std::vector<Sample> samplePath(Point &anchor, Point target, double spacing)
{
    std::vector<Sample> samples;
    if (!std::isfinite(spacing) || spacing < 1) return samples;
    double dx = target.x-anchor.x, dy=target.y-anchor.y;
    const double length=std::hypot(dx,dy);
    if (!std::isfinite(length) || length>320) { anchor=target; return samples; }
    if (length<spacing) return samples;
    dx *= spacing/length;
    dy *= spacing/length;
    const int n=int(length/spacing);
    for (int i=0;i<n;++i) {
        const Point end{anchor.x+dx,anchor.y+dy};
        samples.push_back({anchor,end,spacing});
        anchor=end;
    }
    return samples;
}
}
