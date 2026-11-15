"""Desktop upgrade/restore and native Plasma frame geometry regression checks."""
from pathlib import Path
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import sys
import tempfile
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import desktop_update as desktop


def main():
    desktop.HERE=ROOT;desktop.native.program=lambda name:name
    # Exercise actual command construction, absent keys, gdbus tuple decoding and
    # positive/negative live-report matching before substituting apply fixtures.
    settings={};calls=[];confirmed={'value':True};original_run=desktop.native.run
    def native_command(argv):
        calls.append(argv)
        if argv[-1].endswith('reconfigure'):return ''
        if argv[-1].endswith('supportInformation'):
            return repr(('Decoration\nTheme: '+(settings.get(('kwinrc','org.kde.kdecoration2','theme'),'') if confirmed['value'] else 'OtherTheme')+'\n',))
        filename=Path(argv[argv.index('--file')+1]).name
        group=argv[argv.index('--group')+1];key=argv[argv.index('--key')+1];identity=(filename,group,key)
        if argv[0]=='kreadconfig6':return settings.get(identity,argv[-1])
        if argv[-1]=='--delete':settings.pop(identity,None)
        else:settings[identity]=argv[-1]
        return ''
    desktop.native.run=native_command
    actual_kwin_command=desktop.kwin_command
    desktop.kwin_command=lambda method:['fixture','org.kde.KWin.'+method]
    config=Path('/isolated-test/config')
    assert desktop.decoration(config)=={'library':None,'theme':None}
    selected={'library':'org.kde.kwin.aurorae','theme':'__aurorae__svg__ScarletProtocolGlobal81'}
    desktop.set_decoration(config,selected);assert desktop.decoration(config)==selected
    assert desktop.appearance(config)['kwin_confirmed']
    confirmed['value']=False;assert not desktop.appearance(config)['kwin_confirmed']
    desktop.set_decoration(config,{'library':None,'theme':None});assert desktop.decoration(config)=={'library':None,'theme':None}
    desktop.native.run=original_run;desktop.kwin_command=actual_kwin_command
    print('PASS: native settings command arguments, deletion, D-Bus supportInformation parsing and no false live-confirmation')
    state={'style':'ScarletProtocolPlasma7','decor':{'library':None,'theme':None}}
    desktop.kwin_command=lambda method:['fixture',method]
    desktop.current_style=lambda config:state['style']
    desktop.decoration=lambda config:dict(state['decor'])
    def set_decor(config,values):state['decor']=dict(values)
    desktop.set_decoration=set_decor
    desktop.appearance=lambda config:{'plasma_style':state['style'],'decoration':dict(state['decor']),'icons':'ScarletProtocolIcons','application_style':'Breeze','kwin_confirmed':True}
    def apply_style(name):state['style']=name;return 'Selected '+name
    desktop.apply_style=apply_style
    with tempfile.TemporaryDirectory(prefix='scarlet-desktop-update-') as directory:
        root=Path(directory);data=root/'data';config=root/'config';backups=root/'state';config.mkdir()
        panels='[Containments][9]\nplugin=org.kde.panel\n'
        (config/'plasma-org.kde.plasma.desktop-appletsrc').write_text(panels)
        result=desktop.apply(data,config,backups,widgets=False)
        assert result['changed']==17 and state['style']=='ScarletProtocolPlasma8'
        assert state['decor']=={'library':'org.kde.kwin.aurorae','theme':'__aurorae__svg__ScarletProtocolGlobal81'}
        again=desktop.apply(data,config,backups,night=True,widgets=False)
        assert again['changed']==0 and again['same']==17 and state['style']=='ScarletProtocolNightPlasma8'
        assert state['decor']['theme']=='__aurorae__svg__ScarletProtocolNight81'
        desktop.restore(config,Path(again['backup']));assert state['style']=='ScarletProtocolPlasma8'
        assert state['decor']['theme']=='__aurorae__svg__ScarletProtocolGlobal81'
        desktop.restore(config,Path(result['backup']));assert state['style']=='ScarletProtocolPlasma7'
        assert state['decor']=={'library':None,'theme':None}
        state['decor']={'library':'breeze','theme':'ExistingSelection'}
        keep=desktop.apply(data,config,backups,widgets=False,window_frame=False)
        assert state['decor']['theme']=='ExistingSelection'
        desktop.restore(config,Path(keep['backup']));assert state['decor']['theme']=='ExistingSelection'
        assert (config/'plasma-org.kde.plasma.desktop-appletsrc').read_text()==panels
        def overridden(name):state['style']='AutomaticOverride' if name=='ScarletProtocolPlasma8' else name;return ''
        desktop.apply_style=overridden
        try:desktop.apply(data,config,backups,widgets=False)
        except RuntimeError:pass
        else:raise AssertionError('Expected style readback mismatch')
        assert state['style']=='ScarletProtocolPlasma7' and state['decor']['theme']=='ExistingSelection'
        desktop.apply_style=apply_style
        def rejected(config,values):
            state['decor']=dict(values)
            if values['theme']=='__aurorae__svg__ScarletProtocolGlobal81':state['decor']['theme']='Override'
        desktop.set_decoration=rejected
        try:desktop.apply(data,config,backups,widgets=False)
        except RuntimeError:pass
        else:raise AssertionError('Expected decoration readback mismatch')
        assert state['style']=='ScarletProtocolPlasma7' and state['decor']['theme']=='ExistingSelection'
        legacy=backups/'legacy';legacy.mkdir();(legacy/'desktop-style.json').write_text('{"previous_style":"LegacyStyle"}')
        desktop.restore(config,legacy);assert state['style']=='LegacyStyle'
        assert state['decor']['theme']=='ExistingSelection'
    print('PASS: both editions, default new decoration, opt-out preservation, absent-key restore, legacy restore, repeat install and style/decoration failure rollback (native-command fixture)')
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtSvg import QSvgRenderer
    app=QGuiApplication([]);checked=0
    paths=['dialogs/background.svg','widgets/tooltip.svg','widgets/background.svg','widgets/translucentbackground.svg',
        'widgets/panel-background.svg','widgets/button.svg','widgets/lineedit.svg','widgets/viewitem.svg',
        'widgets/tasks.svg','widgets/bar_meter_horizontal.svg','widgets/bar_meter_vertical.svg']
    nine={'top','bottom','left','right','topleft','topright','bottomleft','bottomright','center'}
    for style in ['ScarletProtocolPlasma8','ScarletProtocolNightPlasma8']:
        for name in paths:
            path=ROOT/'plasma-style'/style/name;svg=QSvgRenderer(str(path));assert svg.isValid()
            for group in ET.parse(path).getroot():
                children=list(group);identity=group.get('id','')
                if identity.rsplit('-',1)[-1] not in nine or len(children)<2 or children[0].tag.rsplit('}',1)[-1]!='rect':continue
                width=float(children[0].get('width',0));height=float(children[0].get('height',0));bounds=svg.boundsOnElement(identity)
                assert bounds.width()<=width+.01 and bounds.height()<=height+.01,(path,identity,bounds)
                checked+=1
    print(f'PASS: {checked} changed FrameSvg tile bounds fit their native footprints')


if __name__=='__main__':main()
