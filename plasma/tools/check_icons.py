"""Icon coverage, native Qt SVG/theme lookup and safe per-user update regression checks."""
from pathlib import Path
import json
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import sys
import tempfile
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tools')]
import icon_studio as studio
from icon_art import recolor_svg


def installer_checks(work):
    user=work/'user';system=work/'system';config=work/'config';state=work/'state'
    for root in (user,system):(root/'applications').mkdir(parents=True)
    base='[Desktop Entry]\nType=Application\nName=Test App\nExec=example --argument %U\nIcon=org.test.Unique\nActions=Inspect;\n\n[Desktop Action Inspect]\nName=Inspect\nExec=example --inspect %f\nIcon=edit-find\n'
    (system/'applications/unique.desktop').write_text(base)
    (system/'applications/known.desktop').write_text(base.replace('org.test.Unique','org.kde.dolphin'))
    (system/'applications/hidden.desktop').write_text(base)
    (user/'applications/hidden.desktop').write_text(base.replace('Type=Application','Type=Application\nHidden=true'))
    logo=system/'icons/hicolor/scalable/apps/org.test.Unique.svg';logo.parent.mkdir(parents=True)
    logo.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M2 2h20v20H2Z" fill="#2980b9"/></svg>')
    absolute=work/'absolute.svg';absolute.write_text(logo.read_text())
    absolute_desktop=base.replace('org.test.Unique',str(absolute))
    (system/'applications/absolute.desktop').write_text(absolute_desktop)
    from PySide6.QtGui import QImage,QColor
    png=work/'original.png';picture=QImage(8,8,QImage.Format_ARGB32_Premultiplied);picture.fill(QColor('#2080e0'));picture.save(str(png))
    (system/'applications/raster.desktop').write_text(base.replace('org.test.Unique',str(png)))
    (system/'applications/empty.desktop').write_text(base.replace('Icon=org.test.Unique\n',''))
    widget=system/'plasma/plasmoids/testwidget/metadata.json';widget.parent.mkdir(parents=True)
    widget.write_text(json.dumps({'KPlugin':{'Id':'testwidget','Icon':'test-widget-icon','Name':'Test widget'}}))
    report=studio.audit([user,system]);assert len(report['apps'])==5 and len(report['missing_apps'])==4
    derived,overrides=studio.plan(report,[user,system])
    assert 'org.test.Unique' in derived and 'test-widget-icon' in derived
    assert len(overrides)==3
    replaced=dict(overrides)['absolute.desktop']
    assert 'Exec=example --argument %U' in replaced and 'Exec=example --inspect %f' in replaced
    assert '[Desktop Action Inspect]\nName=Inspect\nExec=example --inspect %f\nIcon=edit-find' in replaced
    assert studio.desktop_values(replaced)['Icon']!=str(absolute)
    identity,target=studio.stage(user,derived);assert studio.stage(user,derived)==(identity,target)
    assert (target/'apps/scalable/org.test.Unique.svg').is_file()
    prior={'Icons/Theme':'OldIcons','KDE/ShowIconsOnPushButtons':'false'}
    settings=dict(prior);studio.program=lambda name:name
    def setting(home,group,key,value=studio.READ):
        if value is studio.READ:return settings.get(group+'/'+key)
        if value is None:settings.pop(group+'/'+key,None)
        else:settings[group+'/'+key]=value
    studio.setting=setting;studio.notify=lambda:None
    selected,backup=studio.apply(user,config,state,report,derived,overrides)
    assert selected==identity and settings['KDE/ShowIconsOnPushButtons']=='true'
    assert (user/'applications/absolute.desktop').is_file()
    repeated=studio.audit([user,system]);new_art,new_overrides=studio.plan(repeated,[user,system])
    assert new_art==derived and new_overrides==overrides,'Repeat update changed a derived app logo'
    studio.restore(config,backup);assert settings==prior
    assert not (user/'applications/absolute.desktop').exists()
    assert (system/'applications/absolute.desktop').read_text()==absolute_desktop
    def fail():raise RuntimeError('simulated native icon refresh failure')
    studio.notify=fail
    try:studio.apply(user,config,state,report,derived,overrides)
    except RuntimeError:pass
    else:raise AssertionError('Expected refresh failure')
    assert settings==prior and not (user/'applications/absolute.desktop').exists()
    print('PASS: app/widget discovery, hidden-entry precedence, absolute/missing icons, unchanged Exec/actions, repeat staging, backup/restore and failure rollback (native-command fixture)',flush=True)
    return target,derived


