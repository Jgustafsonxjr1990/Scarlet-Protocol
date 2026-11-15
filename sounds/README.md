# Scarlet Protocol — Cyber Circuit 2

39 newly synthesized desktop cues in three editions: **Cyber Circuit**, **Night Shift** and **Overdrive**. These replace the softer chime design with FM packet tones, saturated bass pulses, data glitches, metallic transients and filtered power sweeps. All audio is original.

## Double-click installation

1. Extract this ZIP.
2. Open **Scarlet-Sound-Studio**, the Linux x86-64 executable at the top of the folder.
3. Choose an edition, select a sound and click **Preview Selected**. Double-clicking a sound also previews it.
4. Click **Install & Apply Sounds**. The app installs the three editions, selects your chosen one and verifies the saved sound settings.

No Python setup or compilation is required. Run as your normal user, without sudo. If the extractor drops executable permissions, open Properties → Permissions → Is executable. After applying, Sound Studio adds itself to the application launcher.

**Restore Previous Sounds** recovers the previous sound selection, including settings that were originally absent, and rolls back audio directories changed by that installation. Changed files and selection settings are backed up per user; the backup path appears in the app. Repeating an already-current installation does not replace the original selection backup.

## Editions

| Edition | Character |
| --- | --- |
| Cyber Circuit | Gritty synth transients, short glitch detail, clear packet motifs and low-end weight |
| Night Shift | Darker filtering, less digital grain and 56% of the corresponding peak amplitude |
| Overdrive | Stronger saturation and sample-held texture; peaks stay close to Cyber Circuit |

Frequent interface cues stay short and quieter than alerts. Short fades, high-pass filtering, oversampled synthesis and controlled peaks keep the transients contained. The WAV masters are 48 kHz, 16-bit stereo; installed themes use Ogg Vorbis. Each edition contains 39 original cues, 17 standard event-name aliases and a theme demo.

## Hear the collection

**preview.html** is a local sound browser: no web server or extension is required. Select an edition, filter by event group, play individual sounds or audition the demo. The three Theme-Demo WAV files are also playable directly.

The demo order is Startup, Circuit click, Notification, Incoming message, New mail, Charger connected, Device connected, Window open, Minimize, Maximize, Completed, Warning, Error, Timer complete and Logout.

The native preview uses the system's pw-play, paplay or aplay utility. If none is available, **Open Sound Browser** provides browser playback. Preview stops the preceding cue when another is selected or the edition changes.

## Desktop events

The pack follows the freedesktop sound naming/layout convention. It selects the KDE Sounds Theme and Enable keys using kwriteconfig6 change notifications, with kreadconfig6 readback. It installs under your user sounds directory and does not change the visual theme or application notification policies.

Playback depends on the named events an application emits and its notification settings. Window, menu and button cues are supplied for applications that request those events; installing a sound theme does not add global click/window hooks. For an app using a fixed sound file, select the matching WAV in its notification settings. Reopen Sound Theme settings or sign in again if an application retains cached audio.

## Source and verification

Editable synthesis code, audio masters, app/build source and runtime license notices are included. Audio generation requires NumPy, SciPy and FFmpeg; rebuilding the GUI uses PySide6-Essentials 6.8.3 and PyInstaller 6.22.3. Installation itself uses the bundled runtime and system KDE tools.

Checks cover audio decoding, duration/peak/DC/mono consistency, alias resolution, distinct cues, fresh/repeated upgrades, setting readback/rollback and graphical actions. Native GUI startup/search/profile routing is tested offscreen. Playback on Jon's actual audio device and live notification routing remain on-device checks.

Optional terminal interface: `python3 install.py --apply --profile protocol`, or `--profile night` / `--profile overdrive`. Use the graphical executable for normal installation.
