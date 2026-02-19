"""
Configuration consistency tests

Verifies that config.yaml is consistent with the actual codebase:
- All commands have corresponding Python classes
- All Python classes have corresponding DSA scripts
- No duplicate command names
- All class paths are valid
"""
import pytest
import os
from core.framework import load_config, load_class


class TestConfigConsistency:
    """Test suite for config.yaml consistency"""

    def test_all_commands_have_classes(self):
        """Verify every command in config has a valid Python class"""
        config = load_config('config.yaml')

        for cmd in config['commands']:
            class_path = cmd['class']
            command_name = cmd['name']

            # Should not raise exception
            try:
                CommandClass = load_class(class_path)
                assert CommandClass is not None, f"Command '{command_name}' class is None"
            except SystemExit:
                pytest.fail(f"Command '{command_name}' has invalid class path: {class_path}")

    def test_all_commands_have_dsa_scripts(self):
        """Verify every command has a corresponding .dsa script file"""
        config = load_config('config.yaml')

        # Commands that don't require DSA scripts (e.g., help command)
        commands_without_dsa = {'help'}

        for cmd in config['commands']:
            class_path = cmd['class']
            command_name = cmd['name']

            # Skip commands that don't require DSA scripts
            if command_name in commands_without_dsa:
                continue

            # Extract class name from path (e.g., "LoadMergeSU" from "vangard.commands.LoadMergeSU.LoadMergeSU")
            class_name = class_path.split('.')[-1]
            script_path = f"vangard/scripts/{class_name}.dsa"

            assert os.path.exists(script_path), \
                f"Command '{command_name}' missing DSA script: {script_path}"

    def test_no_duplicate_command_names(self):
        """Verify there are no duplicate command names"""
        config = load_config('config.yaml')

        command_names = [cmd['name'] for cmd in config['commands']]
        unique_names = set(command_names)

        assert len(command_names) == len(unique_names), \
            f"Duplicate command names found: {[name for name in command_names if command_names.count(name) > 1]}"

    def test_all_argument_types_are_valid(self):
        """Verify all argument types are valid"""
        config = load_config('config.yaml')
        valid_types = ['str', 'int', 'float']

        for cmd in config['commands']:
            command_name = cmd['name']
            for arg in cmd.get('arguments', []):
                arg_type = arg.get('type')

                # Skip arguments without explicit type or with action (like store_true)
                if not arg_type or 'action' in arg:
                    continue

                assert arg_type in valid_types, \
                    f"Command '{command_name}' has invalid argument type '{arg_type}' for {arg['names']}"

    def test_all_commands_have_help_text(self):
        """Verify all commands have help text"""
        config = load_config('config.yaml')

        for cmd in config['commands']:
            command_name = cmd['name']
            assert 'help' in cmd, f"Command '{command_name}' missing help text"
            assert cmd['help'], f"Command '{command_name}' has empty help text"

    def test_all_arguments_have_help_text(self):
        """Verify all arguments have help text"""
        config = load_config('config.yaml')

        for cmd in config['commands']:
            command_name = cmd['name']
            for arg in cmd.get('arguments', []):
                arg_names = arg.get('names', [])
                assert 'help' in arg, \
                    f"Command '{command_name}' argument {arg_names} missing help text"
                assert arg['help'], \
                    f"Command '{command_name}' argument {arg_names} has empty help text"

    def test_required_arguments_have_dest(self):
        """Verify all arguments have dest field"""
        config = load_config('config.yaml')

        for cmd in config['commands']:
            command_name = cmd['name']
            for arg in cmd.get('arguments', []):
                arg_names = arg.get('names', [])
                assert 'dest' in arg, \
                    f"Command '{command_name}' argument {arg_names} missing dest field"

    def test_class_paths_follow_convention(self):
        """Verify class paths follow the expected convention"""
        config = load_config('config.yaml')

        for cmd in config['commands']:
            class_path = cmd['class']
            command_name = cmd['name']

            # Class path should be: vangard.commands.ClassName.ClassName
            parts = class_path.split('.')
            assert len(parts) == 4, \
                f"Command '{command_name}' has unexpected class path format: {class_path}"

            assert parts[0] == 'vangard', \
                f"Command '{command_name}' class path should start with 'vangard': {class_path}"

            assert parts[1] == 'commands', \
                f"Command '{command_name}' class path should have 'commands' as second part: {class_path}"

            # Module name and class name should match (with known exceptions for typos in source)
            known_exceptions = {
                'vangard.commands.CopyCurerentSceneFileSU.CopyCurrentSceneFileSU'  # Typo in filename
            }

            if class_path not in known_exceptions:
                assert parts[2] == parts[3], \
                    f"Command '{command_name}' module and class names should match: {class_path}"
