# vangard/commands/base.py
import os
from abc import ABC, abstractmethod
import argparse
import json
import subprocess
from typing import Any, Dict, Optional, Set
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
    
    def exec_default_script(self, args):
        script_name = f"{self.__class__.__name__}.dsa"
        self.exec_remote_script(
            script_name=script_name,
            script_vars=args,
            daz_command_line=None
        )

    @staticmethod
    def exec_remote_script (script_name:str, script_vars:dict|None=None, daz_command_line:str|None=None):    

        print (os.environ['DAZ_ROOT'])

        daz_root = os.getenv("DAZ_ROOT")
        daz_args = os.getenv("DAZ_ARGS")
        
        if (daz_args is None):
            daz_args = ""
        if (daz_command_line is None):
            daz_command_line = ""
        elif (isinstance(daz_command_line, list)):
            daz_command_line = " ".join(daz_command_line)


        mark = __file__.replace("\\","/")
        parts = mark.split("/")[:-2]
        parts.append("scripts")
        new_path = "/".join(parts)
        script_path = f"{new_path}/{script_name}"

        if script_path is not None:
            mark_args="";
            if script_vars is not None:
                mark_args += f'{json.dumps(script_vars)}'

            command_expanded = f'"{daz_root}" -scriptArg \'{mark_args}\' {daz_args} {daz_command_line} {script_path}'

            print (f'Executing script file with command line: {command_expanded}') 

            process = subprocess.Popen (command_expanded, shell=False)

        else:
            print (f"No valid script file was presented for command.")
        

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