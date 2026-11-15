// SPDX-License-Identifier: MIT
"use strict";

class ScarletProtocolOverdrive {
    constructor() {
        this.duration = animationTime(380);
        this.shader = effect.addFragmentShader(Effect.MapTexture, "overdrive.frag");
        effects.windowAdded.connect(this.manage.bind(this));
        for (const window of effects.stackingOrder) {
            this.manage(window);
        }
    }

    manage(window) {
        window.windowMaximizedStateAboutToChange.connect(
            this.beforeGeometryChange.bind(this));
        window.windowMaximizedStateChanged.connect(this.afterGeometryChange.bind(this));
        window.windowFrameGeometryChanged.connect(this.onGeometryChanged.bind(this));
    }

    eligible(window) {
        return window.visible && !effects.hasActiveFullScreenEffect &&
            !window.fullScreen && !window.lockScreen && !window.popupWindow &&
            !window.outline && window.managed && window.normalWindow;
    }

    beforeGeometryChange(window) {
        if (!this.eligible(window)) {
            return;
        }
        window.scarletOldGeometry = Object.assign({}, window.geometry);
        if (window.scarletExpand) {
            cancel(window.scarletExpand);
            delete window.scarletExpand;
        }
        if (window.scarletCrossfade) {
            cancel(window.scarletCrossfade);
            delete window.scarletCrossfade;
        }
        // Capture the previous frame before the application resizes its content.
        window.scarletCrossfade = animate({
            window: window,
            duration: this.duration,
            animations: [{
                type: Effect.CrossFadePrevious,
                from: 0.0,
                to: 1.0,
                curve: QEasingCurve.OutCubic
            }]
        });
    }

    afterGeometryChange(window) {
        const old = window.scarletOldGeometry;
        if (!old || !this.eligible(window)) {
            if (window.scarletCrossfade) {
                cancel(window.scarletCrossfade);
                delete window.scarletCrossfade;
            }
            return;
        }
        const now = window.geometry;
        if (old.width === now.width && old.height === now.height &&
            old.x === now.x && old.y === now.y) {
            if (window.scarletCrossfade) {
                cancel(window.scarletCrossfade);
                delete window.scarletCrossfade;
            }
            return;
        }

        const growing = now.width * now.height >= old.width * old.height;
        window.scarletExpand = animate({
            window: window,
            duration: this.duration,
            animations: [
                {
                    type: Effect.Size,
                    from: {value1: old.width, value2: old.height},
                    to: {value1: now.width, value2: now.height},
                    curve: QEasingCurve.OutCubic
                },
                {
                    type: Effect.Translation,
                    from: {
                        value1: old.x - now.x - (now.width - old.width) / 2,
                        value2: old.y - now.y - (now.height - old.height) / 2
                    },
                    to: {value1: 0.0, value2: 0.0},
                    curve: QEasingCurve.OutCubic
                },
                {
                    type: Effect.ShaderUniform,
                    fragmentShader: this.shader,
                    uniform: "uProgress",
                    from: growing ? 0.0 : 1.0,
                    to: growing ? 1.0 : 0.0,
                    curve: QEasingCurve.Linear
                }
            ]
        });
        if (window.scarletCrossfade) {
            retarget(window.scarletCrossfade, 1.0, this.duration);
        }
    }

    onGeometryChanged(window, previous) {
        if (!window.scarletExpand || !window.scarletOldGeometry) {
            return;
        }
        const now = window.geometry;
        const start = window.scarletOldGeometry;
        if ((now.width === previous.width && now.height === previous.height) ||
            (start.width === previous.width && start.height === previous.height)) {
            return;
        }
        // If the user resizes during the sweep, stop using stale geometry.
        cancel(window.scarletExpand);
        delete window.scarletExpand;
        if (window.scarletCrossfade) {
            cancel(window.scarletCrossfade);
            delete window.scarletCrossfade;
        }
    }
}

new ScarletProtocolOverdrive();
