# vangard/commands/base.py
import os
import urllib.request
from abc import ABC
import argparse
import json
import subprocess
from typing import Any, Dict, Optional, Set, Union
from dotenv import load_dotenv
load_dotenv()

class BaseCommand(ABC):
    """
    Abstract base class for all Vangard commands.
    Includes utility methods for command implementation.
    """
    def __init__(self, parser: Optional[argparse.ArgumentParser] = None,  config: Optional[Dict[str, Any]] = None):
        """
        The main execution method for the command.
        """
        self.parser = parser
        self.config = config
        
        #args = parser.parse_args() if parser else None 
        # if args is not None:
        #     args_dict = self.to_dict(args)

        #     print("--- Arguments received by command (as dict) ---")
        #     print(json.dumps(args_dict, indent=2))

        #     script_name = f"{self.__class__.__name__}.dsa"
        #     self.exec_remote_script(
        #         script_name=script_name,
        #         script_vars=args_dict,
        #         daz_command_line=None
        #     )

    def process(self, args: argparse.Namespace) -> Any:
        """
        Process the command with the given arguments.
        This method can be overridden by subclasses to implement specific behavior.
        """
        if self.parser is None:
            raise ValueError("Parser is not set for this command.")

        if args is not None:
            args_dict = self.to_dict(args)
            self.script_vars = args_dict  # Store for subclass access
            self.exec_default_script(args_dict)
    
    def exec_default_script(self, args: Dict[str, Any]) -> None:
        """
        Executes the default .dsa script with the same name as the command class.

        Args:
            args: Dictionary of arguments to pass to the script
        """
        script_name = f"{self.__class__.__name__}.dsa"
        self.exec_remote_script(
            script_name=script_name,
            script_vars=args,
            daz_command_line=None
        )

    @staticmethod
    def exec_remote_script(
        script_name: str,
        script_vars: Optional[Dict[str, Any]] = None,
        daz_command_line: Optional[Union[str, list]] = None
    ) -> None:
        """
        Executes a DAZ Script either via subprocess or DAZ Script Server.

        Args:
            script_name: Name of the .dsa script file to execute
            script_vars: Dictionary of variables to pass to the script as JSON
            daz_command_line: Additional command line arguments for DAZ Studio (string or list)

        Environment Variables:
            DAZ_SCRIPT_SERVER_ENABLED: Set to 'true' to use server mode
            DAZ_SCRIPT_SERVER_HOST: Server host (default: 127.0.0.1)
            DAZ_SCRIPT_SERVER_PORT: Server port (default: 18811)
            DAZ_ROOT: Path to DAZ Studio executable
            DAZ_ARGS: Default arguments for DAZ Studio
        """

        mark = __file__.replace("\\", "/")
        parts = mark.split("/")[:-2]
        parts.append("scripts")
        script_path = "/".join(parts) + f"/{script_name}"

        server_enabled = os.getenv("DAZ_SCRIPT_SERVER_ENABLED", "false").strip().lower() in ("true", "1", "yes")

        if server_enabled:
            host = os.getenv("DAZ_SCRIPT_SERVER_HOST", "127.0.0.1")
            port = os.getenv("DAZ_SCRIPT_SERVER_PORT", "18811")
            url = f"http://{host}:{port}/execute"

            mark_args = script_vars if script_vars is not None else {}

            payload = {
                "scriptFile": script_path,
                "args": mark_args
            }
            

            print(f"Sending script to DAZ Script Server: {url}")
            print(f"  payload: {json.dumps(payload, indent=2)}")

            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            # Set a 30-second timeout to prevent hanging on unresponsive servers
            timeout = 30
            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = response.read().decode("utf-8")
                print(f"DAZ Script Server response: {result}")

        else:
            print(os.environ['DAZ_ROOT'])

            daz_root = os.getenv("DAZ_ROOT")
            daz_args = os.getenv("DAZ_ARGS", "")

            # Build command as a list for cross-platform compatibility
            command_list = [daz_root]

            # Add script arguments
            mark_args = json.dumps(script_vars) if script_vars is not None else ""
            if mark_args:
                command_list.extend(["-scriptArg", mark_args])

            # Add DAZ_ARGS if present
            if daz_args:
                command_list.extend(daz_args.split())

            # Add custom command line arguments
            if daz_command_line:
                if isinstance(daz_command_line, list):
                    command_list.extend(daz_command_line)
                else:
                    command_list.extend(daz_command_line.split())

            # Add script path
            command_list.append(script_path)

            print(f'Executing script file with command: {" ".join(command_list)}')

            subprocess.Popen(command_list, shell=False)
        

    @staticmethod
    def to_dict(args: argparse.Namespace, exclude: Optional[Set[str]] = None) -> Dict[str, Any]:
        """
        Converts an argparse.Namespace object to a clean dictionary.
        
        It automatically excludes framework-specific keys ('command', 'class_to_run').
        """
        args_dict = vars(args)
        default_exclude = {'command', 'class_to_run'}
        
        if exclude:
            keys_to_exclude = default_exclude.union(exclude)
        else:
            keys_to_exclude = default_exclude

        return {
            key: value
            for key, value in args_dict.items()
            if key not in keys_to_exclude
        }