import QtQuick
import QtQuick.Layouts
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.plasmoid
import org.kde.ksysguard.sensors as Sensors

PlasmoidItem {
    id: root
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground
    Plasmoid.icon: "utilities-system-monitor"
    width: 470
    height: 466
    preferredRepresentation: Plasmoid.formFactor === PlasmaCore.Types.Planar ? fullRepresentation : compactRepresentation
    toolTipMainText: "Scarlet Protocol — System Core"
    toolTipSubText: "Live status and focus timer"

    property color accent: plasmoid.configuration.accentColor
    property int remainingSeconds: Math.max(1, plasmoid.configuration.focusMinutes) * 60
    property bool focusRunning: false
    property double focusEndsAt: 0
    property string clockText: Qt.formatTime(new Date(), "hh:mm")
    property string dateText: Qt.formatDate(new Date(), "ddd, MMM d")
    property var sensorCards: [
        { label: "CPU", path: plasmoid.configuration.cpuSensor, show: true, percent: true },
        { label: "MEMORY", path: plasmoid.configuration.memorySensor, show: true, percent: true },
        { label: "GPU", path: plasmoid.configuration.gpuSensor, show: plasmoid.configuration.showGpu, percent: false },
        { label: "TEMPERATURE", path: plasmoid.configuration.temperatureSensor, show: plasmoid.configuration.showTemperature, percent: false },
        { label: "NETWORK", path: plasmoid.configuration.networkSensor, show: plasmoid.configuration.showNetwork, percent: false }
    ]

    Timer {
        interval: 1000
        repeat: true
        running: root.focusRunning
        onTriggered: {
            root.remainingSeconds = Math.max(0, Math.ceil((root.focusEndsAt - Date.now()) / 1000))
            if (root.remainingSeconds === 0) root.focusRunning = false
        }
    }
    Timer {
        interval: 10000
        repeat: true
        running: true
        onTriggered: {
            root.clockText = Qt.formatTime(new Date(), "hh:mm")
            root.dateText = Qt.formatDate(new Date(), "ddd, MMM d")
        }
    }

    compactRepresentation: Rectangle {
        implicitWidth: 42
        implicitHeight: 40
        radius: 13
        color: "#171318"
        border.color: root.accent
        Text { anchors.centerIn: parent; text: "◇"; color: root.accent; font.pixelSize: 23 }
        MouseArea { anchors.fill: parent; onClicked: root.expanded = !root.expanded }
    }

    fullRepresentation: Item {
        implicitWidth: 470
        implicitHeight: content.implicitHeight + 44
        Layout.minimumWidth: 300
        Layout.minimumHeight: implicitHeight

        Rectangle {
            anchors.fill: parent
            radius: 24
            color: "#101116"
            border.color: root.accent
            border.width: 1
        }
        Rectangle {
            anchors.fill: parent
            anchors.margins: 7
            radius: 19
            color: "transparent"
            border.color: "#3E1E2D"
            border.width: 1
        }
        ColumnLayout {
            id: content
            anchors.fill: parent
            anchors.margins: 22
            spacing: 13

            RowLayout {
                Layout.fillWidth: true
                spacing: 10
                Rectangle { width: 10; height: 10; radius: 5; color: root.accent }
                ColumnLayout {
                    spacing: 1
                    Text { text: "SCARLET / SYSTEM CORE"; color: "#E8DCE0"; font.bold: true; font.family: "monospace"; font.pixelSize: 16 }
                    Text { text: "LIVE TELEMETRY  //  DESKTOP"; color: "#A56D80"; font.family: "monospace"; font.pixelSize: 10 }
                }
                Item { Layout.fillWidth: true }
                ColumnLayout {
                    spacing: 1
                    Text { text: root.clockText; color: root.accent; font.family: "monospace"; font.bold: true; font.pixelSize: 17 }
                    Text { text: root.dateText; color: "#A56D80"; font.family: "monospace"; font.pixelSize: 9 }
                }
            }
            Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 1; color: "#70213D" }

            GridLayout {
                Layout.fillWidth: true
                columns: width < 390 ? 1 : 2
                rowSpacing: 10
                columnSpacing: 10
                Repeater {
                    model: root.sensorCards
                    delegate: Rectangle {
                        id: card
                        required property var modelData
                        visible: modelData.show
                        Layout.fillWidth: true
                        Layout.preferredWidth: 190
                        Layout.preferredHeight: visible ? 81 : 0
                        radius: 17
                        color: hovered.hovered ? "#301823" : "#1B151C"
                        border.color: hovered.hovered ? root.accent : "#5B2038"
                        border.width: 1
                        Behavior on color { ColorAnimation { duration: 170 } }
                        Behavior on border.color { ColorAnimation { duration: 170 } }
                        HoverHandler { id: hovered }
                        Sensors.Sensor {
                            id: sensor
                            sensorId: card.modelData.path || ""
                            enabled: card.visible && sensorId.length > 0
                            updateRateLimit: 1000
                        }
                        Text {
                            x: 16; y: 13
                            text: "// " + card.modelData.label
                            color: hovered.hovered ? root.accent : "#B9738B"
                            font.family: "monospace"; font.pixelSize: 11; font.bold: true
                        }
                        Text {
                            x: 16; y: 33
                            width: trace.visible ? trace.x - x - 5 : parent.width - 32
                            text: card.modelData.path ? (sensor.status === Sensors.Sensor.Ready && sensor.formattedValue ? sensor.formattedValue : "—") : "SET SENSOR ID"
                            color: card.modelData.path ? "#E8DCE0" : "#876373"
                            elide: Text.ElideRight
                            font.family: "monospace"; font.pixelSize: card.modelData.path ? 20 : 12
                            font.bold: true
                        }
                        HistoryTrace {
                            id: trace
                            visible: card.modelData.percent && card.width >= 150
                            x: card.width - width - 16
                            y: 36
                            width: Math.min(70, card.width * 0.28)
                            height: 21
                            ink: root.accent
                        }
                        Timer {
                            property double lastSample: 0
                            interval: 1000
                            running: trace.visible && sensor.enabled
                            repeat: true
                            onTriggered: {
                                const now = Date.now()
                                if (lastSample > 0 && now - lastSample > 2000) trace.readings = []
                                lastSample = now
                                const value = sensor.value
                                const ready = sensor.status === Sensors.Sensor.Ready && value != null && isFinite(Number(value))
                                trace.append(ready ? Number(value) : null)
                            }
                            onRunningChanged: if (!running) trace.readings = []
                        }
                        Rectangle {
                            visible: card.modelData.percent
                            x: 16; y: parent.height - 12
                            width: parent.width - 32; height: 3; radius: 2
                            color: "#422033"
                            Rectangle {
                                width: parent.width * (isFinite(Number(sensor.value)) ? Math.max(0, Math.min(100, Number(sensor.value))) : 0) / 100
                                height: parent.height; radius: 2; color: root.accent
                                Behavior on width { NumberAnimation { duration: 220 } }
                            }
                        }
                    }
                }
            }
            Item { Layout.fillHeight: true }
            Rectangle {
                visible: plasmoid.configuration.showFocus
                Layout.fillWidth: true
                Layout.preferredHeight: visible ? 74 : 0
                radius: 17
                color: "#21141D"
                border.color: "#70213D"
                RowLayout {
                    anchors.fill: parent; anchors.margins: 14; spacing: 12
                    ColumnLayout {
                        spacing: 2
                        Text { text: "FOCUS SEQUENCE"; color: root.accent; font.family: "monospace"; font.bold: true; font.pixelSize: 11 }
                        Text {
                            text: Math.floor(root.remainingSeconds / 60).toString().padStart(2, "0") + ":" +
                                  ("0" + (root.remainingSeconds % 60)).slice(-2)
                            color: "#E8DCE0"; font.family: "monospace"; font.pixelSize: 21
                        }
                    }
                    Item { Layout.fillWidth: true }
                    CoreButton {
                        text: root.focusRunning ? "PAUSE" : "START"
                        iconName: root.focusRunning?"media-playback-pause":"media-playback-start"
                        actionName: root.focusRunning ? qsTr("Pause focus timer") : qsTr("Start focus timer")
                        accent: root.accent
                        onClicked: {
                            if (root.focusRunning) {
                                root.remainingSeconds = Math.max(0, Math.ceil((root.focusEndsAt - Date.now()) / 1000))
                                root.focusRunning = false
                            } else {
                                if (root.remainingSeconds === 0) root.remainingSeconds = Math.max(1, plasmoid.configuration.focusMinutes) * 60
                                root.focusEndsAt = Date.now() + root.remainingSeconds * 1000
                                root.focusRunning = true
                            }
                        }
                    }
                    CoreButton {
                        implicitWidth: 38
                        text: ""
                        iconName: "view-refresh"
                        actionName: qsTr("Reset focus timer")
                        accent: root.accent
                        onClicked: {
                            root.focusRunning = false
                            root.remainingSeconds = Math.max(1, plasmoid.configuration.focusMinutes) * 60
                        }
                    }
                }
            }
            RowLayout {
                Layout.fillWidth: true
                Text { text: "◇  PROTOCOL ACTIVE"; color: root.accent; font.family: "monospace"; font.pixelSize: 10 }
                Item { Layout.fillWidth: true }
                Text { text: "KDE / PLASMA 6"; color: "#8E6373"; font.family: "monospace"; font.pixelSize: 10 }
            }
        }
    }
}
