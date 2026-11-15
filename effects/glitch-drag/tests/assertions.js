a.move=true;a.windowStartUserMovedResized.emit(a);
assert(live.size===1,'shader attaches immediately before any geometry change');
for(var i=0;i<1000;i++){a.x+=i%2?3:-2;a.y++;a.windowStepUserMovedResized.emit(a,{invalidGeometry:true});}
assert(attachments===1&&cancellations===0,'1000 movement events never restart the animation');
assert(uniforms.uMotion[0]!==0,'motion follows numeric window coordinates');
a.move=false;a.windowFinishUserMovedResized.emit();assert(live.size===0,'release detaches shader even with no signal arguments');
b.resize=true;b.windowStartUserMovedResized.emit();assert(live.size===0,'resizing excluded');b.resize=false;
b.move=true;b.windowStepUserMovedResized.emit();assert(live.size===1,'missing start signal recovers at first step');
a.move=true;a.windowStartUserMovedResized.emit();assert(live.size===1,'only one moving window owns shader');
effects.screenLockingChanged.emit(true);assert(live.size===0,'screen lock cleans up');
a.windowStepUserMovedResized.emit();assert(live.size===0,'cannot restart while locked');effects.screenLockingChanged.emit(false);
a.windowStartUserMovedResized.emit();effects.hasActiveFullScreenEffect=true;effects.hasActiveFullScreenEffectChanged.emit();assert(live.size===0,'fullscreen effect cleans up');effects.hasActiveFullScreenEffect=false;
dialog.move=true;dialog.windowStartUserMovedResized.emit();assert(live.size===1,'dialogs supported');
effect.configChanged.emit();assert(live.size===0,'configuration detaches active shader');
dialog.windowStepUserMovedResized.emit();effects.windowClosed.emit(dialog);assert(live.size===0,'closing dragged window releases shader before close animation');
a.windowStartUserMovedResized.emit();effects.desktopChanged.emit();assert(live.size===0,'desktop change cleanup');
for(var excluded of ['minimized','fullScreen','lockScreen','popupWindow','outline']) { a[excluded]=true;a.windowStartUserMovedResized.emit();assert(live.size===0,excluded+' excluded');a[excluded]=false; }
// No methods for activation, elevation, translation, scaling or opacity exist in
// this harness. Any accidental interaction with switching/closing would throw.
var checksPassed=true;
