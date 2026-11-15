import QtQuick
import "../plasmoids/org.scarletprotocol.launcher/contents/ui" as Launcher
import "../plasmoids/org.scarletprotocol.clock/contents/ui" as Clock

Rectangle {
    id: stage
    objectName: "previewStage"
    width: 1440; height: 1020
    color: "#090b10"
    property bool nightShift: false
    readonly property color accent: nightShift?"#c93e62":"#ff315b"
    property var pinEvents: []
    property var launches: []
    property var toolEntries: [{display:"Settings",decoration:"systemsettings",favoriteId:"settings",sourceIndex:2},{display:"Konsole",decoration:"org.kde.konsole",favoriteId:"konsole",sourceIndex:1}]
    property var recentEntries: [{display:"Dolphin",decoration:"org.kde.dolphin",favoriteId:"dolphin",sourceIndex:0},{display:"Konsole",decoration:"org.kde.konsole",favoriteId:"konsole",sourceIndex:1}]
    property var savedNotes: ({"2026-11-13":"Scarlet Protocol · desktop design review.\nCheck frame focus and button glow."})
    property var changes: []
    Image { anchors.fill: parent; source: "../wallpapers/ScarletProtocolNoirWall/contents/images/1920x1200.png"; fillMode: Image.PreserveAspectCrop; opacity: .5 }
    Text { x: 58; y: 36; text: "SCARLET  /  PROTOCOL"; color: stage.accent; font.pixelSize: 13; font.letterSpacing: 3 }
    Text { x: 57; y: 66; text: "Classic Slits. The original character."; color: "#f9e0eb"; font.pixelSize: 33; font.weight: Font.DemiBold }
    Text { anchors.right: parent.right; anchors.rightMargin: 60; y: 83; text: "8.1  /  NATIVE COMPONENT PREVIEW"; color: "#aa7188"; font.family: "monospace"; font.pixelSize: 11 }
    Image { x: 36; y: 128; width: 1368; height: 844; source: "rendered-frame.png" }
    Image { x: 58; y: 148; width: 38; height: 34; source: closeHover.containsMouse?"rendered-close.png":"rendered-close-active.png"; MouseArea { id: closeHover; anchors.fill: parent; hoverEnabled: true } }
    Image { x: 100; y: 148; width: 38; height: 34; source: minimizeHover.containsMouse?"rendered-minimize.png":"rendered-minimize-active.png"; MouseArea { id: minimizeHover; anchors.fill: parent; hoverEnabled: true } }
    Image { x: 142; y: 148; width: 38; height: 34; source: maximizeHover.containsMouse?"rendered-maximize.png":"rendered-maximize-active.png"; MouseArea { id: maximizeHover; anchors.fill: parent; hoverEnabled: true } }
    Text { x: 206; y: 159; text: "SCARLET PROTOCOL  /  "+(stage.nightShift?"NIGHT SHIFT":"BLACKOUT"); color: "#e7bacd"; font.pixelSize: 11; font.letterSpacing: 1.1 }
    Text { anchors.right: parent.right; anchors.rightMargin: 72; y: 159; text: "STRAIGHT CUTS  ·  SEGMENTED RAILS  ·  SCARLET EDGE"; color: "#b2748b"; font.pixelSize: 9; font.letterSpacing: 1 }
    ListModel {
        id: sampleApps
        ListElement { display: "Dolphin"; decoration: "org.kde.dolphin"; favoriteId: "dolphin" }
        ListElement { display: "Konsole"; decoration: "org.kde.konsole"; favoriteId: "konsole" }
        ListElement { display: "Settings"; decoration: "systemsettings"; favoriteId: "settings" }
        ListElement { display: "Documents"; decoration: "folder-documents"; favoriteId: "documents" }
        ListElement { display: "Music"; decoration: "folder-music"; favoriteId: "music" }
        ListElement { display: "Pictures"; decoration: "folder-pictures"; favoriteId: "pictures" }
        ListElement { display: "Downloads"; decoration: "folder-downloads"; favoriteId: "downloads" }
        ListElement { display: "Videos"; decoration: "folder-videos"; favoriteId: "videos" }
        ListElement { display: "Home"; decoration: "user-home"; favoriteId: "home" }
        ListElement { display: "Recent files"; decoration: "folder-recent"; favoriteId: "recent" }
    }
    Launcher.LauncherView {
        id: launcher
        objectName: "launcher"
        x: 73; y: 211; width: 760; height: 550
        applicationModel: sampleApps; favoritesModel: sampleApps; searchModel: sampleApps
        toolsModel: stage.toolEntries; recentModel: stage.recentEntries
        section: 1
        accent: stage.accent; glowStrength: stage.nightShift?.45:.7
        favoriteIds: ["dolphin","konsole","settings"]
        iconFactory: Component {
            Image {
                source: "../icons/ScarletProtocolIcons/"+(["org.kde.dolphin","org.kde.konsole","systemsettings"].indexOf(parent.iconSource)>=0?"apps":"places")+"/scalable/"+parent.iconSource+".svg"
                fillMode: Image.PreserveAspectFit
            }
        }
        onPinRequested: id => { stage.pinEvents.push(id); favoriteIds=favoriteIds.indexOf(id)>=0?favoriteIds.filter(x=>x!==id):favoriteIds.concat([id]) }
        onLaunchRequested: (index,id,sourceIndex) => stage.launches.push(sourceIndex>=0?sourceIndex:index)
        onClearRecentRequested: stage.recentEntries=[]
    }
    Clock.CalendarView {
        id: calendar
        objectName: "calendar"
        x: 868; y: 211; width: 460; height: 660
        now: new Date(2026,10,13,23,41,27)
        selectedDate: new Date(2026,10,13,12)
        displayYear: 2026; displayMonth: 10
        accent: stage.accent; glowStrength: stage.nightShift?.45:.7
        notes: stage.savedNotes
        onNoteSaved: (key,content) => {
            var copy=Object.assign({},stage.savedNotes)
            if(content.length) copy[key]=content; else delete copy[key]
            stage.savedNotes=copy
        }
    }
    Text { x: 79; y: 799; text: "CONTROL FEEDBACK"; color: "#b97d94"; font.pixelSize: 10; font.letterSpacing: 1.7 }
    Row { x: 74; y: 825; spacing: 12
        Launcher.ProtocolButton { text: "Normal"; width: 112 }
        Launcher.ProtocolButton { text: "Selected"; chosen: true; width: 112 }
        Launcher.ProtocolButton { objectName: "hoverControl"; text: "Hover / focus"; width: 140 }
        Launcher.ProtocolButton { text: "Disabled"; enabled: false; width: 112 }
    }
    Image { x: 714; y: 786; width: 104; height: 104; source: "rendered-analog.png" }
    Text { x: 693; y: 898; width: 145; horizontalAlignment: Text.AlignHCenter; text: "NATIVE ANALOG CLOCK"; color: "#b97d94"; font.pixelSize: 9; font.letterSpacing: .7 }
    Text { x: 79; y: 933; text: "QUICK TOOLS  /  RECENT APPS  /  MONTH PICKER  /  SEARCHABLE DATE NOTES"; color: "#95687d"; font.pixelSize: 10; font.letterSpacing: .6 }
}
