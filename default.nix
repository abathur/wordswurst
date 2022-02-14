{ pkgs ? import <nixpkgs> { } }:

pkgs.callPackage ./wordswurst.nix { }
