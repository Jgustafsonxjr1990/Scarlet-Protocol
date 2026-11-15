"""Write Plasma metadata and configuration for the two native Scarlet applets."""
from pathlib import Path
import json
import shutil

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'plasmoids'

def build():
    launcher=BASE/'org.scarletprotocol.launcher'
    clock=BASE/'org.scarletprotocol.clock'
    for name in ('Surface.qml','ProtocolButton.qml'):
        shutil.copy2(launcher/'contents/ui'/name,clock/'contents/ui'/name)
    common='''<entry name="accentColor" type="String"><default>#ff315b</default></entry>
      <entry name="glowStrength" type="Int"><default>70</default><min>0</min><max>100</max></entry>
      <entry name="animate" type="Bool"><default>true</default></entry>'''
    for folder,title,description,icon,extra in [
        (launcher,'Scarlet Protocol Launcher','A detailed app launcher with Plasma search and pinnable favorites','start-here-kde',
         '<entry name="favoriteApps" type="StringList"><default>org.kde.dolphin.desktop,org.kde.konsole.desktop,systemsettings.desktop,firefox.desktop,google-chrome.desktop</default></entry><entry name="favoritesInitialized" type="Bool"><default>false</default></entry>'),
        (clock,'Scarlet Protocol Clock','A detailed clock, month calendar and local notes by date','preferences-system-time',
         '<entry name="twentyFourHour" type="Bool"><default>true</default></entry><entry name="showSeconds" type="Bool"><default>true</default></entry><entry name="mondayFirst" type="Bool"><default>false</default></entry><entry name="showWeekNumbers" type="Bool"><default>true</default></entry><entry name="notes" type="String"><default>{}</default></entry>')]:
        meta={'KPackageStructure':'Plasma/Applet','KPlugin':{'Id':folder.name,'Name':title,'Description':description,'Icon':icon,'Version':'6.0.0','License':'GPL-2.0-or-later','Category':'Application Launchers' if folder==launcher else 'Date and Time','Authors':[{'Name':'Scarlet Protocol'}]},'X-Plasma-API-Minimum-Version':'6.0'}
        if folder==launcher: meta['X-Plasma-Provides']=['org.kde.plasma.launchermenu']
        else: meta['X-Plasma-Provides']=['org.kde.plasma.time','org.kde.plasma.date']
        folder.joinpath('metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
        cfg=folder/'contents/config';cfg.mkdir(parents=True,exist_ok=True)
        cfg.joinpath('main.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><kcfg xmlns="http://www.kde.org/standards/kcfg/1.0"><kcfgfile name=""/><group name="General">'+common+extra+'</group></kcfg>\n')
        cfg.joinpath('config.qml').write_text('import org.kde.plasma.configuration\nConfigModel { ConfigCategory { name: qsTr("Appearance"); icon: "preferences-desktop-color"; source: "configGeneral.qml" } }\n')
        options='''
    property alias cfg_animate: motion.checked
    property alias cfg_glowStrength: strength.value
    property alias cfg_accentColor: accent.text
'''
        fields='''
    Label { text: qsTr("Accent color") }
    TextField { id: accent; placeholderText: "#ff315b"; validator: RegularExpressionValidator { regularExpression: /^#[0-9a-fA-F]{6}$/ } }
    Label { text: qsTr("Glow strength") }
    Slider { id: strength; from: 0; to: 100; stepSize: 1; Layout.preferredWidth: 260 }
    CheckBox { id: motion; text: qsTr("Animate hover transitions") }
'''
        if folder==clock:
            for key,label in [('twentyFourHour','Use a 24-hour clock'),('showSeconds','Show seconds in the calendar'),('mondayFirst','Start weeks on Monday'),('showWeekNumbers','Show ISO week numbers')]:
                options+=f'    property alias cfg_{key}: {key}Check.checked\n'
                fields+=f'    CheckBox {{ id: {key}Check; text: qsTr("{label}") }}\n'
        folder.joinpath('contents/ui/configGeneral.qml').write_text('import QtQuick\nimport QtQuick.Controls\nimport QtQuick.Layouts\n\nColumnLayout {\n'+options+fields+'    Item { Layout.fillHeight: true }\n}\n')

if __name__=='__main__':build()
