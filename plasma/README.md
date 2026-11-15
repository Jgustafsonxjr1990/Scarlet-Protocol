# Scarlet Protocol 8.1 — Classic Slits

Restores the fine straight-cut, segmented border pattern Jon selected in the Status and Notifications / Panel Settings photos. Rounded outlines, the scarlet halo, border/titlebar sizes, current window controls and their red/yellow/green hover colors are retained. The newer large diagonal vent pockets are replaced with narrow perpendicular cuts at a fixed 32-pixel pitch. Launcher/calendar surface borders use the same straight-cut pattern.

## Apply the update

Extract the ZIP and double-click **Scarlet-Desktop-Studio**, the Linux x86-64 executable at the top of the folder. Leave **Apply the restored Classic Slits window frame** checked and click **Upgrade & Apply Desktop**.

The update also corrects `Plasmoid.backgroundHints: 0` in both launcher and clock wrappers to the documented `PlasmaCore.Types.NoBackground`, with the matching import. This addresses the line shown in Jon's launcher screenshot (`main.qml:14:31: Invalid property assignment: unknown enumeration`). The previously reported Qt view tests did not instantiate these native Plasma wrappers; they did not establish native wrapper compatibility.

The graphical installer refreshes KDE's application registry when installing its menu shortcut. **Reload Plasma panels after applying** is enabled by default. If the existing `plasma-plasmashell.service` user service is active, it restarts that service to load fresh widget QML and menu state, leaving application windows open. It does not restart KWin. If the service is unavailable, the app asks you to sign out and back in once. Uncheck this option to defer panel reload.

A second photo shows **Unknown application folder**. Cache refresh and a fresh Plasma panel process address stale menu state; the exact invalid launcher target cannot be established from that notification alone. No pinned shortcuts or application commands are deleted or rewritten by this update.

**Check Active Theme** reports saved style/decoration selections and separately attempts live KWin confirmation. **Restore…** restores the previous appearance selection. Changed component files are backed up. The same native Plasma style, wallpaper, icons, cursor and existing effects remain selected; the new Aurorae identity ends in `81` so the replacement frame is loaded freshly.

## Verification

Checks cover fixed slit spacing at multiple sizes/high DPI, native SVG tile bounds, unchanged outline layers/dimensions/window-button artwork, package references, Qt view interactions, wrapper-enum source guards, isolated apply/restore/readback failure behavior, panel-service reload guards, graphical actions and the packaged executable. Existing Plasma SVGs, icon files, cursors and effect artwork are compared with release 8. Live wrapper loading and menu event behavior on Jon's ThinkPad remain on-device checks after panel reload.

The included preview renders the shipped artwork and Qt views. It is a component preview, not a screenshot of an installed desktop.

## New launcher features

- **Tools** shows installed system tools such as Settings, Spectacle, System Monitor, Info Center, Calculator, Konsole, Dolphin and KWrite. Entries are projected from the real installed-app model; missing applications are omitted.
- **Recent** keeps the last 12 distinct successful app launches locally. Reopening an app moves it to the front. **Clear recent** clears the list. The launcher’s Configure page can turn recording off.
- **Ctrl+1–4** switches Favorites, All Applications, Tools and Recent. **Ctrl+L** focuses search. Arrow/Enter navigation and star pinning are retained.
- Favorite state is read from native model rows and the supported `isFavorite` API, avoiding the deprecated favorites-list getter/setter. Existing statistics-backed favorites remain in their native model.

## New calendar features

- Click the month/year heading to choose any month, with year navigation.
- Click the list icon beside the note’s Save button to browse saved date notes.
- Filter notes by content or date. Each result shows its date and days remaining/elapsed; selecting it opens that date and its note.
- Day differences use calendar dates, so daylight-saving transitions do not add or remove a day. Date notes keep their existing local storage format.

## Surface details

Native dialog, notification, tooltip and background frames gain etched corner contacts and small edge marks. Buttons, text inputs, menu/list selections and task states have stronger distinct hover, pressed, active and keyboard-focus treatment. Progress meters use a fixed segment pitch. Existing masks and compositor-shadow parts are retained.

`Scarlet-Protocol-Surface-Details.png` renders shipped SVG states side by side. The main preview/movie exercises shipped QML with sample applications and a fixed date. These are component previews rather than a recording of an installed Plasma desktop. Native Kicker integration and live Plasma activation still require the on-device check; Qt interaction, model routing, tile geometry and upgrade/restore fixtures are tested separately.

