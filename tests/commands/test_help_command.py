"""
Tests for HelpCommand (help)

Tests help command functionality. Note: HelpCommand does NOT call exec_remote_script,
it returns help text directly.
"""
import pytest
from argparse import Namespace
from unittest import mock
from vangard.commands.HelpCommand import HelpCommand


class TestHelpCommand:
    """Test suite for HelpCommand"""

    def test_help_no_command(self):
        """Test help without specific command (general help)"""
        args = Namespace(
            command_name=None
        )

        config = {
            'app': {
                'prog': 'vangard',
                'description': 'Test description'
            },
            'commands': [
                {'name': 'test-cmd', 'help': 'Test command', 'arguments': []}
            ]
        }

        cmd = HelpCommand(parser=mock.Mock(), config=config)
        result = cmd.process(args)

        # Should return formatted help text
        assert isinstance(result, str)
        assert 'vangard' in result
        assert 'Available Commands' in result

    def test_help_specific_command(self):
        """Test help for a specific command"""
        import argparse
        args = Namespace(
            command_name='load-scene'
        )

        # Create a mock parser with subparsers
        mock_parser = mock.Mock()
        mock_subparser = mock.Mock()
        mock_subparsers_action = mock.Mock(spec=argparse._SubParsersAction)
        mock_subparsers_action.choices = {'load-scene': mock_subparser}
        mock_parser._actions = [mock_subparsers_action]

        cmd = HelpCommand(parser=mock_parser, config={})
        result = cmd.process(args)

        # Should call print_help on the subparser
        mock_subparser.print_help.assert_called_once()
        assert isinstance(result, str)

    def test_help_various_commands(self):
        """Test help for various different commands"""
        commands_config = {
            'app': {'prog': 'vangard', 'description': 'Test'},
            'commands': [
                {'name': 'batch-render', 'help': 'Batch render', 'arguments': []},
                {'name': 'create-cam', 'help': 'Create camera', 'arguments': []},
                {'name': 'scene-render', 'help': 'Render scene', 'arguments': []},
            ]
        }

        args = Namespace(command_name=None)
        cmd = HelpCommand(parser=mock.Mock(), config=commands_config)
        result = cmd.process(args)

        # All commands should be in the help output
        assert 'batch-render' in result
        assert 'create-cam' in result
        assert 'scene-render' in result

    def test_help_command_with_dashes(self):
        """Test help for commands with dashes in names"""
        args = Namespace(command_name='rotate-render')

        mock_parser = mock.Mock()
        mock_subparser = mock.Mock()
        import argparse
        mock_subparsers_action = mock.Mock(spec=argparse._SubParsersAction)
        mock_subparsers_action.choices = {'rotate-render': mock_subparser}
        mock_parser._actions = [mock_subparsers_action]

        cmd = HelpCommand(parser=mock_parser, config={})
        result = cmd.process(args)

        mock_subparser.print_help.assert_called_once()

    def test_help_nonexistent_command(self):
        """Test help for a command that doesn't exist"""
        args = Namespace(command_name='nonexistent-command')

        mock_parser = mock.Mock()
        import argparse
        mock_subparsers_action = mock.Mock(spec=argparse._SubParsersAction)
        mock_subparsers_action.choices = {}  # No commands
        mock_parser._actions = [mock_subparsers_action]

        cmd = HelpCommand(parser=mock_parser, config={})
        result = cmd.process(args)

        # Should return error message
        assert isinstance(result, str)
        assert 'Unknown command' in result

    def test_help_empty_string(self):
        """Test help with empty string command name (treated as None)"""
        args = Namespace(command_name='')

        mock_parser = mock.Mock()
        import argparse
        mock_subparsers_action = mock.Mock(spec=argparse._SubParsersAction)
        mock_subparsers_action.choices = {'': mock.Mock()}  # Empty command name
        mock_parser._actions = [mock_subparsers_action]

        cmd = HelpCommand(parser=mock_parser, config={})
        result = cmd.process(args)

        # Should handle empty string
        assert isinstance(result, str)
