#!/usr/bin/env python3
"""Install the complete Scarlet Protocol Global Theme for one Plasma 6 user."""
from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMPONENTS = (
    ("look-and-feel/ScarletProtocolGlobal", "plasma/look-and-feel/ScarletProtocolGlobal"),
    ("plasma-style/ScarletProtocolPlasma8", "plasma/desktoptheme/ScarletProtocolPlasma8"),
    ("aurorae/ScarletProtocolGlobal81", "aurorae/themes/ScarletProtocolGlobal81"),
    ("color-schemes/ScarletProtocol.colors", "color-schemes/ScarletProtocol.colors"),
    ("icons/ScarletProtocolIcons", "icons/ScarletProtocolIcons"),
    ("wallpapers/ScarletProtocolWall", "wallpapers/ScarletProtocolWall"),
    ("wallpapers/ScarletProtocolNoirWall", "wallpapers/ScarletProtocolNoirWall"),
    ("plasmoids/org.scarletprotocol.systemcore", "plasma/plasmoids/org.scarletprotocol.systemcore"),
    ("look-and-feel/ScarletProtocolNight", "plasma/look-and-feel/ScarletProtocolNight"),
    ("plasma-style/ScarletProtocolNightPlasma8", "plasma/desktoptheme/ScarletProtocolNightPlasma8"),
    ("aurorae/ScarletProtocolNight81", "aurorae/themes/ScarletProtocolNight81"),
    ("cursors/ScarletProtocolCursors", "icons/ScarletProtocolCursors"),
    ("wallpaper-plugins/org.scarletprotocol.orbit", "plasma/wallpapers/org.scarletprotocol.orbit"),
    ("konsole/ScarletProtocol.colorscheme", "konsole/ScarletProtocol.colorscheme"),
    ("plasmoids/org.scarletprotocol.launcher", "plasma/plasmoids/org.scarletprotocol.launcher"),
    ("plasmoids/org.scarletprotocol.clock", "plasma/plasmoids/org.scarletprotocol.clock"),
    ("window-switchers/ScarletProtocolDeck", "kwin/tabbox/ScarletProtocolDeck"),
)


def same_tree(source: Path, target: Path) -> bool:
    if source.is_file():
        return target.is_file() and filecmp.cmp(source, target, shallow=False)
    if not target.is_dir():
        return False
    originals = {p.relative_to(source) for p in source.rglob("*") if p.is_file()}
    installed = {p.relative_to(target) for p in target.rglob("*") if p.is_file()}
    return originals == installed and all(
        filecmp.cmp(source / p, target / p, shallow=False) for p in originals
    )


def install(data_home: Path) -> tuple[int, int]:
    targets = [(HERE / src, data_home / dst) for src, dst in COMPONENTS]
    for source, target in targets:
        if not source.exists():
            raise FileNotFoundError(f"Package is incomplete: {source}")
        if source.is_symlink() or any(p.is_symlink() for p in source.rglob("*")):
            raise ValueError(f"Package contains an unsupported symlink: {source}")
        if target.is_symlink():
            raise ValueError(f"Target is a symbolic link: {target}")
        if target.exists() and not same_tree(source, target):
            raise FileExistsError(f"A different Scarlet Protocol component already exists: {target}\n"
                                  "Move that one aside, then rerun the installer.")
    installed = 0
    existing = 0
    created = []
    try:
        for source, target in targets:
            if target.exists():
                existing += 1
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)
            created.append(target)
            installed += 1
    except Exception:
        for target in reversed(created):
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink(missing_ok=True)
        raise
    return installed, existing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-home", type=Path, default=Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share"),
                        help="XDG user data location (default: ~/.local/share)")
    args = parser.parse_args()
    try:
        installed, existing = install(args.data_home.expanduser())
    except (OSError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f"Scarlet Protocol ready: {installed} components installed, {existing} already present.")
    print("Apply in System Settings → Colors & Themes → Global Theme → Scarlet Protocol — Blackout.")
    print("Select the wallpaper component if Plasma offers a component chooser.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
