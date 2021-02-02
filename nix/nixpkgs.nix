# Pinned version of Nixpkgs + default overlays.
let
  pkgsTarball = fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/c46b679be03303111d3b14d4e65495766c6b01e9.tar.gz";
    sha256 = "sha256:1ia0hn5mh0nbshq3hsza4qnqp0hl16p1gj2xaihcgy0pz28prwhk";
  };

  breakingOverlay = import ./overlay.nix;
in

# Capture the arguments we pass to Nixpkgs when this file is imported.
# Ensure we add our own default nixpkgs overlay so we don't need to
# specify it at all call-sites.
args@{
  overlays ? [],
  ...
}:
  let
    newOverlays = [ breakingOverlay ] ++ overlays;
    newArgs = args // { overlays = newOverlays; };
  in
    import pkgsTarball newArgs
