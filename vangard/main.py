# main.py
import sys
import argparse

# We need to import the main functions from our interface modules
from vangard import cli
from vangard import interactive
from vangard import server
from vangard import gui
from vangard import pro

def main():
    parser = argparse.ArgumentParser(
        description="A generic command-line system with multiple interfaces."
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # CLI mode
    parser_cli = subparsers.add_parser("cli", help="Run in standard command-line mode.")
    # 'REMAINDER' captures all arguments after 'cli' for our script to handle
    parser_cli.add_argument("args", nargs=argparse.REMAINDER, help="Arguments for the command.")

    # Interactive mode
    subparsers.add_parser("interactive", help="Run in interactive prompt mode.")

    # Server mode
    subparsers.add_parser("server", help="Run as a FastAPI web server.")

    # GUI mode
    subparsers.add_parser("gui", help="Run in a simple GUI window.")

    # Pro mode
    subparsers.add_parser("pro", help="Run the professional web interface.")


    args = parser.parse_args()

    print (f"Selected mode: {args.mode}")
    if args.mode == "cli":
        cli.main(args.args)
    elif args.mode == "interactive":
        interactive.main()
    elif args.mode == "server":
        server.main()
    elif args.mode == "gui":  # <--- ADD THE LOGIC TO LAUNCH THE GUI
        gui.main()
    elif args.mode == "pro":
        pro.main()        

if __name__ == "__main__":
    main()