## Source and verification

Editable source, artwork and the build script accompany Desktop Studio. `tools/check_views.py` exercises actual Qt views, shortcuts, source-row routing, history clearing, month/year selection and note search/navigation. `tools/validate.py` checks package references and rehearses per-user upgrades. The GUI tests use isolated native-command fixtures for install/restore and verify the built executable’s real startup/read-only audit. Existing effects, cursors and icon artwork are retained from the preceding release.

## Complete icon coverage

This edition expands the previous 64 custom icons to **9,286 named icons** in 12 categories: applications, folders/places, toolbar actions, status, devices, file types, settings, applets, categories, emblems, emotes and animations. Common applications have distinct glyphs inside carbon housings with scarlet contacts. Folder badges distinguish documents, downloads, media, code, Git, archives, private folders and network/cloud locations. `folder-nanook` is available as a custom folder icon.

Apply the icon update from the freshly extracted folder:

```bash
python3 icon_studio.py --apply
```

Run as your normal desktop user, without sudo. This installs and selects a fresh copy of the complete icon theme, updates the three Scarlet applets with icon-bearing buttons, enables supplied icons on KDE push buttons/menu items, and sends KDE's icon-change notification. It preserves the current window-decoration selection, wallpaper, panel positions and effects. No compilation or extra Python packages are required.

The installer checks this machine's visible desktop entries and widget metadata. Missing named app icons get a matching local vector or framed original logo when available; otherwise they receive an app-name monogram. Absolute-path or absent desktop-entry icons receive per-user launcher overrides. Those overrides retain the original command, actions, translations and launch flags. Their original icon reference is retained so a repeat update preserves the artwork. System launcher files remain untouched.

To inspect coverage without applying changes:

```bash
python3 icon_studio.py --report icon-coverage.json
```

Reopen applications to refresh cached icons. Already-loaded Scarlet widget QML refreshes at your next Plasma login. Run the installer again after adding applications. The saved report is also under `~/.local/state/ScarletProtocol/icon-coverage.json` after applying. Undo with `python3 icon_studio.py --restore /path/to/printed/backup`.

The theme provides icons to apps that request themed icons. It cannot insert an icon into an arbitrary third-party button that has no icon, replace embedded application artwork, or rewrite a website's controls. Widgets with embedded/absolute icons are identified in the report. Date cells retain their readable day numbers. Original folder icons use distinct badges; no recursive edits are made to your folders.

The broad-coverage vectors adapt KDE Breeze Icons under LGPL-3.0-or-later; signature housings/glyphs and folder badges are included. Source SVGs, provenance and license texts are in `icons/ScarletProtocolIcons`. Semantic green and yellow paints retain success/warning meaning. The pack includes symbolic variants and Breeze/hicolor fallback for additional native names. `tools/check_icons.py` exercises real Qt icon lookups and renders every vector, alongside installer/rollback fixtures. Live Plasma integration and the app inventory on your machine are checked when you run the installer.

**Blackout** has a rounded carbon frame, fine straight slits on all four edges, curved corner joints and illuminated contacts. The outer scarlet halo follows the whole window. Unfocused windows retain the slot detail with a quieter plum rim. **Night Shift** uses a softer rim and the Noir wallpaper.

## Restore the window slots now

From this freshly extracted folder, run as your normal desktop user:

```bash
python3 customize_windows.py --apply
```

This applies the new **Signature** frame directly, keeps the existing window buttons, and adds **Scarlet Protocol Window Studio** to the application launcher. It updates only the decoration selection; the wallpaper, panel layout, applets and desktop effects keep their current settings. It does not need compilation or sudo. Content-named decoration copies make KWin load fresh artwork instead of reusing a same-name SVG cache.

Open Window Studio from the launcher, or run `python3 customize_windows.py --configure`. Its native KDE dialogs offer Stealth, Signature and Overdrive profiles, Blackout/Night Shift, slot density and outer glow strength. Dialog mode uses `kdialog`. The command line works without it.

| Profile | Slots | Glow | Border / titlebar |
| --- | --- | --- | --- |
| Stealth | Sparse | 32% | 6 / 31 px |
| Signature | Standard | 75% | 8 / 34 px |
| Overdrive | Dense | 100% | 10 / 36 px |

