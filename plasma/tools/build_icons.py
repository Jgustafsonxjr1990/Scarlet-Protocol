"""Build a complete Scarlet palette edition of KDE Breeze, with original signature icons."""
from pathlib import Path
import collections
import configparser
import hashlib
import json
import shutil
from icon_art import recolor_svg, housing, GLYPHS, line

ROOT=Path(__file__).resolve().parents[1]
THEME=ROOT/'icons/ScarletProtocolIcons'
BASE=Path('/usr/share/icons/breeze-dark')
CONTEXTS={'apps':'Applications','places':'Places','actions':'Actions','status':'Status',
          'devices':'Devices','mimetypes':'MimeTypes','categories':'Categories',
          'preferences':'Categories','applets':'Applications','emblems':'Emblems','emotes':'Emotes','animations':'Animations'}

APPS={
 'terminal':'utilities-terminal org.kde.konsole konsole org.gnome.Terminal gnome-terminal xfce4-terminal alacritty Alacritty kitty foot wezterm org.wezfurlong.wezterm terminator tilix',
 'code':'code code-oss visual-studio-code com.visualstudio.code codium vscodium neovim nvim gvim vim org.kde.kate kate org.kde.kwrite kwrite sublime-text jetbrains-toolbox',
 'browser':'web-browser chromium chromium-browser vivaldi vivaldi-stable torbrowser-launcher tor-browser org.torproject.torbrowser',
 'chrome':'google-chrome google-chrome-stable com.google.Chrome',
 'firefox':'firefox firefox-esr org.mozilla.firefox',
 'brave':'brave-browser brave-browser-stable com.brave.Browser',
 'edge':'microsoft-edge microsoft-edge-stable com.microsoft.Edge',
 'mail':'thunderbird org.mozilla.Thunderbird org.kde.kmail kmail proton-mail protonmail-desktop ch.protonmail.protonmail-desktop',
 'files':'system-file-manager org.kde.dolphin dolphin thunar org.gnome.Nautilus nautilus pcmanfm',
 'settings':'systemsettings systemsettings5 systemsettings6 org.kde.systemsettings preferences-system org.kde.discover plasma-discover',
 'music':'org.kde.elisa elisa clementine rhythmbox amarok audacious',
 'spotify':'spotify com.spotify.Client',
 'video':'vlc org.videolan.VLC mpv io.mpv.Mpv haruna org.kde.haruna',
 'photo':'org.kde.gwenview gwenview org.gnome.Loupe org.gnome.eog shotwell digikam org.kde.digikam',
 'brush':'gimp org.gimp.GIMP krita org.kde.krita',
 'vector':'inkscape org.inkscape.Inkscape',
 'cube':'blender org.blender.Blender freecad org.freecad.FreeCAD',
 'camera':'org.kde.spectacle spectacle accessories-screenshot ksnip flameshot org.flameshot.Flameshot',
 'obs':'com.obsproject.Studio obs obs-studio',
 'chat':'org.kde.konversation konversation element im.riot.Riot org.kde.neochat slack com.slack.Slack',
 'discord':'discord com.discordapp.Discord vesktop dev.vencord.Vesktop',
 'telegram':'telegram telegram-desktop org.telegram.desktop',
 'signal':'signal-desktop org.signal.Signal',
 'steam':'steam com.valvesoftware.Steam',
 'game':'lutris net.lutris.Lutris heroic com.heroicgameslauncher.hgl org.kde.kpat org.kde.kmines',
 'lock':'keepassxc org.keepassxc.KeePassXC bitwarden com.bitwarden.desktop',
 'shield':'protonvpn proton-vpn-gnome-desktop com.protonvpn.www mullvad-vpn wireguard',
 'network':'org.kde.krdc krdc remmina org.remmina.Remmina rustdesk com.rustdesk.RustDesk syncthing syncthing-gtk',
 'radar':'nmap zenmap kali-nmap kali-zenmap',
 'shark':'wireshark org.wireshark.Wireshark kali-wireshark',
 'bug':'burpsuite kali-burpsuite zaproxy kali-zaproxy metasploit-framework kali-metasploit-framework',
 'docker':'docker docker-desktop com.docker.docker podman-desktop io.podman_desktop.PodmanDesktop',
 'chip':'virtualbox virtualbox-vbox org.virtualbox.VirtualBox virt-manager qemu aqemu',
 'monitor':'utilities-system-monitor org.kde.plasma-systemmonitor plasma-systemmonitor org.gnome.SystemMonitor ksysguard',
 'document':'org.kde.okular okular libreoffice-writer libreoffice-startcenter libreoffice org.libreoffice.LibreOffice',
 'sheet':'libreoffice-calc',
 'slides':'libreoffice-impress',
 'calendar':'org.kde.korganizer korganizer org.kde.merkuro.calendar org.gnome.Calendar',
 'clock':'preferences-system-time org.kde.kclock kclock org.gnome.clocks',
 'archive':'org.kde.ark ark file-roller org.gnome.FileRoller peazip',
 'cloud':'proton-drive protondrive rclone-browser nextcloud com.nextcloud.desktopclient.nextcloud owncloud',
 'phone':'kdeconnect org.kde.kdeconnect org.kde.kdeconnect.app kdeconnect-app',
 'paw':'org.scarletprotocol.pointer',
}
SPECIAL_APPS={
 'vscode':'code code-oss visual-studio-code com.visualstudio.code codium vscodium',
 'kate':'org.kde.kate kate org.kde.kwrite kwrite',
 'neovim':'neovim nvim',
 'store':'org.kde.discover plasma-discover',
 'eye':'org.kde.okular okular',
 'gimp':'gimp org.gimp.GIMP',
 'cone':'vlc org.videolan.VLC',
 'onion':'torbrowser-launcher tor-browser org.torproject.torbrowser',
 'chrome':'chromium chromium-browser',
}
FOLDERS={
 'files':'folder folder-open folder-closed inode-directory folder-root folder-generic folder-grey folder-red',
 'home':'user-home folder-home',
 'document':'folder-documents folder-text',
 'download':'folder-download folder-downloads',
 'music':'folder-music folder-sound',
 'video':'folder-videos folder-video',
 'photo':'folder-pictures folder-images folder-photos',
 'cloud':'folder-cloud folder-nextcloud folder-owncloud folder-proton-drive',
 'network':'folder-network folder-remote folder-shared folder-publicshare folder-public',
 'lock':'folder-locked folder-encrypted folder-private',
 'code':'folder-development folder-code folder-source',
 'git':'folder-git',
 'archive':'folder-archive folder-backup folder-compressed',
 'star':'folder-favorites folder-favourites folder-important',
 'calendar':'folder-calendar',
 'clock':'folder-recent folder-recently-used',
 'monitor':'user-desktop folder-desktop',
 'paw':'folder-nanook',
}


