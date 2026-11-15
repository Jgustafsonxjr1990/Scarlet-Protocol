// Runs inside both Node and Qt 6's actual QJSEngine (see run_checks.py).
function assert(value,message) { if (!value) throw new Error(message); }
function signal() { const slots=[]; return {connect(fn){ slots.push(fn); },emit(...args){ for(const fn of slots) fn(...args); }}; }
function makeWindow() {
 return {x:100,y:80,width:600,height:400,normalWindow:true,managed:true,visible:true,move:false,resize:false,
 windowStartUserMovedResized:signal(),windowStepUserMovedResized:signal(),windowFinishUserMovedResized:signal()};
}
var a=makeWindow(),b=makeWindow(),dialog=makeWindow();dialog.normalWindow=false;dialog.dialog=true;
var live=new Map(),attachments=0,cancellations=0,uniforms={},writes=[];
var effect={configChanged:signal(),addFragmentShader(){return 1;},readConfig(k,d){return d;},setUniform(id,name,value){uniforms[name]=value;}};
var effects={stackingOrder:[a,b,dialog],windowAdded:signal(),windowClosed:signal(),windowDeleted:signal(),screenLockingChanged:signal(),hasActiveFullScreenEffectChanged:signal(),desktopChanged:signal(),hasActiveFullScreenEffect:false};
var Effect={MapTexture:1,ShaderUniform:77},QEasingCurve={Linear:0};
function set(spec) {
 assert(spec.animations.length===1,'one shader track');assert(spec.duration===86400000,'continuous clock');
 var track=spec.animations[0];assert(track.uniform==='uClock'&&track.type===Effect.ShaderUniform,'named scalar clock');
 assert(!spec.keepAlive,'never retain closed windows');var id=++attachments;live.set(id,spec);return[id];
}
function cancel(ids){for(const id of ids){live.delete(id);cancellations++;}}