Fine-tune a profile with `--slots off\|sparse\|normal\|dense`, `--glow 0..100`, `--frame-width 6..10` and `--title-height 28..40`. Append `--night-shift` for the softer edition. For example:

```bash
python3 customize_windows.py --preset overdrive --glow 85 --apply
```

To prepare a selectable frame without switching to it, omit `--apply`. Every applied change prints its backup directory. Undo with `python3 customize_windows.py --restore /path/to/printed/backup`; this restores the previous decoration selection without replacing your other KWin settings. The launcher's Studio copy remains usable after you move or delete the extracted ZIP folder.

Slots repeat at a fixed spacing as windows resize. Maximized windows use a flush dark frame, preserving screen-edge behavior. These frames apply to windows decorated by KWin; applications drawing their own titlebars control those independently.

Release 6 introduces a dedicated application launcher and clock/calendar. Beveled window buttons, illuminated Plasma controls, detailed analog clock artwork and additional application icons carry the same design through the desktop. The existing Window Deck, Orbit Dial, System Core, cursors, splash and optional window motions are included.

## Install or upgrade

1. Open the ZIP in Ark and extract it into a fresh directory.
2. Open a terminal inside the new `Scarlet-Protocol-Plasma-Global` folder and run the following.

```bash
python3 upgrade.py --apply --panel-tools
```

This installs the theme, applies Blackout and uses the new launcher and clock at the positions of existing standard Application Launcher/Application Menu and Digital Clock instances. The panel replacement first creates the new applets, then replaces the existing ones. It retains their order and the launcher's favorites and shortcut. Other panel applets keep their positions. Repeating the command does not create duplicate applets. The files are installed per user and require no compilation.

For Night Shift, append `--night-shift`. To install the artwork and apply the preset while choosing applets yourself, leave off `--panel-tools`. Both applets also appear under **Add Widgets** and **Show Alternatives**. The clock provides its own calendar and date notes.

The updater prints its backup directory, normally under `~/.local/state/ScarletProtocol/`. Activation also backs up the relevant desktop settings. Release 6 uses fresh decoration and Plasma style identifiers so changing to it loads the new artwork. Existing release 5 decoration/style directories remain available. You can apply **Scarlet Protocol — Blackout** or **Scarlet Protocol — Night Shift** manually under **System Settings → Colors & Themes → Global Theme**.

## Launcher and calendar

| Feature | Use |
| --- | --- |
| App search | Type in the launcher to search installed applications and System Settings through Plasma. Enter launches the selected result. Down moves into the grid; arrows select applications. Escape clears search, then closes the launcher. |
| Favorites | Choose **All applications** and use an application's star to pin it. Pinning is stored by Plasma. **Favorites** shows the pinned applications. |
| Quick actions | Home and Downloads open their configured folders. Lock uses Plasma's session action. |
| Clock | Click the panel clock for large local time, optional seconds, UTC time, a 24-hour day-progress ring and ISO week number. The standard Analog Clock also has a new face and tick marks. |
| Calendar | Use the arrows to change months and **Today** to return. Keyboard arrows and Enter select dates; Page Up/Down change months. Today, the selected date and days with notes have separate marks. |
| Date notes | Select a date, type a note and click **Save**. Changing the selected date or closing the popup saves edits too. Notes are stored locally in that clock instance's configuration. |
| Appearance | Right-click the launcher or clock and choose **Configure** to set accent color, glow strength and hover animation. Clock options include 12/24-hour time, seconds, Sunday/Monday week start and week numbers. |

The launcher uses Plasma's Kicker backend. Native discovery, runner results and session actions require a running Plasma desktop. The new clock's notes are independent of external calendar services.

## Window Deck

After upgrading, open **System Settings → Window Management → Task Switcher**. In the visualization selector choose **Scarlet Protocol — Window Deck** and Apply. Hold Alt and press Tab to open it. Arrow keys move between window cards, and clicking a card activates that window. The layout adapts to narrow displays and scrolls when many windows are open. Window thumbnails come from KWin.

## What to try

