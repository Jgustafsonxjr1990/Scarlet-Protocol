// SPDX-License-Identifier: MIT
"use strict";

class ScarletProtocolRecall {
    constructor() {
        this.duration = animationTime(320);
        this.shader = effect.addFragmentShader(Effect.MapTexture, "recall.frag");
        effects.windowAdded.connect(this.manage.bind(this));
        for (const window of effects.stackingOrder) {
            this.manage(window);
        }
    }

    manage(window) {
        window.minimizedChanged.connect(() => this.onStateChanged(window));
    }

    canAnimate(window) {
        return !effects.hasActiveFullScreenEffect && !window.lockScreen &&
            !window.popupWindow && !window.outline && window.managed &&
            (window.normalWindow || window.dialog);
    }

    destination(window) {
        const frame = window.geometry;
        const icon = window.iconGeometry;
        if (icon && icon.width > 0 && icon.height > 0) {
            return {
                width: icon.width,
                height: icon.height,
                dx: icon.x - frame.x - (frame.width - icon.width) / 2,
                dy: icon.y - frame.y - (frame.height - icon.height) / 2
            };
        }
        // Apps without a taskbar icon fold into their own center.
        return {width: 52, height: 34, dx: 0, dy: 0};
    }

    onStateChanged(window) {
        if (!this.canAnimate(window)) {
            return;
        }
        const minimizing = window.minimized;
        const role = minimizing ? Effect.WindowMinimizedGrabRole :
            Effect.WindowUnminimizedGrabRole;
        if (effect.isGrabbed(window, role)) {
            return;
        }

        const opposite = minimizing ? window.scarletRecallOut : window.scarletRecallIn;
        if (opposite) {
            if (redirect(opposite, Effect.Backward)) {
                return;
            }
            cancel(opposite);
        }
        if (minimizing) {
            delete window.scarletRecallOut;
        } else {
            delete window.scarletRecallIn;
        }
        const same = minimizing ? window.scarletRecallIn : window.scarletRecallOut;
        if (same) {
            if (redirect(same, Effect.Forward)) {
                return;
            }
            cancel(same);
        }
        if (minimizing) {
            delete window.scarletRecallIn;
        } else {
            delete window.scarletRecallOut;
        }

        const frame = window.geometry;
        const dest = this.destination(window);
        const fromSize = {value1: frame.width, value2: frame.height};
        const toSize = {value1: dest.width, value2: dest.height};
        const origin = {value1: 0, value2: 0};
        const target = {value1: dest.dx, value2: dest.dy};
        const handle = animate({
            window: window,
            duration: this.duration,
            keepAlive: false,
            curve: minimizing ? QEasingCurve.InCubic : QEasingCurve.OutCubic,
            animations: [
                {
                    type: Effect.Size,
                    from: minimizing ? fromSize : toSize,
                    to: minimizing ? toSize : fromSize
                },
                {
                    type: Effect.Translation,
                    from: minimizing ? origin : target,
                    to: minimizing ? target : origin
                },
                {
                    type: Effect.ShaderUniform,
                    fragmentShader: this.shader,
                    uniform: "uProgress",
                    from: minimizing ? 0.0 : 1.0,
                    to: minimizing ? 1.0 : 0.0
                }
            ]
        });
        if (minimizing) {
            window.scarletRecallIn = handle;
        } else {
            window.scarletRecallOut = handle;
        }
    }
}

new ScarletProtocolRecall();
