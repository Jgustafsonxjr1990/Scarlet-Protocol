// SPDX-License-Identifier: MIT
"use strict";

const SCARLET_EFFECT_ID = "kwin6_effect_scarlet_protocol_pulse";
const EXCLUDED_CLASSES = [
    "ksmserver ksmserver",
    "ksmserver-logout-greeter ksmserver-logout-greeter",
    "ksplashqml ksplashqml",
    "spectacle org.kde.spectacle"
];

class ScarletProtocolPulse {
    constructor() {
        this.shader = effect.addFragmentShader(Effect.MapTexture, "scarlet_pulse.frag");
        effects.windowAdded.connect(this.onAdded.bind(this));
        effects.windowClosed.connect(this.onClosed.bind(this));
        effects.windowDataChanged.connect(this.onWindowDataChanged.bind(this));
    }

    canAnimate(window) {
        if (effects.hasActiveFullScreenEffect || !window.visible ||
            window.lockScreen || window.outline || window.popupWindow ||
            !window.managed || EXCLUDED_CLASSES.indexOf(window.windowClass) !== -1) {
            return false;
        }
        if (window.windowClass === "plasmashell plasmashell" ||
            window.windowClass === "plasmashell org.kde.plasmashell") {
            return window.hasDecoration;
        }
        return window.normalWindow || window.dialog;
    }

    onAdded(window) {
        if (!this.canAnimate(window) ||
            effect.isGrabbed(window, Effect.WindowAddedGrabRole)) {
            return;
        }
        window.scarletPulseOpen = animate({
            window: window,
            duration: animationTime(340),
            curve: QEasingCurve.Linear,
            animations: [
                {
                    type: Effect.ShaderUniform,
                    fragmentShader: this.shader,
                    uniform: "uProgress",
                    from: 0.0,
                    to: 1.0
                },
                {type: Effect.Scale, from: 0.975}
            ]
        });
    }

    onClosed(window) {
        if (!this.canAnimate(window) || window.skipsCloseAnimation ||
            effect.isGrabbed(window, Effect.WindowClosedGrabRole)) {
            return;
        }
        if (window.scarletPulseOpen) {
            cancel(window.scarletPulseOpen);
            delete window.scarletPulseOpen;
        }
        window.scarletPulseClose = animate({
            window: window,
            duration: animationTime(270),
            curve: QEasingCurve.Linear,
            animations: [
                {
                    type: Effect.ShaderUniform,
                    fragmentShader: this.shader,
                    uniform: "uProgress",
                    from: 1.0,
                    to: 0.0
                },
                {type: Effect.Scale, to: 0.975}
            ]
        });
    }

    onWindowDataChanged(window, role) {
        if (role === Effect.WindowAddedGrabRole && window.scarletPulseOpen &&
            effect.isGrabbed(window, role)) {
            cancel(window.scarletPulseOpen);
            delete window.scarletPulseOpen;
        }
        if (role === Effect.WindowClosedGrabRole && window.scarletPulseClose &&
            effect.isGrabbed(window, role)) {
            cancel(window.scarletPulseClose);
            delete window.scarletPulseClose;
        }
    }
}

new ScarletProtocolPulse();
