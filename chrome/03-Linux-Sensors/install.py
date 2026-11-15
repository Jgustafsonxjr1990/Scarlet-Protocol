#!/usr/bin/env python3
"""Install the bundled native messaging helper for one unpacked Chrome extension."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil

NAME = 'ooo.gustafson.scarlet_sensors'


def install(extension_id, browser='google-chrome', home=None):
    if not re.fullmatch(r'[a-p]{32}', extension_id):
        raise ValueError('Extension ID must be 32 letters from a through p. Find it at chrome://extensions with Developer mode on.')
    if browser not in ('google-chrome', 'chromium'):
        raise ValueError('Choose google-chrome or chromium')
    base = Path(home) if home is not None else Path.home()
    target = base / '.local/share/scarlet-protocol/host.py'
    manifest = base / '.config' / browser / 'NativeMessagingHosts' / (NAME + '.json')
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(Path(__file__).with_name('host.py'), target)
    target.chmod(0o700)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    config = {'name': NAME, 'description': 'Scarlet Protocol local Linux readings', 'path': str(target.absolute()), 'type': 'stdio', 'allowed_origins': ['chrome-extension://' + extension_id + '/']}
    temp = manifest.with_suffix('.json.tmp')
    temp.write_text(json.dumps(config, indent=2) + '\n')
    os.replace(temp, manifest)
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('extension_id', help='ID of the loaded 02-Animated-New-Tab extension')
    parser.add_argument('--browser', choices=('google-chrome', 'chromium'), default='google-chrome')
    arguments = parser.parse_args()
    try:
        path = install(arguments.extension_id, arguments.browser)
    except (ValueError, OSError) as error:
        parser.exit(2, f'Install failed: {error}\n')
    print('Installed local sensor helper at', path)
    print('Return to a Scarlet Protocol new tab, then press Connect sensors.')
