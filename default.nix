{ pkgs ? import <nixpkgs> {} }:

with pkgs.python35Packages;
buildPythonPackage rec {
  pname = "webkov";
  version = "0.0.1";
  name = "${pname}-${version}";
  src = ./.;
  propagatedBuildInputs = [
    (pkgs.python3.withPackages (ps: [ ps.nltk ps.twisted ]))
  ];
}
  