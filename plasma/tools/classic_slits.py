"""Restore straight segmented border cuts, retaining the approved rounded frame."""
from pathlib import Path
import shutil,xml.etree.ElementTree as ET
from afterglow import ROOT,stroke
ET.register_namespace('','http://www.w3.org/2000/svg')


def cuts(vertical=False,lower=False,live=True):
    # Straight, perpendicular cuts, as in the supplied notification-header photo.
    # They repeat at a constant logical 32px pitch, independent of window size.
    out=''
    for pos in (16,48,80):
        start,end=(50,61.8) if lower else (12,22)
        path=f'M{pos} {start}V{end}'
        ink='#05060b' if live else '#0b0c11'
        out+=f'<path data-classic-slit="true" data-pitch="32" d="{path}" stroke="{ink}" stroke-width="1.8" stroke-linecap="butt"/>'
        out+=stroke(f'M{pos+1.4} {start+.5}v2.1','#ffb5cf',.6,.53 if live else .22)
    if vertical:out='<g transform="matrix(0 1 1 0 0 0)">'+out+'</g>'
    return out


def decoration(source,target,night):
    shutil.copytree(source,target,dirs_exist_ok=True)
    source_rc=target/(source.name+'rc');source_rc.rename(target/(target.name+'rc'))
    metadata=(target/'metadata.desktop').read_text().replace(source.name,target.name).replace('8.0.0','8.1.0').replace('8 — Obsidian','8.1 — Classic Slits')
    (target/'metadata.desktop').write_text(metadata)
    path=target/'decoration.svg';tree=ET.parse(path)
    for group in tree.getroot():
        identity=group.get('id','')
        if not identity.startswith('decoration-') or 'maximized' in identity:continue
        part=identity.rsplit('-',1)[-1]
        if part=='center':continue
        live='inactive' not in identity;ink=('#c53c62' if night else '#ff315b') if live else '#86506a'
        art=list(group)[1]
        # Seven halo/rim layers plus the original face remain byte-for-byte geometry.
        for node in list(art)[8:]:art.remove(node)
        detail=''
        if part=='top':
            detail+=stroke('M1.1 13H94.9',ink,1.8,1 if live else .6)
            detail+=stroke('M1.1 15H94.9','#ffd8e6',.6,.3 if live else .12)
            detail+=stroke('M1.1 59.6H94.9',ink,1.8,.98 if live else .5)
            detail+=stroke('M1.1 61.5H94.9','#8d3e5e',.7,.7)
            detail+=cuts(live=live)+cuts(lower=True,live=live)
        elif part in ('left','right'):
            detail+=stroke('M13 1.1V94.9',ink,1.8,1 if live else .6)
            detail+=stroke('M23 1.1V94.9','#724052',.65,.65)
            detail+=cuts(vertical=True,live=live)
        elif part=='bottom':
            detail+=stroke('M1.1 13H94.9',ink,1.8,1 if live else .6)
            detail+=stroke('M1.1 23H94.9','#724052',.65,.65)
            detail+=cuts(live=live)
        else:
            detail+=stroke('M30.8 15Q15 15 15 30.8',ink,2.2,.95 if live else .45)
            detail+=stroke('M30.8 18Q18 18 18 30.8','#ffd8e6',.65,.58 if live else .18)
            detail+='<circle cx="22.7" cy="22.7" r="2.5" fill="#05070b" stroke="'+ink+'" stroke-width=".9"/>'
            detail+=stroke('M21.5 22.7h2.4','#ffd8e6',.6,.7 if live else .23)
            if part.startswith('top'):
                detail+=stroke('M15.9 59.6H30.8',ink,1.8,.98 if live else .5)
                detail+='<path data-classic-slit="true" d="M25 50V61.8" stroke="#05060b" stroke-width="1.8"/>'
    
        for node in ET.fromstring('<g>'+detail+'</g>'):art.append(node)
    tree.write(path,encoding='unicode')


def main():
    for old,new,night in [('ScarletProtocolGlobal8','ScarletProtocolGlobal81',False),('ScarletProtocolNight8','ScarletProtocolNight81',True)]:
        decoration(ROOT/'aurorae'/old,ROOT/'aurorae'/new,night)
    for name in ('ScarletProtocolGlobal','ScarletProtocolNight'):
        path=ROOT/'look-and-feel'/name/'contents/defaults';path.write_text(path.read_text().replace(name+'8',name+'81'))


if __name__=='__main__':main()
