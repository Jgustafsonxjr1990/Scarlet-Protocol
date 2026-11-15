#!/usr/bin/env python3
"""Install Scarlet's complete icon theme and cover this machine's app/widget icon names."""
from __future__ import annotations
import argparse
import base64
import configparser
import filecmp
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'tools'))
from icon_art import housing,monogram,recolor_svg
SOURCE=HERE/'icons/ScarletProtocolIcons'
SAFE=re.compile(r'^[A-Za-z0-9][A-Za-z0-9._+-]*$')
READ=object()
ABSENT='__SCARLET_ICON_SETTING_ABSENT_62__'


def desktop_values(text):
    values={};inside=False
    for line in text.splitlines():
        if line.startswith('['):inside=line.strip()=='[Desktop Entry]'
        elif inside and '=' in line and not line.lstrip().startswith('#'):
            key,value=line.split('=',1);values[key.strip()]=value.strip()
    return values


def with_desktop_icon(text,icon,original_icon=None):
    """Replace only the main entry's Icon; retain Exec, actions, translations and flags."""
    lines=text.splitlines(keepends=True);inside=False;found=False
    for i,line in enumerate(lines):
        if line.startswith('['):
            if inside and not found:lines.insert(i,'Icon='+icon+'\n');found=True;break
            inside=line.strip()=='[Desktop Entry]'
        elif inside and re.match(r'^Icon\s*=',line):
            lines[i]='Icon='+icon+'\n';found=True
    if not found:
        if inside:
            if lines and not lines[-1].endswith('\n'):lines[-1]+='\n'
            lines.append('Icon='+icon+'\n')
        else:raise ValueError('Missing Desktop Entry group')
    if original_icon is not None:
        output=[];inside=False
        for line in lines:
            if line.startswith('['):inside=line.strip()=='[Desktop Entry]'
            if inside and line.startswith(('X-ScarletProtocol-OriginalIcon=','X-ScarletProtocol-ManagedIcon=')):continue
            output.append(line)
            if inside and re.match(r'^Icon\s*=',line):
                output+=['X-ScarletProtocol-OriginalIcon='+original_icon+'\n','X-ScarletProtocol-ManagedIcon='+icon+'\n']
        lines=output
    return ''.join(lines)


def data_roots(data_home):
    paths=[data_home]+[Path(x) for x in os.environ.get('XDG_DATA_DIRS','/usr/local/share:/usr/share').split(':') if x]
    paths += [Path.home()/'.local/share/flatpak/exports/share',Path('/var/lib/flatpak/exports/share')]
    return list(dict.fromkeys(paths))


def fallback_index(roots):
    result={}
    for root in roots:
        for theme in ('breeze-dark','breeze','hicolor','Adwaita'):
            folder=root/'icons'/theme
            if folder.is_dir():
                for p in sorted(folder.rglob('*')):
                    if p.suffix.lower() in ('.svg','.png','.xpm','.jpg') and p.is_file():result.setdefault(p.stem,p)
        folder=root/'pixmaps'
        if folder.is_dir():
            for p in sorted(folder.iterdir()):
                if p.is_file() and p.suffix.lower() in ('.svg','.png','.xpm','.jpg'):result.setdefault(p.stem,p)
    return result


def app_art(label,source):
    """Use an existing local logo inside the housing, or a named monogram fallback."""
    if source and source.is_file() and source.stat().st_size<4*1024*1024:
        try:
            if source.suffix.lower()=='.svg':
                svg=ET.fromstring(recolor_svg(source.read_bytes()))
                if any(node.tag.rsplit('}',1)[-1] in ('script','foreignObject') for node in svg.iter()):raise ValueError('Unsupported SVG')
                for node in svg.iter():
                    for key,value in node.attrib.items():
                        if key.endswith('href') and not value.startswith(('#','data:')):raise ValueError('External reference')
                box=svg.get('viewBox')
                if box:x,y,w,h=[float(v) for v in box.replace(',',' ').split()]
                else:x=y=0;w=float(re.sub('[^0-9.]','',svg.get('width','24')));h=float(re.sub('[^0-9.]','',svg.get('height','24')))
                if w<=0 or h<=0:raise ValueError('Invalid view box')
                inner=''.join(ET.tostring(n,encoding='unicode') for n in svg)
                scale=16/max(w,h)
                artwork=f'<g color="{svg.get("color","#ff466f")}" transform="translate({12-w*scale/2:.4f} {12-h*scale/2:.4f}) scale({scale:.6f}) translate({-x} {-y})">{inner}</g>'
                return housing('',label).replace('</svg>',artwork+'</svg>'),'local-vector'
            if source.suffix.lower() in ('.png','.jpg','.jpeg'):
                mime='image/png' if source.suffix.lower()=='.png' else 'image/jpeg'
                encoded=base64.b64encode(source.read_bytes()).decode()
                artwork=f'<image x="4" y="4" width="16" height="16" preserveAspectRatio="xMidYMid meet" href="data:{mime};base64,{encoded}"/>'
                return housing('',label).replace('</svg>',artwork+'</svg>'),'original-logo-in-frame'
        except (OSError,ValueError,ET.ParseError,OverflowError):pass
    return monogram(label),'monogram'