def main():
    from PySide6.QtCore import qInstallMessageHandler,QRectF
    from PySide6.QtGui import QGuiApplication,QIcon,QImage,QPainter,QColor
    from PySide6.QtSvg import QSvgRenderer
    app=QGuiApplication([])
    with tempfile.TemporaryDirectory(prefix='scarlet-icons-check-') as directory:
        target,derived=installer_checks(Path(directory))
        QIcon.setThemeSearchPaths([str(target.parent)])
        QIcon.setThemeName(target.name)
        required=['document-save','document-open','window-close','go-home','folder-download','folder-pictures',
            'folder-nanook','edit-find','configure','view-grid','non-starred','weather-clear','network-wireless',
            'audio-volume-high','battery-full','org.kde.dolphin','org.kde.dolphin-symbolic','org.scarletprotocol.launcher',
            'org.scarletprotocol.clock','org.scarletprotocol.systemcore','firefox-esr','google-chrome','proton-drive',
            'com.discordapp.Discord','org.test.Unique','test-widget-icon']
        for name in required:
            assert QIcon.hasThemeIcon(name),name
            icon=QIcon.fromTheme(name)
            assert not icon.pixmap(32,32).isNull(),name
        raster_name=next(name for name,art in derived.items() if 'data:image/png' in art)
        center=QIcon.fromTheme(raster_name).pixmap(32,32).toImage().pixelColor(16,16)
        assert center.blue()>center.red()+70,'Embedded original raster logo did not render'
        # Render every shipped icon, not just a synthetic name-resolution mock.
        messages=[];issues=[];empty=[]
        qInstallMessageHandler(lambda kind,context,msg:messages.append(msg))
        files=sorted(target.glob('*/scalable/*.svg'))
        for index,path in enumerate(files):
            messages.clear();renderer=QSvgRenderer(str(path))
            if not renderer.isValid():issues.append((path.name,'invalid SVG'));continue
            image=QImage(32,32,QImage.Format_ARGB32_Premultiplied);image.fill(QColor('transparent'))
            painter=QPainter(image);renderer.render(painter,QRectF(0,0,32,32));painter.end()
            if messages:issues.append((str(path.relative_to(target)),list(messages)))
            if all(image.pixelColor(x,y).alpha()==0 for x in range(32) for y in range(32)):empty.append(str(path.relative_to(target)))
        if issues:print('SVG warnings:',json.dumps(issues[:30],indent=2),flush=True)
        if empty:print('Empty source icons:',empty[:40],flush=True)
        assert not issues,f'{len(issues)} SVGs have renderer warnings'
        # Deliberately invisible input-method spacer/cursor states are recorded, not styled as controls.
        allowed={'input-none.svg','im-invisible.svg','transparent.svg','blank.svg','cursor-blank.svg'}
        assert all(Path(name).name in allowed for name in empty),empty
        assert '#38ea77' in recolor_svg('<svg xmlns="http://www.w3.org/2000/svg"><path fill="#27ae60"/></svg>')
        assert '#ffd43b' in recolor_svg('<svg xmlns="http://www.w3.org/2000/svg"><path fill="#f39c12"/></svg>')
        print(f'PASS: {len(required)} native Qt icon-theme lookups; {len(files)} valid rendered SVGs; semantic success/warning colors',flush=True)


if __name__=='__main__':main()
