# Scarlet Protocol — Glitch Drag 3.0

A focused replacement for Wobbly Windows. Drag a window by its title bar to produce broken horizontal scanlines, displaced image strips, scarlet echoes, and two scanning red light columns. Release it and the native window returns immediately. The window remains opaque and follows the pointer normally.

## Install on your ThinkPad

1. Extract this ZIP completely.
2. Open the extracted **Scarlet-Protocol-Glitch-Drag** folder.
3. Double-click **Install-Glitch-Drag** (the Linux x86-64 executable). If Dolphin asks, choose Execute.
4. Wait for the result dialog, then drag a window by its title bar.

Terminal alternative, from the extracted folder:

```sh
bash install.sh
```

Run as your normal desktop user, **without sudo**, inside your active Plasma 6 session. Requires Python 3, kpackagetool6, kwriteconfig6, and gdbus or qdbus6. The graphical result dialog uses kdialog; command-line installation also works without it.

The installer replaces the earlier Vector Wake package in place, reloads it and checks KWin's loaded state. Only after the replacement loads does it disable Wobbly Windows. It backs up the previous package and restores it if KWin rejects the replacement. It upgrades an existing preferred kwin-wayland copy when present so an old copy cannot silently shadow the update.

This package changes only dragging. Your visual theme, opening/closing/minimizing animations, pointer effect, and Phase Relay/window switching are not installed or modified here.

## Customize

System Settings → Desktop Effects → **Scarlet Protocol — Glitch Drag** → configure.

Controls: strength, tear width, band height, glitch rate, echo strength, and RGB color. Default color is #FF2056. Strength 0 makes the effect invisible. Dragging produces an effect even at slow speeds and while briefly pausing with the drag held. Resizing, menus, popups, fullscreen windows, and the lock screen are excluded. Disable Glitch Drag in Desktop Effects to turn it off.

## Why this implementation is different

The earlier implementation cancelled and restarted a short fading animation on every geometry event. This version attaches one shader at drag start and drives a continuous scalar clock for the entire operation. Movement only adjusts direction; it does not reset the animation. It reads numeric window coordinates and size directly, captures the window in signal callbacks, and recovers from a missed start signal. Release, closing the window, desktop changes, screen locking and fullscreen effects detach it.

No exact cause of the failure on Jon's live session has been proven here. This is a redesigned drag lifecycle with explicit installation/load verification, not a claim that a preview proves live integration.

## Verification and limits

- Executed the actual JavaScript in Node and Qt 6 QJSEngine, with a simulated KWin host: immediate attachment; 1,000 move events without restart; release with no signal arguments; missed-start recovery; dialog support; resize, lock, fullscreen, close, desktop and configuration cleanup.
- Compiled and rendered both GLSL variants in a headless OpenGL context. Tested sustained visible output through 300 seconds, time-varying frames, alpha preservation and zero-strength identity.
- Tested installer upgrades in legacy and preferred user package locations, restoration after failed loading, and preservation of unrelated Phase Relay files/settings.
- Compiled the supplied native launcher with warnings treated as errors. Source is included in launcher.c.
- Preview.mp4 renders the shipped shader against sample window content. It is **not a recording of KWin**. The preview uses SDR color-conversion stubs. Live compositor playback, HDR and multi-monitor scaling still need on-device confirmation.

Reference API checked against KDE/kwin Plasma/6.7:
https://github.com/KDE/kwin/blob/Plasma/6.7/src/scripting/scriptedeffect.cpp
https://github.com/KDE/kwin/blob/Plasma/6.7/src/effect/effectwindow.h
https://github.com/KDE/kwin/blob/Plasma/6.7/src/effect/animationeffect.cpp

Diagnostic log: ~/.local/state/scarlet-protocol/glitch-drag-install.log (or your XDG_STATE_HOME equivalent). Installation failures display its location. Successful loading confirms script/shader initialization, but visual behavior must still be checked by dragging a window.

GPL-2.0-or-later. This focused package retains the established effect ID kwin6_effect_scarlet_vector_wake so older copies are upgraded, not enabled alongside it.
