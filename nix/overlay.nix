self: super:
rec {
  python39 = super.python39.override {
    packageOverrides = pythonSelf: pythonSuper: {
      pdoc = pythonSelf.callPackage ./pdoc.nix {};
    };
  };

  python39Packages = super.recurseIntoAttrs (python39.pkgs);
}
