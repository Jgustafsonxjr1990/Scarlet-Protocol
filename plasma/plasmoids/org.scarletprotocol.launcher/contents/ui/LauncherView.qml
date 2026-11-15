// SPDX-License-Identifier: GPL-2.0-or-later
import QtQuick
import QtQuick.Controls
import QtQuick.Window

FocusScope {
    id: root
    property var applicationModel
    property var favoritesModel
    property var searchModel
    property var toolsModel
    property var recentModel
    property var favoriteIds: []
    property var favoriteLookup: null
    property Component iconFactory
    property color accent: "#ff315b"
    property real glowStrength: .7
    property bool animate: true
    property int section: 0
    property alias query: search.text
    property alias currentIndex: grid.currentIndex
    readonly property bool searching: query.trim().length > 0
    readonly property var activeModel: searching ? searchModel : section===0 ? favoritesModel : section===2 ? toolsModel : section===3 ? recentModel : applicationModel
    signal launchRequested(int index,string favoriteId,int sourceIndex)
    signal pinRequested(string favoriteId)
    signal placeRequested(string place)
    signal lockRequested()
    signal closeRequested()
    signal clearRecentRequested()
    implicitWidth: 680
    implicitHeight: 550
    function begin() { search.clear(); search.forceActiveFocus(); grid.currentIndex=0 }
    function activate() { if(grid.currentIndex>=0 && grid.count>0) launchRequested(grid.currentIndex,grid.currentItem?grid.currentItem.appId:"",grid.currentItem && grid.currentItem.entry.sourceIndex!==undefined?grid.currentItem.entry.sourceIndex:-1) }
    function setSection(value) { search.clear(); section=value; grid.currentIndex=0 }
    Shortcut { sequence: "Ctrl+L"; context: Qt.WindowShortcut; enabled: root.visible; onActivated: search.forceActiveFocus() }
    Shortcut { sequence: "Ctrl+1"; context: Qt.WindowShortcut; enabled: root.visible; onActivated: root.setSection(0) }
    Shortcut { sequence: "Ctrl+2"; context: Qt.WindowShortcut; enabled: root.visible; onActivated: root.setSection(1) }
    Shortcut { sequence: "Ctrl+3"; context: Qt.WindowShortcut; enabled: root.visible; onActivated: root.setSection(2) }
    Shortcut { sequence: "Ctrl+4"; context: Qt.WindowShortcut; enabled: root.visible; onActivated: root.setSection(3) }

    Surface { anchors.fill: parent; accent: root.accent; glowStrength: root.glowStrength }
    Text { x: 27; y: 22; text: "SCARLET  /  PROTOCOL"; color: root.accent; font.pixelSize: 10; font.letterSpacing: 2; font.weight: Font.DemiBold }
    Text { x: 26; y: 45; text: qsTr("Applications"); color: "#ffe7ef"; font.pixelSize: 28; font.weight: Font.DemiBold }
    Text { anchors.right: parent.right; anchors.rightMargin: 29; y: 58; text: String(grid.count).padStart(2,"0")+" / "+(root.searching?qsTr("RESULTS"):qsTr("APPS")); color: "#b97f93"; font.family: "monospace"; font.pixelSize: 11 }
    TextField {
        id: search
        objectName: "launcherSearch"
        x: 26; y: 96; width: parent.width-52; height: 44
        color: "#ffe5ee"; placeholderTextColor: "#a78593"; font.pixelSize: 14
        placeholderText: qsTr("Search applications and settings…")
        leftPadding: 16; rightPadding: 38; selectByMouse: true
        background: Rectangle { radius: 14; color: "#17141c"; border.color: search.activeFocus ? root.accent : "#563042" }
        onTextChanged: grid.currentIndex=0
        Keys.onDownPressed: { grid.forceActiveFocus(); grid.currentIndex=0 }
        Keys.onReturnPressed: root.activate()
        Keys.onEnterPressed: root.activate()
        Image { anchors.right: parent.right; anchors.rightMargin: 15; anchors.verticalCenter: parent.verticalCenter; width: 18; height: 18; source: "../icons/edit-find.svg"; sourceSize.width: 36; sourceSize.height: 36 }
    }
    Row {
        x: 26; y: 154; spacing: 8
        ProtocolButton { objectName: "favoritesTab"; text: qsTr("Favorites"); iconName: "favorites"; width: 105; chosen: root.section===0 && !root.searching; accent: root.accent; animate: root.animate; glowStrength: root.glowStrength; onClicked: root.setSection(0) }
        ProtocolButton { objectName: "applicationsTab"; text: qsTr("All applications"); iconName: "view-grid"; width: 142; chosen: root.section===1 && !root.searching; accent: root.accent; animate: root.animate; glowStrength: root.glowStrength; onClicked: { search.clear(); root.section=1 } }
        ProtocolButton { objectName: "toolsTab"; text: qsTr("Tools"); iconName: "configure"; width: 86; chosen: root.section===2 && !root.searching; accent: root.accent; animate: root.animate; glowStrength: root.glowStrength; onClicked: root.setSection(2) }
        ProtocolButton { objectName: "recentTab"; text: qsTr("Recent"); iconName: "document-open-recent"; width: 92; chosen: root.section===3 && !root.searching; accent: root.accent; animate: root.animate; glowStrength: root.glowStrength; onClicked: root.setSection(3) }
    }
    GridView {
        id: grid
        objectName: "applicationGrid"
        x: 20; y: 202; width: parent.width-40; height: parent.height-286
        cellWidth: width/Math.max(2,Math.floor(width/121)); cellHeight: 110
        clip: true; model: root.activeModel; currentIndex: 0
        keyNavigationEnabled: true; keyNavigationWraps: true
        onCurrentIndexChanged: positionViewAtIndex(currentIndex,GridView.Contain)
        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
        delegate: Item {
            id: app
            required property int index
            required property var model
            readonly property var entry: model.modelData || model
            readonly property string appId: String(entry.favoriteId || "")
            readonly property bool pinned: root.favoriteLookup?root.favoriteLookup(appId):root.favoriteIds.indexOf(appId)>=0
            width: grid.cellWidth; height: grid.cellHeight
            ProtocolButton {
                id: tile
                objectName: "appTile"+app.index
                anchors.fill: parent; anchors.margins: 5
                text: String(app.entry.display || "")
                accent: root.accent; animate: root.animate; glowStrength: root.glowStrength; cornerRadius: 17
                chosen: grid.activeFocus && app.index===grid.currentIndex
                quiet: true; activeFocusOnTab: false
                enabled: !app.entry.disabled
                contentItem: Item {
                    Loader { x: (parent.width-34)/2; y: 12; width: 34; height: 34; property var iconSource: app.entry.decoration; sourceComponent: root.iconFactory }
                    Text { x: 6; y: 57; width: parent.width-12; text: String(app.entry.display || ""); color: "#f5dce6"; font.pixelSize: 12; horizontalAlignment: Text.AlignHCenter; elide: Text.ElideRight; textFormat: Text.PlainText }
                    Rectangle { width: tile.hovered ? 34 : 12; height: 2; radius: 1; anchors.horizontalCenter: parent.horizontalCenter; y: parent.height-10; color: root.accent; opacity: tile.hovered || tile.chosen ? .9 : .15; Behavior on width { enabled: root.animate; NumberAnimation { duration: 140 } } }
                }
                onClicked: { grid.currentIndex=app.index; root.launchRequested(app.index,app.appId,app.entry.sourceIndex===undefined?-1:app.entry.sourceIndex) }
            }
            ProtocolButton {
                objectName: "appPin"+app.index
                x: parent.width-33; y: 8; width: 24; height: 24; cornerRadius: 8; textSize: 14
                text: ""; iconName: app.pinned?"emblem-favorite":"non-starred"; Accessible.name: app.pinned ? qsTr("Unpin %1").arg(app.entry.display) : qsTr("Pin %1").arg(app.entry.display)
                visible: app.appId.length>0 && (tile.hovered || hovered || app.pinned || tile.chosen)
                accent: root.accent; animate: root.animate; chosen: app.pinned
                onClicked: root.pinRequested(app.appId)
            }
        }
        Text { anchors.centerIn: parent; visible: grid.count===0; width: parent.width-30; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap; color: "#b68b9d"; font.pixelSize: 14; text: root.searching ? qsTr("No matching applications") : root.section===0 ? qsTr("Pin an application using its star in All applications.") : root.section===3 ? qsTr("Your recent launches appear here. Enable recent history in Configure if it is turned off.") : qsTr("No applications available") }
        Keys.onReturnPressed: root.activate()
        Keys.onEnterPressed: root.activate()
        Keys.onPressed: event => { if(event.text.length && !event.modifiers && event.key!==Qt.Key_Return && event.key!==Qt.Key_Enter) { search.forceActiveFocus(); search.text+=event.text; event.accepted=true } }
    }
    Rectangle { x: 27; y: parent.height-77; width: parent.width-54; height: 1; color: "#432332" }
    Row {
        x: 26; y: parent.height-61; spacing: 8
        ProtocolButton { text: qsTr("Home"); iconName: "go-home"; accent: root.accent; animate: root.animate; onClicked: root.placeRequested("Home") }
        ProtocolButton { text: qsTr("Downloads"); iconName: "folder-download"; accent: root.accent; animate: root.animate; onClicked: root.placeRequested("Downloads") }
        ProtocolButton { text: qsTr("Lock"); iconName: "system-lock-screen"; accent: root.accent; animate: root.animate; onClicked: root.lockRequested() }
    }
    ProtocolButton { objectName: "clearRecentButton"; anchors.right: parent.right; anchors.rightMargin: 26; y: parent.height-61; width: 136; text: qsTr("Clear recent"); iconName: "edit-clear-history"; visible: root.section===3 && !root.searching; accent: root.accent; animate: root.animate; onClicked: root.clearRecentRequested() }
    Text { visible: root.section!==3 || root.searching; anchors.right: parent.right; anchors.rightMargin: 29; y: parent.height-48; text: qsTr("↑ ↓  select   ↵  launch"); color: "#a36f83"; font.pixelSize: 10 }
    Keys.onEscapePressed: { if(search.text.length) search.clear(); else root.closeRequested() }
}
