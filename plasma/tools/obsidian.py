"""Scarlet 8: sculpted window frames and bold native desktop surfaces."""
from pathlib import Path
import configparser
import json
import shutil
from afterglow import ROOT,stroke,write_svg,render_frames,GLYPHS,STATES,SEMANTIC
import xml.etree.ElementTree as ET
ET.register_namespace('','http://www.w3.org/2000/svg')


def shape(part,w,h,inset):
    if part=='center':return f'M0 0H{w}V{h}H0Z'
    if part in ('top','bottom'):return f'M0 {inset}H{w}V{h}H0Z'
    if part in ('left','right'):return f'M{inset} 0H{w}V{h}H{inset}Z'
    return f'M{w} {inset}A{w-inset} {w-inset} 0 0 0 {inset} {w}V{h}H{w}Z'


def window(folder,night):
    accent='#c53c62' if night else '#ff315b';pale='#ffd8e6';body=''
    parts=[('topleft',0,0,32,64),('top',36,0,96,64),('topright',136,0,32,64),
           ('left',0,68,32,96),('center',36,68,96,96),('right',136,68,32,96),
           ('bottomleft',0,168,32,32),('bottom',36,168,96,32),('bottomright',136,168,32,32)]
    for row,prefix in enumerate(('decoration','decoration-inactive','decoration-maximized','decoration-maximized-inactive')):
        live=not prefix.endswith('inactive');maxed='maximized' in prefix
        ink=accent if live else '#86506a';power=(.67 if night else 1) if live else .22
        bands=[(0,ink,.035*power),(4,ink,.065*power),(8,ink,.15*power),(10,ink,.3*power),
               (12,ink,1),(13,'#882c49' if live else '#462b3b',1),(14,'#2e2530',1)]
        for part,x,y,w,h in parts:
            art=''
            if maxed:art=f'<rect width="{w}" height="{h}" fill="#11131a"/>'
            else:
                if part!='center':
                    for inset,color,alpha in bands:art+=f'<path d="{shape(part,w,h,inset)}" fill="{color}" fill-opacity="{alpha}"/>'
                art+=f'<path d="{shape(part,w,h,15)}" fill="'+('url(#header)' if part.startswith('top') else '#12141b')+'"/>'
            if part=='top':
                line_y=47 if maxed else 59
                art+=f'<rect x="0" y="{line_y-6}" width="{w}" height="7" fill="#05070c"/>'
                art+=stroke(f'M1.2 {line_y}H{w-1.2}',ink,1.7,.95 if live else .45)
                art+=stroke(f'M1.2 {line_y-5.5}H{w-1.2}',pale,.65,.28 if live else .1)
                for pos in (6,24,42,60,78):
                    art+=f'<path d="M{pos} {line_y-4.8}h9l-1.5 2.6h-9Z" fill="{ink}" fill-opacity="{.85 if live else .38}"/>'
                if not maxed:
                    art+=stroke(f'M1.2 15H{w-1.2}',pale,.8,.32*power)
                    # Faint titlebar machining is below the caption's contrast level.
                    art+=stroke('M9 22l7 7m28-7 7 7m28-7 7 7','#d487a6',.6,.08)
            elif not maxed and part in ('left','right'):
                art+='<rect x="15.5" y="0" width="8" height="96" fill="#211b27"/>'
                art+=stroke('M14.9 1.3V94.7',ink,.9,.7)
                art+=stroke('M23.1 1.3V94.7','#825064',.7,.7)
                for pos in (6,38,70):
                    art+=f'<path d="M17 {pos}h5l-2.3 12h-5Z" fill="#030509" stroke="#512237" stroke-width=".7"/>'
                    art+=stroke(f'M21.4 {pos+1}l-1.7 9.5',ink,1.8,.95 if live else .45)
                    art+=stroke(f'M17.3 {pos+1}h2.5',pale,.8,.8 if live else .28)
                    art+=f'<rect x="16.6" y="{pos+19}" width="4.5" height="3" rx=".7" fill="{ink}" fill-opacity="{.85 if live else .35}"/>'
            elif not maxed and part=='bottom':
                art+='<rect x="0" y="15.5" width="96" height="8" fill="#211b27"/>'
                art+=stroke('M1.3 15H94.7',ink,1.2,.8 if live else .35)
                art+=stroke('M1.3 23H94.7','#754358',.65,.65)
                for pos in (6,24,42,60,78):
                    art+=f'<path d="M{pos} 17h9l-2.2 4h-9Z" fill="#04060a" stroke="{ink}" stroke-opacity="{.9 if live else .35}" stroke-width=".7"/>'
            elif not maxed and part in ('topleft','topright','bottomleft','bottomright'):
                art+=stroke('M30.8 15Q15 15 15 30.8',ink,2.2,.95 if live else .45)
                art+=stroke('M30.8 18Q18 18 18 30.8',pale,.65,.58 if live else .18)
                art+='<circle cx="22.7" cy="22.7" r="2.5" fill="#05070b" stroke="'+ink+'" stroke-width=".9"/>'
                art+=stroke('M21.5 22.7h2.4',pale,.6,.7 if live else .23)
                if part.startswith('top'):
                    art+=f'<path d="M16 39h6l-2 10h-6Z" fill="#030509" stroke="{ink}" stroke-width=".7"/>'
                    art+=stroke('M22 58h8',ink,1.7,.9 if live else .35)
            # Stroke endpoints remain inside each native tile's declared footprint.
            flipx=part.endswith('right');flipy=part.startswith('bottom')
            transform=f'translate({w if flipx else 0},{h if flipy else 0}) scale({-1 if flipx else 1},{-1 if flipy else 1})'
            body+=f'<g id="{prefix}-{part}" transform="translate({x},{row*208+y})"><rect width="{w}" height="{h}" opacity="0"/><g transform="{transform}">{art}</g></g>'
    defs='<defs><linearGradient id="header" x1="0" y1="12" x2="0" y2="64" gradientUnits="userSpaceOnUse"><stop stop-color="#302633"/><stop offset=".35" stop-color="#191923"/><stop offset="1" stop-color="#11131b"/></linearGradient></defs>'
    write_svg(folder/'decoration.svg',172,832,defs+body)
    cfg=configparser.ConfigParser(interpolation=None);cfg.optionxform=str;cfg.read(folder/(folder.name+'rc'))
    cfg['General']['ActiveTextColor']='255,225,238,255';cfg['General']['Animation']='180'
    values={'TitleHeight':42,'TitleEdgeTop':4,'TitleEdgeBottom':4,'TitleEdgeLeft':12,'TitleEdgeRight':12,
            'TitleEdgeTopMaximized':4,'TitleEdgeBottomMaximized':4,'ButtonWidth':38,'ButtonHeight':34,'ButtonSpacing':4}
    for edge in ('Left','Right','Bottom'):values['Border'+edge]=12
    for edge in ('Left','Right','Top','Bottom'):values['Padding'+edge]=12
    for key,value in values.items():cfg['Layout'][key]=str(value)
    with (folder/(folder.name+'rc')).open('w') as f:cfg.write(f,space_around_delimiters=False)
    buttons(folder,night)


