#!/usr/bin/env python3
"""Safely update an installed Scarlet Protocol Global Theme in place."""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path

from install import COMPONENTS, HERE, same_tree


def identity(path: Path) -> bool:
    if path.is_symlink() or not path.exists():
        return False
    if path.is_dir() and any(p.is_symlink() for p in path.rglob("*")):
        return False
    if path.is_file():
        return path.name in ("ScarletProtocol.colors", "ScarletProtocol.colorscheme") and "Scarlet Protocol" in path.read_text(encoding="utf-8")
    metadata = path / ("index.theme" if path.name in ("ScarletProtocolIcons", "ScarletProtocolCursors") else "metadata.json")
    if path.parent.name == "themes":
        metadata = path / "metadata.desktop"
    if not metadata.is_file() or metadata.is_symlink():
        return False
    text = metadata.read_text(encoding="utf-8")
    return "ScarletProtocol" in text or "Scarlet Protocol" in text


def upgrade(data_home: Path, state_home: Path) -> tuple[int, int, Path | None]:
    targets = [(HERE / src, data_home / dst) for src, dst in COMPONENTS]
    for source, target in targets:
        if not source.exists() or source.is_symlink() or (source.is_dir() and any(p.is_symlink() for p in source.rglob("*"))):
            raise ValueError(f"Invalid source component: {source}")
        if target.is_symlink() or (target.exists() and not identity(target)):
            raise ValueError(f"This is not a safe Scarlet Protocol component to replace: {target}")
    changed = [(src, dest) for src, dest in targets if not same_tree(src, dest)]
    if not changed:
        return 0, len(targets), None
    state_home.mkdir(parents=True, exist_ok=True)
    backup = Path(tempfile.mkdtemp(prefix="before-theme-upgrade-", dir=state_home))
    staged: list[tuple[Path, Path, Path | None]] = []
    installed: list[tuple[Path, Path | None]] = []
    try:
        for source, target in changed:
            target.parent.mkdir(parents=True, exist_ok=True)
            holding = Path(tempfile.mkdtemp(prefix=".scarlet-stage-", dir=target.parent))
            staged.append((source, target, holding))
            stage = holding / target.name
            if source.is_dir():
                shutil.copytree(source, stage)
            else:
                shutil.copy2(source, stage)
            if target.exists():
                saved = backup / target.relative_to(data_home)
                saved.parent.mkdir(parents=True, exist_ok=True)
                if target.is_dir():
                    shutil.copytree(target, saved)
                else:
                    shutil.copy2(target, saved)
        for source, target, holding in staged:
            old = holding / "original"
            if target.exists():
                target.rename(old)
            try:
                (holding / target.name).rename(target)
            except Exception:
                if old.exists():
                    old.rename(target)
                raise
            installed.append((target, old if old.exists() else None))
    except Exception:
        for target, old in reversed(installed):
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink(missing_ok=True)
            if old is not None and old.exists():
                old.rename(target)
        raise
    finally:
        for _, _, holding in staged:
            if holding is not None:
                shutil.rmtree(holding, ignore_errors=True)
    return len(changed), len(targets) - len(changed), backup


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-home", type=Path, default=Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share"))
    parser.add_argument("--state-home", type=Path, default=Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state") / "ScarletProtocol")
    parser.add_argument("--apply", action="store_true", help="Apply the updated Blackout preset after installation")
    parser.add_argument("--night-shift", action="store_true", help="Use Night Shift with --apply")
    parser.add_argument("--panel-tools", action="store_true", help="With --apply, use the Scarlet launcher and clock at their current panel positions")
    args = parser.parse_args()
    try:
        changed, same, backup = upgrade(args.data_home.expanduser(), args.state_home.expanduser())
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    print(f"Scarlet Protocol: {changed} components updated, {same} already current.")
    if backup:
        print(f"Previous components saved in {backup}")
    if args.apply:
        from activate import activate
        try:
            activate(args.night_shift, args.panel_tools)
        except Exception as error:
            print(f"The files are installed. Activation stopped: {error}", file=sys.stderr)
            return 1
    else:
        print("Apply Scarlet Protocol — Blackout in System Settings → Colors & Themes → Global Theme.")
        print("To use the new launcher and clock too: python3 activate.py --panel-tools")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
