"""Package original audio, editable source and the executable with launch mode."""
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]


def main():
    target=ROOT.parent/'Scarlet-Protocol-Sounds.zip'
    prefix='Scarlet-Protocol-Sounds/'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for path in sorted(ROOT.rglob('*')):
            if not path.is_file():continue
            relative=path.relative_to(ROOT)
            if '__pycache__' in relative.parts or relative.parts[:2]==('desktop','build'):continue
            if relative.name in ('sound-payload.zip','payload.sha256'):continue
            archive.write(path,prefix+str(relative))
        archive.write(ROOT/'desktop/READ-ME-FIRST.txt',prefix+'READ-ME-FIRST.txt')
        archive.write(ROOT.parent/'Scarlet-Protocol-Sound-Preview.mp3',prefix+'Sound-Preview.mp3')
        archive.write(ROOT.parent/'Scarlet-Protocol-Sound-Studio-Preview.png',prefix+'Sound-Studio-Preview.png')
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        binary=archive.getinfo(prefix+'Scarlet-Sound-Studio')
        assert (binary.external_attr>>16)&0o111
        assert archive.read(binary.filename)[:4]==b'\x7fELF'
        assert not any('desktop/build/' in item.filename or '__pycache__' in item.filename for item in archive.infolist())
        assert len([name for name in archive.namelist() if name.endswith('.oga')])==171
        assert len([name for name in archive.namelist() if '/WAV/' in name and name.endswith('.wav')])==117
    print(target,target.stat().st_size,'bytes; executable, source, 117 masters and 171 Ogg files verified')


if __name__=='__main__':main()
