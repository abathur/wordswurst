{ lib
, runCommand
, python39
, fetchFromGitHub
}:

let
  dmark = python39.pkgs.buildPythonPackage {
    #src = pkgs.lib.cleanSource ../d-mark-python;
    src = fetchFromGitHub {
      owner = "abathur";
      repo = "d-mark-python";
      rev = "886d32f8fd1635ceac3e13ff04338a7a1717d6de";
      hash = "sha256-b9UqOc+SyxO2gCzAC+4602MiuvssTFwdvXXSOtThuT0=";
    };
    name = "d-mark-python";
    version = "unstable";
  };

in
python39.pkgs.buildPythonPackage {
  name = "wordswurst-test";
  version = "unset";
  src = lib.cleanSource ./.;
  # dontInstall = true;
  propagatedBuildInputs = [
    python39.pkgs.tinycss2
    python39.pkgs.cssselect2
    python39.pkgs.inflect
    dmark
  ];

  /*
  TODO: find a place to document some things that are useful
        alongside wordswurst: groff, sass, grip, ...
  */
}


