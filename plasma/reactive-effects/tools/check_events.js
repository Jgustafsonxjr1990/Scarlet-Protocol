// Regression harness for the actual KWin 6.7 named-uniform and completion semantics.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.dirname(__dirname);
function signal(){const f=[];return{connect(fn){f.push(fn)},emit(...a){for(const fn of f)fn(...a)}}}
function window(x=0,y=0){return{geometry:{x,y,width:500,height:350},expandedGeometry:{x,y,width:500,height:350},normalWindow:true,managed:true,visible:true,minimized:false,fullScreen:false,onCurrentDesktop:true,onCurrentActivity:true,move:false,resize:false,keepAbove:false,windowStartUserMovedResized:signal(),windowStepUserMovedResized:signal(),windowFinishUserMovedResized:signal()}}
function runtime(source,windows,{strict=true,legacyElevation=[]}={}){
 let next=0;const live=new Map(),elevated=new Set(legacyElevation),uniforms=new Map(),calls=[],elevationCalls=[];
 const effects={stackingOrder:windows.slice(),activeWindow:windows.at(-1),hasActiveFullScreenEffect:false,windowAdded:signal(),windowActivated:signal(),windowClosed:signal(),windowDeleted:signal(),screenLockingChanged:signal(),hasActiveFullScreenEffectChanged:signal(),desktopChanged:signal(),stackingOrderChanged:signal(),setElevatedWindow(w,on){elevationCalls.push(on);if(on)elevated.add(w);else elevated.delete(w)}};
 const effect={configChanged:signal(),animationEnded:signal(),addFragmentShader(){return ++next},setUniform(shader,key,value){uniforms.set(shader+':'+key,value)},readConfig(key,def){return def}};
 const context={effects,effect,Effect:{MapTexture:1,Modulate:4,ShaderUniform:77},QEasingCurve:{Linear:0},animationTime:n=>n,
 animate(spec){
  if(strict){assert(Array.isArray(spec.animations),'KWin resolves named uniforms only in animations[]');assert.strictEqual(spec.type,undefined)}
  const entries=spec.animations||[spec],ids=[];
  for(const animation of entries){assert.strictEqual(animation.type,77);assert.strictEqual(spec.keepAlive,false);const id=++next;live.set(id,{...animation,window:spec.window,namedUniform:!!spec.animations});calls.push(spec);ids.push(id)}return ids;
 },cancel(ids){for(const id of ids||[])live.delete(id)},retarget(ids,target,duration){for(const id of ids||[]){const a=live.get(id);if(a){a.to=target;a.duration=duration}}}};
 vm.runInNewContext(fs.readFileSync(source,'utf8'),context);
 return{effects,effect,live,elevated,uniforms,calls,elevationCalls,
 activate(w){effects.stackingOrder=effects.stackingOrder.filter(x=>x!==w).concat([w]);effects.activeWindow=w;effects.stackingOrderChanged.emit();effects.windowActivated.emit(w)},
 finish(){for(const [id,a]of [...live]){live.delete(id);effect.animationEnded.emit(a.window,0)}}};
}
const wakeFile=path.join(root,'kwin6_effect_scarlet_vector_wake/contents/code/main.js');
const relayFile=path.join(root,'kwin6_effect_scarlet_phase_relay/contents/code/main.js');
// Archived v1 must fail exactly the native conditions our original mock omitted.
if(fs.existsSync(path.join(__dirname,'regression/v1-relay.js'))){
 const a=window(),b=window(100,80),old=runtime(path.join(__dirname,'regression/v1-relay.js'),[a,b],{strict:false});
 old.activate(a);assert(old.elevated.size>0);assert([...old.live.values()].every(x=>!x.namedUniform));
 old.finish();assert(old.elevated.size>0,'v1 should reproduce its stuck elevation after completion ID zero');
 const c=window(),d=window(20,20),strictOld=runtime(path.join(__dirname,'regression/v1-relay.js'),[c,d]);
 assert.throws(()=>strictOld.activate(c),/animations/);
 console.log('REPRODUCED v1: unresolved named uniform and stale elevation with KWin completion ID 0');
}
const a=window(),b=window(200,100),wake=runtime(wakeFile,[a,b]);
a.move=true;a.windowStartUserMovedResized.emit(a);
for(let i=0;i<120;i++){a.geometry={...a.geometry,x:i+1};a.expandedGeometry={...a.geometry};a.windowStepUserMovedResized.emit(a,a.geometry);assert.strictEqual(wake.live.size,1)}
assert(wake.uniforms.get('1:uMotion')[0]>0);
a.move=false;a.windowFinishUserMovedResized.emit(a);wake.finish();assert.strictEqual(wake.live.size,0);
const before=wake.calls.length;wake.effect.configChanged.emit();assert.strictEqual(wake.calls.length,before,'zero completion ID must clear the animation cache');
b.resize=true;b.windowStartUserMovedResized.emit(b);b.windowStepUserMovedResized.emit(b,{...b.geometry,x:220});assert.strictEqual(wake.live.size,0);b.resize=false;
a.move=true;a.windowStartUserMovedResized.emit(a);a.windowStepUserMovedResized.emit(a,{...a.geometry,x:170});wake.effects.screenLockingChanged.emit(true);assert.strictEqual(wake.live.size,0);a.move=false;
const c=window(300,200),relay=runtime(relayFile,[a,b,c],{legacyElevation:[b]});
assert.strictEqual(relay.elevated.size,0,'startup must release v1 elevation');
for(let i=0;i<50;i++){const target=i%2?a:b;relay.activate(target);assert.strictEqual(relay.effects.stackingOrder.at(-1),target);assert.strictEqual(relay.live.size,1);assert.strictEqual(relay.elevated.size,0)}
assert(relay.elevationCalls.every(x=>x===false),'v2 must never elevate a window');
relay.finish();assert.strictEqual(relay.live.size,0);
relay.effects.activeWindow=null;relay.effects.windowActivated.emit(null);
relay.activate(c);assert.strictEqual(relay.live.size,1,'intermediate null focus must preserve handover');relay.finish();
const count=relay.calls.length;relay.effect.configChanged.emit();assert.strictEqual(relay.calls.length,count);
relay.activate(c);relay.effects.hasActiveFullScreenEffect=true;relay.effects.hasActiveFullScreenEffectChanged.emit();assert.strictEqual(relay.live.size,0);
relay.effects.hasActiveFullScreenEffect=false;relay.effects.hasActiveFullScreenEffectChanged.emit();
relay.activate(a);relay.effects.screenLockingChanged.emit(true);assert.strictEqual(relay.live.size,0);relay.effects.screenLockingChanged.emit(false);
const fresh=window(500,100);relay.effects.stackingOrder.push(fresh);relay.effects.windowAdded.emit(fresh);relay.activate(fresh);assert.strictEqual(relay.live.size,0,'new opens should retain their separate animation');
relay.activate(b);relay.effects.windowClosed.emit(b);assert.strictEqual(relay.live.size,0);
console.log('PASS v2: nested named uniforms; zero-ID completion cleanup; 120 drag updates; 50 immediate native focus changes; no elevation during animations; legacy recovery; open/resize/fullscreen/lock/close cleanup');
