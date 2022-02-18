{
  pkgs ? import <nixpkgs> { },
  # source ? pkgs.callPackage ./source.nix { }
}:

with pkgs;
let
  wordswurst = callPackage ./default.nix { };
  inherit (callPackage ./test.nix {
    inherit wordswurst;
  })
    basic;

in
basic
# runCommand "resholve-ci" { } ''
#   diff ${resholvedScript} ${resholvedScriptBin}/bin/resholved-script-bin
#   mkdir $out
#   printf "\033[33m============================= resholve Nix demo ===============================\033[0m\n"
#   env -i ${module3}/bin/conjure.sh |& tee nix-demo.ansi
#   ${bat}/bin/bat --paging=never --color=always ${module3}/bin/conjure.sh ${module2}/bin/openssl.sh ${module1}/bin/libressl.sh |& tee -a nix-demo.ansi
#   ${ansifilter}/bin/ansifilter -o $out/test.txt --text ${cli}/test.ansi
#   ${ansifilter}/bin/ansifilter -o $out/demo.txt --text ${cli}/demo.ansi
#   ${ansifilter}/bin/ansifilter -o $out/nix-demo.txt --text nix-demo.ansi
# ''
