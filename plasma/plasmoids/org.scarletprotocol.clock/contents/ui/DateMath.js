.pragma library
function fromKey(value) {
    if(!/^\d{4}-\d{2}-\d{2}$/.test(value)) return null;
    var parts=value.split("-").map(Number),date=new Date(parts[0],parts[1]-1,parts[2],12);
    return date.getFullYear()===parts[0] && date.getMonth()===parts[1]-1 && date.getDate()===parts[2]?date:null;
}
function daysBetween(a,b) {
    return Math.round((Date.UTC(b.getFullYear(),b.getMonth(),b.getDate())-Date.UTC(a.getFullYear(),a.getMonth(),a.getDate()))/86400000);
}
// SPDX-License-Identifier: GPL-2.0-or-later
function key(date) {
    return date.getFullYear()+"-"+String(date.getMonth()+1).padStart(2,"0")+"-"+String(date.getDate()).padStart(2,"0")
}
function monthCells(year,month,monday) {
    var first=new Date(year,month,1,12)
    var offset=(first.getDay()+(monday?6:0))%7
    var cells=[]
    for(var i=0;i<42;i++) {
        var d=new Date(year,month,1-offset+i,12)
        cells.push({date:d,day:d.getDate(),inMonth:d.getMonth()===month,key:key(d)})
    }
    return cells
}
function isoWeek(date) {
    var d=new Date(Date.UTC(date.getFullYear(),date.getMonth(),date.getDate()))
    d.setUTCDate(d.getUTCDate()+4-(d.getUTCDay()||7))
    var first=new Date(Date.UTC(d.getUTCFullYear(),0,1))
    return Math.ceil((((d-first)/86400000)+1)/7)
}
function shiftMonth(year,month,delta) { return new Date(year,month+delta,1,12) }
