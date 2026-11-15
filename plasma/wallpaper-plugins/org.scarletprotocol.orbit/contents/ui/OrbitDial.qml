import QtQuick 2.15

Rectangle {
    id: surface
    color: "#101116"
    property date now: new Date()
    property bool dialOnLeft: false
    property bool showDate: true
    property bool digitalReadout: false
    readonly property bool portrait: width < height
    function syncClock() {
        const observed = new Date()
        now = observed
        minuteClock.interval = 60000 - (observed.getSeconds() * 1000 + observed.getMilliseconds())
        minuteClock.restart()
    }
    Timer { id: minuteClock; onTriggered: surface.syncClock() }
    Component.onCompleted: if (visible) syncClock()
    onVisibleChanged: {
        if (visible) syncClock()
        else minuteClock.stop()
    }

    Item {
        id: dial
        width: Math.min(surface.width * (surface.portrait ? 0.79 : 0.43), surface.height * 0.75)
        height: width
        x: surface.width * (surface.portrait ? 0.5 : surface.dialOnLeft ? 0.29 : 0.71) - width/2
        y: surface.height * (surface.portrait ? 0.39 : 0.50) - height/2
        Image { anchors.fill: parent; source: "face.png"; mipmap: true; fillMode: Image.PreserveAspectFit }
        Item {
            anchors.fill: parent
            rotation: (surface.now.getHours() % 12 + surface.now.getMinutes()/60) * 30
            Rectangle { x: parent.width*.493; y: parent.height*.25; width: parent.width*.014; height: parent.height*.25; radius: width/2; color: "#f1cad5" }
        }
        Item {
            anchors.fill: parent
            rotation: surface.now.getMinutes()*6
            Rectangle { x: parent.width*.495; y: parent.height*.10; width: parent.width*.010; height: parent.height*.40; radius: width/2; color: "#ff245d" }
            Rectangle { x: parent.width*.492; y: parent.height*.04; width: parent.width*.016; height: width; radius: width/2; color: "#ff799a" }
        }
        Rectangle { anchors.centerIn: parent; width: parent.width*.041; height: width; radius: width/2; color:"#101116"; border.color:"#ed4776"; border.width:2 }
    }
    Column {
        x: surface.width*(surface.portrait ? .1 : surface.dialOnLeft ? .63 : .09)
        y: surface.height*(surface.portrait ? .74 : .63)
        spacing: 5
        Text { text:"SCARLET  /  PROTOCOL"; color:"#ff547e"; font.family:"monospace"; font.bold:true; font.pixelSize:Math.max(12, surface.width*.014) }
        Text { visible:surface.digitalReadout; text:Qt.formatTime(surface.now, "HH:mm"); color:"#f3e3e8"; font.family:"monospace"; font.pixelSize:Math.max(24, surface.width*.031) }
        Text { visible:surface.showDate; text:Qt.formatDate(surface.now,"dddd, d MMMM"); color:"#bb9ba6"; font.pixelSize:Math.max(11, surface.width*.010) }
    }
}
