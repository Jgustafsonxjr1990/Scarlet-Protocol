"""Scarlet vector palette, cyber housings and app-specific glyphs."""
import colorsys
import html
import re
import xml.etree.ElementTree as ET

NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)
ET.register_namespace('xlink','http://www.w3.org/1999/xlink')
ACCENT='#ff315b'


def scarlet_color(value, symbolic=False):
    raw=value.lstrip('#')
    if len(raw)==3: raw=''.join(x*2 for x in raw)
    if len(raw)!=6: return value
    r,g,b=(int(raw[i:i+2],16)/255 for i in (0,2,4))
    hue,sat,light=colorsys.rgb_to_hsv(r,g,b)
    # Keep distinct success/warning states and neutral black/white structure.
    if sat>.35 and .20<hue<.48: return '#38ea77'
    if sat>.45 and .06<hue<.20: return '#ffd43b'
    luminance=.2126*r+.7152*g+.0722*b
    if symbolic and luminance>.35: return '#ff668b'
    if luminance<.08: return '#0c0e13'
    if luminance<.22: return '#27141f'
    if luminance<.40: return '#741d3a'
    if luminance<.62: return '#c22551'
    if luminance<.88: return '#ff466f'
    return '#f7cfdd'


def recolor_svg(data, symbolic=False):
    root=ET.fromstring(data)
    paint={'fill','stroke','stop-color','flood-color','color','style','lighting-color'}
    color=re.compile(r'#[0-9a-fA-F]{6}(?![0-9a-fA-F])|#[0-9a-fA-F]{3}(?![0-9a-fA-F])')
    def convert(text):
        # Gradient references are identifiers, not literal paint colors.
        urls=[]
        def hold(m): urls.append(m.group());return f'__SCARLET_URL_{len(urls)-1}__'
        text=re.sub(r'url\([^)]*\)',hold,text)
        text=color.sub(lambda m:scarlet_color(m.group(),symbolic),text)
        for i,url in enumerate(urls): text=text.replace(f'__SCARLET_URL_{i}__',url)
        return text
    # A few upstream files reuse a gradient ID on the painted path. Keep the
    # paint server's ID so url(#name) still resolves; rename the shape instead.
    groups={}
    for node in root.iter():
        if node.get('id'):groups.setdefault(node.get('id'),[]).append(node)
    definitions={'linearGradient','radialGradient','pattern','filter','clipPath','mask','symbol'}
    seen_ids=set(groups)
    for identity,nodes in groups.items():
        canonical=next((n for n in nodes if n.tag.rsplit('}',1)[-1] in definitions),nodes[0])
        for node in nodes:
            if node is canonical:continue
            suffix=2
            while f'{identity}-scarlet-{suffix}' in seen_ids:suffix+=1
            node.set('id',f'{identity}-scarlet-{suffix}');seen_ids.add(node.get('id'))
    for node in root.iter():
        for key,value in list(node.attrib.items()):
            if key=='filter':
                del node.attrib[key]
                continue
            if key.endswith('href') and value.startswith('#') and value[1:] not in seen_ids:
                del node.attrib[key]
                continue
            if key=='style':value=re.sub(r'filter\s*:[^;]+;?','',value)
            if key in paint:
                value=re.sub(r'url\(#([^)]*)\)',lambda m:m.group() if m.group(1) in seen_ids else 'currentColor',value)
                node.set(key,convert(value))
        if node.tag.rsplit('}',1)[-1]=='style' and node.text: node.text=convert(node.text)
    # Explicit base currentColor prevents an unclassified SVG becoming black on carbon.
    root.set('color','#ff668b' if symbolic else '#ff466f')
    return ET.tostring(root,encoding='unicode')+'\n'


def line(path,color=ACCENT,width=1.5):
    return f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'


