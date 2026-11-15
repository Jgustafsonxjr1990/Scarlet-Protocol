.pragma library
function remember(current, id, limit) {
    if(typeof id!=="string" || !id.length) return current;
    var result=[id];
    for(var i=0;i<current.length && result.length<limit;i++)
        if(typeof current[i]==="string" && current[i].length && result.indexOf(current[i])<0) result.push(current[i]);
    return result;
}
