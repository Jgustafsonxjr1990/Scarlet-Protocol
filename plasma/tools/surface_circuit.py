"""Scarlet 7 native Plasma surfaces, retaining masks and compositor shadows."""
from pathlib import Path
import json
import shutil
import xml.etree.ElementTree as ET
from afterglow import ROOT,render_frames,stroke
ET.register_namespace('','http://www.w3.org/2000/svg')


def contacts(path,accent):
    tree=ET.parse(path)
    for group in tree.getroot():
        identity=group.get('id','')
        if identity.startswith(('mask','shadow')) or identity.startswith('hint'):continue
        part=identity.rsplit('-',1)[-1]
        if part not in ('top','bottom','left','right','topleft','topright','bottomleft','bottomright'):continue
        children=list(group)
        if len(children)<2 or children[0].tag.rsplit('}',1)[-1]!='rect':continue
        size=float(children[0].get('width',0))
        if size<10:continue
        inside=children[1];end=size-1
        if part in ('topleft','topright','bottomleft','bottomright'):
            art=stroke(f'M5.5 {end}Q5.5 5.5 {end} 5.5',accent,.65,.8)
            art+=stroke(f'M8 {end}Q8 8 {end} 8','#754052',.55,.65)
            art+=f'<circle cx="{size*.54:.2f}" cy="{size*.54:.2f}" r=".7" fill="{accent}"/>'
        elif part in ('left','right'):
            art=stroke(''.join(f'M4 {size*t:.2f}v{min(2,size/8):.2f}' for t in (.12,.42,.72)),accent,.8,.4)
            art+=stroke('M5.7 5v2','#ffd6e4',.5,.45)
        else:
            art=stroke(''.join(f'M{size*t:.2f} 4h{min(2,size/8):.2f}' for t in (.12,.42,.72)),accent,.8,.4)
        # Keep a fixed tile footprint: no strokes extend beyond its transparent bounds.
        for node in ET.fromstring('<g>'+art.replace('stroke-linecap="round"','stroke-linecap="butt"')+'</g>'):inside.append(node)
    tree.write(path,encoding='unicode')


def build():
    for night,old,new in [(False,'ScarletProtocolPlasma6','ScarletProtocolPlasma7'),
                          (True,'ScarletProtocolNightPlasma6','ScarletProtocolNightPlasma7')]:
        source=ROOT/'plasma-style'/old;style=ROOT/'plasma-style'/new
        shutil.copytree(source,style,dirs_exist_ok=True)
        accent='#c93e62' if night else '#ff315b'
        def item(prefix,face,hot=False,outline=False):
            return (prefix,[(0,accent,.07 if hot else .025),(1,accent,.23 if hot else .07),
                            (2,accent if hot else '#713047',1),(3,'#2b1a26',1)],face,outline)
        w=style/'widgets'
        render_frames(w/'button.svg',[item('normal','#1c1721'),item('hover','#411b2d',True),
            item('pressed','#641d38',True),item('focus','none',True,True),
            item('toolbutton-hover','#371b29',True),item('toolbutton-pressed','#5d1c35',True),
            item('toolbutton-focus','none',True,True)],12)
        render_frames(w/'lineedit.svg',[item('base','#141319'),item('hover','#21151f',True),
            item('focus','#261620',True),item('focusframe','none',True,True)],11)
        render_frames(w/'viewitem.svg',[item('normal','#141319'),item('hover','#381a2a',True),
            item('selected','#501a30',True),item('selected+hover','#6c203d',True)],11)
        render_frames(w/'tasks.svg',[item('normal','#141319'),item('hover','#371a2a',True),
            item('focus','#50192f',True),item('attention','#70223b',True),item('minimized','#111116')],13)
        for path in ['dialogs/background.svg','widgets/tooltip.svg','widgets/background.svg',
                     'widgets/translucentbackground.svg','widgets/panel-background.svg',
                     'widgets/button.svg','widgets/lineedit.svg','widgets/viewitem.svg','widgets/tasks.svg']:
            contacts(style/path,accent)
        # Segmented meter centers repeat at native size rather than stretching into long marks.
        for filename in ('bar_meter_horizontal.svg','bar_meter_vertical.svg'):
            render_frames(w/filename,[item('background','#17131b'),item('bar-active','#c91f4c',True),
                                      item('bar-inactive','#432031')],8)
            tree=ET.parse(w/filename);root=tree.getroot()
            for group in root:
                if group.get('id')=='bar-active-center':
                    vertical='vertical' in filename
                    art=stroke('M1 1h6m-6 6h6' if vertical else 'M1 1v6m6-6v6','#ffb1cb',.6,.55)
                    for mark in ET.fromstring('<g>'+art+'</g>'):list(group)[1].append(mark)
            ET.SubElement(root,'rect',{'id':'bar-active-hint-tile-center','width':'1','height':'1','opacity':'0'})
            tree.write(w/filename,encoding='unicode')
        meta=json.loads((style/'metadata.json').read_text());meta['KPlugin']['Id']=new
        meta['KPlugin']['Version']='7.0.0';meta['KPlugin']['Name']='Scarlet Protocol — '+('Night Shift' if night else 'Blackout')+' 7'
        (style/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    for name,style in [('ScarletProtocolGlobal','ScarletProtocolPlasma7'),('ScarletProtocolNight','ScarletProtocolNightPlasma7')]:
        path=ROOT/'look-and-feel'/name/'contents/defaults'
        text=path.read_text().replace('ScarletProtocolNightPlasma6','ScarletProtocolNightPlasma7').replace('ScarletProtocolPlasma6','ScarletProtocolPlasma7')
        path.write_text(text)
        path=ROOT/'look-and-feel'/name/'metadata.json';meta=json.loads(path.read_text());meta['KPlugin']['Version']='7.0.0';path.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':build()
