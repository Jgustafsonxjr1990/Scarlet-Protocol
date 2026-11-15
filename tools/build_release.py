#!/usr/bin/env python3
"""Package tracked source plus freshly built portable Studio apps."""
from pathlib import Path
import argparse,hashlib,importlib.metadata,json,platform,re,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--tag',default='v1.0.0');args=parser.parse_args()
 if not re.fullmatch(r'v[0-9]+\.[0-9]+\.[0-9]+(?:[-.][A-Za-z0-9.-]+)?',args.tag):raise SystemExit('Invalid release tag')
 files=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0');files=[f for f in files if f]
 apps=['plasma/Scarlet-Desktop-Studio','sounds/Scarlet-Sound-Studio']
 for name in apps:
  p=ROOT/name
  if p.read_bytes()[:4]!=b'\x7fELF':raise SystemExit('Missing Linux executable: '+name)
 out=ROOT/'dist';out.mkdir(exist_ok=True);path=out/('Scarlet-Protocol-Complete-'+args.tag+'.zip');prefix='Scarlet-Protocol-'+args.tag+'/'
 versions={'python':platform.python_version(),'PySide6-Essentials':importlib.metadata.version('PySide6-Essentials'),'PyInstaller':importlib.metadata.version('PyInstaller'),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'platform':platform.platform()}
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for name in sorted(set(files+apps)):
   p=ROOT/name
   if p.is_file():z.write(p,prefix+name)
  z.writestr(prefix+'BUILD-INFO.json',json.dumps(versions,indent=2)+'\n')
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
  for name in apps+['effects/glitch-drag/Install-Glitch-Drag','effects/phase-relay/Install-Phase-Relay']:
   assert (z.getinfo(prefix+name).external_attr>>16)&0o111,name
  assert not any('BRAIN.md' in n or '__pycache__' in n for n in z.namelist())
 digest=hashlib.sha256(path.read_bytes()).hexdigest();(out/'SHA256SUMS').write_text(digest+'  '+path.name+'\n');print(path,digest)
if __name__=='__main__':main()
