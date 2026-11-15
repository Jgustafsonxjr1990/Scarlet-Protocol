#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ "$(id -u)" == 0 ]]; then
    echo "Run bash install.sh as your normal user. Sudo is requested only for the final installation." >&2
    exit 1
fi
build_dir="$root_dir/build-plasma6-$(id -u)"
if ! command -v cmake >/dev/null; then
    echo "Install CMake and the KDE build requirements listed in README.md, then run this command again." >&2
    exit 1
fi
cmake -S "$root_dir" -B "$build_dir" -DQT_MAJOR_VERSION=6 -DBUILD_WITH_QT6=ON -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr -DKDE_INSTALL_USE_QT_SYS_PATHS=ON
cmake --build "$build_dir" --parallel 2
sudo cmake --install "$build_dir"
echo "Open System Settings → Desktop Effects. Enable Scarlet Protocol Pointer and click its settings button."