def audit(roots):
    names={p.stem for p in SOURCE.glob('*/scalable/*.svg')}
    apps=[];widgets=[];seen=set();widget_seen=set();missing=[]
    for root in roots:
        folder=root/'applications'
        if folder.is_dir():
            for path in sorted(folder.rglob('*.desktop')):
                relative=path.relative_to(folder);identity=str(relative).replace('/','-')
                if identity in seen:continue
                seen.add(identity)
                try:text=path.read_text(encoding='utf-8');values=desktop_values(text)
                except (OSError,UnicodeError):continue
                if values.get('Hidden')=='true' or values.get('NoDisplay')=='true':continue
                if values.get('Type','Application') not in ('Application','Link'):continue
                icon=values.get('Icon','');label=values.get('Name',path.stem)
                if values.get('X-ScarletProtocol-ManagedIcon')==icon:
                    icon=values.get('X-ScarletProtocol-OriginalIcon',icon)
                row={'id':identity,'relative':str(relative),'path':str(path),'name':label,'icon':icon}
                row['coverage']='themed' if icon in names else 'absolute' if Path(icon).is_absolute() else 'needs-icon'
                apps.append(row)
                if row['coverage']!='themed':missing.append(row)
        folder=root/'plasma/plasmoids'
        if folder.is_dir():
            for path in sorted(folder.glob('*/metadata.json')):
                try:data=json.loads(path.read_text());plugin=data.get('KPlugin',{});icon=plugin.get('Icon','')
                except (OSError,ValueError):continue
                identity=plugin.get('Id',path.parent.name)
                if identity in widget_seen:continue
                widget_seen.add(identity)
                widgets.append({'id':identity,'name':plugin.get('Name',path.parent.name),
                                'icon':icon,'coverage':'themed' if icon in names else 'external' if Path(icon).is_absolute() else 'needs-icon'})
    return {'apps':apps,'widgets':widgets,'missing_apps':missing,'shipped_names':len(names)}


def plan(report,roots):
    derived={};overrides=[];originals=fallback_index(roots) if report['missing_apps'] or any(w['coverage']=='needs-icon' for w in report['widgets']) else {}
    for row in report['missing_apps']:
        icon=row['icon'];lookup=re.sub(r'\.(svg|png|xpm|jpe?g)$','',icon,flags=re.I)
        source=Path(icon) if Path(icon).is_absolute() else originals.get(lookup)
        target=lookup if SAFE.fullmatch(lookup) and '.'!=lookup and '..'!=lookup else 'scarlet-app-'+hashlib.sha256(row['id'].encode()).hexdigest()[:16]
        art,kind=app_art(row['name'],source)
        derived[target]=art;derived[target+'-symbolic']=art
        row['generated_icon']=target;row['generated_kind']=kind
        if icon!=target:
            path=Path(row['path']);text=path.read_text(encoding='utf-8')
            overrides.append((row['relative'],with_desktop_icon(text,target,icon)))
    for row in report['widgets']:
        if row['coverage']=='needs-icon' and SAFE.fullmatch(row['icon']):
            art,kind=app_art(row['name'],originals.get(row['icon']))
            derived.setdefault(row['icon'],art);derived.setdefault(row['icon']+'-symbolic',art)
            row['generated_kind']=kind
    return derived,overrides


