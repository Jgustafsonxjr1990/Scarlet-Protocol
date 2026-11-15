// SPDX-License-Identifier: GPL-2.0-or-later
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.plasmoid
import "DateMath.js" as Dates

PlasmoidItem {
    id: root
    Plasmoid.icon: "preferences-system-time"
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground
    preferredRepresentation: compactRepresentation
    switchWidth: 0; switchHeight: 0
    property date now: new Date()
    property var savedNotes: {
        try { const data=JSON.parse(Plasmoid.configuration.notes); return data && typeof data==="object" ? data : {} }
        catch(error) { return {} }
    }
    Timer { interval: root.expanded && Plasmoid.configuration.showSeconds ? 1000 : Math.max(100,60000-root.now.getSeconds()*1000-root.now.getMilliseconds()); running: root.visible; repeat: true; onTriggered: root.now=new Date() }
    onExpandedChanged: {
        root.now=new Date()
        if(!expanded && fullRepresentationItem) fullRepresentationItem.flushNote()
    }
    compactRepresentation: ProtocolButton {
        iconName: "chronometer"
        text: Qt.formatTime(root.now,Plasmoid.configuration.twentyFourHour?"HH:mm":"h:mm AP")
        textSize: 14; cornerRadius: 12; implicitWidth: 90
        accent: Plasmoid.configuration.accentColor; chosen: root.expanded
        Accessible.name: Qt.formatDateTime(root.now,Qt.DefaultLocaleLongDate)
        onClicked: root.expanded=!root.expanded
        Rectangle { x: 13; y: parent.height-5; width: (parent.width-26)*(root.now.getHours()*60+root.now.getMinutes())/1440; height: 1; color: Plasmoid.configuration.accentColor; opacity: .8 }
    }
    fullRepresentation: CalendarView {
        Layout.minimumWidth: 410; Layout.preferredWidth: 460; Layout.minimumHeight: 650; Layout.preferredHeight: 660
        now: root.now; notes: root.savedNotes
        twentyFourHour: Plasmoid.configuration.twentyFourHour
        showSeconds: Plasmoid.configuration.showSeconds
        mondayFirst: Plasmoid.configuration.mondayFirst
        showWeekNumbers: Plasmoid.configuration.showWeekNumbers
        accent: Plasmoid.configuration.accentColor
        glowStrength: Plasmoid.configuration.glowStrength/100
        animate: Plasmoid.configuration.animate
        onNoteSaved: (key,content) => {
            var copy=Object.assign({},root.savedNotes)
            if(content.length) copy[key]=content; else delete copy[key]
            Plasmoid.configuration.notes=JSON.stringify(copy)
        }
        onCloseRequested: root.expanded=false
    }
}
