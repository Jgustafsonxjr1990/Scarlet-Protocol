"""Build the fifth release's native Plasma control artwork."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET

from afterglow import ROOT, render_frames, stroke, write_svg

NINE = ("topleft", "top", "topright", "left", "center", "right", "bottomleft", "bottom", "bottomright")


def hints(body, prefix, margin, y=0):
    for i, side in enumerate(("left", "right", "top", "bottom")):
        width, height = (margin, 1) if side in ("left", "right") else (1, margin)
        name = f"{prefix}-hint-{side}-margin" if prefix else f"hint-{side}-margin"
        body += f'<rect id="{name}" x="110" y="{y+i*12}" width="{width}" height="{height}" opacity="0"/>'
    return body


def ring_handle(name, x, y, rim, glow, hollow=False, pressed=False):
    arc = "M4.8 9.8a7.5 7.5 0 0 1 12.1-3.5M19.2 14.2a7.5 7.5 0 0 1-12.1 3.5"
    parts = ['<rect width="24" height="24" opacity="0"/>']
    if not hollow:
        parts.append('<circle cx="12" cy="12" r="7.2" fill="#18151c" stroke="#613042" stroke-width="1"/>')
    if glow:
        parts += [stroke(arc, rim, 5, glow*.11), stroke(arc, rim, 3, glow*.20)]
    parts.append(stroke(arc, rim, 1.2, 1))
    if not hollow:
        parts.append(stroke("M11 9.5v5m2-5v5", "#d9a3b4" if pressed else "#f6cfdb", .85))
    return f'<g id="{name}" transform="translate({x},{y})">{"".join(parts)}</g>'


def switches(folder, accent, quiet):
    face = "#4b1b30" if quiet else "#6d1937"
    parts = []
    for row, (prefix, fill, rim) in enumerate((("inactive", "#17151b", "#653045"), ("active", face, accent))):
        y = row*28
        parts += [
            f'<g id="{prefix}-left" transform="translate(0,{y})"><rect width="12" height="20" opacity="0"/><path d="M12 1H10C-2 1-2 19 10 19H12" fill="{fill}" stroke="{rim}" stroke-width="1"/></g>',
            f'<g id="{prefix}-center" transform="translate(16,{y})"><rect width="12" height="20" opacity="0"/><rect y="1" width="12" height="18" fill="{fill}"/><path d="M0 1h12M0 19h12" stroke="{rim}" stroke-width="1"/></g>',
            f'<g id="{prefix}-right" transform="translate(32,{y})"><rect width="12" height="20" opacity="0"/><path d="M0 1h2C14 1 14 19 2 19H0" fill="{fill}" stroke="{rim}" stroke-width="1"/></g>',
        ]
    for i, state in enumerate(("handle", "handle-active", "handle-hover", "handle-pressed", "handle-focus", "handle-shadow")):
        if state == "handle-shadow":
            content = '<circle cx="12" cy="12" r="9" fill="none" stroke="#000000" stroke-opacity=".35" stroke-width="3"/>'
            parts.append(f'<g id="{state}" transform="translate({i*28},64)"><rect width="24" height="24" opacity="0"/>{content}</g>')
        else:
            glow = .4 if state == "handle" else .65 if quiet else 1
            parts.append(ring_handle(state, i*28, 64, accent, glow, state == "handle-focus", state == "handle-pressed"))
    parts.append('<rect id="hint-bar-size" x="0" y="100" width="42" height="20" opacity="0"/>')
    parts.append('<rect id="hint-stretch-borders" x="48" y="100" width="1" height="1" opacity="0"/>')
    write_svg(folder/"switch.svg", 174, 124, "".join(parts))


def sliders(folder, accent, quiet):
    entries = [
        ("groove", [(0, "#5c293e", 1)], "#18151d", False),
        ("groove-highlight", [(0, accent, .45)], "#b81c4b", False),
    ]
    path = folder/"slider.svg"
    render_frames(path, entries, 3)
    tree = ET.parse(path)
    svg = tree.getroot()
    extra = []
    for row, orientation in enumerate(("horizontal", "vertical")):
        for i, state in enumerate(("handle", "hover", "focus", "shadow")):
            name = f"{orientation}-slider-{state}"
            if state == "shadow":
                extra.append(f'<g id="{name}" transform="translate({i*28},{row*28+28})"><rect width="24" height="24" opacity="0"/><circle cx="12" cy="12" r="9" fill="#0c0a0e" fill-opacity=".30"/></g>')
            else:
                extra.append(ring_handle(name, i*28, row*28+28, accent, .5 if quiet else 1, state != "handle"))
    extra.append('<rect id="hint-handle-size" x="122" y="28" width="24" height="24" opacity="0"/>')
    body = "".join(ET.tostring(child, encoding="unicode") for child in svg)
    write_svg(path, 152, 88, body+"".join(extra))


def checks(folder, accent, quiet):
    tick = "M5.5 11.5l4 4 9-9"
    body = '<g id="checkbox"><rect width="24" height="24" opacity="0"/>'
    body += stroke(tick, accent, 5, .12 if quiet else .22)
    body += stroke(tick, accent, 2.8) + stroke(tick, "#ffd8e5", .8) + "</g>"
    body += f'<g id="radiobutton" transform="translate(28)"><rect width="24" height="24" opacity="0"/><circle cx="12" cy="12" r="4.5" fill="{accent}"/><circle cx="12" cy="12" r="2" fill="#ffe3eb"/></g>'
    write_svg(folder/"checkmarks.svg", 52, 24, body)
    groups = []
    for i, (state, fill, rim, hollow) in enumerate((
        ("normal", "#17151b", "#7c3d53", False),
        ("checked", "#331422", accent, False),
        ("hover", "none", accent, True),
        ("focus", "none", "#ffd0df", True),
        ("shadow", "none", "#000000", True),
        ("symbol", accent, accent, False),
    )):
        r = 4 if state == "symbol" else 8.5
        shape = f'<circle cx="12" cy="12" r="{r}" fill="{fill}" stroke="{rim}" stroke-width="{.9 if hollow else 1.3}"/>'
        if state == "symbol":
            shape += '<circle cx="12" cy="12" r="1.5" fill="#ffe3eb"/>'
        groups.append(f'<g id="{state}" transform="translate({i*28})"><rect width="24" height="24" opacity="0"/>{shape}</g>')
    groups.append('<rect id="hint-size" x="0" y="30" width="24" height="24" opacity="0"/>')
    write_svg(folder/"radiobutton.svg", 172, 56, "".join(groups))


def surfaces(style, accent, quiet):
    def ring(prefix, fill, bright=False, outline=False):
        return (prefix, [(0, accent, .08), (1, accent, .24 if bright else .12),
                          (2, accent if bright else "#6d344a", .85), (3, "#2c1924", 1)], fill, outline)
    render_frames(style/"widgets/tabbar.svg",
                  [ring(side+"-active-tab", "#381725", True) for side in ("north", "south", "east", "west")], 10)
    render_frames(style/"widgets/listitem.svg",
                  [ring("normal", "#17151b"), ring("hover", "#301923", True),
                   ring("pressed", "#5d1a34", True), ring("section", "#16131a")], 9)
    render_frames(style/"widgets/menubaritem.svg",
                  [ring("normal", "#17151b"), ring("hover", "#301923", True),
                   ring("pressed", "#5d1a34", True)], 9)
    for filename, size in (("dialogs/background.svg", 16), ("widgets/tooltip.svg", 13)):
        path = style/filename
        render_frames(path, [ring("", "#141218")], size)
        tree = ET.parse(path).getroot()
        body = "".join(ET.tostring(child, encoding="unicode") for child in tree)
        # A mask describes the opaque surface independently of its exterior shadow.
        mask = [("mask", [(0, "#ffffff", 1)], "#ffffff", False)]
        temp = path.with_suffix(".parts")
        render_frames(temp, mask, size)
        body += "".join(ET.tostring(child, encoding="unicode") for child in ET.parse(temp).getroot())
        shadow = [("shadow", [(0, "#9b1940", .02), (2, "#af1746", .04), (4, "#be1d4c", .06 if quiet else .1), (7, "#100b10", .12)], "none", True)]
        render_frames(temp, shadow, 20)
        body += "".join(ET.tostring(child, encoding="unicode") for child in ET.parse(temp).getroot())
        temp.unlink()
        body = hints(body, "", 12) + hints("", "shadow", 8, 55)
        write_svg(path, 130, 120, body)
    path = style/"widgets/lineedit.svg"
    tree = ET.parse(path).getroot()
    for child in list(tree):
        if (child.get("id") or "").startswith("focusframe-"):
            tree.remove(child)
    body = "".join(ET.tostring(child, encoding="unicode") for child in tree)
    # Plasma 6's focused text field requests focusframe as a separate overlay.
    temp = path.with_suffix(".parts")
    render_frames(temp, [ring("focusframe", "none", True, True)], 8)
    body += "".join(ET.tostring(child, encoding="unicode") for child in ET.parse(temp).getroot())
    temp.unlink()
    write_svg(path, 130, 160, body)


def icon_additions():
    root = ROOT/"icons/ScarletProtocolIcons"
    additions = {
        "places": {
            "folder-music": "M3 8v11h18V8h-9l-2-3H3zM12 10v6m0-5 5-1v5m-5 0a1.5 1.5 0 1 0 0 2m5-3a1.5 1.5 0 1 0 0 2",
            "folder-videos": "M3 8v11h18V8h-9l-2-3H3zM10 10v6l6-3z",
            "folder-recent": "M3 8v11h18V8h-9l-2-3H3zM12 10v4h4",
            "user-trash": "M5 7h14M8 7V4h8v3M7 8l1 12h8l1-12M10 11v6m4-6v6",
        },
        "actions": {
            "window-new": "M4 5h16v15H4zM4 9h16M12 12v5m-2.5-2.5h5",
            "view-fullscreen": "M8 4H4v4m12-4h4v4M4 16v4h4m8 0h4v-4",
            "view-restore": "M8 4v4H4m12-4v4h4M4 16h4v4m8 0v-4h4",
            "edit-cut": "M10 14l9-9M9 10l10 9M6 9a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm0 12a3 3 0 1 0 0-6 3 3 0 0 0 0 6z",
            "edit-undo": "M8 5L3 10l5 5M4 10h10a6 6 0 0 1 6 6v3",
            "edit-redo": "M16 5l5 5-5 5m4-5H10a6 6 0 0 0-6 6v3",
            "view-sort-ascending": "M4 5h14M4 10h10M4 15h6M18 11v9m-3-3 3 3 3-3",
            "view-list-details": "M4 5h2m4 0h10M4 12h2m4 0h10M4 19h2m4 0h10",
            "view-list-icons": "M4 4h6v6H4zm10 0h6v6h-6zM4 14h6v6H4zm10 0h6v6h-6z",
            "document-properties": "M6 3h9l4 4v14H6zM14 3v5h5M9 12h7m-7 4h5",
            "media-skip-forward": "M4 6l8 6-8 6zm9 0 8 6-8 6z",
            "media-skip-backward": "M20 6l-8 6 8 6zm-9 0-8 6 8 6z",
            "system-lock-screen": "M5 10h14v11H5zM8 10V7a4 4 0 0 1 8 0v3M12 14v3",
        },
        "status": {
            "notification-active": "M5 17h14l-2-3V9A5 5 0 0 0 7 9v5zM10 20h4",
            "notification-disabled": "M5 17h14l-2-3V9A5 5 0 0 0 7 9v5M4 20L20 4M10 20h4",
            "network-bluetooth": "M11 3v18l7-5-12-9m0 10L18 8z",
            "dialog-warning": "M12 3L2 21h20zM12 9v5m0 3v1",
            "dialog-error": "M6 3h12l3 3v12l-3 3H6l-3-3V6zM8 8l8 8m0-8-8 8",
        },
    }
    for category, entries in additions.items():
        folder = root/category/"scalable"
        folder.mkdir(parents=True, exist_ok=True)
        for name, glyph in entries.items():
            body = '<rect x="1" y="1" width="22" height="22" rx="8" fill="#101116" stroke="#8E2047" stroke-width="1"/>'
            body += stroke(glyph, "#e41951", 1.55)
            write_svg(folder/(name+".svg"), 24, 24, body)


def build():
    for quiet, name in ((False, "ScarletProtocolPlasma"), (True, "ScarletProtocolNightPlasma")):
        style = ROOT/"plasma-style"/name
        accent = "#ca3b64" if quiet else "#ff2565"
        switches(style/"widgets", accent, quiet)
        sliders(style/"widgets", accent, quiet)
        checks(style/"widgets", accent, quiet)
        surfaces(style, accent, quiet)
    icon_additions()
    for group in ("look-and-feel", "plasma-style"):
        for path in (ROOT/group).glob("*/metadata.json"):
            meta = json.loads(path.read_text())
            meta["KPlugin"]["Version"] = "5.0.0"
            path.write_text(json.dumps(meta, ensure_ascii=False, indent=2)+"\n")
    for path in (ROOT/"aurorae").glob("*/metadata.desktop"):
        path.write_text(path.read_text().replace("Version=4.0.0", "Version=5.0.0"))


if __name__ == "__main__":
    build()
