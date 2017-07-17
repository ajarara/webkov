{ pkgs, ... }:

let
  webkov = pkgs.callPackages ./default.nix  {
    inherit pkgs;
    local = false;
  };
in
{
  environment.systemPackages = [ webkov ];
  systemd.services.webkov = {
    description = "Shakespeare on port 18293";
    wantedBy = [ "multi-user.target" ];
    script = ''
      ${webkov}/bin/shakespeare
    '';
  };

  # reverse proxy for nginx
  services.nginx.virtualHosts =
  let
    helperfn = char: {
      name = "${char}.jarmac.org";
      value = {
        locations."/" = {
          proxyPass = "http://jarmac.org:18293/${char}";
        };
      };
    };
    
    chars = [
        "mercutio"
        # "second-watchman"
        "nurse"
        "paris"
        "gregory"
        # "peter"
        # "third-musician"
        # "abraham"
        # "second-musician"
        "second-servant"
        "benvolio"
        "second-capulet"
        "first-servant"
        "sampson"
        "balthasar"
        "servant"
        # "first-citizen"
        "lady-capulet"
        "romeo"
        # "first-musician"
        "montague"
        "first-watchman"
        "common"
        "lady-montague"
        "prince"
        "chorus"
        # "third-watchman"
        "capulet"
        "friar-john"
        # "musician"
        "page"
        "friar-laurence"
        "tybalt"
        "nurse"
        "apothecary"
        "lady-capulet"
        "juliet"
    ];
  in
  {
    "shakespeare.jarmac.org" = {
      locations."/" = {
        proxyPass = "http://jarmac.org:18293";
      };
    };
  } // (builtins.listToAttrs (map helperfn chars));
  
  # see note in virtual host config
  networking.firewall.allowedTCPPorts = [ 18293 ];
}
  
