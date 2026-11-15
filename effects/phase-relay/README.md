# Scarlet Protocol — Phase Relay 3.0

Replace Slide Back with a brief scarlet scan-and-glitch handoff. Select an inactive existing window: KWin raises it normally, then a bright scarlet beam, trailing scan echo, torn scanlines and perimeter pulse pass across the new active window. It settles into its normal appearance in 380 ms. Neither window slides, flips, shrinks or disappears.

## Install

1. Extract this ZIP completely.
2. Open the extracted **Scarlet-Protocol-Phase-Relay** folder.
3. Double-click **Install-Phase-Relay**, the native Linux x86-64 executable. If Dolphin asks, choose Execute.
4. After the success dialog, click between two overlapping existing windows.

Terminal alternative, from the extracted folder:

```sh
bash install.sh
```

Run inside your active Plasma 6 desktop as your normal user, without sudo. Requires Python 3, kpackagetool6, kwriteconfig6 and gdbus or qdbus6. The graphical result dialog uses kdialog; the terminal installer works without it.

The installer backs up and upgrades the old Phase Relay package, reloads it, and checks KWin's loaded state. It disables Slide Back only after Phase Relay loads. If KWin rejects the package, it restores the previous package. It upgrades an existing preferred kwin-wayland/effects copy when present, avoiding an old user copy shadowing the update.

Your approved Glitch Drag, theme, pointer effects, sound theme, and open/close/minimize/maximize effects are not installed or changed by this package.

## Settings

System Settings → Desktop Effects → **Scarlet Protocol — Phase Relay** → configure.

Adjust duration, strength, tear width, band height, beam width and RGB color. Default color: #FF2056. Set strength to 0 for an invisible effect. To disable it, uncheck Phase Relay in Desktop Effects.

New windows and newly restored windows are briefly excluded so their existing animations can play. Drag/resize cancels the focus shader so Glitch Drag can take over. Clicking the already active window does not retrigger it. Lock screen, desktop changes and fullscreen effects clear the pulse.

Phase Relay follows your existing focus/raise policy; it does not change it. In a normal click-to-focus setup, clicking another window produces the handoff. Windows intentionally kept above other windows retain KWin's existing rules.

## Reliability

The script animates only the incoming active window. It never sets temporary elevation or writes focus, opacity, position, size or stacking order. Both shader endpoints reproduce the original image, and source alpha is preserved throughout. Rapid activation cancels the previous pulse before starting another.

KWin 6.7 API references:
https://github.com/KDE/kwin/blob/Plasma/6.7/src/scripting/scriptedeffect.cpp
https://github.com/KDE/kwin/blob/Plasma/6.7/src/effect/effectwindow.h
https://github.com/KDE/kwin/blob/Plasma/6.7/src/plugins/slideback/metadata.json

## Validation

- Actual shipped JavaScript executed in Node and Qt 6 QJSEngine with a simulated KWin host: 200 rapid activations, native-front preservation, zero-ID completion, null focus, same-window suppression, new-window event ordering, restore, drag, close, lock, fullscreen, configuration and desktop cleanup.
- Both GLSL variants compiled/linked and rendered in headless OpenGL. Alpha preserved; both endpoints reproduce the original; intermediate frames vary visibly; zero strength is identity.
- Installer tested in isolated legacy and preferred package trees, including failed-load rollback and preservation of the Glitch Drag package.
- Native executable compiled with warnings treated as errors. Launcher source included in launcher.c. Qt configuration form and XML checked.

The preview renders the shipped shader on sample window textures at the default 380 ms duration. It is **not a live KWin recording**. SDR conversion is stubbed for this preview. Actual compositor playback, HDR and multi-monitor scaling await on-device testing.

Diagnostic log: ~/.local/state/scarlet-protocol/phase-relay-install.log, or the equivalent path under XDG_STATE_HOME. Successful loading confirms initialization; click between two overlapping windows to check the animation itself.

GPL-2.0-or-later. Established effect ID: kwin6_effect_scarlet_phase_relay.
