{ pkgs ? import <nixpkgs> {}, local ? true }:

with pkgs.python3Packages;
buildPythonPackage rec {
  pname = "webkov";
  version = "0.1.6";
  name = "${pname}-${version}";
  src = ./. + (if local then "/dist/${name}.tar.gz" else "/${name}.tar.gz");
  propagatedBuildInputs = [
    (pkgs.python3.withPackages (ps: [ ps.aiohttp ps.lxml ]))
  ];
}
  
