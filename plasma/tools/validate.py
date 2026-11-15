#!/usr/bin/env python3
"""Validate package references, SVG parts, image sizes and per-user installation."""
from __future__ import annotations

import configparser
import importlib.util
import json
import re
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
NINE = {"center", "top", "topright", "right", "bottomright", "bottom", "bottomleft", "left", "topleft"}
STYLE = ROOT / "plasma-style/ScarletProtocolPlasma8"
AURORAE = ROOT / "aurorae/ScarletProtocolGlobal81"


def read_sections(path: Path) -> configparser.ConfigParser:
    cfg = configparser.ConfigParser(interpolation=None, strict=True)
    cfg.SECTCRE = re.compile(r"\[(?P<header>[^\n]+)\]")
    cfg.optionxform = str
    cfg.read(path, encoding="utf-8")
    return cfg


def ids(path: Path) -> set[str]:
    root = ET.parse(path).getroot()
    found = [element.get("id") for element in root.iter() if element.get("id")]
    assert len(found) == len(set(found)), f"Duplicate SVG IDs: {path}"
    return set(found)


def check_frame(path: Path, prefixes: tuple[str, ...]) -> None:
    present = ids(path)
    for prefix in prefixes:
        needed = {f"{prefix}-{n}" if prefix else n for n in NINE}
        assert needed <= present, f"Missing FrameSvg pieces: {path}: {needed - present}"


