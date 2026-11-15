#!/usr/bin/env bash
set -euo pipefail
root_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ "$(id -u)" == 0 ]]; then
    echo 'Run this as your normal Plasma user, without sudo.' >&2
    exit 1
fi
case "${1:-help}" in
    theme) exec python3 "$root_dir/plasma/install.py" ;;
    sounds) exec python3 "$root_dir/sounds/install.py" --apply ;;
    drag) exec python3 "$root_dir/effects/glitch-drag/install.py" ;;
    focus) exec python3 "$root_dir/effects/phase-relay/install.py" ;;
    pointer) exec bash "$root_dir/effects/pointer/install.sh" ;;
    help|--help|-h) printf '%s\n' 'Usage: bash install.sh theme|sounds|drag|focus|pointer' 'See README.md for graphical installers and Chrome instructions.' ;;
    *) echo "Unknown component: $1" >&2; exit 2 ;;
esac
