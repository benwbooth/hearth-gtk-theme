#!/usr/bin/env bash
# Build the Hearth and Hearth-dark GTK 3 theme extensions for Flatpak apps and
# install them for this user:   flatpak/build.sh [--no-install]
# Needs org.flatpak.Builder and org.freedesktop.Sdk//25.08 (flatpak install
# --user flathub org.flatpak.Builder org.freedesktop.Sdk//25.08).
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
work=${HEARTH_FLATPAK_WORK:-${XDG_CACHE_HOME:-$HOME/.cache}/hearth-gtk-theme-flatpak}
mkdir -p "$work"
# The themes as Nix builds them (the same files the host uses).
out=$(nix build --no-link --print-out-paths "$here/..#hearth-gtk-theme")
rm -rf "$work/src"; mkdir -p "$work/src/themes"
cp -rL "$out/share/themes/Hearth" "$out/share/themes/Hearth-dark" "$work/src/themes/"
chmod -R u+w "$work/src"
for name in Hearth Hearth-dark; do
  cp "$here/org.gtk.Gtk3theme.$name.yml" "$work/src/"
  flatpak run --filesystem="$work" org.flatpak.Builder \
    --force-clean --user --disable-rofiles-fuse \
    --state-dir="$work/state" --repo="$work/repo" \
    "$work/build-$name" "$work/src/org.gtk.Gtk3theme.$name.yml"
done
[[ ${1:-} == --no-install ]] && exit 0
for name in Hearth Hearth-dark; do
  flatpak install --user -y --noninteractive --reinstall "$work/repo" "org.gtk.Gtk3theme.$name//3.22"
done
flatpak list --user --runtime --columns=ref | grep Gtk3theme.Hearth
