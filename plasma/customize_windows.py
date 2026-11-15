#!/usr/bin/env python3
"""Scarlet window appearance: native dialogs, saved presets, safe window-only apply."""
from __future__ import annotations
import argparse
import configparser
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE/'tools'))
from window_art import PRESETS, make_decoration


def command(programs):
    for name in programs:
        if path := shutil.which(name): return path
    raise RuntimeError('Required Plasma command is unavailable: '+', '.join(programs))


def run(argv):
    return subprocess.run(argv,check=True,text=True,capture_output=True,timeout=30).stdout.strip()


def refresh():
    qdbus = next((shutil.which(x) for x in ('qdbus6','qdbus-qt6','qdbus') if shutil.which(x)),None)
    if qdbus:
        run([qdbus,'org.kde.KWin','/KWin','org.kde.KWin.reconfigure'])
    else:
        run([command(('gdbus',)),'call','--session','--dest','org.kde.KWin','--object-path','/KWin','--method','org.kde.KWin.reconfigure'])


def write_setting(config_home, key, value):
    run([command(('kwriteconfig6',)), '--file', str(config_home/'kwinrc'),
         '--group','org.kde.kdecoration2','--key',key,value])


def current_settings(config_home):
    result = {}
    for key in ('library','theme'):
        result[key] = run([command(('kreadconfig6',)), '--file',str(config_home/'kwinrc'),
                          '--group','org.kde.kdecoration2','--key',key])
    return result


def stage(data_home, options, night=False):
    """Immutable content-named decoration avoids a stale same-theme SVG cache."""
    source = HERE/'aurorae'/('ScarletProtocolNight6' if night else 'ScarletProtocolGlobal6')
    manifest = json.dumps(dict(options,night=night),sort_keys=True).encode()
    for p in sorted(source.iterdir()):
        if p.is_file(): manifest += p.name.encode()+p.read_bytes()
    manifest += (HERE/'tools/window_art.py').read_bytes()
    identity = 'ScarletProtocolSlots'+hashlib.sha256(manifest).hexdigest()[:12]
    target = data_home/'aurorae/themes'/identity
    if target.is_symlink(): raise ValueError('Decoration destination is a symlink')
    if target.is_dir(): return identity, target
    target.parent.mkdir(parents=True,exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix='.scarlet-slots-',dir=target.parent))
    try:
        shutil.copytree(source,temporary,dirs_exist_ok=True)
        make_decoration(temporary/'decoration.svg',night,options['slots'],options['glow'],options['frame_width'])
        cfg = configparser.ConfigParser(interpolation=None); cfg.optionxform=str
        cfg.read(temporary/(source.name+'rc'))
        for edge in ('Left','Right','Bottom'): cfg['Layout']['Border'+edge]=str(options['frame_width'])
        cfg['Layout']['TitleHeight']=str(options['title_height'])
        (temporary/(source.name+'rc')).unlink()
        with (temporary/(identity+'rc')).open('w') as stream: cfg.write(stream,space_around_delimiters=False)
        meta = configparser.ConfigParser(interpolation=None); meta.optionxform=str
        meta.read(temporary/'metadata.desktop')
        meta['Desktop Entry']['Name']='Scarlet Protocol — '+('Night Shift' if night else 'Blackout')+' · Slots'
        meta['Desktop Entry']['X-KDE-PluginInfo-Name']=identity
        meta['Desktop Entry']['X-KDE-PluginInfo-Version']='6.1.0'
        with (temporary/'metadata.desktop').open('w') as stream: meta.write(stream,space_around_delimiters=False)
        (temporary/'appearance.json').write_text(json.dumps(dict(options,night=night),indent=2)+'\n')
        temporary.rename(target)
    finally:
        if temporary.exists(): shutil.rmtree(temporary)
    return identity, target


def apply(data_home, config_home, state_home, options, night=False):
    previous = current_settings(config_home)
    identity, target = stage(data_home,options,night)
    if previous == {'library':'org.kde.kwin.aurorae','theme':'__aurorae__svg__'+identity}:
        refresh(); return target, None
    state_home.mkdir(parents=True,exist_ok=True)
    backup = Path(tempfile.mkdtemp(prefix='before-window-slots-',dir=state_home)); backup.chmod(0o700)
    (backup/'previous.json').write_text(json.dumps(previous,indent=2)+'\n')
    if (config_home/'kwinrc').exists(): shutil.copy2(config_home/'kwinrc',backup/'kwinrc.reference')
    try:
        write_setting(config_home,'library','org.kde.kwin.aurorae')
        write_setting(config_home,'theme','__aurorae__svg__'+identity)
        refresh()
    except Exception:
        for key,value in previous.items(): write_setting(config_home,key,value)
        try: refresh()
        except Exception: pass
        raise
    (state_home/'window-appearance.json').write_text(json.dumps(dict(options,night=night),indent=2)+'\n')
    return target, backup


def restore(config_home, backup):
    values = json.loads((backup/'previous.json').read_text())
    if set(values) != {'library','theme'} or not all(isinstance(x,str) for x in values.values()):
        raise ValueError('Invalid window settings backup')
    for key,value in values.items(): write_setting(config_home,key,value)
    refresh()


