"""Scarlet Protocol 6 artwork. All exported parts are native Plasma SVGs."""
from pathlib import Path
import json
import math
import xml.etree.ElementTree as ET
from afterglow import ROOT, NINE, frame, stroke, write_svg, render_frames
ET.register_namespace('', 'http://www.w3.org/2000/svg')


def decorate_frame(folder, night=False):
    from window_art import make_decoration
    make_decoration(folder/'decoration.svg',night)
    cfg = folder/(folder.name+'rc')
    text=cfg.read_text()
    import re
    for edge in ['Left','Right','Bottom']:
        text=re.sub(r'(?m)^Border'+edge+r'=\d+$','Border'+edge+'=8',text)
    cfg.write_text(text)
    controls(folder,night)


def controls(folder,night):
    from afterglow import GLYPHS, STATES, SEMANTIC
    for name,glyph in GLYPHS.items():
        body=''
        for i,state in enumerate(STATES):
            lit=state.startswith(('hover','pressed'))
            idle=state=='active'
            disabled=state.startswith('deactivated')
            color=SEMANTIC.get(name,'#ff547b') if lit else '#ec315b' if name=='close' and idle else '#b28c9a' if idle else '#735c68'
            glow=(.65 if night else 1) if lit else .36 if name=='close' and idle else 0
            shape='M9 4H21L26 9V17L21 22H9L4 17V9Z'
            out=''
            for weight,alpha in ((7,.055),(4,.12),(2.6,.20)):
                out+=stroke(shape,color,weight,alpha*glow)
            out+='<path d="'+shape+'" fill="'+('#34151f' if lit else '#19151d')+'"/>'
            out+=stroke('M4 10V9L9 4H18M26 16v1l-5 5H12',color,1.1,.95 if lit or name=='close' and idle else .28)
            out+=stroke('M9.5 6H17m3 14h-7','#f6c6d4',.6,.5 if lit else .12)
            out+=stroke('M2 13h2m22 0h2',color,1,.9 if lit else .32)
            if lit: out+=stroke(glyph,color,4,.3)
            out+=stroke(glyph,color,1.9 if lit else 1.65)
            if lit: out+=stroke(glyph,'#fff0f3',.65,.9)
            if state.startswith('pressed'): out='<g transform="translate(1.5,1.3) scale(.9)">'+out+'</g>'
            body+=f'<g id="{state}-center" transform="translate({i%4*34},{i//4*30})"><rect width="30" height="26" opacity="0"/><g opacity="{.3 if disabled else 1}">{out}</g></g>'
        write_svg(folder/(name+'.svg'),136,60,body)


def surfaces(style,night=False):
    accent='#c93e62' if night else '#ff315b'
    def item(prefix,face,bright=False,outline=False):
        return (prefix,[(0,accent,.07 if bright else .025),(1,accent,.22 if bright else .08),
                (2,accent if bright else '#653043',1),(3,'#271a24',1)],face,outline)
    w=style/'widgets'
    render_frames(w/'button.svg',[item('normal','#1b1720'),item('hover','#361b28',True),
        item('pressed','#561c30',True),item('focus','none',True,True),
        item('toolbutton-hover','#321925',True),item('toolbutton-pressed','#531a2c',True),
        item('toolbutton-focus','none',True,True)],10)
    render_frames(w/'viewitem.svg',[item('normal','#16151b'),item('hover','#2c1a25',True),
        item('selected','#42182a',True),item('selected+hover','#5a1b31',True)],10)
    render_frames(w/'tasks.svg',[item('normal','#15141b'),item('hover','#2d1a25',True),
        item('focus','#42172a',True),item('attention','#622333',True),item('minimized','#111117')],12)
    render_frames(w/'panel-background.svg',[item('','#101116')],18)
    # Add a fixed corner contact to popup faces, retaining all native mask/shadow parts.
    for name in ['dialogs/background.svg','widgets/tooltip.svg']:
        p=style/name
        tree=ET.parse(p)
        for node in tree.getroot():
            if node.get('id') in ('topleft','topright'):
                corner=list(node)[1]
                for child in list(corner):
                    if child.get('d')=='M7 12Q7 7 12 7':corner.remove(child)
                for mark in ET.fromstring('<g>'+stroke('M7 12Q7 7 12 7',accent,.7,.8)+'</g>'):
                    corner.append(mark)
        tree.write(p,encoding='unicode')
    clock(style,accent)


