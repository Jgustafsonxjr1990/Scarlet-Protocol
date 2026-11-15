// SPDX-License-Identifier: GPL-2.0-or-later
"use strict";

class ScarletPhaseRelay {
    constructor() {
        this.locked=false;this.running=new Map();this.managed=new Set();
        // Fixed-size pool: shaders are not allocated each time focus changes.
        this.shaders=[];
        for(let i=0;i<5;i++) this.shaders.push(effect.addFragmentShader(Effect.MapTexture | Effect.Modulate,"relay.frag"));
        this.configure();this.previous=this.snapshot();
        effect.configChanged.connect(this.configure.bind(this));
        effects.stackingOrderChanged.connect(this.changed.bind(this));
        effects.windowAdded.connect(this.manage.bind(this));
        effects.windowClosed.connect(this.closed.bind(this));
        effects.windowDeleted.connect(this.closed.bind(this));
        effects.screenLockingChanged.connect(locked => {this.locked=locked;this.reset();});
        effects.hasActiveFullScreenEffectChanged.connect(this.reset.bind(this));
        effects.desktopChanged.connect(this.reset.bind(this));
        for(const w of effects.stackingOrder) this.manage(w);
        effect.animationEnded.connect((w,id) => {
            const state=this.running.get(w);
            if(state && state.ids.indexOf(id)>=0) this.stop(w,false);
        });
    }
    configure() {
        this.clear();
        const bounded=(key,def,lo,hi)=>Math.max(lo,Math.min(hi,Number(effect.readConfig(key,def))));
        this.duration=animationTime(bounded("Duration",360,120,900));
        this.limit=bounded("MaxWindows",3,1,4);
        this.corner=bounded("CornerRadius",14,0,32);
        for(const shader of this.shaders) {
            effect.setUniform(shader,"uStrength",bounded("Strength",65,0,100)/100);
            effect.setUniform(shader,"uCellSize",bounded("CellSize",12,4,32));
            effect.setUniform(shader,"uColor",[bounded("Red",255,0,255)/255,bounded("Green",32,0,255)/255,bounded("Blue",86,0,255)/255]);
        }
        this.previous=this.snapshot();
    }
    eligible(w) {
        return w && w.normalWindow && w.managed && w.visible && !w.minimized &&
            !w.fullScreen && !w.lockScreen && !w.popupWindow && !w.outline && !w.keepAbove &&
            w.onCurrentDesktop!==false && w.onCurrentActivity!==false;
    }
    snapshot() {
        const windows=[];
        for(const w of effects.stackingOrder) if(this.eligible(w)) windows.push(w);
        return windows;
    }
    manage(w) {
        if(this.managed.has(w)) return;
        this.managed.add(w);
        w.windowStartUserMovedResized.connect(this.reset.bind(this));
    }
    overlaps(a,b) {
        return a.x<b.x+b.width && a.x+a.width>b.x && a.y<b.y+b.height && a.y+a.height>b.y;
    }
    stop(w,cancelAnimation=true) {
        const state=this.running.get(w);
        if(!state) return;
        this.running.delete(w);
        if(cancelAnimation) cancel(state.ids);
        if(state.elevated) effects.setElevatedWindow(w,false);
    }
    clear() { for(const w of Array.from(this.running.keys())) this.stop(w); }
    reset() { this.clear();this.previous=this.snapshot(); }
    closed(w) {
        this.clear();this.managed.delete(w);
        this.previous=this.snapshot().filter(item=>item!==w);
    }
    shade(w,target,shader,outgoing) {
        const box=w.expandedGeometry || w.geometry;
        const rect=target.geometry;
        effect.setUniform(shader,"uSize",[Math.max(1,box.width),Math.max(1,box.height)]);
        effect.setUniform(shader,"uTarget",[(rect.x-box.x)/box.width,(rect.y-box.y)/box.height,rect.width/box.width,rect.height/box.height]);
        effect.setUniform(shader,"uCorner",target.maximized?0:this.corner);
        effect.setUniform(shader,"uOutgoing",outgoing?1.0:0.0);
        const ids=animate({window:w,duration:this.duration,keepAlive:false,
            type:Effect.ShaderUniform,fragmentShader:shader,uniform:"uProgress",
            from:0.0,to:1.0,curve:QEasingCurve.Linear});
        this.running.set(w,{ids:ids,elevated:outgoing});
        if(outgoing) effects.setElevatedWindow(w,true);
    }
    changed() {
        const old=this.previous,now=this.snapshot();
        this.previous=now;
        if(this.locked || effects.hasActiveFullScreenEffect || !this.duration) {this.clear();return;}
        if(!old.length || !now.length) return;
        const target=now[now.length-1];
        if(target===old[old.length-1] || old.indexOf(target)<0) return;
        this.clear();
        if(target.move || target.resize) return;
        const blockers=old.slice(old.indexOf(target)+1).filter(w=>this.eligible(w) && this.overlaps(w.geometry,target.geometry)).slice(-this.limit);
        if(!blockers.length) return;
        this.shade(target,target,this.shaders[0],false);
        for(let i=0;i<blockers.length;i++) this.shade(blockers[i],target,this.shaders[i+1],true);
    }
}

new ScarletPhaseRelay();
