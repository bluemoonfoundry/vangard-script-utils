# vangard/commands/HelpCommand.py
import argparse
import io
from .BaseCommand import BaseCommand

class HelpCommand(BaseCommand):
    """
    A command to display custom, readable help messages.
    - `help`: Shows a custom list of all commands.
    - `help <command>`: Shows the detailed argparse help for a specific command.
    """

    def _get_argument_signature(self, arguments: list) -> str:
        """Helper to create a concise signature string from argument configs."""
        if not arguments:
            return ""
        
        parts = []
        for arg in arguments:
            # For positional args, use <name>
            if not arg['names'][0].startswith('-'):
                parts.append(f"<{arg['names'][0]}>")
            # For optional args, use the first name listed, e.g., [-s] or [--merge]
            else:
                parts.append(f"[{arg['names'][0]}]")
        
        return " ".join(parts)

    def process(self, args: argparse.Namespace) -> str:
        command_to_help = args.command_name

        # Case 1: `help <command-name>` - Show detailed help for one command
        if command_to_help:
            if self.parser is None:
                return "Error: Help system is not available."
            
            help_output = io.StringIO()
            subparsers_actions = [
                action for action in self.parser._actions 
                if isinstance(action, argparse._SubParsersAction)
            ]
            if subparsers_actions:
                subparser = subparsers_actions[0].choices.get(command_to_help)
                if subparser:
                    subparser.print_help(file=help_output)
                else:
                    print(f"Error: Unknown command '{command_to_help}'", file=help_output)
            return help_output.getvalue()

        # Case 2: `help` - Show the custom-formatted list of all commands
        else:
            if self.config is None:
                return "Error: Configuration not available for help."

            help_lines = []
            app_config = self.config.get('app', {})
            help_lines.append(f"{app_config.get('prog', 'Application')} - {app_config.get('description', '')}")
            help_lines.append("\nAvailable Commands:\n")

            commands = self.config.get('commands', [])
            if not commands:
                return "No commands are configured."

            for cmd in commands:
                name = cmd.get('name', 'N/A')
                help_text = cmd.get('help', '')
                arg_signature = self._get_argument_signature(cmd.get('arguments', []))

                # Use aligned columns for readability
                line = f"  {name:<20} {arg_signature:<35} {help_text}"
                help_lines.append(line)
            
            return "\n".join(help_lines)