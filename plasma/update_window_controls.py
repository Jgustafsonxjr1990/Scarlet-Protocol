#!/usr/bin/env python3
"""Update only Scarlet Protocol's installed Aurorae window-control files."""
from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "aurorae/ScarletProtocolGlobal81"
FILES = ("close.svg", "minimize.svg", "maximize.svg", "restore.svg")


def update(data_home: Path, state_home: Path) -> tuple[int, Path | None]:
    target = data_home / "aurorae/themes/ScarletProtocolGlobal81"
    if not target.is_dir() or target.is_symlink():
        raise FileNotFoundError("Scarlet Protocol decoration is not installed yet. Run python3 install.py first.")
    metadata = (target / "metadata.desktop").read_text(encoding="utf-8")
    if "X-KDE-PluginInfo-Name=ScarletProtocolGlobal" not in metadata:
        raise ValueError("Installed decoration has a different identity; no files were changed.")
    for name in FILES:
        if not (SOURCE / name).is_file() or (SOURCE / name).is_symlink():
            raise FileNotFoundError(f"Update package is incomplete: {name}")
        if (target / name).is_symlink():
            raise ValueError(f"Refusing to overwrite a symlink: {target / name}")
    changed = [name for name in FILES if not (target / name).is_file()
               or not filecmp.cmp(SOURCE / name, target / name, shallow=False)]
    if not changed:
        return 0, None
    state_home.mkdir(parents=True, exist_ok=True)
    backup = Path(tempfile.mkdtemp(prefix="aurorae-before-controls-", dir=state_home))
    for name in changed:
        if (target / name).exists():
            shutil.copy2(target / name, backup / name)
    updated = []
    try:
        for name in changed:
            shutil.copy2(SOURCE / name, target / name)
            updated.append(name)
    except Exception:
        for name in updated:
            if (backup / name).is_file():
                shutil.copy2(backup / name, target / name)
            else:
                (target / name).unlink(missing_ok=True)
        raise
    return len(changed), backup


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-home", type=Path, default=Path.home() / ".local/share")
    parser.add_argument("--state-home", type=Path, default=Path.home() / ".local/state/ScarletProtocol")
    args = parser.parse_args()
    try:
        changed, backup = update(args.data_home.expanduser(), args.state_home.expanduser())
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    if changed:
        print(f"Updated {changed} Scarlet Protocol window-control files. Backup: {backup}")
        print("Reapply Scarlet Protocol — Blackout in System Settings → Window Decorations to refresh KWin.")
    else:
        print("Scarlet Protocol window controls are already up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
