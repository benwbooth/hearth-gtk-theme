{ lib, stdenvNoCC, python3, glib, adw-gtk3, libadwaita, gnome-themes-extra }:

# Hearth and Hearth-dark in share/themes, generated from hearth's palette over
# adw-gtk3 (GTK 3), libadwaita's own stylesheet (GTK 4) and Adwaita's GTK 2
# theme (gnome-themes-extra, whose adwaita engine GTK 2 needs at runtime).
stdenvNoCC.mkDerivation {
  pname = "hearth-gtk-theme";
  version = "0.1.0";
  src = lib.fileset.toSource {
    root = ./.;
    fileset = lib.fileset.unions [ ./hearth_gtk_theme.py ./README.md ./LICENSE ];
  };
  nativeBuildInputs = [ python3 glib.dev ];
  buildPhase = ''
    runHook preBuild
    gresource extract ${libadwaita}/lib/libadwaita-1.so.0 /org/gnome/Adwaita/styles/gtk.css > libadwaita.css
    python3 hearth_gtk_theme.py \
      --adw-gtk3 ${adw-gtk3}/share/themes \
      --libadwaita-css libadwaita.css \
      --adwaita-gtk2 ${gnome-themes-extra}/share/themes \
      --out themes
    runHook postBuild
  '';
  installPhase = ''
    runHook preInstall
    mkdir -p $out/share
    cp -r themes $out/share/themes
    runHook postInstall
  '';
  # GTK 2's adwaita engine.
  propagatedUserEnvPkgs = [ gnome-themes-extra ];
  meta = {
    description = "hearth's macOS-26-style look for GTK 2, 3 and 4 (and libadwaita via gtk.css)";
    homepage = "https://github.com/benwbooth/hearth-gtk-theme";
    license = lib.licenses.lgpl21Plus;
    platforms = lib.platforms.linux;
  };
}
