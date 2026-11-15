"""Apply and verify Scarlet's desktop surfaces and detailed window decoration."""
from pathlib import Path
import json
import os
import shutil
import tempfile
import ast
import re
import time
import icon_studio as native
import upgrade

HERE=Path(__file__).resolve().parent


def reload_panels():
    """Reload widget QML and menu caches through Plasma's existing user service."""
    systemctl=shutil.which('systemctl')
    if not systemctl:return 'Panel reload unavailable; sign out and back in to load the repaired widgets.'
    command=[systemctl,'--user']
    try:
        if native.run(command+['is-active','plasma-plasmashell.service'])!='active':
            return 'Plasma is not managed by its user service; sign out and back in to load the repaired widgets.'
    except Exception:
        return 'Plasma user service unavailable; sign out and back in to load the repaired widgets.'
    native.run(command+['restart','plasma-plasmashell.service'])
    if native.run(command+['is-active','plasma-plasmashell.service'])!='active':
        raise RuntimeError('Plasma panel service has not returned to active. Sign out and back in to refresh the desktop.')
    return 'Plasma panels reloaded. Application windows were kept open.'


def current_style(config_home):
    return native.run([native.program('kreadconfig6'),'--file',str(config_home/'plasmarc'),
                       '--group','Theme','--key','name','--default','default'])


def apply_style(name):
    return native.run([native.program('plasma-apply-desktoptheme'),name])


def decoration(config_home):
    result={}
    for key in ('library','theme'):
        value=native.run([native.program('kreadconfig6'),'--file',str(config_home/'kwinrc'),'--group','org.kde.kdecoration2','--key',key,'--default',native.ABSENT])
        result[key]=None if value==native.ABSENT else value
    return result


def kwin_command(method):
    for name in ('qdbus6','qdbus-qt6','qdbus'):
        if program:=shutil.which(name):return [program,'org.kde.KWin','/KWin','org.kde.KWin.'+method]
    return [native.program('gdbus'),'call','--session','--dest','org.kde.KWin','--object-path','/KWin','--method','org.kde.KWin.'+method]


def set_decoration(config_home,values):
    for key,value in values.items():
        argv=[native.program('kwriteconfig6'),'--file',str(config_home/'kwinrc'),'--group','org.kde.kdecoration2','--key',key]
        native.run(argv+(['--delete'] if value is None else [value]))
    native.run(kwin_command('reconfigure'))


def appearance(config_home):
    result={'plasma_style':current_style(config_home),'decoration':decoration(config_home),
            'icons':native.setting(config_home,'Icons','Theme'),'application_style':native.setting(config_home,'KDE','widgetStyle'),
            'kwin_confirmed':False}
    try:
        info=native.run(kwin_command('supportInformation'))
        if info.startswith('('):
            try:info=ast.literal_eval(info)[0]
            except (ValueError,SyntaxError,TypeError):pass
        expected=result['decoration']['theme']
        result['kwin_confirmed']=bool(expected and re.search(r'(?m)^\s*Theme:\s*'+re.escape(expected)+r'\s*$',info))
    except Exception:pass
    return result


def panel_command(night):
    script='var scarletNightShift = '+str(night).lower()+';\n'+(HERE/'tools/panel_tools.js').read_text()
    for program in ('qdbus6','qdbus-qt6','qdbus'):
        if executable:=shutil.which(program):
            return [executable,'org.kde.plasmashell','/PlasmaShell','org.kde.PlasmaShell.evaluateScript',script]
    return [native.program('gdbus'),'call','--session','--dest','org.kde.plasmashell','--object-path','/PlasmaShell',
            '--method','org.kde.PlasmaShell.evaluateScript',script]


def apply(data_home,config_home,state_home,night=False,widgets=True,window_frame=True):
    if hasattr(os,'geteuid') and os.geteuid()==0:raise RuntimeError('Open Desktop Studio as your normal user, without sudo.')
    native.program('plasma-apply-desktoptheme');native.program('kreadconfig6')
    command=panel_command(night) if widgets else None
    previous=current_style(config_home)
    previous_decoration=decoration(config_home) if window_frame else None
    if window_frame:native.program('kwriteconfig6');kwin_command('reconfigure')
    upgrade.HERE=HERE
    changed,same,component_backup=upgrade.upgrade(data_home,state_home)
    state_home.mkdir(parents=True,exist_ok=True)
    backup=Path(tempfile.mkdtemp(prefix='before-desktop-update-',dir=state_home));backup.chmod(0o700)
    (backup/'desktop-style.json').write_text(json.dumps({'previous_style':previous,'decoration':previous_decoration,'components_backup':str(component_backup) if component_backup else None},indent=2)+'\n')
    panel_config=config_home/'plasma-org.kde.plasma.desktop-appletsrc'
    if command and panel_config.is_file():shutil.copy2(panel_config,backup/'panel-settings.reference')
    target='ScarletProtocolNightPlasma8' if night else 'ScarletProtocolPlasma8'
    try:
        message=apply_style(target)
        if current_style(config_home)!=target:raise RuntimeError('Plasma did not retain the requested desktop style.')
        if window_frame:
            selected={'library':'org.kde.kwin.aurorae','theme':'__aurorae__svg__'+('ScarletProtocolNight81' if night else 'ScarletProtocolGlobal81')}
            set_decoration(config_home,selected)
            if decoration(config_home)!=selected:raise RuntimeError('KWin did not retain the requested window decoration.')
        if command:
            panel_result=native.run(command)
            (backup/'panel-result.txt').write_text(panel_result)
    except Exception:
        try:apply_style(previous)
        except Exception:pass
        if previous_decoration is not None:
            try:set_decoration(config_home,previous_decoration)
            except Exception:pass
        raise
    report=appearance(config_home)
    if window_frame and not report['kwin_confirmed']:
        for _ in range(4):
            time.sleep(.15);report=appearance(config_home)
            if report['kwin_confirmed']:break
    return {'changed':changed,'same':same,'backup':str(backup),'message':message,'widgets':widgets,'window_frame':window_frame,'appearance':report}


def restore(config_home,backup):
    data=json.loads((backup/'desktop-style.json').read_text())
    previous=data['previous_style']
    if not isinstance(previous,str) or not previous:raise ValueError('Invalid previous style backup')
    result=apply_style(previous)
    if data.get('decoration') is not None:set_decoration(config_home,data['decoration'])
    return result
