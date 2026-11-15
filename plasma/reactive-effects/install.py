#!/usr/bin/env python3
"""Upgrade the two effects and reload their active KWin instances."""
from pathlib import Path
import argparse,os,shutil,subprocess,sys

ROOT=Path(__file__).resolve().parent
IDS=('kwin6_effect_scarlet_vector_wake','kwin6_effect_scarlet_phase_relay')

class KWin:
    def __init__(self):
        self.gdbus=shutil.which('gdbus')
        self.qdbus=next((shutil.which(name) for name in ('qdbus6','qdbus-qt6','qdbus') if shutil.which(name)),None)
        if not self.gdbus and not self.qdbus:raise RuntimeError('No D-Bus command is available')
    def call(self,method,plugin):
        interface='org.kde.kwin.Effects.'+method
        if self.gdbus:
            args=[self.gdbus,'call','--session','--dest','org.kde.KWin','--object-path','/Effects','--method',interface,plugin]
        else:args=[self.qdbus,'org.kde.KWin','/Effects',interface,plugin]
        return subprocess.run(args,check=True,capture_output=True,text=True).stdout.strip()
    def loaded(self,plugin):return 'true' in self.call('isEffectLoaded',plugin).lower()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--enable',action='store_true',help='Enable and reload both corrected effects now')
    args=parser.parse_args()
    if os.geteuid()==0:
        print('Run bash install.sh as your normal desktop user.',file=sys.stderr);return 1
    package_tool=shutil.which('kpackagetool6')
    if not package_tool:
        print('KDE Plasma 6 kpackagetool6 is required.',file=sys.stderr);return 1
    client=None;active={plugin:False for plugin in IDS}
    try:
        client=KWin()
        for plugin in IDS:active[plugin]=client.loaded(plugin)
    except (RuntimeError,subprocess.CalledProcessError):client=None
    installed=subprocess.run([package_tool,'--type','KWin/Effect','--list'],check=True,capture_output=True,text=True).stdout
    for plugin in IDS:
        operation='--upgrade' if plugin in installed else '--install'
        subprocess.run([package_tool,'--type','KWin/Effect',operation,str(ROOT/plugin)],check=True)
    if client:
        # Unload before loading: an already running v1 script would otherwise stay cached.
        for plugin in IDS:
            if active[plugin]:client.call('unloadEffect',plugin)
        for plugin in IDS:
            if args.enable or active[plugin]:
                if 'true' not in client.call('loadEffect',plugin).lower():
                    raise RuntimeError('KWin could not load '+plugin)
                print('Loaded corrected effect: '+plugin)
        if args.enable:
            writer=shutil.which('kwriteconfig6')
            if writer:
                for plugin in IDS:
                    subprocess.run([writer,'--file','kwinrc','--group','Plugins','--key',plugin+'Enabled','true'],check=True)
            else:print('Use Desktop Effects to save the enabled selections for future sessions.')
    else:print('Files installed. In Desktop Effects, turn both Scarlet effects off, Apply, then on and Apply to load the corrected scripts.')
    print('Installed Reactive Effects 3.0. Glitch Drag and Phase Relay have configurable settings.')
    print('Use the two Scarlet effects with Wobbly Windows and Slide Back turned off.')
    return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,RuntimeError,subprocess.CalledProcessError) as error:
        print('Installation stopped: '+str(error),file=sys.stderr);raise SystemExit(1)
