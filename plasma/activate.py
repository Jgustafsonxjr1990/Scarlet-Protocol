#!/usr/bin/env python3
"""Apply Scarlet Protocol and optionally use its launcher and clock on existing panels."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
PANEL_SCRIPT=(HERE/'tools/panel_tools.js').read_text(encoding='utf-8')

def dbus_command(script: str) -> list[str]:
    for program in ('qdbus6','qdbus-qt6','qdbus'):
        executable=shutil.which(program)
        if executable:
            return [executable,'org.kde.plasmashell','/PlasmaShell','org.kde.PlasmaShell.evaluateScript',script]
    executable=shutil.which('gdbus')
    if executable:
        return [executable,'call','--session','--dest','org.kde.plasmashell','--object-path','/PlasmaShell','--method','org.kde.PlasmaShell.evaluateScript',script]
    raise RuntimeError('No qdbus or gdbus command is available in this session.')

def activate(night: bool=False,panel_tools: bool=False,dry_run: bool=False) -> Path | None:
    theme='ScarletProtocolNight' if night else 'ScarletProtocolGlobal'
    if dry_run:
        print('Apply global theme: '+theme)
        print('Use fresh release 6 desktop and decoration artwork identifiers.')
        if panel_tools: print(PANEL_SCRIPT)
        return None
    program=shutil.which('plasma-apply-lookandfeel')
    if not program:
        raise RuntimeError('Apply from a Plasma 6 desktop session, or choose Scarlet Protocol in System Settings → Global Theme.')
    script="var scarletNightShift = "+str(night).lower()+";\n"+PANEL_SCRIPT
    panel_command=dbus_command(script) if panel_tools else None
    config=Path(os.environ.get('XDG_CONFIG_HOME') or Path.home()/'.config')
    state=Path(os.environ.get('XDG_STATE_HOME') or Path.home()/'.local/state')/'ScarletProtocol'
    state.mkdir(parents=True,exist_ok=True)
    backup=Path(tempfile.mkdtemp(prefix='before-activation-',dir=state))
    backup.chmod(0o700)
    for name in ('kdeglobals','kwinrc','plasmarc','kcminputrc','ksplashrc','plasma-org.kde.plasma.desktop-appletsrc'):
        source=config/name
        if source.is_file(): shutil.copy2(source,backup/name)
    (backup/'activation.json').write_text(json.dumps({'theme':theme,'panel_tools':panel_tools,'created':datetime.now(timezone.utc).isoformat()},indent=2)+'\n')
    subprocess.run([program,'--apply',theme],check=True)
    if panel_command:
        result=subprocess.run(panel_command,check=True,text=True,capture_output=True)
        (backup/'panel-result.txt').write_text(result.stdout)
        print(result.stdout.strip())
    print('Applied Scarlet Protocol '+('Night Shift' if night else 'Blackout')+'.')
    print('Previous settings saved in '+str(backup))
    return backup

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--night-shift',action='store_true')
    parser.add_argument('--panel-tools',action='store_true',help='Replace standard launcher and digital clock instances while keeping panel positions and recording their settings')
    parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args()
    try: activate(args.night_shift,args.panel_tools,args.dry_run)
    except (OSError,RuntimeError,subprocess.CalledProcessError) as error:
        print('Activation stopped: '+str(error),file=sys.stderr)
        return 1
    return 0

if __name__=='__main__':raise SystemExit(main())
