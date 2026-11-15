# Component map

| Directory | Purpose |
| --- | --- |
| plasma | Complete 8.1 visual theme, desktop tools, current bundled effect scripts, motion suite, icons and cursors |
| sounds | Cyber Circuit 2 synthesis, Ogg theme editions, WAV masters, Sound Studio source and runtime notices |
| effects/glitch-drag | Focused 3.0 Wobbly Windows replacement and installer |
| effects/phase-relay | Focused 3.0 Slide Back replacement and installer |
| effects/pointer | Native KWin pointer effects, click/trail artwork and CMake build |
| chrome | Companion Chrome theme, new-tab dashboard and optional web treatment |
| LICENSES | Runtime licenses, in addition to component-specific licenses |

Portable applications are included in the complete release ZIP. Build source is beside its corresponding component:

- Desktop Studio: `plasma/desktop/build_studio.py` and `plasma/desktop/icon_studio_gui.py`.
- Sound Studio: `sounds/desktop/build_studio.py` and `sounds/desktop/sound_studio.py`.
- Effect installer launchers: each focused effect's `launcher.c`, built with `cc -Os -o Install-Glitch-Drag launcher.c` or the Phase Relay filename.
- Native pointer plugin: `effects/pointer/CMakeLists.txt` and its README.

Desktop/Sound Studio build notices document Python, Qt/PySide, PyInstaller and third-party source locations. Artwork generation scripts are under `plasma/tools`; sound generation scripts are under `sounds/tools`. Do not overwrite generated assets unless intentionally rebuilding them.

The original project included a combined reactive-effects installer; the bundled scripts now match the focused 3.0 releases. Prefer the independent drag/focus installers in the repository root instructions. This avoids changing both effects when updating one.

## Validation status for this publication

This release assembles approved project components and replaces the two old reactive scripts with their current focused releases. The established visual artwork and sound files are retained. Publication checks cover file integrity, component versions, packaging permissions, Python/shell syntax, secret-pattern scanning, fresh isolated theme installation, and the focused effects' script/shader/installer tests.

No CI status or broad distribution compatibility is implied. Phase Relay and the native pointer plugin still need wider on-device testing. Contribute reproducible issues and version information.
