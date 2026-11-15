#!/usr/bin/env python3
"""Build the portable x86-64 graphical Icon Studio executable."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'desktop/build'


def main():
    BUILD.mkdir(parents=True,exist_ok=True)
    payload=ROOT/'desktop/desktop-studio-payload.zip'
    with zipfile.ZipFile(payload,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        sys.path.insert(0,str(ROOT))
        from install import COMPONENTS
        for part in dict.fromkeys(source for source,_ in COMPONENTS):
            source=ROOT/part
            for p in ([source] if source.is_file() else sorted(source.rglob('*'))):
                if p.is_file() and '__pycache__' not in p.parts:z.write(p,p.relative_to(ROOT))
        for name in ('icon_studio.py','desktop_update.py','upgrade.py','install.py','tools/icon_art.py','tools/panel_tools.js','desktop/icon_studio_gui.py','desktop/build_studio.py','LICENSE'):
            z.write(ROOT/name,name)
    checksum=ROOT/'desktop/payload.sha256';checksum.write_text(hashlib.sha256(payload.read_bytes()).hexdigest()+'\n')
    subprocess.run([sys.executable,'-m','PyInstaller','--noconfirm','--clean','--onefile','--windowed',
        '--name','Scarlet-Desktop-Studio','--distpath',str(BUILD/'dist'),'--workpath',str(BUILD/'work'),
        '--specpath',str(BUILD),'--paths',str(ROOT),'--paths',str(ROOT/'tools'),
        '--add-data',str(payload)+':.','--add-data',str(checksum)+':.',
        '--exclude-module','numpy','--exclude-module','PIL','--exclude-module','matplotlib',
        str(ROOT/'desktop/icon_studio_gui.py')],check=True)
    target=ROOT/'Scarlet-Desktop-Studio';shutil.copy2(BUILD/'dist/Scarlet-Desktop-Studio',target);target.chmod(0o755)
    print('Built '+str(target)+' ('+str(target.stat().st_size)+' bytes)',flush=True)


if __name__=='__main__':main()