def build():
    # Select the native closest vector once per name/context; scalable directories
    # cover every requested size without thousands of identical size copies.
    choices={};broken=0
    for path in BASE.rglob('*.svg'):
        if not path.is_file(): broken+=1;continue
        category=path.relative_to(BASE).parts[0]
        if category not in CONTEXTS:continue
        size=path.relative_to(BASE).parts[1]
        desired=48 if category in ('apps','places','mimetypes','devices') else 22
        try: score=abs(int(size)-desired)
        except ValueError: score=100
        key=(category,path.name)
        if key not in choices or score<choices[key][0]:choices[key]=(score,path)
    THEME.mkdir(parents=True,exist_ok=True)
    for category in CONTEXTS:
        destination=THEME/category/'scalable'
        if destination.is_dir():shutil.rmtree(destination)
        destination.mkdir(parents=True,exist_ok=True)
    # Preserve the preexisting signature names; replace their drawings below or
    # inherit their corresponding native glyph when no new housing is needed.
    for (category,name),(_,path) in sorted(choices.items()):
        symbolic=category in ('actions','status','preferences','applets','emblems') or '-symbolic' in name
        (THEME/category/'scalable'/name).write_text(recolor_svg(path.read_bytes(),symbolic))
    for glyph,names in list(APPS.items())+list(SPECIAL_APPS.items()):
        for name in names.split():
            artwork=housing(GLYPHS[glyph],name)
            (THEME/'apps/scalable'/(name+'.svg')).write_text(artwork)
            # Plasma may request the symbolic spelling first, including reverse-DNS IDs.
            (THEME/'apps/scalable'/(name+'-symbolic.svg')).write_text(artwork)
    for glyph,names in FOLDERS.items():
        for name in names.split():
            art=housing(GLYPHS[glyph],name,True)
            for suffix in ('','-symbolic'):(THEME/'places/scalable'/(name+suffix+'.svg')).write_text(art)
    for name,filled in [('non-starred',False),('emblem-favorite',True),('favorites',True)]:
        art=line(GLYPHS['star'],'#ff668b',1.4)
        if filled:art=art.replace('fill="none"','fill="#741d3a"')
        (THEME/'actions/scalable'/(name+'.svg')).write_text('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">'+art+'</svg>\n')
    for glyph,names in {'settings':'org.scarletprotocol.windowstudio org.scarletprotocol.iconstudio',
                        'monitor':'org.scarletprotocol.systemcore',
                        'clock':'org.scarletprotocol.clock',
                        'radar':'org.scarletprotocol.launcher start-here start-here-kde start-here-kde-plasma'}.items():
        for name in names.split():
            for suffix in ('','-symbolic'):(THEME/'apps/scalable'/(name+suffix+'.svg')).write_text(housing(GLYPHS[glyph],name))
    cfg=configparser.ConfigParser(interpolation=None);cfg.optionxform=str
    cfg['Icon Theme']={'Name':'Scarlet Protocol Icons — Complete','Comment':'Scarlet vector edition with cyber housings and semantic status colors',
        'Inherits':'breeze-dark,breeze,hicolor','Directories':','.join(x+'/scalable' for x in CONTEXTS),
        'DesktopDefault':'48','DesktopSizes':'16,22,24,32,48,64,128,256','ToolbarDefault':'22','SmallDefault':'16','PanelDefault':'32','DialogDefault':'32'}
    for category,context in CONTEXTS.items():
        cfg[category+'/scalable']={'Size':str(48 if category in ('apps','places','devices','mimetypes') else 24),
            'Type':'Scalable','MinSize':'16','MaxSize':'512','Context':context}
    with (THEME/'index.theme').open('w') as f:cfg.write(f,space_around_delimiters=False)
    license_dir=THEME/'LICENSES';license_dir.mkdir(exist_ok=True)
    shutil.copy2('/usr/share/doc/breeze-icon-theme/copyright',license_dir/'Breeze-copyright.txt')
    for name in ('LGPL-3','GPL-3'):shutil.copy2('/usr/share/common-licenses'/Path(name),license_dir/(name+'.txt'))
    (THEME/'ATTRIBUTION.md').write_text('# Artwork provenance\n\nThe broad-coverage vectors are a modified palette edition of KDE Breeze Icons, Copyright 2014 Uri Herrera and KDE contributors, LGPL-3.0-or-later. Original source: https://invent.kde.org/frameworks/breeze-icons . The included SVGs are the editable source of these modifications. See LICENSES for the original notice and license terms.\n\nScarlet modifications: scarlet/carbon palette, preserved green/yellow status meanings, carbon cyber housings, original app glyphs and folder badges. Original Scarlet housing/glyph additions are also LGPL-3.0-or-later. Distribution of this icon theme is independent of the surrounding application code license.\n')
    # Missing symbolic aliases use the corresponding themed base name when present.
    all_files=list(THEME.glob('*/scalable/*.svg'))
    names={p.stem for p in all_files}
    for name in sorted(names):
        if not name.endswith('-symbolic'):
            src=next(p for p in all_files if p.stem==name)
            alias=src.with_name(name+'-symbolic.svg')
            if not alias.exists():shutil.copy2(src,alias)
    files=sorted(THEME.glob('*/scalable/*.svg'))
    digest=hashlib.sha256()
    for p in files:digest.update(str(p.relative_to(THEME)).encode());digest.update(p.read_bytes())
    manifest={'version':'6.2.0','source':'KDE Breeze Icons, local installed source snapshot',
        'svg_files':len(files),'unique_names':len({p.stem for p in files}),
        'categories':dict(collections.Counter(p.relative_to(THEME).parts[0] for p in files)),
        'source_broken_links_skipped':broken,'tree_sha256':digest.hexdigest()}
    (THEME/'coverage.json').write_text(json.dumps(manifest,indent=2)+'\n')
    # The applets use bundled action glyphs so missing system lookups cannot blank them.
    names=['go-home','folder-download','system-lock-screen','favorites','view-grid','go-previous','go-next','view-calendar','document-save','emblem-favorite','non-starred','edit-find','chronometer','media-playback-start','media-playback-pause','view-refresh']
    byname={p.stem:p for p in files}
    for applet in ('launcher','clock','systemcore'):
        dest=ROOT/f'plasmoids/org.scarletprotocol.{applet}/contents/icons';dest.mkdir(parents=True,exist_ok=True)
        for name in names:
            source=byname.get(name) or byname.get('application-x-executable')
            if source:shutil.copy2(source,dest/(name+'.svg'))
    print(json.dumps(manifest,indent=2))


if __name__=='__main__':build()
