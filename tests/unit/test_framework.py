"""
Unit tests for core/framework.py

Tests the core framework functions without any external dependencies.
"""
import pytest
import argparse
import os
from core.framework import load_config, build_parser, load_class, run_command, TYPE_MAP


class TestLoadConfig:
    """Test suite for load_config function"""

    def test_load_valid_config(self):
        """Test loading a valid config.yaml file"""
        config = load_config('config.yaml')

        assert config is not None
        assert 'app' in config
        assert 'commands' in config
        assert isinstance(config['commands'], list)

    def test_config_has_app_metadata(self):
        """Test that config contains app metadata"""
        config = load_config('config.yaml')

        assert 'prog' in config['app']
        assert 'description' in config['app']
        assert config['app']['prog'] == 'vangard-cli'

    def test_config_has_commands(self):
        """Test that config contains command definitions"""
        config = load_config('config.yaml')

        assert len(config['commands']) > 0

        # Verify command structure
        first_cmd = config['commands'][0]
        assert 'name' in first_cmd
        assert 'class' in first_cmd
        assert 'help' in first_cmd

    def test_load_missing_config_exits(self):
        """Test that loading missing config file exits gracefully"""
        with pytest.raises(SystemExit):
            load_config('nonexistent_config.yaml')


class TestBuildParser:
    """Test suite for build_parser function"""

    def test_build_parser_creates_parser(self, sample_config):
        """Test that build_parser creates an ArgumentParser"""
        parser = build_parser(sample_config)

        assert isinstance(parser, argparse.ArgumentParser)
        assert parser.prog == 'vangard-cli'

    def test_parser_has_subparsers(self, sample_config):
        """Test that parser has subparsers for commands"""
        parser = build_parser(sample_config)

        # Try parsing a known command
        args = parser.parse_args(['help'])
        assert args.command == 'help'

    def test_parser_registers_all_commands(self, sample_config):
        """Test that all commands from config are registered"""
        parser = build_parser(sample_config)

        command_names = [cmd['name'] for cmd in sample_config['commands']]

        # Get the subparsers from the parser
        subparsers_actions = [
            action for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)
        ]

        assert len(subparsers_actions) > 0, "No subparsers found"
        subparser_choices = subparsers_actions[0].choices

        # Verify each command is registered
        for cmd_name in command_names:
            assert cmd_name in subparser_choices, f"Command '{cmd_name}' not registered in parser"

    def test_parser_handles_arguments(self, sample_config):
        """Test that parser correctly handles command arguments"""
        parser = build_parser(sample_config)

        # Test load-scene command with arguments
        args = parser.parse_args(['load-scene', '/path/to/scene.duf'])
        assert args.command == 'load-scene'
        assert args.scene_file == '/path/to/scene.duf'
        assert args.merge == False  # Default value

    def test_parser_handles_optional_flags(self, sample_config):
        """Test that parser correctly handles optional flags"""
        parser = build_parser(sample_config)

        # Test load-scene with --merge flag
        args = parser.parse_args(['load-scene', '/path/to/scene.duf', '--merge'])
        assert args.merge == True

    def test_parser_handles_optional_arguments(self, sample_config):
        """Test that parser correctly handles optional arguments"""
        parser = build_parser(sample_config)

        # Test scene-render with optional output file
        args = parser.parse_args(['scene-render', '-o', '/output/path.png'])
        assert args.output_file == '/output/path.png'


class TestLoadClass:
    """Test suite for load_class function"""

    def test_load_valid_class(self):
        """Test loading a valid class"""
        CommandClass = load_class('vangard.commands.LoadMergeSU.LoadMergeSU')

        assert CommandClass is not None
        assert CommandClass.__name__ == 'LoadMergeSU'

    def test_load_invalid_module_exits(self):
        """Test that loading invalid module exits gracefully"""
        with pytest.raises(SystemExit):
            load_class('nonexistent.module.Class')

    def test_load_invalid_class_exits(self):
        """Test that loading invalid class name exits gracefully"""
        with pytest.raises(SystemExit):
            load_class('vangard.commands.LoadMergeSU.NonexistentClass')

    def test_load_malformed_path_exits(self):
        """Test that malformed class path exits gracefully"""
        with pytest.raises(SystemExit):
            load_class('NotAValidPath')


class TestRunCommand:
    """Test suite for run_command function"""

    def test_run_command_instantiates_class(self, sample_config, mock_daz_execution):
        """Test that run_command instantiates the correct command class"""
        parser = build_parser(sample_config)
        args = parser.parse_args(['load-scene', '/test/scene.duf'])

        run_command(parser, sample_config, args)

        # Verify that exec_remote_script was called (meaning command ran)
        assert mock_daz_execution.called

    def test_run_command_passes_arguments(self, sample_config, mock_daz_execution):
        """Test that run_command passes arguments correctly"""
        parser = build_parser(sample_config)
        args = parser.parse_args(['load-scene', '/test/scene.duf', '--merge'])

        run_command(parser, sample_config, args)

        # Verify correct arguments were passed to the script
        call_kwargs = mock_daz_execution.call_args.kwargs
        assert call_kwargs['script_vars']['scene_file'] == '/test/scene.duf'
        assert call_kwargs['script_vars']['merge'] == True


class TestTypeMap:
    """Test suite for TYPE_MAP constant"""

    def test_type_map_has_basic_types(self):
        """Test that TYPE_MAP contains basic Python types"""
        assert 'str' in TYPE_MAP
        assert 'int' in TYPE_MAP
        assert 'float' in TYPE_MAP

    def test_type_map_values_are_types(self):
        """Test that TYPE_MAP values are actual type objects"""
        assert TYPE_MAP['str'] == str
        assert TYPE_MAP['int'] == int
        assert TYPE_MAP['float'] == float
