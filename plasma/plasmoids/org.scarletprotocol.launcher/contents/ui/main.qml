// SPDX-License-Identifier: GPL-2.0-or-later
import QtQuick
import QtQuick.Layouts
import QtCore
import QtQml.Models
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.plasmoid
import org.kde.kirigami as Kirigami
import org.kde.plasma.private.kicker as Kicker
import "AppHistory.js" as History

PlasmoidItem {
    id: root
    Plasmoid.icon: "start-here-kde"
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground
    preferredRepresentation: compactRepresentation
    switchWidth: 0
    switchHeight: 0
    readonly property var favorites: apps.favoritesModel
    property var allApps: null
    property var matches: null
    Kicker.RootModel {
        id: apps
        appletInterface: root
        flat: true; sorted: true
        showAllApps: true; showAllAppsCategorized: false
        showTopLevelItems: false; showRecentApps: false; showRecentDocs: false
        onRefreshed: root.allApps=modelForRow(0)
        Component.onCompleted: {
            favoritesModel.initForClient("org.scarletprotocol.launcher."+Plasmoid.id)
            if(!Plasmoid.configuration.favoritesInitialized) {
                favoritesModel.portOldFavorites(Plasmoid.configuration.favoriteApps)
                Plasmoid.configuration.favoritesInitialized=true
            }
            systemFavoritesModel.favorites=["lock-screen"]
            root.allApps=modelForRow(0)
        }
    }
    Kicker.RunnerModel {
        id: runner
        appletInterface: root; favoritesModel: root.favorites
        mergeResults: true
        runners: ["krunner_services","krunner_systemsettings"]
        onCountChanged: root.matches=count>0?modelForRow(0):null
        onQueryFinished: root.matches=count>0?modelForRow(0):null
    }
    property int catalogRevision: 0
    property int favoriteRevision: 0
    function refreshCatalog() { catalogRevision++ }
    function project(ids) {
        const revision=catalogRevision;
        function normalized(id) { return String(id).replace(/^applications:/,"").replace(/\.desktop$/,"") }
        var result=[];
        for(var i=0;i<ids.length;i++) {
            for(var j=0;j<catalog.count;j++) {
                var item=catalog.objectAt(j);
                if(item && item.favoriteId.length && normalized(item.favoriteId)===normalized(ids[i])) { result.push(item);break; }
            }
        }
        return result;
    }
    function persistFavorites() {
        var ids=[];
        for(var i=0;i<favoriteRows.count;i++) {
            var item=favoriteRows.objectAt(i);
            if(item && item.favoriteId.length) ids.push(item.favoriteId);
        }
        favoriteRevision++;
        if(ids.join("\n")!==Plasmoid.configuration.favoriteApps.join("\n")) Plasmoid.configuration.favoriteApps=ids;
    }
    Instantiator {
        id: catalog
        model: root.allApps
        delegate: QtObject {
            required property int index
            required property var model
            readonly property int sourceIndex: index
            readonly property string favoriteId: String(model.favoriteId || "")
            readonly property string display: String(model.display || "")
            readonly property var decoration: model.decoration
            readonly property bool disabled: !!model.disabled
            onFavoriteIdChanged: Qt.callLater(root.refreshCatalog)
        }
        onObjectAdded: Qt.callLater(root.refreshCatalog)
        onObjectRemoved: Qt.callLater(root.refreshCatalog)
    }
    Instantiator {
        id: favoriteRows
        model: root.favorites
        delegate: QtObject {
            required property var model
            readonly property string favoriteId: String(model.favoriteId || "")
            onFavoriteIdChanged: Qt.callLater(root.persistFavorites)
        }
        onObjectAdded: Qt.callLater(root.persistFavorites)
        onObjectRemoved: Qt.callLater(root.persistFavorites)
    }
    onExpandedChanged: {
        if(expanded && fullRepresentationItem) fullRepresentationItem.begin()
        if(!expanded) runner.query=""
    }
    compactRepresentation: ProtocolButton {
        iconName: "view-grid"
        text: ""; textSize: 24; cornerRadius: 13
        accent: Plasmoid.configuration.accentColor
        Accessible.name: qsTr("Scarlet Protocol application launcher")
        chosen: root.expanded
        onClicked: root.expanded=!root.expanded
    }
    fullRepresentation: LauncherView {
        id: view
        Layout.minimumWidth: 520; Layout.preferredWidth: 680; Layout.maximumWidth: 900
        Layout.minimumHeight: 440; Layout.preferredHeight: 550
        applicationModel: root.allApps
        favoritesModel: root.favorites
        searchModel: root.matches
        toolsModel: root.project(Plasmoid.configuration.quickTools)
        recentModel: root.project(Plasmoid.configuration.recentApps)
        favoriteIds: Plasmoid.configuration.favoriteApps
        favoriteLookup: id => { const revision=root.favoriteRevision;return root.favorites && root.favorites.isFavorite(id) }
        accent: Plasmoid.configuration.accentColor
        glowStrength: Plasmoid.configuration.glowStrength/100
        animate: Plasmoid.configuration.animate
        iconFactory: Component { Kirigami.Icon { source: parent.iconSource || "application-x-executable" } }
        onQueryChanged: runner.query=query.trim()
        onLaunchRequested: (index,favoriteId,sourceIndex) => {
            const projected=!searching && (section===2 || section===3);
            if(projected && sourceIndex<0) return;
            const target=projected?root.allApps:activeModel;
            if(target && target.trigger(projected?sourceIndex:index,"",null)) {
                if(Plasmoid.configuration.rememberRecent && favoriteId.length)
                    Plasmoid.configuration.recentApps=History.remember(Plasmoid.configuration.recentApps,favoriteId,12)
                root.expanded=false
            }
        }
        onClearRecentRequested: Plasmoid.configuration.recentApps=[]
        onPinRequested: id => { if(root.favorites.isFavorite(id)) root.favorites.removeFavorite(id); else root.favorites.addFavorite(id) }
        onPlaceRequested: place => {
            const location=StandardPaths.writableLocation(place==="Downloads"?StandardPaths.DownloadLocation:StandardPaths.HomeLocation)
            if(location.length) Qt.openUrlExternally("file://"+location)
            root.expanded=false
        }
        onLockRequested: { apps.systemFavoritesModel.trigger(0,"",null); root.expanded=false }
        onCloseRequested: root.expanded=false
        Component.onCompleted: begin()
    }
}
