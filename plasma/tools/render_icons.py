"""Contact sheet rendered from the shipped icon theme through Qt's real icon loader."""
import json
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
from PySide6.QtCore import Qt,QRectF
from PySide6.QtGui import QGuiApplication,QImage,QPainter,QColor,QFont,QIcon,QPen

ROOT=Path(__file__).resolve().parents[1]


def main():
    app=QGuiApplication([])
    QIcon.setThemeSearchPaths([str(ROOT/'icons')]);QIcon.setThemeName('ScarletProtocolIcons')
    image=QImage(1600,1270,QImage.Format_ARGB32_Premultiplied);image.fill(QColor('#0b0d12'))
    p=QPainter(image);p.setRenderHint(QPainter.Antialiasing)
    def text(x,y,w,h,label,size=13,color='#e8bdcf',bold=False,center=False):
        p.setPen(QColor(color));p.setFont(QFont('DejaVu Sans',size,QFont.Bold if bold else QFont.Normal))
        p.drawText(QRectF(x,y,w,h),(Qt.AlignCenter if center else Qt.AlignVCenter)|Qt.TextSingleLine,label)
    def panel(x,y,w,h,title,subtitle):
        p.setPen(QPen(QColor('#63243b'),1));p.setBrush(QColor('#101116'));p.drawRoundedRect(QRectF(x,y,w,h),22,22)
        p.setPen(QPen(QColor('#ff315b'),1.2));p.drawLine(x+25,y,x+160,y)
        text(x+23,y+13,w-46,24,title,10,'#ff6386',True)
        text(x+23,y+39,w-46,22,subtitle,9,'#987082')
    def grid(x,y,width,items,cols,icon_size=44,row_height=93):
        cell=width/cols
        for index,(label,name) in enumerate(items):
            xx=x+(index%cols)*cell;yy=y+(index//cols)*row_height
            icon=QIcon.fromTheme(name)
            assert not icon.isNull(),name
            rect=QRectF(xx+(cell-icon_size)/2,yy,icon_size,icon_size)
            p.drawPixmap(rect,icon.pixmap(icon_size*2,icon_size*2),QRectF(0,0,icon_size*2,icon_size*2))
            text(xx+3,yy+icon_size+5,cell-6,24,label,8,'#e2b9cb',center=True)
    text(54,25,1300,25,'S C A R L E T   /   P R O T O C O L',10,'#ff315b',True)
    text(52,64,1450,58,'Every surface gets its mark.',31,'#ffe1eb',True)
    count=json.loads((ROOT/'icons/ScarletProtocolIcons/coverage.json').read_text())['unique_names']
    text(55,126,1490,27,f'{count:,} ICON NAMES   /   12 CATEGORIES   /   SCALABLE VECTOR ARTWORK',10,'#a47b8e')
    panel(44,182,1512,347,'APPLICATIONS','Carbon housings · scarlet contacts · recognizable app glyphs')
    apps=[('Dolphin','org.kde.dolphin'),('Konsole','org.kde.konsole'),('Settings','systemsettings'),('Discover','org.kde.discover'),('Kate','org.kde.kate'),('Okular','org.kde.okular'),('Ark','org.kde.ark'),('Firefox','firefox'),('Chrome','google-chrome'),('Brave','brave-browser'),('Edge','microsoft-edge'),('Thunderbird','thunderbird'),('VS Code','code'),('Neovim','nvim'),
          ('Krita','krita'),('GIMP','gimp'),('Inkscape','inkscape'),('Blender','blender'),('Spectacle','spectacle'),('OBS Studio','obs'),('VLC','vlc'),('Elisa','elisa'),('Spotify','spotify'),('Steam','steam'),('Discord','discord'),('Telegram','telegram-desktop'),('Signal','signal-desktop'),('Element','element'),
          ('Writer','libreoffice-writer'),('Calc','libreoffice-calc'),('Impress','libreoffice-impress'),('KeePassXC','keepassxc'),('Proton Drive','proton-drive'),('Proton VPN','protonvpn'),('KDE Connect','kdeconnect'),('VirtualBox','virtualbox'),('Docker','docker'),('Wireshark','wireshark'),('Nmap','nmap'),('Burp Suite','burpsuite'),('System Monitor','utilities-system-monitor'),('Calendar','org.kde.korganizer')]
    grid(66,260,1468,apps,14,44,88)
    panel(44,550,1512,227,'FOLDERS & PLACES','Dedicated badges · local and remote storage · Nanook’s folder')
    folders=[('Home','user-home'),('Documents','folder-documents'),('Downloads','folder-download'),('Pictures','folder-pictures'),('Music','folder-music'),('Videos','folder-videos'),('Desktop','folder-desktop'),('Code','folder-code'),('Git','folder-git'),('Backup','folder-backup'),('Archive','folder-archive'),('Nanook','folder-nanook'),
          ('Network','folder-network'),('Shared','folder-shared'),('Cloud','folder-cloud'),('Proton Drive','folder-proton-drive'),('Private','folder-private'),('Encrypted','folder-encrypted'),('Favorites','folder-favorites'),('Recent','folder-recent'),('Calendar','folder-calendar'),('Root','folder-root'),('Folder','folder'),('Trash','user-trash')]
    grid(66,620,1468,folders,12,38,72)
    panel(44,798,745,353,'BUTTONS & TOOLBARS','Sharp action glyphs at small sizes')
    controls=[('Open','document-open'),('Save','document-save'),('New','document-new'),('Print','document-print'),('Copy','edit-copy'),('Paste','edit-paste'),('Cut','edit-cut'),('Undo','edit-undo'),('Redo','edit-redo'),('Find','edit-find'),('Refresh','view-refresh'),('Configure','configure'),('Home','go-home'),('Back','go-previous'),('Forward','go-next'),('Lock','system-lock-screen'),('Play','media-playback-start'),('Pause','media-playback-pause'),('Favorite','emblem-favorite'),('Apps','view-grid'),('Close','window-close')]
    grid(60,877,711,controls,7,28,82)
    panel(811,798,745,353,'WIDGETS & SYSTEM STATUS','Weather, connectivity, battery and device states')
    status=[('Launcher','org.scarletprotocol.launcher'),('Clock','org.scarletprotocol.clock'),('System Core','org.scarletprotocol.systemcore'),('Wi-Fi','network-wireless'),('Bluetooth','preferences-system-bluetooth'),('Volume','audio-volume-high'),('Battery','battery-full'),('Clear','weather-clear'),('Cloudy','weather-clouds'),('Rain','weather-showers'),('Snow','weather-snow'),('Storm','weather-storm'),('Headphones','audio-headphones'),('USB drive','drive-removable-media-usb'),('Success','dialog-ok-apply'),('Warning','dialog-warning'),('Error','dialog-error'),('Screen','video-display'),('Power','system-shutdown'),('Calendar','view-calendar'),('Download','folder-download')]
    grid(827,877,711,status,7,28,82)
    text(55,1183,1490,30,'Matching local artwork for extra apps  ·  Symbolic aliases  ·  Per-user backups  ·  Native icon-theme lookup',11,'#d5a2ba')
    text(55,1220,1490,25,'Broad coverage adapts KDE Breeze vectors; signature app housings, folder badges and Scarlet glyphs are included.',9,'#876579')
    p.end()
    output=ROOT.parent/'Scarlet-Protocol-Icons-Preview.png';assert image.save(str(output));print(output)


if __name__=='__main__':main()
