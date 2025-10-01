# To learn more about how to use Nix to configure your environment
# see: https://firebase.google.com/docs/studio/customize-workspace
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"
  # Use https://search.nixos.org/packages to find packages
  packages = [ 
      pkgs.python3
      pkgs.gtk3 
      pkgs.pango 
      pkgs.harfbuzz
      pkgs.atk
      pkgs.cairo
      pkgs.fontconfig
      pkgs.sqlite
    ]; 

  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      "ms-python.python"
    ] ;
    workspace = {
      # Runs when a workspace is first created with this `dev.nix` file
      onCreate = {
        install =
          "pip install --upgrade pip &&  python -m venv .venv && && source .venv/bin/activate && pip install -r requirements.txt " ;
        # Open editors for the following files by default, if they exist:
      }; # To run something each time the workspace is (re)started, use the `onSt
    };
    # Enable previews and customize configuration
    previews = {
      enable = true;
      previews = {
        web = {
          command = [
            "bash" # Запускаем bash
            "-c"
            # Активируем venv, затем запускаем flet.
            # Убедитесь, что 'flet' скрипт доступен после активации venv
            "source .venv/bin/activate && flet run --web --port 9002 main.py"
          ];
          manager = "web";
        };
      };
    };
  };
}