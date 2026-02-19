# interactive.py
import shlex
import argparse
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory

from core.framework import load_config, build_parser, run_command

def main():
    """The main entry point for the interactive shell."""
    print("Welcome to the interactive shell. Type 'exit' or 'quit' to leave.")
    config = load_config()
    parser = build_parser(config)

    command_names = [cmd['name'] for cmd in config.get('commands', [])]
    option_names = set()
    for cmd in config.get('commands', []):
        for arg in cmd.get('arguments', []):
            option_names.update(arg['names'])
    
    completer = WordCompleter(command_names + list(option_names), ignore_case=True)
    session = PromptSession(history=FileHistory('.cli_history'))

    while True:
        try:
            user_input = session.prompt(f"{config.get('app', {}).get('prog', 'cli')}> ", completer=completer)
            
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input.strip():
                continue

            input_args = shlex.split(user_input)
            
            try:
                args = parser.parse_args(input_args)
                result = run_command(parser, config, args)
                if result is not None:
                    print(result)
            except (argparse.ArgumentError, SystemExit):
                # Argparse prints its own help/error messages, so we just continue.
                pass

        except KeyboardInterrupt:
            continue
        except EOFError:
            break

    print("Goodbye!")

if __name__ == "__main__":
    main()