def clock(style,accent):
    face='<circle cx="64" cy="64" r="61" fill="#101116" stroke="#462332"/>'
    face+='<circle cx="64" cy="64" r="56" fill="none" stroke="'+accent+'" stroke-width="1.4"/>'
    face+='<circle cx="64" cy="64" r="42" fill="none" stroke="#452331" stroke-width=".6"/>'
    for n in range(60):
        angle=math.radians(n*6)
        inner=46 if n%5==0 else 50
        face+=stroke(f'M{64+inner*math.sin(angle):.3f} {64-inner*math.cos(angle):.3f}L{64+53*math.sin(angle):.3f} {64-53*math.cos(angle):.3f}',accent if n%5==0 else '#80616e',1.4 if n%5==0 else .6,.9)
    face+=stroke('M59 30h10m-5-3v6',accent,1,.75)
    face+='<text x="64" y="91" text-anchor="middle" font-family="sans-serif" font-size="5.5" letter-spacing="1" fill="#ac7185">SCARLET</text>'
    out='<g id="ClockFace">'+face+'</g>'
    out+='<rect id="HourHand" x="148" y="45" width="6" height="21" rx="3" fill="#f8dce6"/>'
    out+='<rect id="MinuteHand" x="172" y="38" width="4" height="28" rx="2" fill="'+accent+'"/>'
    out+='<rect id="SecondHand" x="194" y="30" width="2" height="36" rx="1" fill="#ff6483"/>'
    out+='<circle id="HandCenterScrew" cx="64" cy="64" r="4" fill="'+accent+'" stroke="#ffe3eb" stroke-width="1"/>'
    out+='<circle id="Glass" cx="64" cy="64" r="59" fill="none" stroke="'+accent+'" stroke-opacity=".1" stroke-width="3"/>'
    write_svg(style/'widgets/clock.svg',210,128,out)


def build():
    for night,gid,sid in [(False,'ScarletProtocolGlobal6','ScarletProtocolPlasma6'),(True,'ScarletProtocolNight6','ScarletProtocolNightPlasma6')]:
        decorate_frame(ROOT/'aurorae'/gid,night)
        surfaces(ROOT/'plasma-style'/sid,night)
    icons = {
        'org.kde.konsole': ('apps','M5 7l5 5-5 5m7 0h7'),
        'org.kde.kate': ('apps','M6 4h9l4 4v12H6zM10 10h5m-5 4h5'),
        'org.kde.spectacle': ('apps','M4 8h4l2-3h4l2 3h4v12H4zM16 14a4 4 0 1 1-8 0 4 4 0 0 1 8 0'),
        'preferences-system-time': ('apps','M20 12a8 8 0 1 1-16 0 8 8 0 0 1 16 0M12 6v6l4 2'),
        'view-calendar': ('actions','M4 6h16v15H4zM4 10h16M8 3v5m8-5v5M8 14h2m4 0h2m-8 3h2'),
        'appointment-new': ('actions','M4 6h16v15H4zM4 10h16M8 3v5m8-5v5M12 13v5m-2.5-2.5h5'),
    }
    for name,(category,glyph) in icons.items():
        folder=ROOT/'icons/ScarletProtocolIcons'/category/'scalable'
        folder.mkdir(parents=True,exist_ok=True)
        body='<rect x="1" y="1" width="22" height="22" rx="7" fill="#14141c" stroke="#6a2541"/>'
        body+=stroke('M3 9V7a4 4 0 0 1 4-4h6m8 12v2a4 4 0 0 1-4 4h-5','#e41951',.7,.9)
        body+=stroke(glyph,'#ff426b',1.4)
        write_svg(folder/(name+'.svg'),24,24,body)
    for group in ['look-and-feel','plasma-style']:
        for p in (ROOT/group).glob('*/metadata.json'):
            meta=json.loads(p.read_text());meta['KPlugin']['Version']='6.1.0'
            if group=='plasma-style' and not meta['KPlugin']['Name'].endswith(' 6'):
                meta['KPlugin']['Name']+=' 6'
            p.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    for p in (ROOT/'aurorae').glob('*/metadata.desktop'):
        lines=p.read_text().replace('Version=5.0.0','Version=6.1.0').replace('Version=6.0.0','Version=6.1.0').splitlines()
        lines=[line+' 6' if line.startswith('Name=') and not line.endswith(' 6') else line for line in lines]
        p.write_text('\n'.join(lines)+'\n')


if __name__=='__main__':build()
