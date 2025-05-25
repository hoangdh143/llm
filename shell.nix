let
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-24.11";
  pkgs = import nixpkgs { config = {}; overlays = []; };
in

pkgs.mkShellNoCC {
  packages = with pkgs; [
    #pandoc
    #texliveTeTeX
    cowsay
    lolcat
    python312Full
    python312Packages.pip
    python312Packages.llm
    
  ];
}
