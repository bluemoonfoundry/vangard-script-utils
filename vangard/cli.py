# cli.py
import sys
import argparse
from core.framework import load_config, build_parser, run_command, apply_startup_flags

def main(argv=None):
    """The main entry point for the standard command-line application."""

    print("Running in CLI mode... argv:", argv)

    if argv is None:
        argv = sys.argv[1:]

    if argv and argv[0] == 'cli':
        argv = argv[1:]

    argv = apply_startup_flags(argv)

    config = load_config()
    parser = build_parser(config)
    
    try:
        #print (f'Argv: {argv}')
        args = parser.parse_args(argv)
        #print (f"Parsed arguments: {parser} {args}")
        result = run_command(parser, config, args)
        #print ( f"Command result: {result}")
        if result is not None:
            print(result)
    except argparse.ArgumentError as e:
        print(f"Error: {e}", file=sys.stderr)
        parser.print_usage(file=sys.stderr)
        sys.exit(1)
    except SystemExit:
        #print("Exiting without error.")
        # This catches help messages (-h) and allows the interactive shell to continue
        pass

if __name__ == "__main__":
    main()