import QtQuick
import org.kde.plasma.plasmoid

WallpaperItem {
    id: wallpaperRoot
    OrbitDial {
        anchors.fill: parent
        dialOnLeft: wallpaperRoot.configuration.DialOnLeft
        showDate: wallpaperRoot.configuration.ShowDate
        digitalReadout: wallpaperRoot.configuration.DigitalReadout
    }
}
