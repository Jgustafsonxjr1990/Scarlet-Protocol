#!/usr/bin/env python3
"""Generate the Scarlet Protocol Plasma 6 artwork with reproducible primitives."""
from __future__ import annotations

import math
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
STYLE = ROOT / "plasma-style/ScarletProtocolPlasma"
AURORAE = ROOT / "aurorae/ScarletProtocolGlobal"
WALL = ROOT / "wallpapers/ScarletProtocolWall/contents/images"
PREV = ROOT / "look-and-feel/ScarletProtocolGlobal/contents/previews"
ICONS = ROOT / "icons/ScarletProtocolIcons"
FONT_DIR = ROOT / "tools/fonts"

INK = "#101116"
INK2 = "#171318"
RED = "#E41951"
HOT = "#FF0051"
TEXT = "#E8DCE0"


def svg(width: int, height: int, body: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}">\n{body}\n</svg>\n')


def write(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")


def frame(prefix: str, x: int, y: int, *, fill: str, rim: str,
          top: str | None = None, bottom: str | None = None,
          width: int = 48, height: int = 40, margin: int = 12) -> str:
    """Nine separate SVG pieces with real transparent rounded corner pixels."""
    w, h, m = width, height, margin
    if not 2 * m < min(w, h):
        raise ValueError("Nine-patch margins must leave a stretchable center")
    prefix = f"{prefix}-" if prefix else ""
    top = top or rim
    bottom = bottom or rim
    parts = [
        ("topleft", 0, 0, m, m), ("top", m, 0, w-2*m, m),
        ("topright", w-m, 0, m, m), ("left", 0, m, m, h-2*m),
        ("center", m, m, w-2*m, h-2*m), ("right", w-m, m, m, h-2*m),
        ("bottomleft", 0, h-m, m, m), ("bottom", m, h-m, w-2*m, m),
        ("bottomright", w-m, h-m, m, m),
    ]
    out = []
    for name, px, py, pw, ph in parts:
        if name == "topleft":
            face = f'M {m} 0 L {m} {m} L 0 {m} A {m} {m} 0 0 1 {m} 0 Z'
            edge = f'M 0 {m} A {m} {m} 0 0 1 {m} 0'
        elif name == "topright":
            face = f'M 0 0 L 0 {m} L {m} {m} A {m} {m} 0 0 0 0 0 Z'
            edge = f'M 0 0 A {m} {m} 0 0 1 {m} {m}'
        elif name == "bottomleft":
            face = f'M 0 0 L {m} 0 L {m} {m} A {m} {m} 0 0 1 0 0 Z'
            edge = f'M 0 0 A {m} {m} 0 0 0 {m} {m}'
        elif name == "bottomright":
            face = f'M 0 0 L {m} 0 A {m} {m} 0 0 1 0 {m} Z'
            edge = f'M {m} 0 A {m} {m} 0 0 1 0 {m}'
        else:
            face = f'M 0 0 H {pw} V {ph} H 0 Z'
            edge = None
        layers = [f'<path d="{face}" fill="{fill}"/>']
        if edge:
            color = top if name.startswith("top") else bottom
            # The second wider stroke is a gentle inner corona, clipped to
            # the same corner tile; the outer corner stays transparent.
            layers += [f'<path d="{edge}" fill="none" stroke="{color}" stroke-width="3" opacity=".25"/>',
                       f'<path d="{edge}" fill="none" stroke="{color}" stroke-width="1.6"/>']
        elif name == "top":
            layers += [f'<path d="M 0 .7 H {pw}" stroke="{top}" stroke-width="1.4"/>',
                       f'<path d="M 0 2 H {pw}" stroke="{top}" stroke-width="2" opacity=".14"/>']
        elif name == "bottom":
            layers += [f'<path d="M 0 {ph-.7} H {pw}" stroke="{bottom}" stroke-width="1.4"/>',
                       f'<path d="M 0 {ph-2} H {pw}" stroke="{bottom}" stroke-width="2" opacity=".14"/>']
        elif name == "left":
            layers += [f'<path d="M .7 0 V {ph}" stroke="{rim}" stroke-width="1.4"/>']
        elif name == "right":
            layers += [f'<path d="M {pw-.7} 0 V {ph}" stroke="{rim}" stroke-width="1.4"/>']
        out.append(f'<g id="{prefix}{name}" transform="translate({x+px},{y+py})">'
                   + "".join(layers) + "</g>")
    return "\n".join(out)


def frames_file(rel: str, states: list[tuple[str, str, str]],
                *, width: int = 48, height: int = 40, margin: int = 12) -> None:
    body = []
    for i, (prefix, fill, rim) in enumerate(states):
        body.append(frame(prefix, (i % 5) * (width + 8), (i // 5) * (height + 8),
                          fill=fill, rim=rim, width=width, height=height, margin=margin))
    write(STYLE / rel, svg(5*(width+8), math.ceil(len(states)/5)*(height+8), "\n".join(body)))


def build_plasma_style() -> None:
    weak = "#542138"
    medium = "#A21B45"
    pale = "#802345"
    frames_file("widgets/panel-background.svg", [("", INK, medium)], margin=17)
    frames_file("widgets/background.svg", [("", INK2, pale)], margin=16)
    frames_file("widgets/translucentbackground.svg", [("", INK2, pale)], margin=16)
    frames_file("dialogs/background.svg", [("", INK, RED)], margin=16)
    frames_file("widgets/tooltip.svg", [("", "#1B141C", RED)], margin=15)
    frames_file("widgets/toolbar.svg", [("", INK, medium)])
    frames_file("widgets/button.svg", [
        ("normal", "#1B141B", weak), ("hover", "#45172D", HOT),
        ("pressed", "#781438", HOT), ("focus", "#27141E", RED),
        ("toolbutton-hover", "#45172D", HOT),
        ("toolbutton-focus", "#27141E", RED),
        ("toolbutton-pressed", "#781438", HOT),
    ])
    frames_file("widgets/lineedit.svg", [
        ("base", INK, weak), ("hover", INK, RED),
        ("focus", INK, HOT),
    ])
    frames_file("widgets/tasks.svg", [
        ("normal", INK, weak), ("focus", "#381423", HOT),
        ("hover", "#341424", RED), ("attention", "#5C172F", HOT),
        ("minimized", "#141217", "#451A2D"),
    ])
    frames_file("widgets/viewitem.svg", [
        ("normal", INK, weak), ("hover", "#311823", RED),
        ("selected", "#671634", HOT),
        ("selected+hover", "#921838", HOT),
    ])
    frames_file("widgets/plasmoidheading.svg", [
        ("header", "#22141E", RED), ("footer", "#22141E", RED),
    ])
    frames_file("widgets/listitem.svg", [
        ("normal", INK, weak), ("hover", "#3C1728", RED),
        ("pressed", "#701635", HOT), ("section", INK2, pale),
    ])
    frames_file("widgets/menubaritem.svg", [
        ("normal", INK, weak), ("hover", "#3C1728", RED),
        ("pressed", "#701635", HOT),
    ])
    frames_file("widgets/pager.svg", [
        ("normal", INK, weak), ("hover", "#3C1728", RED),
        ("active", "#701635", HOT),
    ])
    frames_file("widgets/tabbar.svg", [
        (f"{side}-active-tab", "#411525", HOT)
        for side in ("north", "south", "east", "west")
    ])
    frames_file("widgets/glowbar.svg", [("", "#25121F", HOT)], width=48, height=20, margin=8)
    frames_file("widgets/scrollwidget.svg", [("border", INK, weak)])
    frames_file("widgets/frame.svg", [
        ("sunken", "#121117", "#64203A"),
        ("plain", "#171318", pale),
        ("raised", "#21131B", RED),
    ])
    frames_file("widgets/bar_meter_horizontal.svg", [
        ("background", INK, weak), ("bar-active", "#B51A47", HOT),
        ("bar-inactive", "#221820", "#4F2035"),
    ], height=18, margin=7)
    frames_file("widgets/bar_meter_vertical.svg", [
        ("background", INK, weak), ("bar-active", "#B51A47", HOT),
        ("bar-inactive", "#221820", "#4F2035"),
    ], width=18, height=48, margin=7)
    extra_controls()
    # Plasma Style colors control text and glyphs in applets as well as the SVGs.
    shutil.copy2(ROOT / "color-schemes/ScarletProtocol.colors", STYLE / "colors")
    plasmarc = STYLE / "plasmarc"
    content = plasmarc.read_text()
    content = content.split("\n[Wallpaper]\n", 1)[0].rstrip() + "\n"
    plasmarc.write_text(content +
                        "\n[Wallpaper]\n"
                        "defaultWallpaperTheme=ScarletProtocolWall\n"
                        "defaultFileSuffix=.png\n"
                        "defaultWidth=1920\n"
                        "defaultHeight=1200\n")


def extra_controls() -> None:
    """Detailed indicators used by common Plasma settings and popups."""
    arrows = []
    for i, (name, path) in enumerate((
        ("up", "M6 16L12 8L18 16"),
        ("right", "M8 6L16 12L8 18"),
        ("down", "M6 8L12 16L18 8"),
        ("left", "M16 6L8 12L16 18"),
    )):
        arrows.append(f'<path id="{name}-arrow" transform="translate({i*26},0)" '
                      f'd="{path}" fill="none" stroke="{RED}" '
                      f'stroke-width="2.5" stroke-linejoin="round"/>')
    write(STYLE / "widgets/arrows.svg", svg(104, 24, "\n".join(arrows)))
    write(STYLE / "widgets/line.svg", svg(100, 100,
        '<rect id="horizontal-line" x="0" y="12" width="100" height="1" fill="#8F2245"/>'
        '<rect id="vertical-line" x="12" y="24" width="1" height="76" fill="#8F2245"/>'))
    write(STYLE / "widgets/checkmarks.svg", svg(48, 24,
        '<path id="checkbox" d="M4 12L9 17L20 6" fill="none" '
        'stroke="#FF0051" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
        '<circle id="radiobutton" cx="36" cy="12" r="5" fill="#FF0051"/>'))
    radios = []
    for i, (name, rim, fill) in enumerate((
        ("normal", "#79223E", INK), ("checked", HOT, "#481629"),
        ("hover", HOT, "#2F1724"), ("focus", RED, INK),
    )):
        radios.append(f'<circle id="{name}" cx="{12+i*28}" cy="12" r="9" '
                      f'fill="{fill}" stroke="{rim}" stroke-width="2"/>')
    radios.append('<circle id="symbol" cx="12" cy="39" r="5" fill="#FF0051"/>')
    radios.append('<rect id="hint-size" x="34" y="30" width="20" height="20" fill="none"/>')
    write(STYLE / "widgets/radiobutton.svg", svg(112, 54, "\n".join(radios)))

    slider = frame("groove", 0, 0, fill=INK, rim="#6A2039", width=46, height=18, margin=7)
    slider += frame("groove-highlight", 54, 0, fill="#9C1942", rim=HOT,
                    width=46, height=18, margin=7)
    for name, x, y, col in (
        ("horizontal-slider-handle", 6, 30, RED),
        ("horizontal-slider-hover", 36, 30, HOT),
        ("horizontal-slider-focus", 66, 30, HOT),
        ("vertical-slider-handle", 6, 58, RED),
        ("vertical-slider-hover", 36, 58, HOT),
        ("vertical-slider-focus", 66, 58, HOT),
    ):
        slider += (f'<circle id="{name}" cx="{x+11}" cy="{y+11}" r="10" '
                   f'fill="#21121C" stroke="{col}" stroke-width="2"/>')
    write(STYLE / "widgets/slider.svg", svg(104, 86, slider))

    # Overlay assets for clickable applet toolbar icons.
    controls = []
    for i, (name, fill, edge) in enumerate((
        ("normal", INK, "#61213A"), ("hover", "#4B152A", HOT),
        ("pressed", "#9C1942", HOT), ("focus", "#391625", RED),
    )):
        controls.append(f'<rect id="{name}" x="{i*30}" y="0" width="24" height="24" '
                        f'rx="10" fill="{fill}" stroke="{edge}" stroke-width="2"/>')
    write(STYLE / "widgets/actionbutton.svg", svg(120, 24, "\n".join(controls)))

    # Desktop edit mode, icon actions and widget chrome have their own Plasma
    # SVGs. Keep their geometry rounded and their accents in the same palette.
    overlays = []
    paths = {"add": "M9 5v8M5 9h8", "remove": "M5 9h8",
             "open": "M5 7l4 4 4-4"}
    for row, (action, path) in enumerate(paths.items()):
        for col, (state, fill, rim) in enumerate((
            ("normal", "#21141C", "#A1264A"),
            ("hover", "#57162C", HOT),
            ("pressed", "#8A1639", HOT),
        )):
            x, y = col*26, row*26
            overlays.append(f'<g id="{action}-{state}" transform="translate({x},{y})">'
                f'<rect x="1" y="1" width="18" height="18" rx="8" fill="{fill}" stroke="{rim}"/>'
                f'<path d="{path}" fill="none" stroke="{HOT if state != "normal" else TEXT}" '
                'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></g>')
    write(STYLE / "widgets/action-overlays.svg", svg(78, 78, "\n".join(overlays)))

    edit_paths = {
        "close": "M5 5l12 12m0-12L5 17", "configure": "M11 3v3m0 10v3M3 11h3m10 0h3M11 8a3 3 0 1 0 0 6a3 3 0 0 0 0-6",
        "move": "M11 3v16M3 11h16m-8-8-3 3m3-3 3 3m-11 5 3-3m-3 3 3 3m8-3 3-3m-3 3-3 3m-3 5-3-3m3 3 3-3",
        "size-vertical": "M11 3v16m-4-12 4-4 4 4m-8 8 4 4 4-4",
        "size-horizontal": "M3 11h16M7 7l-4 4 4 4m8-8 4 4-4 4",
        "size-diagonal-tl2br": "M4 4l14 14M4 9V4h5m9 9v5h-5",
        "size-diagonal-tr2bl": "M18 4 4 18m9-14h5v5M4 13v5h5",
        "rotate": "M17 6a8 8 0 1 0 2 8M17 3v4h-4",
        "help": "M8 8a3.5 3.5 0 1 1 5 3.2c-2 1-2 2-2 3m0 3v.3",
        "maximize": "M5 16l6-9 6 9", "unmaximize": "M5 8l6 9 6-9",
        "collapse": "M5 8l6 7 6-7", "restore": "M5 15l6-7 6 7",
        "status": "M11 3v10m0 4v1M4 4h14v14H4z",
        "return-to-source": "M4 9a7 7 0 1 1 2 7M4 4v5h5",
        "add": "M11 4v14M4 11h14", "remove": "M4 11h14",
        "delete": "M5 6h12M8 6V4h6v2M7 8l1 10h6l1-10",
        "showbackground": "M3 4h16v14H3zM5 15l4-5 3 3 3-4 2 3",
        "filter": "M4 5h14l-5 6v6l-4 2v-8z",
        "menu": "M4 6h14M4 11h14M4 16h14",
    }
    icons = []
    for i, (name, path) in enumerate(edit_paths.items()):
        x, y = (i % 7)*28, (i // 7)*28
        color = "#FF315B" if name in ("close", "delete") else RED
        icons.append(f'<g id="{name}" transform="translate({x},{y})">'
            f'<rect x="1" y="1" width="20" height="20" rx="8" fill="#1B141B" stroke="#65213B"/>'
            f'<path d="{path}" fill="none" stroke="{color}" stroke-width="1.6" '
            'stroke-linecap="round" stroke-linejoin="round"/></g>')
    write(STYLE / "widgets/configuration-icons.svg", svg(196, 84, "\n".join(icons)))

    containment = []
    for i, direction in enumerate(("north", "east", "south", "west")):
        for j, slider_name in enumerate(("", "maxslider", "minslider", "offsetslider")):
            pre = direction + ("-" + slider_name if slider_name else "")
            containment.append(frame(pre, j*54, i*46, fill="#1C131B",
                                     rim=HOT if slider_name else "#7D2140",
                                     width=46, height=38, margin=12))
    containment.append('<path id="horizontal-centerindicator" d="M0 193h20" stroke="#FF0051" stroke-width="2"/>')
    containment.append('<path id="vertical-centerindicator" d="M29 187v20" stroke="#FF0051" stroke-width="2"/>')
    write(STYLE / "widgets/containment-controls.svg", svg(216, 208, "\n".join(containment)))

    note_colors = {"white": "#CCC0C5", "black": "#1B141B", "red": "#6E1D36",
        "orange": "#6A3627", "yellow": "#6D592C", "green": "#285847",
        "blue": "#273E5E", "pink": "#66334E", "translucent": "#321621",
        "translucent-light": "#694051"}
    notes = []
    for i, (name, fill) in enumerate(note_colors.items()):
        x, y = (i % 5)*72, (i // 5)*72
        notes.append(f'<g id="{name}-notes" transform="translate({x},{y})">'
            f'<rect x="2" y="2" width="64" height="64" rx="14" fill="{fill}" '
            'stroke="#E41951" stroke-width="1.4"/>'
            '<path d="M12 17h30M12 24h42" fill="none" stroke="#E41951" opacity=".45"/>'
            '</g>')
    write(STYLE / "widgets/notes.svg", svg(360, 144, "\n".join(notes)))

    # Plasma scales and rotates these individual clock parts itself.
    clock_parts = [
        '<g id="ClockFace"><circle cx="64" cy="64" r="59" fill="#121117" stroke="#E41951" stroke-width="2"/><circle cx="64" cy="64" r="49" fill="none" stroke="#5D1C35"/></g>',
        '<rect id="HourHand" x="148" y="45" width="6" height="21" rx="3" fill="#E8DCE0"/>',
        '<rect id="MinuteHand" x="172" y="38" width="4" height="28" rx="2" fill="#E41951"/>',
        '<rect id="SecondHand" x="194" y="30" width="2" height="36" rx="1" fill="#FF0051"/>',
        '<circle id="HandCenterScrew" cx="64" cy="64" r="5" fill="#FF0051"/>',
        '<circle id="Glass" cx="64" cy="64" r="57" fill="none" stroke="#FF0051" opacity=".13" stroke-width="3"/>',
    ]
    write(STYLE / "widgets/clock.svg", svg(210, 128, "\n".join(clock_parts)))

    # Native Plasma scrollbar tracks and handles share the same rounded
    # silhouette as the task items, including brighter hover/press states.
    bar = frame("background-vertical", 0, 0, fill=INK, rim="#4E1D32",
                width=20, height=48, margin=8)
    bar += frame("background-horizontal", 30, 0, fill=INK, rim="#4E1D32",
                 width=48, height=20, margin=8)
    for idx, (name, fill, rim) in enumerate((
        ("slider", "#78203D", RED),
        ("mouseover-slider", "#A31A44", HOT),
        ("sunken-slider", "#D51A4E", HOT),
    )):
        bar += frame(name, idx*30, 60, fill=fill, rim=rim,
                     width=20, height=48, margin=8)
    arrow_paths = {"top":"M6 13l4-5 4 5", "right":"M7 6l5 4-5 4",
                   "bottom":"M6 7l4 5 4-5", "left":"M13 6l-5 4 5 4"}
    for row, (state, color) in enumerate((("", RED), ("mouseover-", HOT), ("sunken-", HOT))):
        for col, (direction, path) in enumerate(arrow_paths.items()):
            bar += (f'<path id="{state}arrow-{direction}" transform="translate({110+col*18},{row*18})" '
                    f'd="{path}" fill="none" stroke="{color}" stroke-width="2" '
                    'stroke-linejoin="round" stroke-linecap="round"/>')
    bar += '<rect id="hint-scrollbar-size" x="190" y="60" width="14" height="14" fill="none"/>'
    write(STYLE / "widgets/scrollbar.svg", svg(216, 116, bar))


def build_aurorae() -> None:
    # These 9-patch groups wrap every window; maximized windows use the
    # uninterrupted dark center, while regular windows retain scarlet edges.
    out = frame("decoration", 0, 0, fill=INK, rim=RED, top=HOT, bottom=RED, margin=15)
    out += frame("decoration-inactive", 56, 0, fill=INK, rim="#612039", margin=15)
    out += frame("decoration-maximized", 112, 0, fill=INK, rim=RED, margin=15)
    write(AURORAE / "decoration.svg", svg(170, 48, out))

    symbols = {
        "close": "M10 10L22 22M22 10L10 22",
        "minimize": "M9 17H23",
        "maximize": "M9 20L16 12L23 20",
        "restore": "M9 12L16 20L23 12",
    }
    hover_colors = {
        "close": "#FF315B",      # Close: red
        "minimize": "#FFD43B",   # Minimize: yellow
        "maximize": "#38EA77",   # Maximize: green
        "restore": "#38EA77",    # Restore follows maximize
    }
    for name, shape in symbols.items():
        body = []
        for idx, prefix in enumerate(("active", "inactive", "hover", "hover-inactive", "pressed", "pressed-inactive")):
            dx, dy = (idx % 3)*38, (idx // 3)*38
            lit = prefix.startswith("hover") or prefix.startswith("pressed")
            color = hover_colors[name] if lit else ("#E41951" if name == "close" and prefix == "active" else "#C36681" if prefix == "active" else "#805267")
            edge = color
            body.append(f'<g id="{prefix}-center" transform="translate({dx},{dy})">'
                        '<rect width="32" height="32" fill="#000" fill-opacity="0"/>'
                        + (f'<path d="{shape}" fill="none" stroke="{color}" '
                           f'stroke-width="{8 if lit else 5}" stroke-opacity="{.18 if lit else .12}" '
                           'stroke-linejoin="round" stroke-linecap="round"/>' if name == "close" or lit else '')
                        + (f'<path d="{shape}" fill="none" stroke="{color}" '
                           'stroke-width="5" stroke-opacity=".23" '
                           'stroke-linejoin="round" stroke-linecap="round"/>' if name == "close" and lit else '')
                        + f'<path d="{shape}" fill="none" stroke="{edge}" stroke-width="2.4" '
                          'stroke-linejoin="round" stroke-linecap="round"/>'
                        + (f'<path d="M5 5h4 M23 5h4 M5 27h4 M23 27h4" fill="none" '
                           f'stroke="{color}" stroke-width="1.2" opacity=".85"/>' if name == "close" and lit else '')
                        + '</g>')
        write(AURORAE / f"{name}.svg", svg(114, 76, "\n".join(body)))


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    source = FONT_DIR / name
    if not source.exists():
        source = Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
    return ImageFont.truetype(str(source), size)


def wallpaper(width: int = 1920, height: int = 1200) -> Image.Image:
    image = Image.new("RGB", (width, height), INK)
    d = ImageDraw.Draw(image)
    # Low-key grid and circuitry: leave the left half quiet for desktop icons.
    for x in range(0, width, 80):
        d.line([(x, 0), (x, height)], fill="#19151C", width=1)
    for y in range(0, height, 80):
        d.line([(0, y), (width, y)], fill="#19151C", width=1)
    haze = Image.new("RGBA", image.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    cx, cy = int(width*.69), int(height*.50)
    for rad in (180, 248, 322, 440):
        hd.arc((cx-rad, cy-rad, cx+rad, cy+rad), 210, 515,
               fill=(228, 25, 81, 120), width=6)
    hd.line([(cx-500, cy), (cx+500, cy)], fill=(228, 25, 81, 100), width=3)
    hd.line([(cx, cy-500), (cx, cy+500)], fill=(228, 25, 81, 100), width=3)
    image = Image.alpha_composite(image.convert("RGBA"), haze.filter(ImageFilter.GaussianBlur(24)))
    image = Image.alpha_composite(image, haze)
    d = ImageDraw.Draw(image)
    for rad, start, end, color, line in (
        (190, 214, 324, "#E41951", 3),
        (268, 28, 164, "#63203A", 2),
        (330, 200, 345, "#B31B46", 2),
        (445, 80, 165, "#4A1B30", 2),
    ):
        d.arc((cx-rad, cy-rad, cx+rad, cy+rad), start, end, fill=color, width=line)
    # Reticle, compact signal tracks, and small labels follow the dashboard.
    d.ellipse((cx-82, cy-82, cx+82, cy+82), outline=HOT, width=2)
    d.ellipse((cx-5, cy-5, cx+5, cy+5), fill=HOT)
    d.line((cx-120,cy,cx-20,cy), fill=RED, width=2)
    d.line((cx+20,cy,cx+120,cy), fill=RED, width=2)
    for i in range(9):
        y=150+i*25
        d.line((1060,y,1110+i%3*30,y), fill="#542038", width=2)
        d.ellipse((1110+i%3*30-3,y-3,1110+i%3*30+3,y+3), fill=RED)
    d.text((118, 200), "SCARLET", font=font("display.ttf", 104), fill=TEXT)
    d.text((123, 310), "PROTOCOL", font=font("display.ttf", 72), fill=RED)
    d.line((125, 398, 677, 398), fill=RED, width=3)
    d.text((126, 430), "BLACKOUT  /  DESKTOP SYSTEM", font=font("mono.ttf", 20), fill="#A87484")
    d.text((126, 1070), "S C A R L E T  //  P R O T O C O L", font=font("mono.ttf", 18), fill="#8F4761")
    for y in (1015, 1023):
        d.line((126,y,673,y), fill="#6C1B3B", width=1)
    return image.convert("RGB")


def wallpaper_noir(width: int = 1920, height: int = 1200) -> Image.Image:
    """Quiet alternate wallpaper with clear icon space and a soft corner beacon."""
    im = Image.new("RGB", (width, height), INK)
    d = ImageDraw.Draw(im)
    for x in range(0, width, 96):
        d.line((x, 0, x, height), fill="#18141B")
    for y in range(0, height, 96):
        d.line((0, y, width, y), fill="#18141B")
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    p = ImageDraw.Draw(layer)
    cx, cy = int(width*.79), int(height*.50)
    for rad in (150, 205, 300):
        p.arc((cx-rad,cy-rad,cx+rad,cy+rad), 205, 475, fill=(228,25,81,110), width=4)
    p.rounded_rectangle((width-235,height-120,width-75,height-88),radius=16,
                        fill=(30,18,27,180),outline=(228,25,81,150),width=2)
    p.text((width-220,height-115),"// SCARLET",font=font("mono.ttf",16),fill=(228,25,81,235))
    im = Image.alpha_composite(im.convert("RGBA"), layer.filter(ImageFilter.GaussianBlur(19)))
    im = Image.alpha_composite(im, layer)
    return im.convert("RGB")


def build_wallpaper_and_preview() -> None:
    WALL.mkdir(parents=True, exist_ok=True)
    PREV.mkdir(parents=True, exist_ok=True)
    wall = wallpaper()
    wall.save(WALL / "1920x1200.png", optimize=True)
    wall.resize((960, 600), Image.Resampling.LANCZOS).save(WALL / "960x600.png", optimize=True)
    noir_dir = ROOT / "wallpapers/ScarletProtocolNoirWall/contents/images"
    noir_dir.mkdir(parents=True, exist_ok=True)
    noir = wallpaper_noir()
    noir.save(noir_dir / "1920x1200.png", optimize=True)
    noir.resize((960, 600), Image.Resampling.LANCZOS).save(noir_dir / "960x600.png", optimize=True)
    splash = Image.new("RGB", (960, 600), INK)
    s = ImageDraw.Draw(splash)
    for x in range(0,960,70): s.line((x,0,x,600), fill="#18151B",width=1)
    for y in range(0,600,70): s.line((0,y,960,y), fill="#18151B",width=1)
    s.rounded_rectangle((180,186,780,412), radius=28, fill="#171318", outline=RED, width=2)
    s.rounded_rectangle((190,196,770,402), radius=22, outline="#39202E", width=1)
    s.text((220,220),"// SCARLET PROTOCOL",font=font("mono.ttf",22),fill=RED)
    s.text((220,266),"BLACKOUT / DESKTOP",font=font("display.ttf",32),fill=TEXT)
    s.ellipse((704,224,747,267),fill="#351723",outline=HOT,width=3)
    s.ellipse((721,241,730,250),fill=HOT)
    s.text((220,351),"SYSTEM INITIALIZING",font=font("mono.ttf",14),fill="#AF7185")
    s.text((691,351),"04 / 06",font=font("mono.ttf",14),fill=RED)
    s.rounded_rectangle((220,376,740,381),radius=2,fill="#3B1D2C")
    s.rounded_rectangle((220,376,560,381),radius=2,fill=HOT)
    splash.save(PREV / "splash.png", optimize=True)

    core = Image.new("RGB", (960, 600), INK)
    c = ImageDraw.Draw(core)
    c.rounded_rectangle((192,42,768,558), radius=29, fill=INK, outline=RED, width=2)
    c.rounded_rectangle((201,51,759,549), radius=24, outline="#3E1E2D", width=1)
    c.ellipse((226,84,238,96),fill=RED)
    c.text((247,75),"SCARLET / SYSTEM CORE",font=font("mono.ttf",21),fill=TEXT)
    c.text((247,105),"LIVE TELEMETRY  //  DESKTOP",font=font("mono.ttf",11),fill="#A56D80")
    c.text((665,76),"23:41",font=font("mono.ttf",20),fill=RED)
    c.line((225,141,735,141),fill="#70213D",width=2)
    for i,(label,value,bar) in enumerate((("CPU","18%",.18),("MEMORY","48%",.48),
            ("GPU","2%",.02),("TEMPERATURE","163°F",0),("NETWORK","↓ 861 B/s",0))):
        x=225+(i%2)*260; y=160+(i//2)*103
        c.rounded_rectangle((x,y,x+247,y+91),radius=18,fill="#1B151C",outline="#5B2038",width=2)
        c.text((x+16,y+13),"// "+label,font=font("mono.ttf",13),fill=RED)
        c.text((x+16,y+37),value,font=font("mono.ttf",23),fill=TEXT)
        if bar:
            c.rounded_rectangle((x+16,y+78,x+230,y+81),radius=1,fill="#422033")
            c.rounded_rectangle((x+16,y+78,x+16+int(214*bar),y+81),radius=1,fill=RED)
    c.rounded_rectangle((225,474,735,529),radius=17,fill="#21141D",outline="#70213D",width=2)
    c.text((243,482),"FOCUS SEQUENCE",font=font("mono.ttf",12),fill=RED)
    c.text((243,502),"25:00",font=font("mono.ttf",18),fill=TEXT)
    c.rounded_rectangle((610,486,701,519),radius=13,fill="#381826",outline=RED,width=2)
    c.text((629,492),"START",font=font("mono.ttf",14),fill=TEXT)
    core.save(PREV / "systemcore.png", optimize=True)


def icon(group: str, name: str, paths: str) -> None:
    # Matching foreground glyphs for frequent desktop controls; missing icons
    # inherit Breeze Dark. 24px scalable SVGs work at all common panel sizes.
    dest = ICONS / f"{group}/scalable/{name}.svg"
    body = (f'<rect x="1" y="1" width="22" height="22" rx="8" fill="#101116" '
            f'stroke="#8E2047" stroke-width="1"/>'
            f'<g fill="none" stroke="{RED}" stroke-width="1.7" '
            f'stroke-linecap="round" stroke-linejoin="round">{paths}</g>')
    write(dest, svg(24, 24, body))


def build_icons() -> None:
    directories = ["actions", "places", "status", "apps"]
    index = "[Icon Theme]\nName=Scarlet Protocol Icons\nComment=Scarlet accents with Breeze Dark fallback\nInherits=breeze-dark,breeze,hicolor\nDirectories=" + ",".join(f"{a}/scalable" for a in directories) + "\n\n"
    for category in directories:
        context = "Applications" if category == "apps" else category.capitalize()
        index += f"[{category}/scalable]\nSize=24\nType=Scalable\nMinSize=16\nMaxSize=256\nContext={context}\n\n"
    write(ICONS / "index.theme", index)
    icon("places", "start-here-kde", '<path d="M12 3L20 8V16L12 21L4 16V8Z"/><path d="M12 6L8 12L12 18L16 12Z"/>')
    icon("places", "folder", '<path d="M3 8V18H21V8H12L10 5H3Z"/>')
    icon("places", "user-home", '<path d="M3 11L12 4L21 11V20H3Z"/><path d="M9 20V13H15V20"/>')
    icon("places", "folder-downloads", '<path d="M3 8V19H21V8H11L9 5H3Z"/><path d="M12 10V17M9 14L12 17L15 14"/>')
    icon("places", "folder-pictures", '<path d="M3 8v11h18V8h-9l-2-3H3zM6 16l4-4 3 3 2-2 4 3"/>')
    icon("places", "folder-documents", '<path d="M3 8v11h18V8h-9l-2-3H3zM8 12h9M8 15h7"/>')
    icon("apps", "systemsettings", '<circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/><path d="M12 3V6M12 18V21M3 12H6M18 12H21"/>')
    icon("apps", "org.kde.dolphin", '<path d="M3 8V19H21V8H12L10 5H3Z"/><path d="M7 14H17"/>')
    icon("actions", "system-shutdown", '<path d="M12 3V12M7 6A9 9 0 1 0 17 6"/>')
    icon("actions", "system-reboot", '<path d="M19 10A7 7 0 1 0 18 16"/><path d="M19 5V10H14"/>')
    icon("actions", "edit-find", '<circle cx="10" cy="10" r="5"/><path d="M14 14L20 20"/>')
    icon("actions", "list-add", '<path d="M12 5V19M5 12H19"/>')
    icon("actions", "window-close", '<path d="M6 6L18 18M18 6L6 18"/>')
    icon("actions", "window-minimize", '<path d="M6 15h12"/>')
    icon("actions", "window-maximize", '<path d="M6 17l6-8 6 8"/>')
    icon("actions", "edit-copy", '<rect x="8" y="7" width="11" height="13" rx="2"/><path d="M5 16H4V4h11v1"/>')
    icon("actions", "edit-paste", '<rect x="5" y="6" width="14" height="15" rx="2"/><path d="M8 7V4h8v3M8 11h8M8 15h6"/>')
    icon("actions", "edit-delete", '<path d="M5 7h14M8 7V5h8v2M7 8l1 12h8l1-12M10 11v6M14 11v6"/>')
    icon("actions", "document-open", '<path d="M3 8V19H21V8H12L10 5H3Z"/>')
    icon("actions", "document-save", '<path d="M5 3h13l2 3v15H4V3zM8 3v6h9V3M8 21v-8h9v8"/>')
    icon("actions", "folder-new", '<path d="M3 8v12h18V8h-9l-2-3H3zM15 11v6m-3-3h6"/>')
    icon("actions", "view-refresh", '<path d="M19 9a7 7 0 1 0 1 5M19 4v5h-5"/>')
    icon("actions", "go-home", '<path d="M3 11l9-7 9 7M5 11v9h14v-9M9 20v-7h6v7"/>')
    icon("actions", "go-previous", '<path d="M14 5l-7 7 7 7M7 12h13"/>')
    icon("actions", "go-next", '<path d="M10 5l7 7-7 7M4 12h13"/>')
    icon("actions", "media-playback-start", '<path d="M7 4v16l13-8z"/>')
    icon("actions", "media-playback-pause", '<path d="M6 4h4v16H6zM14 4h4v16h-4z"/>')
    icon("actions", "configure", '<circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/><path d="M12 3v3m0 12v3M3 12h3m12 0h3"/>')
    icon("status", "network-wireless", '<path d="M4 10Q12 3 20 10M7 13Q12 9 17 13M10 16Q12 14 14 16"/><circle cx="12" cy="19" r=".7"/>')
    icon("status", "audio-volume-high", '<path d="M4 10H8L13 6V18L8 14H4Z M16 9Q20 12 16 15 M18 6Q24 12 18 18"/>')
    icon("status", "battery-full", '<rect x="4" y="7" width="15" height="10" rx="2"/><path d="M20 10V14M7 10H16M7 13H16"/>')
    icon("status", "battery-charging", '<rect x="4" y="7" width="15" height="10" rx="2"/><path d="M20 10V14M13 8L9 12H12L10 16"/>')
    icon("status", "dialog-information", '<circle cx="12" cy="12" r="9"/><path d="M12 11V17M12 7V8"/>')
    icon("status", "network-wireless-disconnected", '<path d="M4 10q8-7 16 0M7 13q5-4 10 0M10 16q2-2 4 0M4 20L20 4"/>')
    icon("status", "audio-volume-muted", '<path d="M4 10h4l5-4v12l-5-4H4zM16 9l5 6m0-6l-5 6"/>')
    icon("status", "battery-low", '<rect x="4" y="7" width="15" height="10" rx="2"/><path d="M20 10v4M7 10v4"/>')


def main() -> None:
    build_plasma_style()
    build_aurorae()
    build_wallpaper_and_preview()
    build_icons()
    import afterglow, cursors
    import dial  # Regenerate the Orbit Dial face.
    afterglow.editions()
    cursors.build()
    import refinements
    refinements.build()
    print("Generated the Scarlet Protocol desktop artwork and cursor set.")


if __name__ == "__main__":
    main()
