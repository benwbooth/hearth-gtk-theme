{
  description = "Hearth: hearth's macOS-26-style look for GTK 2, 3 and 4";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" ];
      forAll = f: nixpkgs.lib.genAttrs systems (s: f nixpkgs.legacyPackages.${s});
    in {
      packages = forAll (pkgs: rec {
        hearth-gtk-theme = pkgs.callPackage ./package.nix { };
        default = hearth-gtk-theme;
      });
      overlays.default = final: prev: {
        hearth-gtk-theme = final.callPackage ./package.nix { };
      };
    };
}
