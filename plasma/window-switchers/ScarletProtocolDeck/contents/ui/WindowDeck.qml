import QtQuick

FocusScope {
    id: root
    property var windowModel
    property int selectedIndex: 0
    property Component thumbnailFactory
    property Component iconFactory
    readonly property int count: grid.count
    readonly property int columns: Math.max(1, Math.min(count === 4 ? 2 : 3, Math.max(1, count), Math.floor((width - 36) / 240)))
    readonly property int rows: Math.max(1, Math.ceil(count / columns))
    signal selected(int index)
    signal activated(int index)

    function navigate(key) {
        switch (key) {
        case Qt.Key_Left: grid.moveCurrentIndexLeft(); break;
        case Qt.Key_Right: grid.moveCurrentIndexRight(); break;
        case Qt.Key_Up: grid.moveCurrentIndexUp(); break;
        case Qt.Key_Down: grid.moveCurrentIndexDown(); break;
        default: return false;
        }
        return true
    }

    implicitWidth: 900
    implicitHeight: 89 + Math.min(2, rows) * grid.cellHeight
    Accessible.role: Accessible.List
    Accessible.name: qsTr("Window switcher")

    Rectangle {
        anchors.fill: parent
        radius: 26
        color: "#101116"
        border.color: "#952544"
        Rectangle {
            anchors.fill: parent
            anchors.margins: 6
            radius: 21
            color: "transparent"
            border.color: "#351d28"
        }
    }
    Text {
        x: 23
        y: 19
        text: qsTr("Windows")
        color: "#f2dce5"
        font.pixelSize: 18
        font.bold: true
    }
    Text {
        anchors.right: parent.right
        anchors.rightMargin: 24
        y: 23
        text: root.count === 0 ? qsTr("No open windows") : (root.selectedIndex + 1) + " / " + root.count
        color: "#c68a9e"
        font.family: "monospace"
        font.pixelSize: 13
    }

    GridView {
        id: grid
        x: 18
        y: 56
        width: parent.width - 36
        height: Math.max(0, parent.height - y - 17)
        cellWidth: width / root.columns
        cellHeight: Math.round(cellWidth * .58) + 48
        model: root.windowModel
        currentIndex: root.selectedIndex
        focus: true
        clip: true
        keyNavigationEnabled: false
        keyNavigationWraps: true
        highlightMoveDuration: 130
        highlightRangeMode: GridView.ApplyRange
        preferredHighlightBegin: 0
        preferredHighlightEnd: height
        onCurrentIndexChanged: {
            if (currentIndex >= 0) root.selected(currentIndex)
            positionViewAtIndex(currentIndex, GridView.Contain)
        }

        highlight: Rectangle {
            z: 2
            radius: 18
            color: "transparent"
            border.color: "#ff3c70"
            border.width: 2
            Rectangle {
                anchors.fill: parent
                anchors.margins: -3
                color: "transparent"
                radius: 21
                border.width: 2
                border.color: "#3bff1557"
            }
        }
        delegate: Item {
            id: card
            required property int index
            required property var model
            width: grid.cellWidth
            height: grid.cellHeight
            readonly property bool selected: index === grid.currentIndex

            Rectangle {
                anchors.fill: parent
                anchors.margins: 6
                radius: 14
                color: card.selected ? "#24151e" : hovered.containsMouse ? "#201820" : "#17151b"
                Behavior on color { ColorAnimation { duration: 130 } }
            }
            Loader {
                id: thumbnail
                x: 16
                y: 17
                width: parent.width - 32
                height: parent.height - 65
                property var windowId: card.model.windowId
                sourceComponent: root.thumbnailFactory
            }
            Loader {
                x: 16
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 18
                width: 20
                height: 20
                property var iconSource: card.model.icon
                sourceComponent: root.iconFactory
            }
            Text {
                x: 44
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 18
                width: parent.width - x - 18
                text: card.model.caption || ""
                textFormat: Text.PlainText
                elide: Text.ElideRight
                color: card.selected ? "#fff0f5" : "#b799a6"
                font.pixelSize: 13
            }
            MouseArea {
                id: hovered
                anchors.fill: parent
                hoverEnabled: true
                Accessible.role: Accessible.ListItem
                Accessible.name: card.model.caption || ""
                Accessible.selected: card.selected
                onClicked: root.activated(card.index)
            }
        }
        Keys.onPressed: event => {
            if (root.navigate(event.key)) event.accepted = true
        }
    }
}