def stage(data_home,derived):
    manifest=json.loads((SOURCE/'coverage.json').read_text())
    digest=hashlib.sha256(manifest['tree_sha256'].encode()+(SOURCE/'index.theme').read_bytes())
    for name,art in sorted(derived.items()):digest.update(name.encode());digest.update(art.encode())
    identity='ScarletProtocolIcons62_'+digest.hexdigest()[:12]
    target=data_home/'icons'/identity
    if target.is_symlink():raise ValueError('Icon destination is a symlink')
    if not target.is_dir():
        target.parent.mkdir(parents=True,exist_ok=True)
        temporary=Path(tempfile.mkdtemp(prefix='.scarlet-icons-',dir=target.parent))
        try:
            shutil.copytree(SOURCE,temporary,dirs_exist_ok=True)
            for name,art in derived.items():
                if not SAFE.fullmatch(name):raise ValueError('Invalid generated icon name')
                (temporary/'apps/scalable'/(name+'.svg')).write_text(art)
            temporary.rename(target)
        finally:
            if temporary.exists():shutil.rmtree(temporary)
    return identity,target


def run(argv):
    environment=None
    if getattr(sys,'frozen',False):
        # The portable GUI bundles Qt; native KDE utilities must use their own
        # system Qt libraries and plugins instead of inheriting the bundle paths.
        environment=os.environ.copy()
        original=environment.get('LD_LIBRARY_PATH_ORIG')
        if original is None:environment.pop('LD_LIBRARY_PATH',None)
        else:environment['LD_LIBRARY_PATH']=original
        for key in ('QT_PLUGIN_PATH','QT_QPA_PLATFORM_PLUGIN_PATH','QML2_IMPORT_PATH','QML_IMPORT_PATH','PYTHONHOME','PYTHONPATH'):
            environment.pop(key,None)
    return subprocess.run(argv,check=True,text=True,capture_output=True,timeout=45,env=environment).stdout.strip()


def program(name):
    result=shutil.which(name)
    if not result:raise RuntimeError('Run from your Plasma 6 desktop; missing '+name)
    return result


def setting(config_home,group,key,value=READ):
    argv=[program('kreadconfig6' if value is READ else 'kwriteconfig6'),'--file',str(config_home/'kdeglobals'),'--group',group,'--key',key]
    if value is READ:
        result=run(argv+['--default',ABSENT])
        return None if result==ABSENT else result
    return run(argv+(['--delete'] if value is None else [value]))


def notify():
    if exe:=shutil.which('dbus-send'):
        run([exe,'--session','--type=signal','/KIconLoader','org.kde.KIconLoader.iconChanged','int32:0'])
    else:
        run([program('gdbus'),'emit','--session','--object-path','/KIconLoader','--signal','org.kde.KIconLoader.iconChanged','0'])
    if exe:=shutil.which('kbuildsycoca6'):run([exe,'--noincremental'])


def same_tree(source,target):
    if not target.is_dir():return False
    originals={p.relative_to(source) for p in source.rglob('*') if p.is_file()}
    installed={p.relative_to(target) for p in target.rglob('*') if p.is_file()}
    return originals==installed and all(filecmp.cmp(source/p,target/p,shallow=False) for p in originals)


