// SPDX-License-Identifier: GPL-2.0-or-later
"use strict";
class ScarletPhaseRelay {
    constructor() {
        this.running = new Map();
        this.managed = new Set();
        this.quietUntil = new Map();
        this.previous = effects.activeWindow;
        this.locked = false;
        this.shader = effect.addFragmentShader(Effect.MapTexture, "relay.frag");
        this.configure();
        effect.configChanged.connect(() => this.configure());
        effects.windowAdded.connect(w => this.manage(w, false));
        effects.windowActivated.connect(w => this.activated(w));
        effects.windowClosed.connect(w => this.forget(w));
        effects.windowDeleted.connect(w => this.forget(w));
        effects.screenLockingChanged.connect(locked => { this.locked = locked; this.reset(); });
        effects.hasActiveFullScreenEffectChanged.connect(() => this.reset());
        effects.desktopChanged.connect(() => this.reset());
        // Native KWin emits zero for the second completion argument.
        effect.animationEnded.connect(w => this.running.delete(w));
        for (const w of effects.stackingOrder) this.manage(w, true);
        console.info("Scarlet Phase Relay 3.0: ready");
    }
    configure() {
        this.clear();
        const number = (key, fallback, low, high) => {
            const n = Number(effect.readConfig(key, fallback));
            return Number.isFinite(n) ? Math.max(low, Math.min(high, n)) : fallback;
        };
        this.duration = animationTime(number("Duration", 380, 120, 900));
        effect.setUniform(this.shader, "uStrength", number("Strength", 85, 0, 100) / 100);
        effect.setUniform(this.shader, "uOffset", number("GlitchOffset", 14, 0, 32));
        effect.setUniform(this.shader, "uBandHeight", number("BandHeight", 14, 4, 40));
        effect.setUniform(this.shader, "uScanWidth", number("ScanWidth", 32, 8, 80));
        effect.setUniform(this.shader, "uColor", [
            number("Red", 255, 0, 255) / 255, number("Green", 32, 0, 255) / 255,
            number("Blue", 86, 0, 255) / 255
        ]);
    }
    eligible(w) {
        return w && w.managed && (w.normalWindow || w.dialog) && w.visible &&
            !w.minimized && !w.fullScreen && !w.lockScreen && !w.popupWindow &&
            !w.outline && w.onCurrentDesktop !== false && w.onCurrentActivity !== false;
    }
    manage(w, existing) {
        if (!w || this.managed.has(w)) return;
        this.managed.add(w);
        this.quietUntil.set(w, existing ? 0 : Date.now() + animationTime(700));
        w.windowStartUserMovedResized.connect(() => this.reset());
        // Let the separate minimize/restore animation own restored windows.
        if (w.minimizedChanged) w.minimizedChanged.connect(() => {
            this.stop(w);
            this.quietUntil.set(w, Date.now() + animationTime(700));
        });
    }
    stop(w) {
        const ids = this.running.get(w);
        this.running.delete(w);
        if (ids) cancel(ids);
    }
    clear() { for (const w of Array.from(this.running.keys())) this.stop(w); }
    reset() { this.clear(); this.previous = effects.activeWindow; }
    forget(w) {
        this.stop(w); this.managed.delete(w); this.quietUntil.delete(w);
        if (this.previous === w) this.previous = null;
    }
    activated(w) {
        const previous = this.previous;
        this.clear();
        // Preserve the last app across brief null/menu activation.
        if (!this.eligible(w)) return;
        this.previous = w;
        if (!this.managed.has(w)) { this.manage(w, false); return; }
        if (this.locked || effects.hasActiveFullScreenEffect || this.duration <= 0 ||
            !this.eligible(previous) || previous === w || w.move || w.resize ||
            Date.now() < (this.quietUntil.get(w) || 0)) return;
        effect.setUniform(this.shader, "uSize", [
            Math.max(1, Number(w.width) || 1), Math.max(1, Number(w.height) || 1)
        ]);
        // Animate the new active window. KWin owns the real raise/stack order.
        // No visual elevation, translation, scaling, opacity or focus writes.
        const ids = animate({
            window: w, duration: this.duration, keepAlive: false,
            animations: [{type: Effect.ShaderUniform, fragmentShader: this.shader,
                uniform: "uProgress", from: 0.0, to: 1.0, curve: QEasingCurve.Linear}]
        });
        this.running.set(w, ids);
    }
}
new ScarletPhaseRelay();
