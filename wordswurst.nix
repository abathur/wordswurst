{ lib
, runCommand
, python39
, fetchFromGitHub
, version ? "unstable"
, src ? fetchFromGitHub {
    owner = "abathur";
    repo = "wordswurst";
    rev = "66763c5f46cda53d6244383b1322d2699affe167";
    hash = "sha256-d3ieqsYPNghCsid8WcW3z4wqQbtEFOu6kb8j8mxPuc4=";
  }
, d-mark-python
}:

let
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
  pname = "wordswurst";
  inherit src version;

  propagatedBuildInputs = [
    python39.pkgs.tinycss2
    cssselect2
    python39.pkgs.inflect
    d-mark-python
  ];

  /*
  TODO: find a place to document some things that are useful
        alongside wordswurst: groff, sass, grip, ...
  */
}


