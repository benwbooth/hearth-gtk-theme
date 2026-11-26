# Hearth GTK theme

GTK 2, 3 and 4 in the look of [hearth](https://github.com/benwbooth) (a
macOS-26-style desktop shell for the arbor compositor) and its Qt apps' Mac
menus: hearth's dark and light palette, capsule push buttons with the
default one in the accent, rounded text fields with an accent focus ring,
slim scroll bars, and menus and popovers with 14 px corners, 27 px rows,
a 9 px accent selection, grey shortcuts and a translucent glass tint for
the compositor to blur behind.

Two themes are installed in `share/themes`: **Hearth** (light) and
**Hearth-dark**.

| toolkit | how |
| --- | --- |
| GTK 3 | adw-gtk3's stylesheet + hearth's palette (GTK named colours) + hearth's rules |
| GTK 4 | libadwaita's own stylesheet + the same palette and rules, so plain GTK 4 and libadwaita apps match |
| libadwaita | never loads a GTK theme: `gtk-4.0/libadwaita-user.css` goes into `~/.config/gtk-4.0/gtk.css` (both modes by `prefers-color-scheme`, so it follows light/dark live) |
| GTK 2 | Adwaita's GTK 2 theme (gnome-themes-extra's engine) with hearth's `gtk-color-scheme` and flat accent menu rows |

Every accent use goes through `@accent_bg_color`, so a theme that
`@import`s one of these and redefines that colour recolours it all.
hearth's `helpers/hearth-color-scheme` does that for accents other than
the system blue, and does the rest of the wiring (GSettings,
`settings.ini`, `~/.gtkrc-2.0`, the `gtk.css` block) on every light/dark or
accent change.

## Build

```sh
nix build .#hearth-gtk-theme
```

The generator, `hearth_gtk_theme.py`, takes adw-gtk3's themes, libadwaita's
`styles/gtk.css` (from its GResource) and gnome-themes-extra's themes, and
writes `Hearth` and `Hearth-dark`; `package.nix` shows the call. The palette
is at the top of the file (from hearth's `shell/Theme.qml` and
`shared/app-menus/MacMenuStyle.qml`).

## Licence

LGPL-2.1-or-later, as the stylesheets it builds on (adw-gtk3, libadwaita,
gnome-themes-extra).
