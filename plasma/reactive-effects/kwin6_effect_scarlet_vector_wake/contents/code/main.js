// SPDX-License-Identifier: GPL-2.0-or-later
"use strict";
// One persistent shader attachment owns the whole drag; release removes it.
class ScarletGlitchDrag {
    constructor() {
        this.windows = new Map();
        this.locked = false;
        this.shader = effect.addFragmentShader(Effect.MapTexture, "wake.frag");
        this.configure();
        effect.configChanged.connect(() => this.configure());
        effects.windowAdded.connect(w => this.manage(w));
        effects.windowClosed.connect(w => this.forget(w));
        effects.windowDeleted.connect(w => this.forget(w));
        effects.screenLockingChanged.connect(locked => { this.locked = locked; this.clear(); });
        effects.hasActiveFullScreenEffectChanged.connect(() => {
            if (effects.hasActiveFullScreenEffect) this.clear();
        });
        effects.desktopChanged.connect(() => this.clear());
        for (const w of effects.stackingOrder) this.manage(w);
        console.info("Scarlet Glitch Drag 3.0: ready");
    }
    configure() {
        this.clear();
        const number = (key, fallback, low, high) => {
            const value = Number(effect.readConfig(key, fallback));
            return Number.isFinite(value) ? Math.max(low, Math.min(high, value)) : fallback;
        };
        effect.setUniform(this.shader, "uStrength", number("Strength", 85, 0, 100) / 100);
        effect.setUniform(this.shader, "uOffset", number("GlitchOffset", 24, 4, 48));
        effect.setUniform(this.shader, "uBandHeight", number("BandHeight", 14, 4, 40));
        effect.setUniform(this.shader, "uRate", number("GlitchRate", 12, 2, 24));
        effect.setUniform(this.shader, "uEcho", number("EchoAmount", 65, 0, 100) / 100);
        effect.setUniform(this.shader, "uColor", [
            number("Red", 255, 0, 255) / 255, number("Green", 32, 0, 255) / 255,
            number("Blue", 86, 0, 255) / 255
        ]);
    }
    eligible(w) {
        return w && w.managed && (w.normalWindow || w.dialog) && w.visible &&
            !w.minimized && !w.fullScreen && !w.lockScreen && !w.popupWindow &&
            !w.outline && w.onCurrentDesktop !== false && w.onCurrentActivity !== false &&
            !this.locked && !effects.hasActiveFullScreenEffect;
    }
    manage(w) {
        if (!w || this.windows.has(w)) return;
        this.windows.set(w, { animation: null, x: w.x, y: w.y });
        w.windowStartUserMovedResized.connect(() => this.start(w));
        // Capture the window instead of relying on signal argument conversion.
        w.windowStepUserMovedResized.connect(() => this.step(w));
        w.windowFinishUserMovedResized.connect(() => this.stop(w));
        if (w.move) this.start(w);
    }
    start(w) {
        this.clear();
        if (!this.eligible(w) || !w.move || w.resize) return;
        const state = this.windows.get(w);
        if (!state) return;
        state.x = w.x; state.y = w.y;
        effect.setUniform(this.shader, "uSize", [Math.max(1, Number(w.width) || 1), Math.max(1, Number(w.height) || 1)]);
        effect.setUniform(this.shader, "uMotion", [0.0, 0.0]);
        // KWin resolves the named scalar uniform inside animations[].
        // set() holds the shader; the clock runs continuously for 24 hours.
        state.animation = set({
            window: w, duration: 86400000, keepAlive: false,
            animations: [{
                type: Effect.ShaderUniform, fragmentShader: this.shader,
                uniform: "uClock", from: 0.0, to: 86400.0,
                curve: QEasingCurve.Linear
            }]
        });
    }
    step(w) {
        const state = this.windows.get(w);
        if (!state) return;
        if (!this.eligible(w) || !w.move || w.resize) { this.stop(w); return; }
        if (!state.animation) this.start(w);
        const dx = Number(w.x) - Number(state.x), dy = Number(w.y) - Number(state.y);
        state.x = w.x; state.y = w.y;
        if (!Number.isFinite(dx + dy)) return;
        effect.setUniform(this.shader, "uMotion", [
            Math.max(-1, Math.min(1, dx / 20)), Math.max(-1, Math.min(1, dy / 20))
        ]);
    }
    stop(w) {
        const state = this.windows.get(w);
        if (!state) return;
        const ids = state.animation;
        state.animation = null;
        if (ids) cancel(ids);
    }
    clear() { for (const w of this.windows.keys()) this.stop(w); }
    forget(w) { this.stop(w); this.windows.delete(w); }
}
new ScarletGlitchDrag();
