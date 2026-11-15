"""Write metadata, native configuration forms and portable shader variants."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
COMMON=[('Strength','Effect strength','Int',85,0,100),('Red','Scarlet color — red','Int',255,0,255),('Green','Scarlet color — green','Int',32,0,255),('Blue','Scarlet color — blue','Int',86,0,255)]

def build():
    specs=[('kwin6_effect_scarlet_vector_wake','Vector Wake — Glitch','Broken scan bands and scarlet image echoes during window movement','wake',
            [('FadeTime','Release fade (ms)','Int',180,80,800),('GlitchOffset','Image tear width (px)','Int',24,4,48),('BandHeight','Glitch band height (px)','Int',14,4,40),('GlitchRate','Glitch changes per second','Int',12,2,24),('EchoAmount','Scarlet image echo (%)','Int',65,0,100)]),
           ('kwin6_effect_scarlet_phase_relay','Phase Relay','An opaque pixel lock-on scan over the newly active window','relay',
            [('Duration','Transition duration (ms)','Int',380,120,900),('CellSize','Scan cell size (px)','Int',14,4,32)])]
    for plugin,title,description,shader,extra in specs:
        folder=ROOT/plugin
        meta={'KPackageStructure':'KWin/Effect','KPlugin':{'Id':plugin,'Name':'Scarlet Protocol — '+title,'Description':description,'Icon':'preferences-system-windows-effect','Category':'Appearance','License':'GPL-2.0-or-later','Version':'2.0.0','EnabledByDefault':False,'Authors':[{'Name':'Scarlet Protocol'}]},'X-KDE-Ordering':65,'X-Plasma-API':'javascript','X-Plasma-MainScript':'code/main.js','X-KDE-ConfigModule':'kcm_kwin4_genericscripted'}
        (folder/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
        cfg=ET.Element('kcfg',{'xmlns':'http://www.kde.org/standards/kcfg/1.0'})
        ET.SubElement(cfg,'kcfgfile',{'name':''})
        group=ET.SubElement(cfg,'group',{'name':''})
        ui=ET.Element('ui',{'version':'4.0'})
        ET.SubElement(ui,'class').text='ScarletConfig'
        widget=ET.SubElement(ui,'widget',{'class':'QWidget','name':'ScarletConfig'})
        layout=ET.SubElement(widget,'layout',{'class':'QFormLayout','name':'formLayout'})
        for row,(key,label,kind,default,minimum,maximum) in enumerate(extra+COMMON):
            entry=ET.SubElement(group,'entry',{'name':key,'type':kind})
            ET.SubElement(entry,'label').text=label
            ET.SubElement(entry,'default').text=str(default)
            ET.SubElement(entry,'min').text=str(minimum);ET.SubElement(entry,'max').text=str(maximum)
            left=ET.SubElement(layout,'item',{'row':str(row),'column':'0'})
            text=ET.SubElement(left,'widget',{'class':'QLabel','name':'label_'+key})
            prop=ET.SubElement(text,'property',{'name':'text'});ET.SubElement(prop,'string').text=label
            right=ET.SubElement(layout,'item',{'row':str(row),'column':'1'})
            control=ET.SubElement(right,'widget',{'class':'QSpinBox','name':'kcfg_'+key})
            for name,value in [('minimum',minimum),('maximum',maximum),('value',default)]:
                prop=ET.SubElement(control,'property',{'name':name});ET.SubElement(prop,'number').text=str(value)
        ET.SubElement(ui,'resources');ET.SubElement(ui,'connections')
        for path,tree in [(folder/'contents/config/main.xml',cfg),(folder/'contents/ui/config.ui',ui)]:
            path.parent.mkdir(parents=True,exist_ok=True);ET.indent(tree);path.write_text(ET.tostring(tree,encoding='unicode')+'\n')
        modern=folder/f'contents/shaders/{shader}_core.frag'
        legacy=modern.with_name(shader+'.frag')
        legacy.write_text(modern.read_text().replace('#version 140','#version 110').replace('in vec2 texcoord0;','varying vec2 texcoord0;').replace('out vec4 fragColor;','').replace('texture(sampler,','texture2D(sampler,').replace('fragColor','gl_FragColor'))

if __name__=='__main__':build()
