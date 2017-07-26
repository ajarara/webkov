{ pkgs, ... }:

let
  webkov = pkgs.callPackages ./default.nix  {
    inherit pkgs;
    local = false;
  };
  webkovusr = {
    uid = 18294;
    extraGroups = [ "webkov" ];
  };
  webkovgid = 18294;
  port = 18293;
in
{
  environment.systemPackages = [ webkov ];
  
  users.groups = {
    webkov = { name = "webkov"; gid = webkovgid; };
  };
  
  systemd.services.webkov = {
    description = "Shakespeare on port ${port}";
    wantedBy = [ "multi-user.target" ];
    script = ''
      ${webkov}/bin/shakespeare --port ${port} --uid ${webkovusr.uid} --gid ${webkovgid}
    '';
  };

  # reverse proxy for nginx
  services.nginx.virtualHosts =
  let
    helperfn = char: {
      name = "${char}.jarmac.org";
      value = {
        locations."/" = {
          proxyPass = "http://jarmac.org:${port}/${char}";
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
        proxyPass = "http://jarmac.org:${port}";
      };
    };
  } // (builtins.listToAttrs (map helperfn chars));
  
  # see note in virtual host config
  networking.firewall.allowedTCPPorts = [ port ];
}
  