def buttons(folder,night):
    for name,glyph in GLYPHS.items():
        body=''
        for i,state in enumerate(STATES):
            hot=state.startswith(('hover','pressed'));active=state=='active';disabled=state.startswith('deactivated')
            color=SEMANTIC.get(name,'#ff6289') if hot else '#ff315b' if name=='close' and active else '#d7a6bb' if active else '#865e72'
            plate='M7 3H23L28 8V20L23 25H7L3 20V8Z'
            glow=(.7 if night else 1) if hot else .55 if name=='close' and active else .13
            art=''
            for width,alpha in ((5,.1),(3,.18),(1.8,.3)):art+=stroke(plate,color,width,alpha*glow)
            art+='<path d="'+plate+'" fill="'+('#511c32' if hot else '#261b28' if active else '#1a1721')+'"/>'
            art+=stroke(plate,color,.95,.9 if hot or name=='close' and active else .28)
            art+=stroke('M7 5h11m7 15-4 3H12',color,1.3,.95 if hot else .55)
            art+=stroke('M4 12v4m22-4v4','#ffe0eb',.7,.8 if hot else .23)
            # Original glyph silhouettes and semantic hover colors are retained.
            art+='<g transform="translate(0 1)">'+(stroke(glyph,color,4,.26) if hot else '')+stroke(glyph,color,1.9)+('</g>')
            if hot:art+='<g transform="translate(0 1)">'+stroke(glyph,'#fff0f6',.65,.95)+'</g>'
            if state.startswith('pressed'):art='<g transform="translate(1.5,1.4) scale(.9)">'+art+'</g>'
            body+=f'<g id="{state}-center" transform="translate({i%4*36},{i//4*34})"><rect width="32" height="30" opacity="0"/><g opacity="{.35 if disabled else 1}">{art}</g></g>'
        write_svg(folder/(name+'.svg'),144,68,body)


