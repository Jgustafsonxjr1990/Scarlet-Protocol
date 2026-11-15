import QtQuick
import QtQuick.Controls as Controls

Controls.Button {
    id: button
    property color accent: "#e41951"
    property string actionName: text
    property string iconName: ""
    Accessible.name: actionName
    implicitWidth: 80
    implicitHeight: 34
    hoverEnabled: true
    focusPolicy: Qt.StrongFocus
    padding: 4

    background: Rectangle {
        radius: 12
        color: button.down ? "#701a34" : button.hovered ? "#461729" : "#21161d"
        border.color: button.visualFocus ? "#ffe0e9" : button.hovered || button.down ? button.accent : "#7b324a"
        border.width: button.visualFocus ? 2 : 1
        Behavior on color { ColorAnimation { duration: 130 } }
        Behavior on border.color { ColorAnimation { duration: 130 } }
    }
    contentItem: Row {
        spacing: button.text.length?6:0
        anchors.centerIn: parent
        Image { width: visible?18:0; height: 18; visible: button.iconName.length>0; anchors.verticalCenter: parent.verticalCenter; source: visible?"../icons/"+button.iconName+".svg":""; fillMode: Image.PreserveAspectFit; sourceSize.width: 36; sourceSize.height: 36; opacity: button.enabled?1:.4 }
        Text { text: button.text; color: button.enabled?"#f5e4ea":"#927b83"; font.family: "monospace"; font.pixelSize: 12; font.bold: true; anchors.verticalCenter: parent.verticalCenter }
    }
}
