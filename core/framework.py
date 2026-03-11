# core/framework.py
import argparse
import os
import yaml
import importlib
import sys
from typing import Any, Dict, List

TYPE_MAP = {"str": str, "int": int, "float": float}

def apply_startup_flags(argv=None):
    """
    Parse --enable-script-server from argv and set DAZ_SCRIPT_SERVER_ENABLED if present.
    Returns the remaining args with the flag removed.
    """
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument('--enable-script-server', action='store_true', default=False)
    known, remaining = p.parse_known_args(argv)
    if known.enable_script_server:
        os.environ['DAZ_SCRIPT_SERVER_ENABLED'] = 'true'
    return remaining

def load_config(config_file: str = "config.yaml") -> Dict[str, Any]:
    """Loads and returns the configuration from the YAML file."""
    try:
        with open(config_file, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error: Could not parse YAML file '{config_file}'. {e}", file=sys.stderr)
        sys.exit(1)

def load_class(class_path: str) -> Any:
    """Dynamically loads a class from a string path like 'module.ClassName'."""
    try:
        module_path, class_name = class_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError, ValueError) as e:
        print(f"Error: Could not load class '{class_path}'. {e}", file=sys.stderr)
        sys.exit(1)

def build_parser(config: Dict[str, Any]) -> argparse.ArgumentParser:
    """Builds the argparse parser from the configuration dictionary."""
    app_config = config.get("app", {})
    parser = argparse.ArgumentParser(
        prog=app_config.get("prog", ""),
        description=app_config.get("description")
    )
    parser.exit_on_error = False 

    subparsers = parser.add_subparsers(
        dest="command", 
        required=True, 
        help="Available commands"
    )

    for cmd_config in config.get("commands", []):
        subparser = subparsers.add_parser(cmd_config["name"], help=cmd_config["help"])
        subparser.set_defaults(class_to_run=cmd_config["class"])

        for arg in cmd_config.get("arguments", []):
            arg_names = arg["names"]
            arg_kwargs = {}
            
            is_positional = not arg_names[0].startswith('-')

            valid_keys = ["action", "nargs", "default", "help", "choices"]
            
            if not is_positional:
                valid_keys.append("dest")
                valid_keys.append("required")
            
            if "type" in arg and arg["type"] in TYPE_MAP:
                arg_kwargs["type"] = TYPE_MAP[arg["type"]]
            
            for key in valid_keys:
                if key in arg:
                    arg_kwargs[key] = arg[key]
            
            subparser.add_argument(*arg_names, **arg_kwargs)
            
    print (f"Built parser: {parser}")
    return parser

def run_command(parser: argparse.ArgumentParser, config: Dict[str, Any], args: argparse.Namespace) -> Any:    
    """Loads the class and runs the command specified in parsed args."""
    if hasattr(args, "class_to_run"):
        CommandClass = load_class(args.class_to_run)
        command_instance = CommandClass(parser=parser, config=config)
        return command_instance.process(args)
    else:
        print ("Error: No command class specified in arguments.", file=sys.stderr)
    return None