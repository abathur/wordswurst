{
  inputs = {
    nixpkgs = {
      url = "github:nixos/nixpkgs/nixpkgs-unstable";
    };
    flake-utils = {
      url = "github:numtide/flake-utils";
    };
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };
    d-mark-python = {
      url = "github:abathur/d-mark-python/flakify";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.flake-utils.follows = "flake-utils";
      inputs.flake-compat.follows = "flake-compat";
    };
  };

  description = "TODO";

  outputs = { self, nixpkgs, flake-utils, flake-compat, d-mark-python }:
    {
      overlays.default = nixpkgs.lib.composeExtensions d-mark-python.overlays.default (final: prev: {
        wordswurst = final.callPackage ./wordswurst.nix {
          # TODO: this won't work since it isn't in nixpkgs atm
          # version = prev.wordswurst.version + "-" + (self.shortRev or "dirty");
          version = "unstable" + "-" + (self.shortRev or "dirty");
          src = final.lib.cleanSource self;
        };
      });
      # shell = ./shell.nix;
    } // flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [
            d-mark-python.overlays.default
            self.overlays.default
          ];
        };
      in
        {
          packages = {
            inherit (pkgs) wordswurst;
            default = pkgs.wordswurst;
            ci = (pkgs.callPackages ./test.nix {
              inherit (pkgs) wordswurst;
            }).basic;
          };
          checks = pkgs.callPackages ./test.nix {
            inherit (pkgs) wordswurst;
          };
          devShells = {
            default = pkgs.mkShell {
              buildInputs = [ pkgs.wordswurst ];
            };
          };
        }
    );
}
