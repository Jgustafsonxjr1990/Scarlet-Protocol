#!/usr/bin/env python3
"""Small Chrome native-messaging host. Reads local Linux counters; no network access."""
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import time

SYS = Path('/sys')
PROC = Path('/proc')
_previous = None


def read_num(path):
    try:
        return float(path.read_text().strip())
    except (OSError, ValueError):
        return None


def temperatures():
    readings = []
    preferred = ('coretemp', 'k10temp', 'zenpower', 'cpu_thermal', 'acpitz')
    for chip in (SYS / 'class/hwmon').glob('hwmon*'):
        try:
            name = (chip / 'name').read_text().strip().lower()
        except OSError:
            continue
        if name not in preferred:
            continue
        for value in chip.glob('temp*_input'):
            n = read_num(value)
            if n is not None and 0 < n < 120000:
                label = value.with_name(value.name.replace('_input', '_label'))
                try:
                    title = label.read_text().strip().lower()
                except OSError:
                    title = ''
                score = 2 if 'package' in title or 'tctl' in title or 'tdie' in title else 1
                readings.append((score, n / 1000))
    if readings:
        return max(readings)[1]
    for zone in (SYS / 'class/thermal').glob('thermal_zone*'):
        try:
            kind = (zone / 'type').read_text().strip().lower()
        except OSError:
            continue
        if kind not in ('x86_pkg_temp', 'cpu_thermal', 'cpu-thermal'):
            continue
        n = read_num(zone / 'temp')
        if n is not None and 0 < n < 120000:
            return n / 1000
    return None


def gpu():
    for card in (SYS / 'class/drm').glob('card[0-9]*'):
        n = read_num(card / 'device/gpu_busy_percent')
        if n is None:
            continue
        temp = None
        for entry in (card / 'device/hwmon').glob('hwmon*/temp1_input'):
            raw = read_num(entry)
            if raw is not None:
                temp = raw / 1000
                break
        return {'name': 'GPU', 'percent': max(0, min(100, n)), 'temp_c': temp}
    if shutil.which('nvidia-smi'):
        try:
            p = subprocess.run(['nvidia-smi', '--query-gpu=name,utilization.gpu,temperature.gpu', '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=2, check=False)
            line = p.stdout.splitlines()[0]
            name, load, temp = [part.strip() for part in line.split(',', 2)]
            return {'name': name[:80], 'percent': float(load), 'temp_c': float(temp)}
        except (OSError, ValueError, IndexError, subprocess.TimeoutExpired):
            pass
    return {'name': None, 'percent': None, 'temp_c': None}


def interface_name():
    candidates = []
    try:
        interfaces = list((SYS / 'class/net').iterdir())
    except OSError:
        return None
    for iface in interfaces:
        name = iface.name
        if name == 'lo' or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,30}', name):
            continue
        try:
            if (iface / 'operstate').read_text().strip() != 'up':
                continue
        except OSError:
            continue
        candidates.append((bool((iface / 'wireless').exists()), name))
    if not candidates:
        return None
    try:
        for line in (PROC / 'net/route').read_text().splitlines()[1:]:
            columns = line.split()
            if len(columns) > 1 and columns[1] == '00000000' and any(name == columns[0] for _, name in candidates):
                return columns[0]
    except OSError:
        pass
    return sorted(candidates, reverse=True)[0][1]


def network():
    global _previous
    name = interface_name()
    if not name:
        return {'interface': None, 'rx_bps': None, 'tx_bps': None, 'wireless': False, 'link_mbps': None}
    iface = SYS / 'class/net' / name
    rx, tx, now = read_num(iface / 'statistics/rx_bytes'), read_num(iface / 'statistics/tx_bytes'), time.monotonic()
    wireless = (iface / 'wireless').exists()
    rate = read_num(iface / 'speed')
    if rate is None or rate < 0 or rate > 1000000:
        rate = None
    if wireless and shutil.which('iw'):
        try:
            p = subprocess.run(['iw', 'dev', name, 'link'], capture_output=True, text=True, timeout=1, check=False)
            match = re.search(r'tx bitrate:\s*([\d.]+)\s*MBit/s', p.stdout)
            if match:
                rate = float(match.group(1))
        except (OSError, subprocess.TimeoutExpired):
            pass
    rx_bps = tx_bps = None
    if _previous and _previous[0] == name and rx is not None and tx is not None:
        elapsed = now - _previous[3]
        if elapsed > 0 and rx >= _previous[1] and tx >= _previous[2]:
            rx_bps, tx_bps = (rx - _previous[1]) / elapsed, (tx - _previous[2]) / elapsed
    _previous = (name, rx, tx, now)
    return {'interface': name, 'rx_bps': rx_bps, 'tx_bps': tx_bps, 'wireless': wireless, 'link_mbps': rate}


def sample():
    return {'gpu': gpu(), 'cpu_temp_c': temperatures(), 'network': network(), 'time': time.time()}


def receive():
    header = sys.stdin.buffer.read(4)
    if not header:
        return None
    if len(header) != 4:
        raise ValueError('Incomplete request')
    length = struct.unpack('<I', header)[0]
    if length > 16384:
        raise ValueError('Request too large')
    data = sys.stdin.buffer.read(length)
    if len(data) != length:
        raise ValueError('Incomplete request')
    return json.loads(data)


def send(message):
    data = json.dumps(message, separators=(',', ':'), allow_nan=False).encode('utf-8')
    sys.stdout.buffer.write(struct.pack('<I', len(data)) + data)
    sys.stdout.buffer.flush()


def main():
    while True:
        try:
            request = receive()
            if request is None:
                break
            if not isinstance(request, dict) or request.get('action') != 'sample':
                send({'error': 'Unknown request'})
                continue
            send(sample())
        except (ValueError, json.JSONDecodeError):
            send({'error': 'Invalid request'})
        except Exception:
            send({'error': 'Local sensor reading unavailable'})


if __name__ == '__main__':
    main()
