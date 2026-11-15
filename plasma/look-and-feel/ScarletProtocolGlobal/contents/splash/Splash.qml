import QtQuick

Item {
    id: root
    property int stage: 0
    anchors.fill: parent

    Rectangle { anchors.fill: parent; color: "#101116" }

    // The host advances stage during Plasma startup. The motion is visual;
    // there is no timer that delays the session or overrides the host.
    Rectangle {
        width: Math.min(parent.width * 0.82, 580)
        height: 210
        anchors.centerIn: parent
        radius: 26
        color: "#171318"
        border.color: "#872242"
        border.width: 1

        Rectangle {
            anchors.fill: parent
            anchors.margins: 8
            radius: 20
            color: "transparent"
            border.color: "#37202A"
        }

        Text {
            anchors.left: parent.left
            anchors.leftMargin: 34
            anchors.top: parent.top
            anchors.topMargin: 28
            text: "// SCARLET PROTOCOL"
            color: "#E41951"
            font.family: "monospace"
            font.pixelSize: 15
            font.bold: true
            font.letterSpacing: 2
        }
        Text {
            anchors.left: parent.left
            anchors.leftMargin: 34
            anchors.top: parent.top
            anchors.topMargin: 70
            text: "BLACKOUT / DESKTOP"
            color: "#E8DCE0"
            font.family: "monospace"
            font.pixelSize: 22
            font.bold: true
        }
        Text {
            anchors.left: parent.left
            anchors.leftMargin: 34
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 29
            text: "SYSTEM INITIALIZING"
            color: "#AF7185"
            font.family: "monospace"
            font.pixelSize: 11
            font.letterSpacing: 2
        }
        Text {
            anchors.right: parent.right
            anchors.rightMargin: 34
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 29
            text: ("0" + Math.min(6, Math.max(0, root.stage))).slice(-2) + " / 06"
            color: "#E41951"
            font.family: "monospace"
            font.pixelSize: 11
        }
        Rectangle {
            x: 34; y: parent.height - 53
            width: parent.width - 68; height: 4
            radius: 2; color: "#3B1D2C"
            Rectangle {
                width: parent.width * Math.max(0.05, Math.min(1, root.stage / 6))
                height: parent.height; radius: 2
                color: "#FF0051"
                Behavior on width { NumberAnimation { duration: 240; easing.type: Easing.OutCubic } }
            }
        }
        Rectangle {
            id: beacon
            width: 40; height: 40; radius: 20
            anchors.top: parent.top; anchors.topMargin: 36
            anchors.right: parent.right; anchors.rightMargin: 38
            color: "#351723"
            border.color: "#FF0051"
            border.width: 2
            Rectangle { anchors.centerIn: parent; width: 9; height: 9; radius: 5; color: "#FF0051" }
            SequentialAnimation on opacity {
                loops: Animation.Infinite
                NumberAnimation { to: 0.48; duration: 600 }
                NumberAnimation { to: 1; duration: 600 }
            }
        }
    }
}