def plasma(old,new,night):
    target=ROOT/'plasma-style'/new;shutil.copytree(ROOT/'plasma-style'/old,target,dirs_exist_ok=True)
    accent='#c53c62' if night else '#ff315b'
    def item(prefix,face,hot=False,outline=False):
        return (prefix,[(0,accent,.10 if hot else .04),(1,accent,.3 if hot else .12),
                        (2,accent if hot else '#9a3b5b',1),(3,'#ffd4e3',.5 if hot else .13),
                        (4,'#0c0e13',1),(5,'#68374c',.65)],face,outline)
    files={
      'button.svg':([item('normal','url(#metal)'),item('hover','url(#hot)',True),item('pressed','#6a1c39',True),
                    item('focus','none',True,True),item('toolbutton-hover','url(#hot)',True),
                    item('toolbutton-pressed','#6a1c39',True),item('toolbutton-focus','none',True,True)],14),
      'lineedit.svg':([item('base','#10131a'),item('hover','#2b1b29',True),item('focus','#301b2d',True),item('focusframe','none',True,True)],12),
      'viewitem.svg':([item('normal','#15141d'),item('hover','url(#hot)',True),item('selected','#6e203e',True),item('selected+hover','#922d53',True)],12),
      'tasks.svg':([item('normal','url(#metal)'),item('hover','url(#hot)',True),item('focus','#681f3d',True),item('attention','#9a3155',True),item('minimized','#11131a')],14),
    }
    defs='<defs><linearGradient id="metal" x2="0" y2="1"><stop stop-color="#3a2a3e"/><stop offset=".4" stop-color="#211d2b"/><stop offset="1" stop-color="#12151d"/></linearGradient><linearGradient id="hot" x2="0" y2="1"><stop stop-color="#81334f"/><stop offset=".4" stop-color="#4e233a"/><stop offset="1" stop-color="#291927"/></linearGradient></defs>'
    for filename,(entries,size) in files.items():
        path=target/'widgets'/filename;render_frames(path,entries,size)
        tree=ET.parse(path);root=tree.getroot();root.insert(0,ET.fromstring(defs))
        for group in list(root):
            identity=group.get('id','');part=identity.rsplit('-',1)[-1]
            if part in ('topleft','topright','bottomleft','bottomright') and len(list(group))>1:
                art=stroke(f'M{size-1.4} 5.8Q5.8 5.8 5.8 {size-1.4}',accent,1.35,.8)
                art+=stroke(f'M{size-1.4} 8Q8 8 8 {size-1.4}','#ffd8e7',.6,.45)
                for node in ET.fromstring('<g>'+art+'</g>'):list(group)[1].append(node)
        tree.write(path,encoding='unicode')
    for filename in ['dialogs/background.svg','widgets/tooltip.svg','widgets/background.svg','widgets/translucentbackground.svg','widgets/panel-background.svg']:
        path=target/filename;tree=ET.parse(path)
        for group in tree.getroot():
            identity=group.get('id','');part=identity.rsplit('-',1)[-1]
            if identity.startswith(('mask','shadow','hint')):continue
            children=list(group)
            if len(children)<2 or children[0].tag.rsplit('}',1)[-1]!='rect':continue
            size=float(children[0].get('width',0))
            art=''
            if part in ('topleft','topright','bottomleft','bottomright'):
                end=size-3.0
                art+=stroke(f'M{end} 5Q5 5 5 {end}','#341e30',5.2)
                art+=stroke(f'M{end} 5Q5 5 5 {end}',accent,1.75,.95)
                art+=stroke(f'M{end} 8Q8 8 8 {end}','#ffb5d0',.75,.62)
                art+=f'<circle cx="{size*.58}" cy="{size*.58}" r="1.35" fill="#080b11" stroke="{accent}" stroke-width=".7"/>'
            elif part in ('left','right'):
                for pos in (size*.15,size*.65):art+=f'<rect x="3.5" y="{pos}" width="2.6" height="{size*.18}" rx=".5" fill="{accent}" fill-opacity=".7"/>'
            elif part in ('top','bottom'):
                for pos in (size*.15,size*.65):art+=f'<rect x="{pos}" y="3.5" width="{size*.18}" height="2.6" rx=".5" fill="{accent}" fill-opacity=".7"/>'
            for node in ET.fromstring('<g>'+art+'</g>'):children[1].append(node)
        tree.write(path,encoding='unicode')
    meta=json.loads((target/'metadata.json').read_text());meta['KPlugin']['Id']=new
    meta['KPlugin']['Version']='8.0.0';meta['KPlugin']['Name']='Scarlet Protocol — '+('Night Shift' if night else 'Blackout')+' 8 — Obsidian'
    (target/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')


def build():
    plasma('ScarletProtocolPlasma7','ScarletProtocolPlasma8',False)
    plasma('ScarletProtocolNightPlasma7','ScarletProtocolNightPlasma8',True)
    for night,old,new in [(False,'ScarletProtocolGlobal6','ScarletProtocolGlobal8'),(True,'ScarletProtocolNight6','ScarletProtocolNight8')]:
        source=ROOT/'aurorae'/old;target=ROOT/'aurorae'/new;shutil.copytree(source,target,dirs_exist_ok=True)
        (target/(old+'rc')).rename(target/(new+'rc'))
        metadata=(target/'metadata.desktop').read_text().replace(old,new).replace('6.1.0','8.0.0')
        metadata=metadata.replace('Blackout 6','Blackout 8 — Obsidian').replace('Night Shift 6','Night Shift 8 — Obsidian')
        (target/'metadata.desktop').write_text(metadata);window(target,night)
    for name,decor in [('ScarletProtocolGlobal','ScarletProtocolGlobal8'),('ScarletProtocolNight','ScarletProtocolNight8')]:
        path=ROOT/'look-and-feel'/name/'contents/defaults';text=path.read_text().replace('ScarletProtocolNightPlasma7','ScarletProtocolNightPlasma8').replace('ScarletProtocolPlasma7','ScarletProtocolPlasma8').replace('__aurorae__svg__ScarletProtocolGlobal6','__aurorae__svg__ScarletProtocolGlobal8').replace('__aurorae__svg__ScarletProtocolNight6','__aurorae__svg__ScarletProtocolNight8');path.write_text(text)
        path=ROOT/'look-and-feel'/name/'metadata.json';data=json.loads(path.read_text());data['KPlugin']['Version']='8.0.0';path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':build()