def apply(data_home,config_home,state_home,report,derived,overrides):
    program('kwriteconfig6');program('kreadconfig6')
    if not shutil.which('dbus-send') and not shutil.which('gdbus'):raise RuntimeError('No session D-Bus tool is available')
    previous={group+'/'+key:setting(config_home,group,key) for group,key in [('Icons','Theme'),('KDE','ShowIconsOnPushButtons'),('KDE','ShowIconsInMenuItems')]}
    identity,target=stage(data_home,derived)
    state_home.mkdir(parents=True,exist_ok=True)
    backup=Path(tempfile.mkdtemp(prefix='before-icons-',dir=state_home));backup.chmod(0o700)
    changes=[]
    def keep(path):
        if path.is_symlink():raise ValueError('Refusing to overwrite a symlink: '+str(path))
        key=str(len(changes));record={'path':str(path),'backup':key,'exists':path.exists(),'directory':path.is_dir()}
        if path.is_dir():shutil.copytree(path,backup/key)
        elif path.exists():shutil.copy2(path,backup/key)
        changes.append(record)
    try:
        for relative,text in overrides:
            path=data_home/'applications'/relative
            if path.is_file() and path.read_text()==text:continue
            keep(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
        for applet in ('launcher','clock','systemcore'):
            source=HERE/f'plasmoids/org.scarletprotocol.{applet}'
            target_applet=data_home/f'plasma/plasmoids/org.scarletprotocol.{applet}'
            # Metadata and QML update, never the live panel configuration.
            if source.is_dir():
                if not same_tree(source,target_applet):
                    keep(target_applet)
                    if target_applet.exists():shutil.rmtree(target_applet)
                    shutil.copytree(source,target_applet)
        setting(config_home,'Icons','Theme',identity)
        setting(config_home,'KDE','ShowIconsOnPushButtons','true')
        setting(config_home,'KDE','ShowIconsInMenuItems','true')
        notify()
    except Exception:
        for record in reversed(changes):
            path=Path(record['path'])
            if path.is_dir():shutil.rmtree(path)
            else:path.unlink(missing_ok=True)
            if record['exists']:
                if record['directory']:shutil.copytree(backup/record['backup'],path)
                else:shutil.copy2(backup/record['backup'],path)
        for key,value in previous.items():group,name=key.split('/');setting(config_home,group,name,value)
        try:notify()
        except Exception:pass
        raise
    (backup/'restore.json').write_text(json.dumps({'settings':previous,'files':changes},indent=2)+'\n')
    (state_home/'icon-coverage.json').write_text(json.dumps(report,indent=2)+'\n')
    return identity,backup


def restore(config_home,backup):
    data=json.loads((backup/'restore.json').read_text())
    for record in reversed(data['files']):
        path=Path(record['path'])
        if path.is_symlink():raise ValueError('Restore target became a symlink: '+str(path))
        if path.is_dir():shutil.rmtree(path)
        else:path.unlink(missing_ok=True)
        if record['exists']:
            if record['directory']:shutil.copytree(backup/record['backup'],path)
            else:shutil.copy2(backup/record['backup'],path)
    for key,value in data['settings'].items():group,name=key.split('/');setting(config_home,group,name,value)
    notify()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    group=p.add_mutually_exclusive_group();group.add_argument('--apply',action='store_true');group.add_argument('--restore',type=Path)
    p.add_argument('--report',type=Path,help='Write the local app/widget coverage report')
    p.add_argument('--data-home',type=Path,default=Path(os.environ.get('XDG_DATA_HOME') or Path.home()/'.local/share'))
    p.add_argument('--config-home',type=Path,default=Path(os.environ.get('XDG_CONFIG_HOME') or Path.home()/'.config'))
    p.add_argument('--state-home',type=Path,default=Path(os.environ.get('XDG_STATE_HOME') or Path.home()/'.local/state')/'ScarletProtocol')
    args=p.parse_args()
    if hasattr(os,'geteuid') and os.geteuid()==0 and (args.apply or args.restore):p.error('Run as your normal desktop user, without sudo.')
    try:
        if args.restore:restore(args.config_home,args.restore.expanduser());print('Restored previous icon settings and app/widget files.');return 0
        roots=data_roots(args.data_home);report=audit(roots);derived,overrides=plan(report,roots)
        report['generated_names']=len(derived);report['desktop_overrides']=len(overrides)
        report['external_widget_icons']=[w for w in report['widgets'] if w['coverage']=='external' or not w['icon']]
        print(f"Scarlet coverage: {report['shipped_names']} shipped icon names; {len(report['apps'])} visible app entries; {len(report['widgets'])} widget records.")
        print(f"Local additions: {len(derived)} icon names; {len(overrides)} per-user launcher icon overrides.")
        if args.apply:
            identity,backup=apply(args.data_home,args.config_home,args.state_home,report,derived,overrides)
            print('Applied complete Scarlet icons. Backup: '+str(backup))
            print('Reopen applications for their new icons. Already-loaded widget QML refreshes at the next Plasma login.')
        if args.report:args.report.write_text(json.dumps(report,indent=2)+'\n')
        if report['external_widget_icons']:print('Some widgets supply embedded/absolute icons; see the coverage report for those exceptions.')
    except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as error:
        print('Icon update stopped: '+str(error),file=sys.stderr);return 1
    return 0


if __name__=='__main__':raise SystemExit(main())