GLYPHS={
 'vscode':'M3 8l4-3 13-4v22L7 19l-4-3 10-8v8L3 8M7 5l6 7-6 7',
 'kate':'M5 3h11l3 3v15H5zM9 16l10-12 2 2L11 18l-4 2z',
 'neovim':'M4 4v16l4-3V8l9 13 3-2V3l-4 3v10L7 3z',
 'store':'M4 7h16l-1 14H5zM8 7V5a4 4 0 0 1 8 0v2M12 10v7m-3-3 3 3 3-3',
 'eye':'M5 2h9l5 5v15H5zM8 13q4-6 8 0-4 6-8 0M13.2 13a1.2 1.2 0 1 1-2.4 0 1.2 1.2 0 0 1 2.4 0',
 'gimp':'M3 8l5 2 5-2 7-4 1 10c-1 8-14 10-18 3zM7 14h.1m7-2h.1M8 18l7-1m1-2 6 6',
 'cone':'M10 2h4l6 18H4zM8 8h8M6 14h12M2 22h20',
 'onion':'M12 2v6c-9 2-10 13 0 14 10-1 9-12 0-14M12 8c-5 5-5 11 0 14 5-3 5-9 0-14M12 8v14M12 5l5-3',
 'git':'M12 2 22 12 12 22 2 12zM9 7l7 7M9 7v10m-1-10h2M8 17h2m5-3h2',
 'terminal':'M6 8l4 4-4 4m7 0h5',
 'code':'M8 7l-5 5 5 5m8-10 5 5-5 5m-3-13-2 16',
 'browser':'M20 12a8 8 0 1 1-16 0 8 8 0 0 1 16 0M4 12h16M12 4c-5 4-5 12 0 16 5-4 5-12 0-16',
 'chrome':'M20 12a8 8 0 1 1-16 0 8 8 0 0 1 16 0M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0M12 9h7m-5 5-3 6m-2-8L5 6',
 'firefox':'M7 5 5 2l-2 7a9 9 0 1 0 15-4l1 6-5-1 2 4-5 3-5-4 2-4',
 'brave':'M7 3h10l4 5-2 9-7 5-7-5-2-9zM8 8h8l-1 6-3 3-3-3z',
 'edge':'M20 15c-4 9-17 6-16-3C4 2 20 2 20 11H8c0 7 8 7 12 4M8 11c-1-5 7-7 9-1',
 'mail':'M3 6h18v13H3zM3 6l9 7 9-7',
 'music':'M9 17V5l10-2v12M9 17c0 4-7 4-6 0 1-3 6-3 6 0m10-2c0 4-7 4-6 0 1-3 6-3 6 0M9 8l10-2',
 'video':'M4 4h16v16H4zM9 8l7 4-7 4zM4 8h3m10 0h3M4 16h3m10 0h3',
 'photo':'M3 5h18v15H3zM3 17l6-6 4 4 3-3 5 5M18 8h.1',
 'brush':'M9 14 19 3l2 2-10 12M9 14l2 3c-1 5-4 5-8 4 3-1 1-6 6-7',
 'vector':'M4 4h4v4H4zM16 16h4v4h-4zM6 8c0 8 12 0 12 8M6 8v8m4-10h6M4 16h4v4H4zM16 4h4v4h-4z',
 'cube':'M12 3 22 8v9l-10 5-10-5V8zM2 8l10 5 10-5M12 13v9M7 5l10 5',
 'camera':'M3 7h5l2-3h5l2 3h4v14H3zM16 13a4 4 0 1 1-8 0 4 4 0 0 1 8 0',
 'obs':'M12 3c8-1 12 8 7 13-1-6-8-9-11-4M20 16c-3 8-13 9-17 2 6 2 12-3 9-7M3 18C-2 12 2 2 10 3c-4 4-3 12 3 12',
 'chat':'M3 4h18v13H10l-6 5v-5H3zM7 9h10M7 12h7',
 'discord':'M5 7 9 5l1 2h4l1-2 4 2 3 12-6 2-1-3H9l-1 3-6-2zM8 12v2m8-2v2',
 'telegram':'M2 10 22 2l-5 20-6-7-5 3 1-7 10-5-8 8',
 'signal':'M5 5l2-2m3-1h4m3 1 2 2m2 3v4m-1 4-2 3m-3 2h-4m-4-1-4 2 1-5m-2-3v-4M7 9h10M7 13h7',
 'steam':'M16 4a5 5 0 1 1 0 10 5 5 0 0 1 0-10M19 9a3 3 0 1 1-6 0 3 3 0 0 1 6 0M12 12l-5 6-5-3M9 18a3 3 0 1 1-6 0 3 3 0 0 1 6 0',
 'game':'M6 7h12l4 11-3 2-5-4h-4l-5 4-3-2zM6 12h5m-2.5-2.5v5M16 11h.1m2 3h.1',
 'spotify':'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0M6 9q6-3 12 0M7 13q5-2 10 0M8 16q4-1.5 8 0',
 'lock':'M5 10h14v12H5zM8 10V6a4 4 0 0 1 8 0v4M12 15v3',
 'shield':'M12 2 21 6v7c0 5-6 8-9 10-3-2-9-5-9-10V6zM8 12l3 3 5-6',
 'network':'M12 3v7M4 17v-4h16v4M9 2h6v4H9zM1 17h6v5H1zM17 17h6v5h-6z',
 'radar':'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0M17 12a5 5 0 1 1-10 0 5 5 0 0 1 10 0M12 12l7-7M12 12h.1',
 'shark':'M3 18h18l-5-5-1-11-6 10-6 2 5 1z',
 'bug':'M8 9h8v8a4 4 0 0 1-8 0zM9 9V7a3 3 0 0 1 6 0v2M5 10l3 2m8 0 3-2M4 16h4m8 0h4M5 22l4-3m6 0 4 3M12 11v8',
 'docker':'M2 12h16l3-4 2 2-3 6c-3 7-16 7-18-4M4 7h4v4H4zM9 7h4v4H9zM14 7h4v4h-4zM9 2h4v4H9z',
 'chip':'M6 6h12v12H6zM9 9h6v6H9zM8 2v4m4-4v4m4-4v4M8 18v4m4-4v4m4-4v4M2 8h4m-4 4h4m-4 4h4m12-8h4m-4 4h4m-4 4h4',
 'monitor':'M2 3h20v14H2zM12 17v5m-6 0h12M5 7h5M5 11h10',
 'files':'M3 6h7l2 3h10v12H3zM3 6V3h8l2 3h6v3',
 'document':'M5 2h9l5 5v15H5zM14 2v6h5M8 12h8M8 16h8',
 'sheet':'M4 3h16v18H4zM4 8h16M9 8v13M4 13h16M4 17h16',
 'slides':'M3 3h18v13H3zM12 16v6m0-3-5 3m5-3 5 3M8 7l8 3-8 3z',
 'calendar':'M3 5h18v17H3zM3 10h18M7 2v6m10-6v6M7 14h3m4 0h3m-10 4h3',
 'clock':'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0M12 6v6l4 3',
 'settings':'M8 3h8l1 4 4 1v8l-4 1-1 4H8l-1-4-4-1V8l4-1zM16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0',
 'archive':'M4 3h16v19H4zM4 7h16M10 3v5h4v4h-4v4h4v4',
 'cloud':'M6 19a5 5 0 0 1-1-10 7 7 0 0 1 13-2 6 6 0 0 1 0 12M12 11v11m-4-4 4 4 4-4',
 'phone':'M7 2h10v20H7zM10 5h4m-2 14h.1',
 'star':'M12 2l3 7 8 1-6 5 2 8-7-4-7 4 2-8-6-5 8-1z',
 'home':'M2 11 12 2l10 9M5 9v13h5v-7h4v7h5V9',
 'download':'M12 2v13m-6-6 6 6 6-6M3 16v6h18v-6',
 'paw':'M7 13c-4 5-2 9 2 7 2-1 4-1 6 0 4 2 6-2 2-7-4-5-6-5-10 0M5 6c-3-3-4 4-1 4 2 0 3-2 1-4M10 3C7-1 6 6 9 7c2 1 3-1 1-4M16 3c-1-4-4-2-3 2 1 3 4 2 3-2M21 7c0-4-4-3-4 0 0 3 4 4 4 0',
}


