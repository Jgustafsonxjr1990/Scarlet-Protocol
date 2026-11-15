import QtQuick
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

Kirigami.FormLayout {
    id: page
    property alias cfg_DialOnLeft: left.checked
    property alias cfg_ShowDate: date.checked
    property alias cfg_DigitalReadout: digital.checked
    property bool cfg_DialOnLeftDefault
    property bool cfg_ShowDateDefault
    property bool cfg_DigitalReadoutDefault
    property var configDialog
    property var parentLayout
    signal configurationChanged()

    Controls.CheckBox { id: left; text: qsTr("Place dial on the left in landscape"); onToggled: page.configurationChanged() }
    Controls.CheckBox { id: date; text: qsTr("Show date"); onToggled: page.configurationChanged() }
    Controls.CheckBox { id: digital; text: qsTr("Show digital clock"); onToggled: page.configurationChanged() }
}
