import QtQuick
import org.kde.plasma.core as PlasmaCore
import org.kde.kwin as KWin
import org.kde.kirigami as Kirigami

KWin.TabBoxSwitcher {
    id: tabBox

    Instantiator {
        active: tabBox.visible
        delegate: PlasmaCore.Dialog {
            location: PlasmaCore.Types.Floating
            backgroundHints: PlasmaCore.Dialog.NoBackground
            visible: true
            flags: Qt.Popup | Qt.X11BypassWindowManagerHint
            x: tabBox.screenGeometry.x + (tabBox.screenGeometry.width - deck.width) / 2
            y: tabBox.screenGeometry.y + (tabBox.screenGeometry.height - deck.height) / 2

            mainItem: WindowDeck {
                id: deck
                focus: true
                width: Math.min(900, Math.max(310, count * 276 + 36), tabBox.screenGeometry.width * .87)
                height: Math.min(implicitHeight, tabBox.screenGeometry.height * .78)
                windowModel: tabBox.model
                selectedIndex: tabBox.currentIndex
                onSelected: index => tabBox.currentIndex = index
                onActivated: index => tabBox.model.activate(index)

                thumbnailFactory: Component {
                    KWin.WindowThumbnail {
                        wId: parent.windowId
                    }
                }
                iconFactory: Component {
                    Kirigami.Icon {
                        source: parent.iconSource || "application-x-executable"
                    }
                }
            }
            onSceneGraphError: () => {}
        }
    }
}
