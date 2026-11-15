import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {

    property alias cfg_animate: motion.checked
    property alias cfg_glowStrength: strength.value
    property alias cfg_accentColor: accent.text
    property alias cfg_twentyFourHour: twentyFourHourCheck.checked
    property alias cfg_showSeconds: showSecondsCheck.checked
    property alias cfg_mondayFirst: mondayFirstCheck.checked
    property alias cfg_showWeekNumbers: showWeekNumbersCheck.checked

    Label { text: qsTr("Accent color") }
    TextField { id: accent; placeholderText: "#ff315b"; validator: RegularExpressionValidator { regularExpression: /^#[0-9a-fA-F]{6}$/ } }
    Label { text: qsTr("Glow strength") }
    Slider { id: strength; from: 0; to: 100; stepSize: 1; Layout.preferredWidth: 260 }
    CheckBox { id: motion; text: qsTr("Animate hover transitions") }
    CheckBox { id: twentyFourHourCheck; text: qsTr("Use a 24-hour clock") }
    CheckBox { id: showSecondsCheck; text: qsTr("Show seconds in the calendar") }
    CheckBox { id: mondayFirstCheck; text: qsTr("Start weeks on Monday") }
    CheckBox { id: showWeekNumbersCheck; text: qsTr("Show ISO week numbers") }
    Item { Layout.fillHeight: true }
}
