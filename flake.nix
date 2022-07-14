{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }:
    let out = system:
      let
        pkgs = nixpkgs.legacyPackages."${system}";
        poetry-app = (with pkgs.poetry2nix; mkPoetryApplication {
          projectDir = ./.;
          preferWheels = true;
          propagatedBuildInputs = with pkgs; [ chromedriver ];
        });
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            python3Packages.poetry
            python3Packages.autopep8
            pyright
            taplo-cli
            chromedriver
            (pkgs.poetry2nix.mkPoetryEnv { projectDir = ./.; preferWheels = true; })
          ];
        };

        defaultPackage = poetry-app;
      }; in with utils.lib; eachSystem defaultSystems out;
}
