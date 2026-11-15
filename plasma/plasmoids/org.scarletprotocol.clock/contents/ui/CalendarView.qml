// SPDX-License-Identifier: GPL-2.0-or-later
import QtQuick
import QtQuick.Controls
import "DateMath.js" as Dates

FocusScope {
    id: root
    property date now: new Date()
    property date selectedDate: new Date()
    property int displayYear: now.getFullYear()
    property int displayMonth: now.getMonth()
    property bool twentyFourHour: true
    property bool showSeconds: true
    property bool mondayFirst: false
    property bool showWeekNumbers: true
    property bool animate: true
    property color accent: "#ff315b"
    property real glowStrength: .7
    property var notes: ({})
    property bool loadingNote: false
    property bool noteDirty: false
    property string editKey: ""
    property bool notesIndexOpen: false
    property string notesQuery: ""
    readonly property var indexedNotes: {
        var result=[],query=notesQuery.trim().toLowerCase();
        for(var key in notes) {
            var date=Dates.fromKey(key),content=String(notes[key] || "");
            if(!date || !content.trim().length) continue;
            if(query.length && (key+" "+Qt.formatDate(date,Qt.DefaultLocaleLongDate)+" "+content).toLowerCase().indexOf(query)<0) continue;
            var distance=Dates.daysBetween(root.now,date);
            result.push({key:key,date:date,content:content,label:Qt.formatDate(date,"ddd, d MMM yyyy"),distance:distance});
        }
        result.sort((a,b)=>a.key<b.key?1:a.key>b.key?-1:0);
        return result;
    }
    readonly property var cells: Dates.monthCells(displayYear,displayMonth,mondayFirst)
    readonly property string selectedKey: Dates.key(selectedDate)
    readonly property string todayKey: Dates.key(now)
    signal noteSaved(string dateKey,string content)
    signal closeRequested()
    implicitWidth: 460
    implicitHeight: 660
    function flushNote() {
        if(noteDirty && editKey.length) { noteSaved(editKey,note.text.trim()); noteDirty=false }
    }
    function loadNote() {
        if(!note) return
        flushNote()
        loadingNote=true
        editKey=selectedKey
        note.text=String(notes[editKey] || "")
        loadingNote=false
        noteDirty=false
    }
    function monthStep(delta) {
        notesIndexOpen=false
        var next=Dates.shiftMonth(displayYear,displayMonth,delta)
        displayYear=next.getFullYear(); displayMonth=next.getMonth()
    }
    function today() { notesIndexOpen=false; selectedDate=new Date(now); displayYear=now.getFullYear(); displayMonth=now.getMonth() }
    function openNote(key) {
        var date=Dates.fromKey(key);if(!date) return;
        notesIndexOpen=false;selectedDate=date;displayYear=date.getFullYear();displayMonth=date.getMonth();note.forceActiveFocus();
    }
    onNotesIndexOpenChanged: {
        if(notesIndexOpen) { flushNote();Qt.callLater(()=>notesFilter.forceActiveFocus()); }
        else notesQuery="";
    }
    onSelectedKeyChanged: loadNote()
    Component.onCompleted: loadNote()

    Surface { anchors.fill: parent; accent: root.accent; glowStrength: root.glowStrength }
    Text { x: 26; y: 22; text: "SCARLET  /  LOCAL TIME"; color: root.accent; font.pixelSize: 10; font.letterSpacing: 1.7; font.weight: Font.DemiBold }
    Text { id: time; x: 23; y: 44; text: Qt.formatTime(root.now,root.twentyFourHour?"HH:mm":"h:mm"); color: "#ffe6ef"; font.pixelSize: 57; font.weight: Font.Light; font.family: "monospace" }
    Text { x: time.x+time.width+8; y: 73; text: root.showSeconds?Qt.formatTime(root.now,"ss"):root.twentyFourHour?"":Qt.formatTime(root.now,"AP"); color: root.accent; font.pixelSize: 20; font.family: "monospace" }
    Text { x: time.x+time.width+9; y: 97; visible: !root.twentyFourHour && root.showSeconds; text: Qt.formatTime(root.now,"AP"); color: "#c59aae"; font.pixelSize: 10 }
    Canvas {
        id: dial
        x: parent.width-100; y: 47; width: 70; height: 70
        property real progress: (root.now.getHours()*60+root.now.getMinutes())/1440
        onProgressChanged: requestPaint()
        onPaint: {
            var ctx=getContext("2d");ctx.reset();ctx.translate(35,35)
            ctx.lineWidth=3;ctx.strokeStyle="#462432";ctx.beginPath();ctx.arc(0,0,29,0,Math.PI*2);ctx.stroke()
            ctx.strokeStyle=root.accent;ctx.beginPath();ctx.arc(0,0,29,-Math.PI/2,-Math.PI/2+progress*Math.PI*2);ctx.stroke()
            for(var i=0;i<24;i++) { var a=i*Math.PI/12;ctx.strokeStyle=i%6===0?"#e8bdce":"#69505e";ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(Math.sin(a)*21,-Math.cos(a)*21);ctx.lineTo(Math.sin(a)*24,-Math.cos(a)*24);ctx.stroke() }
        }
        Text { anchors.centerIn: parent; text: "24h"; color: "#b8879b"; font.pixelSize: 11 }
    }
    Text { x: 27; y: 114; text: Qt.formatDate(root.now,"dddd, d MMMM yyyy"); color: "#c59aae"; font.pixelSize: 12 }
    Rectangle { x: 26; y: 143; width: parent.width-52; height: 34; radius: 10; color: "#1c1720"; border.color: "#39212e"
        Text { x: 13; anchors.verticalCenter: parent.verticalCenter; text: qsTr("WEEK %1").arg(Dates.isoWeek(root.now)); color: "#e7b9cc"; font.family: "monospace"; font.pixelSize: 10 }
        Text { anchors.right: parent.right; anchors.rightMargin: 13; anchors.verticalCenter: parent.verticalCenter; text: "UTC "+String(root.now.getUTCHours()).padStart(2,"0")+":"+String(root.now.getUTCMinutes()).padStart(2,"0"); color: root.accent; font.family: "monospace"; font.pixelSize: 11 }
    }
    ProtocolButton { objectName: "chooseMonthButton"; x: 23; y: 190; width: parent.width-216; iconName: "view-calendar"; text: Qt.formatDate(new Date(root.displayYear,root.displayMonth,1),"MMMM yyyy"); textSize: 17; quiet: true; accent: root.accent; animate: root.animate; Accessible.name: qsTr("Choose month and year"); onClicked: { root.notesIndexOpen=false;monthPicker.year=root.displayYear;monthPicker.open(); } }
    Popup {
        id: monthPicker
        objectName: "monthPicker"
        property int year: root.displayYear
        x: 26; y: 231; width: root.width-52; height: 251
        padding: 14; focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        background: Surface { cornerRadius: 18; accent: root.accent; glowStrength: root.glowStrength }
        contentItem: Column {
            spacing: 12
            Row {
                width: parent.width; spacing: 8
                ProtocolButton { objectName: "previousPickerYear"; width: 33; iconName: "go-previous"; Accessible.name: qsTr("Previous year"); accent: root.accent; onClicked: monthPicker.year-- }
                Text { width: parent.width-82; height: 36; text: monthPicker.year; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; color: "#ffe3ee"; font.pixelSize: 18 }
                ProtocolButton { objectName: "nextPickerYear"; width: 33; iconName: "go-next"; Accessible.name: qsTr("Next year"); accent: root.accent; onClicked: monthPicker.year++ }
            }
            Grid {
                columns: 3; spacing: 7; width: parent.width
                Repeater { model: 12; ProtocolButton {
                    required property int index
                    objectName: "monthChoice"+index
                    width: (parent.width-14)/3; height: 34; text: Qt.locale().monthName(index,Locale.ShortFormat)
                    chosen: monthPicker.year===root.displayYear && index===root.displayMonth
                    accent: root.accent; animate: root.animate
                    onClicked: { root.displayYear=monthPicker.year;root.displayMonth=index;monthPicker.close(); }
                } }
            }
        }
    }
    Row { anchors.right: parent.right; anchors.rightMargin: 26; y: 190; spacing: 5
        ProtocolButton { objectName: "previousMonth"; text: ""; iconName: "go-previous"; textSize: 22; width: 31; accent: root.accent; animate: root.animate; Accessible.name: qsTr("Previous month"); onClicked: root.monthStep(-1) }
        ProtocolButton { objectName: "todayButton"; text: qsTr("Today"); iconName: "view-calendar"; width: 81; accent: root.accent; animate: root.animate; onClicked: root.today() }
        ProtocolButton { objectName: "nextMonth"; text: ""; iconName: "go-next"; textSize: 22; width: 31; accent: root.accent; animate: root.animate; Accessible.name: qsTr("Next month"); onClicked: root.monthStep(1) }
    }
    Row {
        x: root.showWeekNumbers?45:26; y: 241
        Repeater { model: 7
            Text { required property int index; width: (root.width-(root.showWeekNumbers?71:52))/7; horizontalAlignment: Text.AlignHCenter; text: Qt.locale().dayName(((index+(root.mondayFirst?1:0)+6)%7)+1,Locale.ShortFormat); color: "#ae788e"; font.pixelSize: 10 }
        }
    }
    Column { x: 24; y: 278; visible: root.showWeekNumbers
        Repeater { model: 6; Text { required property int index; width: 18; height: 38; text: Dates.isoWeek(root.cells[index*7+(root.mondayFirst?0:1)].date); color: "#805566"; font.family: "monospace"; font.pixelSize: 9; verticalAlignment: Text.AlignVCenter } }
    }
    GridView {
        id: dates
        objectName: "calendarGrid"
        x: root.showWeekNumbers?45:26; y: 269
        width: parent.width-x-26; height: 228
        cellWidth: width/7; cellHeight: 38
        model: root.cells; interactive: false; keyNavigationEnabled: true
        currentIndex: { for(var i=0;i<root.cells.length;i++) if(root.cells[i].key===root.selectedKey) return i; return 0 }
        delegate: ProtocolButton {
            required property int index
            required property var modelData
            objectName: "dateCell"+index
            readonly property bool isToday: modelData.key===root.todayKey
            width: dates.cellWidth-5; height: 33
            text: String(modelData.day); textSize: 12; cornerRadius: 11; quiet: true
            accent: root.accent; animate: root.animate; glowStrength: root.glowStrength
            chosen: modelData.key===root.selectedKey
            opacity: modelData.inMonth?1:.32
            Accessible.name: Qt.formatDate(modelData.date,Qt.DefaultLocaleLongDate)
            onClicked: root.selectedDate=modelData.date
            Rectangle { anchors.fill: parent; anchors.margins: 2; radius: 9; color: "transparent"; border.color: root.accent; visible: parent.isToday }
            Rectangle { width: 3; height: 3; radius: 1.5; anchors.horizontalCenter: parent.horizontalCenter; anchors.bottom: parent.bottom; anchors.bottomMargin: 3; color: "#ffd7e6"; visible: !!root.notes[parent.modelData.key] }
        }
        Keys.onReturnPressed: root.selectedDate=root.cells[currentIndex].date
        Keys.onEnterPressed: root.selectedDate=root.cells[currentIndex].date
        Keys.onPressed: event => { if(event.key===Qt.Key_PageUp || event.key===Qt.Key_PageDown) { root.monthStep(event.key===Qt.Key_PageUp?-1:1); event.accepted=true } }
    }
    Rectangle { x: 26; y: 510; width: parent.width-52; height: 1; color: "#432330" }
    Text { x: 27; y: 528; text: Qt.formatDate(root.selectedDate,"ddd, d MMM")+"  /  "+qsTr("Note"); color: "#dcadbf"; font.pixelSize: 12; font.weight: Font.DemiBold }
    ProtocolButton { objectName: "saveNoteButton"; anchors.right: parent.right; anchors.rightMargin: 26; y: 520; height: 29; text: root.noteDirty?qsTr("Save"):qsTr("Saved"); iconName: "document-save"; enabled: root.noteDirty; accent: root.accent; animate: root.animate; onClicked: root.flushNote() }
    ProtocolButton { objectName: "browseNotesButton"; anchors.right: parent.right; anchors.rightMargin: 117; y: 520; width: 36; height: 29; iconName: "view-list-details"; Accessible.name: qsTr("Browse saved date notes"); accent: root.accent; animate: root.animate; onClicked: root.notesIndexOpen=!root.notesIndexOpen }
    ScrollView {
        x: 26; y: 560; width: parent.width-52; height: Math.max(65,parent.height-y-26)
        clip: true
        TextArea {
            id: note
            objectName: "dateNote"
            color: "#f2cfdf"; placeholderTextColor: "#8d6577"; font.pixelSize: 13
            placeholderText: qsTr("A note for this day…"); wrapMode: TextEdit.Wrap
            selectByMouse: true; leftPadding: 12; topPadding: 10
            background: Rectangle { radius: 12; color: "#18141d"; border.color: note.activeFocus?root.accent:"#402331" }
            onTextChanged: if(!root.loadingNote) root.noteDirty=true
        }
    }
    Rectangle {
        objectName: "notesIndex"
        visible: root.notesIndexOpen; z: 20
        x: 23; y: 235; width: parent.width-46; height: parent.height-258
        radius: 18; color: "#15131b"; border.color: "#9b3052"
        Text { x: 16; y: 15; text: qsTr("Saved date notes"); color: "#ffe3ee"; font.pixelSize: 17; font.weight: Font.DemiBold }
        ProtocolButton { objectName: "closeNotesIndex"; anchors.right: parent.right; anchors.rightMargin: 10; y: 10; width: 33; iconName: "go-previous"; Accessible.name: qsTr("Return to calendar"); accent: root.accent; onClicked: root.notesIndexOpen=false }
        TextField {
            id: notesFilter
            objectName: "notesSearch"
            x: 14; y: 58; width: parent.width-28; height: 39
            text: root.notesQuery; onTextChanged: root.notesQuery=text
            color: "#f4d1e0"; placeholderTextColor: "#a17b8d"; placeholderText: qsTr("Find a date or note…")
            background: Rectangle { radius: 12; color: "#0f1016"; border.color: notesFilter.activeFocus?root.accent:"#593046" }
        }
        ListView {
            id: noteList
            objectName: "notesList"
            x: 14; y: 110; width: parent.width-28; height: parent.height-y-14
            clip: true; spacing: 8; model: root.indexedNotes
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
            delegate: ProtocolButton {
                required property int index
                required property var modelData
                objectName: "indexedNote"+index
                width: noteList.width-4; height: 76; accent: root.accent; animate: root.animate
                Accessible.name: modelData.label+" "+modelData.content
                contentItem: Column {
                    x: 12; y: 8; width: parent.width-24; spacing: 5
                    Text { text: modelData.label+"  /  "+(modelData.distance===0?qsTr("Today"):modelData.distance>0?qsTr("In %1 days").arg(modelData.distance):qsTr("%1 days ago").arg(-modelData.distance)); width: parent.width; elide: Text.ElideRight; color: "#ff81a3"; font.pixelSize: 11 }
                    Text { text: modelData.content.replace(/\n/g,"  "); textFormat: Text.PlainText; width: parent.width; elide: Text.ElideRight; color: "#f2cddd"; font.pixelSize: 13 }
                }
                onClicked: root.openNote(modelData.key)
            }
            Text { anchors.centerIn: parent; visible: noteList.count===0; text: qsTr("No saved notes match."); color: "#b1869a"; font.pixelSize: 13 }
        }
    }
    Keys.onEscapePressed: { if(notesIndexOpen) notesIndexOpen=false; else { root.flushNote();root.closeRequested(); } }
}
