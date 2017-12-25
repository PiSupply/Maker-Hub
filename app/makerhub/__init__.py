import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description="Installer for PiSupply products software")
    parser.add_argument("--console", action="store_true")
    args = parser.parse_args()
    if args.console:
        from console import start_app
    else:
        from gui import start_app

    start_app()


if __name__ == '__main__':
    parse_arguments()
