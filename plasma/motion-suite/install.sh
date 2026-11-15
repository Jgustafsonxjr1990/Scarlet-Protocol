#!/usr/bin/env bash
set -euo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if ! command -v kpackagetool6 >/dev/null 2>&1; then
  echo 'KDE Plasma 6 kpackagetool6 is required.' >&2
  exit 1
fi
for id in kwin6_effect_scarlet_protocol_pulse kwin6_effect_scarlet_protocol_recall kwin6_effect_scarlet_protocol_overdrive; do
  package="$here/$id"
  if kpackagetool6 --type KWin/Effect --list | grep -Fq "$id"; then
    kpackagetool6 --type KWin/Effect --upgrade "$package"
  else
    kpackagetool6 --type KWin/Effect --install "$package"
  fi
done
echo 'Installed Pulse (open/close), Recall (minimize/restore), and Overdrive (maximize/restore).'
echo 'Enable them under System Settings → Window Management → Desktop Effects.'