def install_studio(data_home):
    """Keep the application launcher entry working after the extracted ZIP is moved."""
    destination = data_home/'ScarletProtocol/window-studio'
    destination.mkdir(parents=True,exist_ok=True)
    if destination.resolve() != HERE.resolve():
        shutil.copy2(HERE/'customize_windows.py',destination/'customize_windows.py')
        (destination/'tools').mkdir(exist_ok=True)
        for name in ('window_art.py','afterglow.py'):
            shutil.copy2(HERE/'tools'/name,destination/'tools'/name)
        shutil.copytree(HERE/'aurorae',destination/'aurorae',dirs_exist_ok=True)
    def quote(value):
        return '"'+str(value).replace('\\','\\\\').replace('"','\\"').replace('`','\\`').replace('$','\\$')+'"'
    applications = data_home/'applications'; applications.mkdir(parents=True,exist_ok=True)
    (applications/'org.scarletprotocol.windowstudio.desktop').write_text(
        '[Desktop Entry]\nType=Application\nName=Scarlet Protocol Window Studio\n'
        'Comment=Frame profiles, recessed slots and scarlet glow\nIcon=preferences-system-windows\n'
        'Categories=Settings;DesktopSettings;\nTerminal=false\n'
        'Exec='+quote(sys.executable)+' '+quote(destination/'customize_windows.py')+' --configure\n')


def dialogs(options, night, saved=None):
    kdialog = command(('kdialog',))
    def choice(title, values, current):
        argv = [kdialog,'--title','Scarlet Protocol · Window Studio','--radiolist',title]
        for key,label in values: argv += [key,label,'on' if key==current else 'off']
        return run(argv)
    profiles = [('stealth','Stealth · quiet rim, sparse slots'),
        ('signature','Signature · recessed slots, scarlet rim'),('overdrive','Overdrive · dense slots, full halo')]
    if saved: profiles.insert(0,('current','Reuse my last Studio profile'))
    preset = choice('Choose your window profile', profiles, 'current' if saved else 'signature')
    options = {key:saved[key] for key in options} if preset=='current' else dict(PRESETS[preset])
    if preset=='current': night=saved['night']
    edition = choice('Frame edition',[('blackout','Blackout'),('night','Night Shift')],'night' if night else 'blackout')
    options['slots'] = choice('Slot density',[('off','Off'),('sparse','Sparse'),('normal','Standard'),('dense','Dense')],options['slots'])
    value = run([kdialog,'--title','Scarlet Protocol · Window Studio','--inputbox',
                 'Outer glow strength (0–100). The solid rim stays visible.',str(options['glow'])])
    options['glow'] = int(value)
    if not 0 <= options['glow'] <= 100: raise ValueError('Glow must be 0–100')
    return options, edition=='night'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--preset',choices=PRESETS,default='signature')
    p.add_argument('--slots',choices=('off','sparse','normal','dense'))
    p.add_argument('--glow',type=int,choices=range(101),metavar='0..100')
    p.add_argument('--frame-width',type=int,choices=range(6,11),metavar='6..10')
    p.add_argument('--title-height',type=int,choices=range(28,41),metavar='28..40')
    p.add_argument('--night-shift',action='store_true')
    action = p.add_mutually_exclusive_group()
    action.add_argument('--apply',action='store_true',help='Apply only the window decoration')
    action.add_argument('--configure',action='store_true',help='Open native KDE appearance dialogs and apply')
    action.add_argument('--restore',type=Path,help='Restore the prior decoration from a printed backup directory')
    p.add_argument('--data-home',type=Path,default=Path(os.environ.get('XDG_DATA_HOME') or Path.home()/'.local/share'))
    p.add_argument('--config-home',type=Path,default=Path(os.environ.get('XDG_CONFIG_HOME') or Path.home()/'.config'))
    p.add_argument('--state-home',type=Path,default=Path(os.environ.get('XDG_STATE_HOME') or Path.home()/'.local/state')/'ScarletProtocol')
    a = p.parse_args()
    if hasattr(os,'geteuid') and os.geteuid()==0 and (a.apply or a.configure or a.restore):
        p.error('Run as your normal desktop user, without sudo.')
    options = dict(PRESETS[a.preset])
    options.update({k:getattr(a,k) for k in options if getattr(a,k) is not None})
    try:
        if a.restore:
            restore(a.config_home,a.restore.expanduser()); print('Restored the previous window decoration.'); return 0
        night = a.night_shift
        if a.configure:
            saved_path = a.state_home/'window-appearance.json'
            saved = json.loads(saved_path.read_text()) if saved_path.is_file() else None
            options,night = dialogs(options,night,saved)
        if a.apply or a.configure:
            target,backup = apply(a.data_home,a.config_home,a.state_home,options,night)
            print('Applied Scarlet Protocol slotted windows.')
            if backup: print('Previous window settings: '+str(backup))
            try:
                install_studio(a.data_home)
                print('Window Studio is now in your application launcher.')
            except OSError as error:
                print('Frame applied; launcher shortcut could not be installed: '+str(error),file=sys.stderr)
        else:
            identity,target = stage(a.data_home,options,night)
            print('Prepared '+str(target)+'\nSelect Scarlet Protocol · Slots in Window Decorations, or run with --apply.')
    except subprocess.CalledProcessError as error:
        if a.configure and Path(error.cmd[0]).name=='kdialog': return 0
        print('Window appearance stopped: '+(error.stderr or str(error)),file=sys.stderr); return 1
    except (OSError,ValueError,RuntimeError,subprocess.TimeoutExpired) as error:
        print('Window appearance stopped: '+str(error),file=sys.stderr); return 1
    return 0


if __name__=='__main__': raise SystemExit(main())
