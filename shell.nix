let
  pkgs = import ./nix/nixpkgs.nix {};
  pythonEnv = pkgs.python39.withPackages (ps: [
    ps.black
    ps.flake8
    ps.isort
    ps.mypy
    ps.pytest
    ps.requests
  ]);
in
pkgs.mkShell {
  name = "breaking-devenv";
  buildInputs = [
    pythonEnv
  ];
}