def housing(glyph, label='', folder=False):
    body='<defs><linearGradient id="carbon" x2="0" y2="1"><stop stop-color="#2a1723"/><stop offset="1" stop-color="#101116"/></linearGradient></defs>'
    if folder:
        body+='<path d="M2 6Q2 4 4 4h6l2 3h8q2 0 2 2v10q0 2-2 2H4q-2 0-2-2Z" fill="url(#carbon)" stroke="#ff315b" stroke-width=".8"/>'
        body+=line('M3 8h18M4 19h3m10 0h3','#91253f',.6)
        body+='<g transform="translate(5.5 9) scale(.55)">'+line(glyph,'#ff6287',1.7)+'</g>'
    else:
        body+='<rect x="1" y="1" width="22" height="22" rx="6" fill="url(#carbon)" stroke="#8d2140" stroke-width=".7"/>'
        body+=line('M3 9V7q0-4 4-4h5m9 12v2q0 4-4 4h-5','#ff315b',.75)
        body+=line('M3 12v2m18-11v2m-1-3h-2','#ffd5e0',.55)
        body+='<g transform="translate(4 4) scale(.66667)">'+line(glyph,'#ff6d92',1.65)+'</g>'
        body+='<path d="M9 21h1m2 0h1m2 0h1" stroke="#ff315b" stroke-width=".7"/>'
    return f'<svg xmlns="{NS}" width="64" height="64" viewBox="0 0 24 24"><title>{html.escape(label)}</title>{body}</svg>\n'


def monogram(label):
    words=re.findall(r'[\w]+',label,flags=re.UNICODE)
    initials=''.join(w[0] for w in words[:2]).upper() or '?'
    body=housing('',label).replace('</svg>',f'<text x="12" y="15.5" font-family="sans-serif" font-weight="bold" font-size="8" text-anchor="middle" fill="#ffd5e0">{html.escape(initials)}</text></svg>')
    return body