| Feature | Where to use it |
| --- | --- |
| Window controls | Hover a beveled control to illuminate its recessed contacts. Close glows red, Minimize yellow, Maximize green, and Restore uses inward arrows. Pressing contracts the glyph. Pin, keep above/below, shade, help and application menu have matching artwork where supported. |
| Window focus | Switch between two overlapping KDE windows to see the focused rim and pale title transition. A maximized window sits flush with the screen edge. Use **Window Decorations** to select either frame independently. |
| Plasma surfaces | Try the split-ring switches, volume slider and brightness slider in Plasma applets. The Task Manager has distinct active, hover, minimized and attention states. Plasma buttons and text fields have outlined focus states. Rounded popup, tooltip and panel edges use the edition’s accent strength. |
| Orbit Dial | Right-click the desktop → **Configure Desktop and Wallpaper**. In the wallpaper type menu choose **Scarlet Protocol — Orbit Dial**. The hour and minute hands track local time. You can move the dial to either side in landscape, hide the date or show a 24-hour digital clock. Portrait puts the dial above the date. |
| Relay cursors | Both presets select the cursor set. It can also be selected under **Colors & Themes → Cursors**. The arrow, link, text, move, resize and precision tools have distinct silhouettes. The busy and background-working pointers animate at all four native sizes, 24, 32, 48 and 64 px. |
| Carbon terminal colors | In **Konsole → Settings → Edit Current Profile → Appearance**, select **Scarlet Protocol — Carbon**. It uses an ink background and scarlet errors, with distinct greens, yellows and blues for shell output. |
| System Core | **Add Widgets → System Core**. CPU and RAM show a short history of real readings. GPU, temperature and network cards accept the sensor IDs from your machine. The focus timer supports keyboard activation, pause, reset and sessions up to 180 minutes. |

The two static wallpapers and the existing animated session splash are available with both presets. Application content uses the KDE color scheme and its selected widget style. The custom titlebar applies to windows decorated by KWin. Apps with their own titlebars control those themselves.

### System Core sensors

Right-click the widget and open **Configure**. CPU and memory use common Plasma System Monitor sensor IDs. For GPU, temperature or network traffic, use the IDs from **System Monitor → Edit Page → Add Sensor**. The hardware-specific fields start blank. Each percentage graph holds 32 samples taken roughly a second apart while visible. Missing readings create gaps. You can hide individual optional cards or change the widget accent.

### Window motion

The package includes the existing optional **Window Pulse** for open/close, **Recall** for minimize/restore and **Overdrive** for maximize/restore. Run `bash motion-suite/install.sh` from the extracted folder, then enable your choices under **System Settings → Window Management → Desktop Effects**. The supplied GIFs preview each effect.

### Package checks

Run `python3 tools/validate.py` to check artwork references and rehearse installation in a temporary folder. This check requires Pillow. Installing the theme uses the Python 3 standard library. `tools/check_views.py` exercises the shipped views with PySide6/Qt 6, and `node tools/check_panel_tools.js` checks panel replacement behavior with the documented scripting API.

The release preview renders the shipped SVG parts and QML views with sample applications and a fixed date. The older Details MP4 illustrates release 6's launcher/calendar. Release 6.1 corrects the preview's border composition to match KSvg's default repeated edge tiles. `tools/check_windows.py` checks four-edge slot density, immutable profile identities, preserved controls, Studio staging and apply/rollback behavior with a Plasma command fixture. Qt SVG resize checks cover compact, medium, large and high-DPI frames. Native KWin framing, live Studio dialogs and compositor playback still need verification in a real Plasma session.

Source interface references used for the native integrations are [Kicker models](https://github.com/KDE/plasma-workspace/tree/Plasma/6.3/applets/kicker/plugin) and [Plasma scripting](https://github.com/KDE/plasma-workspace/tree/Plasma/6.3/shell/scripting). The package uses GPL-2.0-or-later; see LICENSE.

## Reactive movement and focus — version 2

The optional `reactive-effects` folder supplies **Vector Wake — Glitch Drag**, with visible horizontal image tears and scarlet echoes while dragging, and **Phase Relay**, an opaque pixel-lock scan over the newly active window. Version 2 corrects the named-uniform and completion-signal integration bugs found in version 1. It releases the old stuck visual elevation and never elevates windows during its new focus animation.

```bash
bash reactive-effects/install.sh --enable
```

The updater reloads the installed effects in the running desktop session. Use the two Scarlet effects with Wobbly Windows and Slide Back turned off. See `reactive-effects/README.md` for controls, upgrade behavior and verification limits.
