"""Resizable Aurorae slot artwork; also used by the appearance customizer."""
import xml.etree.ElementTree as ET
from afterglow import frame, stroke, write_svg

PRESETS = {
    'stealth': dict(slots='sparse', glow=32, frame_width=6, title_height=31),
    'signature': dict(slots='normal', glow=75, frame_width=8, title_height=34),
    'overdrive': dict(slots='dense', glow=100, frame_width=10, title_height=36),
}


def make_decoration(path, night=False, slots='normal', glow=75, frame_width=8):
    if slots not in ('off', 'sparse', 'normal', 'dense') or not 0 <= glow <= 100 or not 6 <= frame_width <= 10:
        raise ValueError('Invalid window appearance values')
    accent = '#bf365b' if night else '#ff315b'
    power = glow / 100 * (.65 if night else 1)
    active = [(0,accent,.045*power),(3,accent,.075*power),(6,accent,.15*power),
              (8,accent,.24*power),(9,accent,.46*power),(10,accent,1),
              (11,'#6d2038',1),(12,'#20171f',1)]
    inactive = [(0,'#000000',.015),(5,'#000000',.09),(9,'#6f3b4d',.18),
                (10,'#68404e',1),(11,'#272029',1)]
    body = ''
    positions = {'off': [], 'sparse': [8], 'normal': [4,16], 'dense': [3,11,19]}[slots]
    # The strip stays outside the client edge (10px shadow + chosen border).
    depth = frame_width - 2.6
    for row, prefix in enumerate(('decoration','decoration-inactive',
                                  'decoration-maximized','decoration-maximized-inactive')):
        live = not prefix.endswith('inactive')
        svg = ET.fromstring('<svg>'+frame(prefix,row*76,24,active if live else inactive,
                                          '#101116' if live else '#15141a')+'</svg>')
        for group in svg:
            part = group.get('id').removeprefix(prefix+'-')
            art = ''
            ink = accent if live else '#805564'
            strength = 1 if live else .43
            if 'maximized' in prefix:
                # Flush fullscreen edges; no invisible side borders or fake vents.
                if part == 'top':
                    art += stroke('M.7 .7h22.6',ink,1,.75*strength)
            elif part != 'center':
                if part in ('topleft','topright','bottomleft','bottomright'):
                    art += stroke('M13.2 22Q13.2 13.2 22 13.2','#05070b',3.5)
                    art += stroke('M13.3 23.4Q13.3 13.3 23.4 13.3',ink,.85,strength)
                    art += stroke('M16 23.5Q16 16 23.5 16','#9c3e57',.65,.8*strength)
                    art += stroke('M14.2 19.5l2.2 1.1m2.4-6.4 1.2 2.1','#ffe1e9',.8,.85*strength)
                    art += '<circle cx="17.8" cy="17.8" r="1.05" fill="#05070b" stroke="'+ink+'" stroke-width=".65"/>'
                else:
                    vertical = part in ('left','right')
                    # Draw horizontal then rotate into the vertical edge's local coordinates.
                    details = stroke('M.6 11.5h22.8',ink,.55,.35*strength)
                    details += stroke(f'M.6 {10+frame_width-.6}h22.8','#502332',.7,.8*strength)
                    for y in positions:
                        # Angled recessed opening, red lower lip, fine pale contact.
                        details += f'<path data-slot="true" d="M{y} 12.2h4.5l-1.8 {depth:.2f}h-4.5Z" fill="#030509" stroke="#46202e" stroke-width=".55"/>'
                        details += stroke(f'M{y+3.9} 12.6l-1.35 {depth-.8:.2f}',ink,1.05,strength)
                        details += stroke(f'M{y+.4} 12.45h2.2','#ffe1e9',.55,.55*strength)
                    if vertical: details = '<g transform="matrix(0 1 1 0 0 0)">'+details+'</g>'
                    art += details
            # Round line caps at tile joins would extend the SVG element bounds,
            # changing KSvg's measured tile size and blurring repeated segments.
            art = art.replace('stroke-linecap="round"','stroke-linecap="butt"')
            for node in ET.fromstring('<g>'+art+'</g>'):
                list(group)[1].append(node)
        body += ''.join(ET.tostring(g,encoding='unicode') for g in svg)
    # No hint-stretch-borders: KSvg repeats edge tiles instead of stretching slots.
    write_svg(path,88,304,body)
