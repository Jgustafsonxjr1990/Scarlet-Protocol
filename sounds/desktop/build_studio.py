"""Build the portable, self-contained Sound Studio executable."""
from pathlib import Path
import hashlib,shutil,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]


def main():
    payload=ROOT/'desktop/sound-payload.zip'
    with zipfile.ZipFile(payload,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for folder in ('themes','WAV','desktop/icons'):
            for p in sorted((ROOT/folder).rglob('*')):
                if p.is_file():archive.write(p,p.relative_to(ROOT))
        for name in ['catalog.json','profiles.json','preview.html','preview.js','Theme-Demo.wav','Theme-Demo-night.wav','Theme-Demo-overdrive.wav','sound_backend.py','install.py','desktop/sound_studio.py','desktop/build_studio.py','desktop/sound-studio.svg','README.md','LICENSE.txt']:
            archive.write(ROOT/name,name)
    checksum=ROOT/'desktop/payload.sha256';checksum.write_text(hashlib.sha256(payload.read_bytes()).hexdigest()+'\n')
    build=ROOT/'desktop/build'
    subprocess.run([sys.executable,'-m','PyInstaller','--noconfirm','--clean','--onefile','--windowed','--name','Scarlet-Sound-Studio','--distpath',str(build/'dist'),'--workpath',str(build/'work'),'--specpath',str(build),'--paths',str(ROOT),'--add-data',str(payload)+':.','--add-data',str(checksum)+':.','--exclude-module','numpy','--exclude-module','scipy','--exclude-module','PIL','--exclude-module','matplotlib',str(ROOT/'desktop/sound_studio.py')],check=True)
    target=ROOT/'Scarlet-Sound-Studio';shutil.copy2(build/'dist/Scarlet-Sound-Studio',target);target.chmod(0o755)
    print('Built',target,target.stat().st_size,'bytes',flush=True)


if __name__=='__main__':main()
