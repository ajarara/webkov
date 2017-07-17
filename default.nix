{ pkgs ? import <nixpkgs> {}, local ? true }:

with pkgs.python3Packages;
let
  termcolor = buildPythonPackage rec {
    # this isn't on github.. :(
    pname = "termcolor";
    version = "1.1.0";
    name = "${pname}-${version}";
    src = ./. + (if local then "/dist/${name}.tar.gz" else "/${name}.tar.gz");
  };
in
buildPythonPackage rec {
  pname = "webkov";
  version = "0.2.0";
  name = "${pname}-${version}";
  src = ./. + (if local then "/dist/${name}.tar.gz" else "/${name}.tar.gz");
  propagatedBuildInputs = [
    (pkgs.python3.withPackages (ps: [ ps.aiohttp ps.lxml termcolor ]))
  ];
}
  
