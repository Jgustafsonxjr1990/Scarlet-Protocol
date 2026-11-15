// SPDX-License-Identifier: GPL-2.0-or-later
import QtQuick
import QtQuick.Controls

AbstractButton {
    id: button
    property color accent: "#ff315b"
    property bool chosen: false
    property bool quiet: false
    property bool animate: true
    property real glowStrength: .7
    property real cornerRadius: 12
    property int textSize: 13
    property string iconName: ""
    implicitWidth: Math.max(36,label.implicitWidth+26+(iconName.length?24:0))
    implicitHeight: 36
    hoverEnabled: true
    activeFocusOnTab: true
    Accessible.name: text
    background: Item {
        Rectangle {
            anchors.fill: parent; anchors.margins: -2; radius: button.cornerRadius+2
            color: "transparent"; border.width: 3; border.color: button.accent
            opacity: (button.hovered || button.visualFocus ? .18 : button.chosen ? .1 : 0)*button.glowStrength
            Behavior on opacity { enabled: button.animate; NumberAnimation { duration: 130 } }
        }
        Rectangle {
            id: face
            anchors.fill: parent; radius: button.cornerRadius
            color: button.down ? "#602137" : button.hovered ? "#38202d" : button.chosen ? "#361a28" : button.quiet ? "transparent" : "#19171f"
            border.color: button.hovered || button.visualFocus || button.chosen ? button.accent : "#402331"
            opacity: button.enabled ? 1 : .4
            Behavior on color { enabled: button.animate; ColorAnimation { duration: 130 } }
            gradient: Gradient {
                GradientStop { position: 0; color: button.down ? "#61263f" : button.hovered || button.chosen ? "#553047" : "#2b2532" }
                GradientStop { position: .35; color: button.down ? "#432035" : button.hovered || button.chosen ? "#382034" : "#1b1923" }
                GradientStop { position: 1; color: button.down ? "#2d1525" : button.hovered || button.chosen ? "#261724" : "#12141b" }
            }
            Rectangle {
                x: Math.min(button.cornerRadius, parent.width/3); y: 3
                width: Math.max(0,parent.width-2*x); height: 1
                color: "#ffd7e7"; opacity: button.hovered || button.chosen ? .4 : .12
            }
            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter; y: parent.height-4
                width: Math.min(28,parent.width*.35); height: 2; radius: 1
                color: button.accent; opacity: button.hovered || button.chosen || button.visualFocus ? .95 : .24
                Behavior on opacity { enabled: button.animate; NumberAnimation { duration: 130 } }
            }
            Rectangle { visible: button.visualFocus; anchors.fill: parent; anchors.margins: 3; radius: button.cornerRadius-3; color: "transparent"; border.color: "#fbd8e4" }
        }
    }
    contentItem: Item {
        readonly property real groupWidth: Math.min(width,label.implicitWidth+(button.iconName.length?18+(button.text.length?6:0):0))
        Image {
            id: actionIcon
            objectName: "buttonIcon"
            width: 18; height: 18
            x: (parent.width-parent.groupWidth)/2; anchors.verticalCenter: parent.verticalCenter
            visible: button.iconName.length>0
            source: visible?"../icons/"+button.iconName+".svg":""
            sourceSize.width: 36; sourceSize.height: 36
            fillMode: Image.PreserveAspectFit
            opacity: button.enabled?1:.4
        }
        Text {
            id: label
            x: button.iconName.length?actionIcon.x+24:(parent.width-parent.groupWidth)/2
            width: Math.max(0,parent.groupWidth-(button.iconName.length?24:0)); height: parent.height
            text: button.text; color: button.enabled ? "#f6dce6" : "#7c6570"
            font.pixelSize: button.textSize; font.weight: button.chosen ? Font.DemiBold : Font.Normal
            horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
            textFormat: Text.PlainText; elide: Text.ElideRight
        }
    }
}
