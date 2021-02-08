let
  pkgs = import ./nix/nixpkgs.nix {};
  pythonEnv = pkgs.python39.withPackages (ps: [
    ps.black
    ps.flake8
    ps.flask
    ps.hypothesis
    ps.isort
    ps.mypy
    ps.pdoc
    ps.pytest
    ps.redis
    ps.requests
  ]);
in
pkgs.mkShell {
  name = "breaking-devenv";
  buildInputs = [
    pkgs.envsubst
    pkgs.redis
    pythonEnv
  ];

  shellHook = ''
    mkdir -p $REPO_ROOT/.env/bin
    ln -sf $(which python) $REPO_ROOT/.env/bin/python
  '';
}
