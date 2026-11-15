import QtQuick
import QtQuick.Controls as QQC2
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import org.kde.kquickcontrols as KQuickControls

Kirigami.FormLayout {
    property alias cfg_accentColor: accent.color
    property alias cfg_cpuSensor: cpu.text
    property alias cfg_memorySensor: memory.text
    property alias cfg_gpuSensor: gpu.text
    property alias cfg_temperatureSensor: temperature.text
    property alias cfg_networkSensor: network.text
    property alias cfg_showGpu: showGpu.checked
    property alias cfg_showTemperature: showTemperature.checked
    property alias cfg_showNetwork: showNetwork.checked
    property alias cfg_showFocus: showFocus.checked
    property alias cfg_focusMinutes: focus.value

    Kirigami.Heading { text: "Appearance"; level: 3; Kirigami.FormData.isSection: true }
    KQuickControls.ColorButton { id: accent; Kirigami.FormData.label: "Accent color:" }
    Kirigami.Heading { text: "System Monitor sensor IDs"; level: 3; Kirigami.FormData.isSection: true }
    QQC2.Label {
        text: "CPU and memory work on most systems. Choose hardware-specific IDs in System Monitor → Edit Page → Add Sensor. Leave an ID empty to show a setup prompt."
        wrapMode: Text.WordWrap
        Layout.fillWidth: true
    }
    QQC2.TextField { id: cpu; Kirigami.FormData.label: "CPU:" }
    QQC2.TextField { id: memory; Kirigami.FormData.label: "Memory:" }
    QQC2.TextField { id: gpu; Kirigami.FormData.label: "GPU:" }
    QQC2.TextField { id: temperature; Kirigami.FormData.label: "Temperature:" }
    QQC2.TextField { id: network; Kirigami.FormData.label: "Network speed:" }
    QQC2.CheckBox { id: showGpu; text: "Show GPU" }
    QQC2.CheckBox { id: showTemperature; text: "Show temperature" }
    QQC2.CheckBox { id: showNetwork; text: "Show network speed" }
    Kirigami.Heading { text: "Focus timer"; level: 3; Kirigami.FormData.isSection: true }
    QQC2.CheckBox { id: showFocus; text: "Show focus timer" }
    QQC2.SpinBox { id: focus; Kirigami.FormData.label: "Minutes:"; from: 1; to: 180 }
}
