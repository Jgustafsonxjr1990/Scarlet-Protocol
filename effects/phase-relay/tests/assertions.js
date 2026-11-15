activate(b);assert(live.size===1,'activation must animate');assert(effects.stackingOrder[2]===b,'new window remains in native front position');
for(var i=0;i<200;i++){activate(i%2?b:a);assert(live.size===1,'rapid switching cancels previous pulse');assert(effects.stackingOrder[2]===effects.activeWindow,'never obstruct native raising');}
completeAll();assert(live.size===0,'zero-ID native completion');
activate(null);activate(c);assert(live.size===1,'null focus does not lose app handoff');completeAll();
var n=count;activate(c);assert(count===n,'clicking same active window does not animate');
var fresh=makeWindow();effects.windowAdded.emit(fresh);activate(fresh);assert(live.size===0,'new opens keep their existing animation');now+=1000;activate(a);activate(fresh);assert(live.size===1,'later activation of existing window works');completeAll();
var early=makeWindow();activate(early);assert(live.size===0,'activation before windowAdded is also treated as new open');effects.windowAdded.emit(early);
activate(a);a.minimized=true;a.minimizedChanged.emit(a);assert(live.size===0,'minimize cancels pulse');a.minimized=false;a.minimizedChanged.emit(a);activate(b);activate(a);assert(live.size===0,'restore keeps separate Recall effect');now+=1000;
activate(b);b.windowStartUserMovedResized.emit();assert(live.size===0,'drag cancels focus shader to preserve Glitch Drag');
activate(a);effects.windowClosed.emit(a);assert(live.size===0,'close releases shader to existing close effect');
activate(b);effects.screenLockingChanged.emit(true);assert(live.size===0,'lock clears');activate(c);assert(live.size===0,'no pulse on lock screen');effects.screenLockingChanged.emit(false);
activate(b);effects.hasActiveFullScreenEffect=true;effects.hasActiveFullScreenEffectChanged.emit();assert(live.size===0,'fullscreen clears');activate(c);assert(live.size===0,'no pulse during fullscreen');effects.hasActiveFullScreenEffect=false;effects.hasActiveFullScreenEffectChanged.emit();
activate(b);effect.configChanged.emit();assert(live.size===0,'configure clears');activate(c);effects.desktopChanged.emit();assert(live.size===0,'desktop change clears');
// No setElevatedWindow, focus setters, opacity, translation or scaling APIs are
// supplied. Calling any would fail in both Node and Qt's actual JS engine.
var checksPassed=true;
