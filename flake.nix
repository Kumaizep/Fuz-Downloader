{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }:
    let out = system:
      let
        pkgs = nixpkgs.legacyPackages."${system}";
        poetry-overrides = pkgs.poetry2nix.overrides.withDefaults (self: super: {
          # Prevent "Could not find a version that satisfies the requirement wheel" for readchar and inquerier
          readchar = super.readchar.overrideAttrs (old: {
            nativeBuildInputs = old.nativeBuildInputs ++ [ self.wheel ];
            propagatedBuildInputs = old.propagatedBuildInputs ++ [ self.wheel ];
          });
        });
        poetry-app = (with pkgs.poetry2nix; mkPoetryApplication {
          projectDir = ./.;
          preferWheels = true;
          propagatedBuildInputs = with pkgs; [ chromedriver ];
          overrides = poetry-overrides;
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
            (pkgs.poetry2nix.mkPoetryEnv {
              projectDir = ./.;
              preferWheels = true;
              overrides = poetry-overrides;
            })
          ];
        };

        defaultPackage = poetry-app;
      }; in
    with utils.lib; eachSystem
      defaultSystems
      out;
}