def main() -> None:
    for path in ROOT.rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    global_theme = json.loads((ROOT / "look-and-feel/ScarletProtocolGlobal/metadata.json").read_text())
    assert global_theme["KPackageStructure"] == "Plasma/LookAndFeel"
    defaults = read_sections(ROOT / "look-and-feel/ScarletProtocolGlobal/contents/defaults")
    assert defaults["kdeglobals][General"]["ColorScheme"] == "ScarletProtocol"
    assert defaults["kdeglobals][Icons"]["Theme"] == "ScarletProtocolIcons"
    assert defaults["plasmarc][Theme"]["name"] == "ScarletProtocolPlasma8"
    assert defaults["kwinrc][org.kde.kdecoration2"]["theme"].endswith("ScarletProtocolGlobal81")
    assert defaults["Wallpaper"]["Image"] == "ScarletProtocolWall"
    assert defaults["ksplashrc][KSplash"]["Theme"] == "ScarletProtocolGlobal"
    assert (ROOT / "look-and-feel/ScarletProtocolGlobal/contents/splash/Splash.qml").is_file()
    colors = read_sections(ROOT / "color-schemes/ScarletProtocol.colors")
    for category in ("Window", "View", "Button", "Selection", "Tooltip", "Header"):
        assert f"Colors:{category}" in colors
    for relative, prefixes in {
        "widgets/panel-background.svg": ("",),
        "widgets/background.svg": ("",),
        "widgets/translucentbackground.svg": ("",),
        "widgets/tooltip.svg": ("",),
        "widgets/button.svg": ("normal", "hover", "pressed", "focus", "toolbutton-hover"),
        "widgets/tasks.svg": ("normal", "hover", "focus", "attention", "minimized"),
        "widgets/lineedit.svg": ("base", "hover", "focus"),
        "widgets/viewitem.svg": ("normal", "hover", "selected", "selected+hover"),
        "widgets/plasmoidheading.svg": ("header", "footer"),
        "widgets/tabbar.svg": ("north-active-tab", "south-active-tab", "east-active-tab", "west-active-tab"),
        "widgets/bar_meter_horizontal.svg": ("background", "bar-active", "bar-inactive"),
        "widgets/frame.svg": ("sunken", "plain", "raised"),
        "widgets/containment-controls.svg": tuple(
            direction + ("-" + slider if slider else "")
            for direction in ("north", "east", "south", "west")
            for slider in ("", "maxslider", "minslider", "offsetslider")
        ),
        "dialogs/background.svg": ("",),
    }.items():
        check_frame(STYLE / relative, prefixes)
    check_frame(AURORAE / "decoration.svg", ("decoration", "decoration-inactive", "decoration-maximized"))
    assert {f"{action}-{state}" for action in ("add", "remove", "open")
            for state in ("normal", "hover", "pressed")} <= ids(STYLE / "widgets/action-overlays.svg")
    assert {"close", "configure", "move", "add", "remove", "delete", "menu"} <= ids(STYLE / "widgets/configuration-icons.svg")
    assert {"ClockFace", "HourHand", "MinuteHand", "SecondHand", "Glass"} <= ids(STYLE / "widgets/clock.svg")
    assert {f"{c}-notes" for c in ("white", "black", "red", "orange", "yellow", "green", "blue", "pink", "translucent", "translucent-light")} <= ids(STYLE / "widgets/notes.svg")
    for name in ("close", "minimize", "maximize", "restore"):
        present = ids(AURORAE / f"{name}.svg")
        assert {f"{state}-center" for state in ("active", "inactive", "hover", "pressed")} <= present
        tree = ET.parse(AURORAE / f"{name}.svg")
        hover = next(e for e in tree.iter() if e.get("id") == "hover-center")
        color = {"close": "#FF315B", "minimize": "#FFD43B",
                 "maximize": "#38EA77", "restore": "#38EA77"}[name]
        assert any(p.get("stroke") == color for p in hover.iter())
    decoration = read_sections(AURORAE / "ScarletProtocolGlobal81rc")
    assert decoration["General"]["LeftButtons"] == "XIA"
    assert decoration["General"]["RightButtons"] == ""
    for svg_path in ROOT.rglob("*.svg"):
        ids(svg_path)
    with Image.open(ROOT / "wallpapers/ScarletProtocolWall/contents/images/1920x1200.png") as im:
        assert im.size == (1920, 1200)
    with Image.open(ROOT / "wallpapers/ScarletProtocolNoirWall/contents/images/1920x1200.png") as im:
        assert im.size == (1920, 1200)
    with Image.open(ROOT / "look-and-feel/ScarletProtocolGlobal/contents/previews/preview.png") as im:
        assert im.size == (960, 600)
    for name in ("splash.png", "systemcore.png"):
        with Image.open(ROOT / "look-and-feel/ScarletProtocolGlobal/contents/previews" / name) as im:
            assert im.size == (960, 600)
    for theme, shell, wallpaper in (
        ("ScarletProtocolGlobal", "ScarletProtocolPlasma8", "ScarletProtocolWall"),
        ("ScarletProtocolNight", "ScarletProtocolNightPlasma8", "ScarletProtocolNoirWall"),
    ):
        folder = ROOT / "look-and-feel" / theme
        preset = read_sections(folder / "contents/defaults")
        assert preset["Wallpaper"]["Image"] == wallpaper
        assert preset["kcminputrc][Mouse"]["cursorTheme"] == "ScarletProtocolCursors"
        assert preset["kwinrc][org.kde.kdecoration2"]["theme"] == "__aurorae__svg__" + theme + "81"
        assert preset["plasmarc][Theme"]["name"] == shell
        decor = ROOT / "aurorae" / (theme+"81")
        decor_config = read_sections(decor / (theme + "81rc"))
        assert decor_config.getboolean("General", "Shadow")
        assert all(decor_config.getint("Layout", "Padding" + edge) == 12 for edge in ("Left", "Right", "Top", "Bottom"))
        assert all(decor_config.getint("Layout", "Border" + edge) == 12 for edge in ("Left", "Right", "Bottom"))
        check_frame(decor / "decoration.svg", ("decoration", "decoration-inactive", "decoration-maximized", "decoration-maximized-inactive"))
        states = ("active", "inactive", "hover", "hover-inactive", "pressed", "pressed-inactive", "deactivated", "deactivated-inactive")
        for button in ("close", "maximize", "minimize", "restore", "shade", "help", "keepabove", "keepbelow", "alldesktops", "appmenu"):
            assert {state + "-center" for state in states} <= ids(decor / (button + ".svg"))
    for edition in ("ScarletProtocolPlasma8", "ScarletProtocolNightPlasma8"):
        style = ROOT / "plasma-style" / edition
        switch = ids(style / "widgets/switch.svg")
        assert {prefix + "-" + piece for prefix in ("active", "inactive") for piece in ("left", "center", "right")} <= switch
        assert {"handle", "handle-active", "handle-hover", "handle-pressed", "handle-focus", "handle-shadow", "hint-bar-size"} <= switch
        check_frame(style / "widgets/lineedit.svg", ("base", "hover", "focus", "focusframe"))
        check_frame(style / "dialogs/background.svg", ("", "mask", "shadow"))
        check_frame(style / "widgets/tooltip.svg", ("", "mask", "shadow"))
        handles = ids(style / "widgets/slider.svg")
        assert {axis + "-slider-" + state for axis in ("horizontal", "vertical") for state in ("handle", "hover", "focus", "shadow")} <= handles
        assert "hint-handle-size" in handles
    switcher = ROOT / "window-switchers/ScarletProtocolDeck"
    switch_meta = json.loads((switcher / "metadata.json").read_text())
    assert switch_meta["KPackageStructure"] == "KWin/WindowSwitcher"
    assert switch_meta["KPlugin"]["Id"] == "ScarletProtocolDeck"
    assert "KWin.TabBoxSwitcher" in (switcher / "contents/ui/main.qml").read_text()
    assert (switcher / "contents/ui/WindowDeck.qml").is_file()
    cursor_dir = ROOT / "cursors/ScarletProtocolCursors/cursors"
    assert all(path.read_bytes().startswith(b"Xcur") for path in cursor_dir.iterdir())
    orbit = ROOT / "wallpaper-plugins/org.scarletprotocol.orbit"
    assert json.loads((orbit / "metadata.json").read_text())["KPackageStructure"] == "Plasma/Wallpaper"
    assert (orbit / "contents/ui/face.png").is_file()
    orbit_settings = ET.parse(orbit / "contents/config/main.xml")
    assert {e.get("name") for e in orbit_settings.findall(".//{*}entry")} == {"DialOnLeft", "DigitalReadout", "ShowDate"}
    konsole = read_sections(ROOT / "konsole/ScarletProtocol.colorscheme")
    assert all("Color" in konsole[f"Color{n}{variant}"] for n in range(8) for variant in ("", "Intense", "Faint"))
    widget = ROOT / "plasmoids/org.scarletprotocol.systemcore"
    assert json.loads((widget / "metadata.json").read_text())["KPackageStructure"] == "Plasma/Applet"
    assert "PlasmoidItem" in (widget / "contents/ui/main.qml").read_text()
    assert "Sensors.Sensor" in (widget / "contents/ui/main.qml").read_text()
    cfg = ET.parse(widget / "contents/config/main.xml").getroot()
    assert {"cpuSensor", "memorySensor", "gpuSensor", "temperatureSensor", "networkSensor", "focusMinutes"} <= {x.get("name") for x in cfg.iter("entry")}
    assert (ROOT / "icons/ScarletProtocolIcons/index.theme").is_file()
    spec = importlib.util.spec_from_file_location("scarlet_installer", ROOT / "install.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    update_spec = importlib.util.spec_from_file_location("scarlet_update", ROOT / "update_window_controls.py")
    assert update_spec and update_spec.loader
    update_module = importlib.util.module_from_spec(update_spec)
    update_spec.loader.exec_module(update_module)
    with tempfile.TemporaryDirectory(prefix="scarlet-plasma-test-") as temp:
        data_home = Path(temp)
        assert module.install(data_home) == (len(module.COMPONENTS), 0)
        assert module.install(data_home) == (0, len(module.COMPONENTS))
        assert update_module.update(data_home, data_home / "state") == (0, None)
        assert (data_home / "plasma/look-and-feel/ScarletProtocolGlobal/metadata.json").is_file()
        assert (data_home / "plasma/desktoptheme/ScarletProtocolPlasma8/widgets/tasks.svg").is_file()
        assert (data_home / "aurorae/themes/ScarletProtocolGlobal81/close.svg").is_file()
        assert (data_home / "plasma/desktoptheme/ScarletProtocolPlasma8/widgets/scrollbar.svg").is_file()
        assert (data_home / "plasma/plasmoids/org.scarletprotocol.systemcore/contents/ui/main.qml").is_file()
        installed_button = data_home / "plasma/desktoptheme/ScarletProtocolPlasma8/widgets/button.svg"
        installed_button.write_text("old Scarlet Protocol button SVG", encoding="utf-8")
        import sys
        sys.path.insert(0, str(ROOT))
        upgrade_spec = importlib.util.spec_from_file_location("scarlet_upgrade", ROOT / "upgrade.py")
        assert upgrade_spec and upgrade_spec.loader
        upgrade_module = importlib.util.module_from_spec(upgrade_spec)
        upgrade_spec.loader.exec_module(upgrade_module)
        changed, same, backup = upgrade_module.upgrade(data_home, data_home / "state")
        assert (changed, same) == (1, len(module.COMPONENTS)-1) and backup
        assert (backup / "plasma/desktoptheme/ScarletProtocolPlasma8/widgets/button.svg").read_text() == "old Scarlet Protocol button SVG"
        assert installed_button.read_bytes() == (STYLE / "widgets/button.svg").read_bytes()
        assert upgrade_module.upgrade(data_home, data_home / "state") == (0, len(module.COMPONENTS), None)
    print(f"PASS: metadata, defaults, colors, {len(list(ROOT.rglob('*.svg')))} SVG assets, "
          "semantic hover colors, splash/widget structure, wallpaper/previews, and two-pass installer staging")


if __name__ == "__main__":
    main()
