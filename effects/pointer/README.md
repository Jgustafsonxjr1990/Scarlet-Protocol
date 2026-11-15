# Scarlet Protocol Pointer

A native KWin effect for the Plasma 6 desktop. The default left click echoes the split ring on the Scarlet Protocol window frame. Click animations and trails are independent. The effect observes pointer changes and draws in the compositor overlay. It takes no input grabs, writes no input history to disk, and stops the animation timer when the last mark fades.

## Install

Extract the archive and open a terminal inside the extracted Scarlet-Protocol-Pointer-Effects folder. The effect builds against the KWin development files matching your installed compositor. The package includes source for the effect and its settings panel.

On Fedora KDE Plasma, install the build requirements if needed.

```bash
sudo dnf install cmake make gcc-c++ extra-cmake-modules kwin-devel kf6-kcmutils-devel kf6-kconfig-devel kf6-kcoreaddons-devel qt6-qtbase-devel qt6-qtdeclarative-devel libdrm-devel libepoxy-devel vulkan-headers wayland-devel
```

On Debian-based Plasma 6 systems with KWin 6.3 or newer, use the corresponding development packages.

```bash
sudo apt install cmake make g++ extra-cmake-modules kwin-dev libkf6kcmutils-dev libkf6config-dev libkf6coreaddons-dev qt6-base-dev qt6-declarative-dev libdrm-dev libepoxy-dev libvulkan-dev libwayland-dev
```

Build and install from the extracted folder.

```bash
bash install.sh
```

The installer builds as your user, then requests sudo to copy the effect and settings plugins into the system Qt plugin directory. Open **System Settings**, search for **Desktop Effects**, enable **Scarlet Protocol Pointer**, and click **Apply**. Use the effect’s settings button to change its behavior. If System Settings was open during installation, reopen it. After a KWin version upgrade, rebuild by running the same installer against the updated development package.

Version 1.0.1 fixes the installer’s Qt selection. Qt6 is selected and loaded before the KDE installation modules, and builds use `build-plasma6` so a failed older configuration cannot carry over. If an earlier installer stopped with “No Qt5 qmake executable found,” extract this updated archive and run `bash install.sh` from its folder.

Version 1.0.2 corrects the settings plugin factory constructor from `QWidget *` to `QObject *`. This fixes the reported KPluginFactory conversion error on KWin 6.7.4. Child controls continue to use `widget()`. The installer builds as the normal user in a user-specific directory and requests sudo only to install the resulting plugins.

## Clicks

| Design | Motion | Default |
| --- | --- | --- |
| Split Ring | Two interrupted arcs open outward and rotate around the click point. Two short contacts keep the split visible. | Left |
| Reticle | Four corner brackets draw inward and settle around a fine center ring. | Right |
| Arc Sparks | Four beveled sparks flare outward and twist as the filaments fade. | Middle |
| Nanook’s Paw | A four-toed print lands, briefly overshoots, and settles between two short arcs. | Choose any supported button |
| Off | Disables the selected button’s animation. | Optional |

The **Buttons** tab assigns a design and color to each button. **Click animation** changes size, duration, opacity, glow, stroke weight, and whether an effect fires on press, release, or both. Color selection includes a hex value. The preview pad uses your current edits. Click **Apply** to send them to KWin, or **Defaults** to recover the shipped settings.

## Trails

**Ribbon** draws a continuous scarlet filament. **Twin Trace** draws two parallel lines with different brightness. **Embers** leaves a stream of separate glowing diamonds. **Off** disables trails. Choose always-on or drag-only behavior, then adjust the trail’s color, width, fade time, spacing, opacity and glow. Spacing affects the smoothness of curved ribbons and the distance between embers. Distances use logical desktop pixels. Large jumps reset the trail so marks do not bridge a pointer warp.

## Build and verification notes

The C++ animation engine was compiled and exercised for every design. Checks cover normalized geometry, fade endpoints, paw construction, distance-based trail sampling and large jumps. The preview movie was generated from the compiled shapes and keyframes. The KWin integration was checked against upstream Plasma source interfaces. Jon's KWin 6.7.4 log confirms the effect plugin built; the settings plugin then failed at the factory constructor. Release 1.0.2 corrects that constructor against the KCModule interface. A full rebuild after this correction and compositor playback remain unverified here.

The effect and configuration module use GPL-2.0-or-later. The license text is included.
