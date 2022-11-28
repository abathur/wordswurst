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

  /* TODO: temporarily extracting old version from nixpkgs; ww needs
  to adapt to something about the 5.x or 6.x series but time's short */
  cssselect2 = with python39.pkgs; buildPythonPackage rec {
    pname = "cssselect2";
    version = "0.4.1";
    disabled = pythonOlder "3.5";

    src = fetchPypi {
      inherit pname version;
      sha256 = "93fbb9af860e95dd40bf18c3b2b6ed99189a07c0f29ba76f9c5be71344664ec8";
    };

    postPatch = ''
      sed -i '/^addopts/d' pyproject.toml
    '';

    propagatedBuildInputs = [ tinycss2 ];

    checkInputs = [ pytestCheckHook ];

    pythonImportsCheck = [ "cssselect2" ];
  };

in
python39.pkgs.buildPythonPackage {
  name = "wordswurst-test";
  version = "unset";
  src = lib.cleanSource ./.;
  # dontInstall = true;
  propagatedBuildInputs = [
    python39.pkgs.tinycss2
    cssselect2
    python39.pkgs.inflect
    dmark
  ];

  /*
  TODO: find a place to document some things that are useful
        alongside wordswurst: groff, sass, grip, ...
  */
}


