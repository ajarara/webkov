{ pkgs, ... }:

let
  webkov = pkgs.callPackages ./default.nix  {
    inherit pkgs;
    local = false;
  };
  webkovuser = {
    uid = 18293;
    extraGroups = [ "webkov" ];
    };
  webkovgroup = {
    name = "webkov";
    gid = 18294;
  };
  proto = "http://";
  domain = "jarmac.org";
  port = 18293;
in
{
  environment.systemPackages = [ webkov ];
  
  users.extraUsers.webkov = webkovuser;
  users.extraGroups.webkov = webkovgroup;
  
  systemd.services.webkov = {
    description = "Shakespeare on port ${port}";
    wantedBy = [ "multi-user.target" ];
    serviceConfig = {
      User = "webkov";
      Group = "webkov";
    };
    script = ''
      ${webkov}/bin/shakespeare --port ${port}
    '';
  };

  # reverse proxy for nginx
  services.nginx.virtualHosts =
  let
    helperfn = char: {
      name = "${char}.${domain}";
      value = {
        locations."/" = {
          proxyPass = "${proto}${domain}:${port}/${char}";
        };
      };
    };
    
    chars = [
        "mercutio"
        "second-watchman"
        "nurse"
        "paris"
        "gregory"
        "peter"
        "third-musician"
        "abraham"
        "second-musician"
        "second-servant"
        "benvolio"
        "second-capulet"
        "first-servant"
        "sampson"
        "balthasar"
        "servant"
        "first-citizen"
        "lady-capulet"
        "romeo"
        "first-musician"
        "montague"
        "first-watchman"
        "common"
        "lady-montague"
        "prince"
        "chorus"
        "third-watchman"
        "capulet"
        "friar-john"
        "musician"
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
        proxyPass = "${proto}${domain}:${port}";
      };
    };
    # the next line says: map helperfn (defined in the let expr) on
    # the chars list. Merge the configuration with the base
    # shakespeare one defined immediately above.
  } // (builtins.listToAttrs (map helperfn chars));
  
  networking.firewall.allowedTCPPorts = [ port ];
}
  
