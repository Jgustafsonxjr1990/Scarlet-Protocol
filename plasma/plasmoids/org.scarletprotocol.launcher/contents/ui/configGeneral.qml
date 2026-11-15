import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {

    property alias cfg_animate: motion.checked
    property alias cfg_glowStrength: strength.value
    property alias cfg_accentColor: accent.text
    property alias cfg_rememberRecent: remember.checked

    Label { text: qsTr("Accent color") }
    TextField { id: accent; placeholderText: "#ff315b"; validator: RegularExpressionValidator { regularExpression: /^#[0-9a-fA-F]{6}$/ } }
    Label { text: qsTr("Glow strength") }
    Slider { id: strength; from: 0; to: 100; stepSize: 1; Layout.preferredWidth: 260 }
    CheckBox { id: motion; text: qsTr("Animate hover transitions") }
    CheckBox { id: remember; text: qsTr("Remember my last 12 launched applications locally") }
    Label { text: qsTr("Ctrl+1–4 switches launcher sections. Ctrl+L focuses search."); wrapMode: Text.WordWrap; Layout.maximumWidth: 380 }
    Item { Layout.fillHeight: true }
}
