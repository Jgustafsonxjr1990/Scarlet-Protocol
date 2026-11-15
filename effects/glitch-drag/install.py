#!/usr/bin/env python3
"""Install only Scarlet Glitch Drag, verify loading, then replace Wobbly Windows."""
import argparse, datetime, os, pathlib, shutil, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent
PLUGIN = 'kwin6_effect_scarlet_vector_wake'
STATE = pathlib.Path(os.environ.get('XDG_STATE_HOME', pathlib.Path.home()/'.local/state'))/'scarlet-protocol'
LOG = STATE/'glitch-drag-install.log'

def run(args, check=True):
    # Host KDE utilities must not inherit a frozen application's Qt libraries.
    env = os.environ.copy()
    if getattr(sys, 'frozen', False):
        original = env.pop('LD_LIBRARY_PATH_ORIG', None)
        env.pop('LD_LIBRARY_PATH', None)
        if original: env['LD_LIBRARY_PATH'] = original
        for key in ('QT_PLUGIN_PATH', 'QT_QPA_PLATFORM_PLUGIN_PATH', 'QML2_IMPORT_PATH'):
            env.pop(key, None)
    p = subprocess.run(args, capture_output=True, text=True, env=env, timeout=45)
    with LOG.open('a') as f:
        f.write('$ '+repr(args)+'\n'+p.stdout+p.stderr+'\n')
    if check and p.returncode:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip() or str(args[0])+' failed')
    return p

class KWin:
    def __init__(self):
        self.bus = shutil.which('gdbus')
        self.qbus = next((shutil.which(n) for n in ('qdbus6','qdbus-qt6','qdbus') if shutil.which(n)), None)
        if not self.bus and not self.qbus: raise RuntimeError('A KDE D-Bus utility (qdbus6 or gdbus) is required.')
    def call(self, method, plugin):
        interface = 'org.kde.kwin.Effects.'+method
        args = [self.bus,'call','--session','--dest','org.kde.KWin','--object-path','/Effects','--method',interface,plugin] if self.bus else [self.qbus,'org.kde.KWin','/Effects',interface,plugin]
        return run(args).stdout.strip()
    def loaded(self, plugin): return 'true' in self.call('isEffectLoaded',plugin).lower()

def install():
    if os.geteuid() == 0: raise RuntimeError('Run this installer as your normal Plasma desktop user, without sudo.')
    STATE.mkdir(parents=True, exist_ok=True)
    LOG.write_text('Scarlet Glitch Drag 3.0 — '+datetime.datetime.now().isoformat()+'\n')
    package = shutil.which('kpackagetool6')
    writer = shutil.which('kwriteconfig6')
    if not package or not writer: raise RuntimeError('This effect requires Plasma 6: kpackagetool6 and kwriteconfig6 must be installed.')
    client = KWin()
    was_loaded = client.loaded(PLUGIN) # Fail before changing files if no live KWin session.
    data = pathlib.Path(os.environ.get('XDG_DATA_HOME',pathlib.Path.home()/'.local/share'))
    # KWin 6.7 prefers kwin-wayland/effects over the legacy kwin/effects tree.
    # Upgrade that preferred copy when present instead of leaving a stale shadow.
    preferred = data/'kwin-wayland/effects'
    target = preferred if (preferred/PLUGIN).exists() else data/'kwin/effects'
    existing = target/PLUGIN
    backup = STATE/('glitch-drag-backup-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    if existing.exists(): shutil.copytree(existing,backup)
    if was_loaded: client.call('unloadEffect',PLUGIN)
    try:
        run([package,'--type','KWin/Effect','--packageroot',str(target),'--upgrade' if existing.exists() else '--install',str(ROOT/PLUGIN)])
        client.call('loadEffect',PLUGIN)
        if not client.loaded(PLUGIN):
            raise RuntimeError('KWin did not load Glitch Drag. The previous effect will be restored.')
    except Exception:
        client.call('unloadEffect',PLUGIN)
        if existing.exists(): shutil.rmtree(existing)
        if backup.exists(): shutil.copytree(backup,existing)
        if was_loaded: client.call('loadEffect',PLUGIN)
        run(['journalctl','--user','-b','--no-pager','-n','100'],check=False) if shutil.which('journalctl') else None
        raise
    run([writer,'--file','kwinrc','--group','Plugins','--key',PLUGIN+'Enabled','true'])
    # Only disable wobble once the replacement is confirmed loaded.
    client.call('unloadEffect','wobblywindows')
    run([writer,'--file','kwinrc','--group','Plugins','--key','wobblywindowsEnabled','false'])
    if client.loaded('wobblywindows'): raise RuntimeError('Glitch Drag loaded, but Wobbly Windows is still active. Disable it in Desktop Effects.')
    return 'Scarlet Glitch Drag is loaded.\n\nDrag a window by its title bar: red scan columns and torn image echoes stay active until you release it.\n\nSettings: Desktop Effects → Scarlet Protocol — Glitch Drag → configure.\n\nLog: '+str(LOG)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gui',action='store_true')
    parser.add_argument('--enable',action='store_true',help='Compatibility option; installation always enables only Glitch Drag.')
    args=parser.parse_args()
    try: message=install(); result=0
    except Exception as error: message='Installation stopped: '+str(error)+'\n\nDetails: '+str(LOG);result=1
    print(message)
    dialog=shutil.which('kdialog')
    if args.gui and dialog:
        subprocess.run([dialog,'--title','Scarlet Protocol — Glitch Drag','--error' if result else '--msgbox',message])
    return result
if __name__=='__main__': raise SystemExit(main())
