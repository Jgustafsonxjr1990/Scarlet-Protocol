function assert(condition,message){if(!condition)throw new Error(message);}
function signal(){const callbacks=[];return{connect(fn){callbacks.push(fn);},emit(...args){for(const fn of callbacks)fn(...args);}};}
function makeWindow(){return{x:0,y:0,width:600,height:400,normalWindow:true,managed:true,visible:true,minimized:false,move:false,resize:false,windowStartUserMovedResized:signal(),minimizedChanged:signal()};}
var a=makeWindow(),b=makeWindow(),c=makeWindow();
var now=10000;Date.now=()=>now;
var effects={activeWindow:a,stackingOrder:[b,c,a],windowActivated:signal(),windowAdded:signal(),windowClosed:signal(),windowDeleted:signal(),screenLockingChanged:signal(),hasActiveFullScreenEffectChanged:signal(),desktopChanged:signal(),hasActiveFullScreenEffect:false};
var live=new Map(),count=0,uniforms={},calls=[];
var Effect={MapTexture:1,ShaderUniform:77},QEasingCurve={Linear:0};
var effect={addFragmentShader(){return 1;},setUniform(id,name,value){uniforms[name]=value;},configChanged:signal(),animationEnded:signal(),readConfig(key,fallback){return fallback;}};
function animationTime(ms){return ms;}
function animate(spec){
 assert(spec.keepAlive===false,'no closed-window retention');assert(spec.window===effects.activeWindow,'animate NEW active window');
 assert(spec.animations.length===1&&spec.animations[0].uniform==='uProgress','KWin named-uniform contract');
 assert(spec.animations[0].from===0&&spec.animations[0].to===1,'complete reveal pulse');
 assert(spec.animations[0].type===Effect.ShaderUniform,'no translation/scale/opacity tracks');
 var id=++count;live.set(id,spec);calls.push(spec);return[id];
}
function cancel(ids){for(const id of ids)live.delete(id);}
function activate(w){effects.activeWindow=w;if(w)effects.stackingOrder=effects.stackingOrder.filter(x=>x!==w).concat([w]);effects.windowActivated.emit(w);}
function completeAll(){for(const [id,spec]of Array.from(live)){live.delete(id);effect.animationEnded.emit(spec.window,0);}}
