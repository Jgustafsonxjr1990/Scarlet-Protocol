"""Package the tested portable application and editable global-theme source."""
from pathlib import Path
import shutil,zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent


def source_files():
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file():continue
        relative=path.relative_to(ROOT)
        if '__pycache__' in relative.parts or relative.parts[:2]==('desktop','build'):continue
        if relative.name in ('Scarlet-Desktop-Studio','desktop-studio-payload.zip','payload.sha256'):continue
        if relative.name.startswith('rendered-'):continue
        yield path,relative


def main():
    source=ROOT/'desktop/source.zip'
    # Never recursively include a previous packaging output.
    source.unlink(missing_ok=True)
    files=list(source_files())
    with zipfile.ZipFile(source,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for path,relative in files:z.write(path,str(relative))
    desktop=OUT/'Scarlet-Protocol-Desktop-Studio.zip'
    with zipfile.ZipFile(desktop,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        z.write(ROOT/'Scarlet-Desktop-Studio','Scarlet-Desktop-Studio')
        z.write(ROOT/'desktop/READ-ME-FIRST.txt','READ-ME-FIRST.txt')
        z.write(ROOT/'desktop/OPEN-SOURCE-NOTICES.txt','OPEN-SOURCE-NOTICES.txt')
        z.write(source,'source.zip')
        for path in sorted((ROOT/'desktop/LICENSES').iterdir()):z.write(path,'LICENSES/'+path.name)
        for name in ['Scarlet-Protocol-Classic-Slits-Preview.png','Scarlet-Protocol-Plasma-Preview.png','Scarlet-Protocol-Surface-Details.png']:
            z.write(OUT/name,name)
    source.unlink()
    full=OUT/'Scarlet-Protocol-Plasma-Global-Theme.zip'
    with zipfile.ZipFile(full,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for path,relative in source_files():z.write(path,'Scarlet-Protocol-Plasma-Global/'+str(relative))
        z.write(ROOT/'Scarlet-Desktop-Studio','Scarlet-Protocol-Plasma-Global/Scarlet-Desktop-Studio')
    for path in [desktop,full]:
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None
            exe=next(v for v in z.infolist() if v.filename.endswith('/Scarlet-Desktop-Studio') or v.filename=='Scarlet-Desktop-Studio')
            assert (exe.external_attr>>16)&0o111
            assert not any('desktop/build/' in v.filename or '__pycache__' in v.filename for v in z.infolist())
            assert z.read(exe.filename)[:4]==b'\x7fELF'
        print(path,path.stat().st_size)

if __name__=='__main__':main()
