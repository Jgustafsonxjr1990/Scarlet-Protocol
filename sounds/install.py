#!/usr/bin/env python3
"""Optional command-line installer; double-click Scarlet-Sound-Studio for the GUI."""
import argparse,os
from pathlib import Path
import sound_backend as backend

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-home',type=Path,default=Path(os.environ.get('XDG_DATA_HOME') or Path.home()/'.local/share'))
    parser.add_argument('--config-home',type=Path,default=Path(os.environ.get('XDG_CONFIG_HOME') or Path.home()/'.config'))
    parser.add_argument('--state-home',type=Path,default=Path(os.environ.get('XDG_STATE_HOME') or Path.home()/'.local/state')/'ScarletProtocol')
    parser.add_argument('--profile',choices=['protocol','night','overdrive'],default='protocol')
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--restore',type=Path)
    args=parser.parse_args()
    if args.restore:print(backend.restore(args.data_home,args.config_home,args.restore))
    elif args.apply:print(backend.apply(args.data_home,args.config_home,args.state_home,args.profile))
    else:print(backend.install(args.data_home,args.state_home));print('Select Scarlet Protocol in System Settings → System Sounds.')

if __name__=='__main__':main()
