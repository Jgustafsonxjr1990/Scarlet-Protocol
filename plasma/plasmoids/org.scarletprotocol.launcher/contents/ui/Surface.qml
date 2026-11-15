// SPDX-License-Identifier: GPL-2.0-or-later
import QtQuick

Item {
    id: root
    property color accent: "#ff315b"
    property real glowStrength: .7
    property real cornerRadius: 27
    Rectangle { anchors.fill: parent; anchors.margins: -3; radius: root.cornerRadius+3; color: "transparent"; border.width: 5; border.color: root.accent; opacity: .065*root.glowStrength }
    Rectangle { anchors.fill: parent; radius: root.cornerRadius; color: "#101116"; border.color: Qt.rgba(root.accent.r,root.accent.g,root.accent.b,.75); border.width: 1 }
    Rectangle { anchors.fill: parent; anchors.margins: 5; radius: root.cornerRadius-5; color: "transparent"; border.color: "#38202d" }
    Rectangle { x: 28; y: 5; width: Math.min(104,parent.width/4); height: 1; color: root.accent }
    Rectangle { x: parent.width-65; y: parent.height-6; width: 35; height: 1; color: root.accent; opacity: .65 }
    Row {
        x: parent.width-57; y: 20; spacing: 4
        Repeater { model: 3; Rectangle { required property int index; width: 3; height: index===0?10:6; radius: 1; color: root.accent; opacity: .8-index*.22 } }
    }
    Canvas {
        id: etching
        anchors.fill: parent
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
        Connections { target: root; function onAccentChanged() { etching.requestPaint() } }
        onPaint: {
            var c=getContext("2d");c.reset();
            for(var corner=0;corner<4;corner++) {
                c.save();c.translate(corner%2?width:0,corner>1?height:0);c.scale(corner%2?-1:1,corner>1?-1:1);
                c.lineCap="round";c.lineWidth=7;c.strokeStyle="#321e30";c.beginPath();c.moveTo(37,8);c.quadraticCurveTo(8,8,8,37);c.stroke();
                c.lineWidth=1.8;c.strokeStyle=root.accent;c.beginPath();c.moveTo(37,8);c.quadraticCurveTo(8,8,8,37);c.stroke();
                c.lineWidth=.7;c.strokeStyle="#ffbdd5";c.beginPath();c.moveTo(36,12);c.quadraticCurveTo(12,12,12,36);c.stroke();
                c.fillStyle="#090c12";c.strokeStyle=root.accent;c.lineWidth=.8;c.beginPath();c.arc(20,20,2,0,Math.PI*2);c.fill();c.stroke();
                c.restore();
            }
            // Fine perpendicular cuts continue the reference header's border language.
            c.lineCap="butt";c.lineWidth=1.2;c.strokeStyle=root.accent;
            c.beginPath();c.moveTo(37,5);c.lineTo(width-37,5);c.moveTo(37,height-6);c.lineTo(width-37,height-6);
            c.moveTo(5,37);c.lineTo(5,height-37);c.moveTo(width-6,37);c.lineTo(width-6,height-37);c.stroke();
            for(var x=48;x<width-36;x+=32) {
                c.strokeStyle="#05060b";c.lineWidth=1.8;c.beginPath();c.moveTo(x,0);c.lineTo(x,13);c.moveTo(x,height-14);c.lineTo(x,height-1);c.stroke();
                c.strokeStyle="#ffb5cf";c.lineWidth=.6;c.beginPath();c.moveTo(x+1.5,4);c.lineTo(x+1.5,6);c.moveTo(x+1.5,height-7);c.lineTo(x+1.5,height-5);c.stroke();
            }
            for(var y=48;y<height-36;y+=32) {
                c.strokeStyle="#05060b";c.lineWidth=1.8;c.beginPath();c.moveTo(0,y);c.lineTo(13,y);c.moveTo(width-14,y);c.lineTo(width-1,y);c.stroke();
            }
        }
    }
}
