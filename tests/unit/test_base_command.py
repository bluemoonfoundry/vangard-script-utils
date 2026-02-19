"""
Unit tests for vangard/commands/BaseCommand.py

Tests the base command functionality that all commands inherit.
"""
import pytest
import json
import os
from argparse import Namespace
from unittest import mock
from vangard.commands.BaseCommand import BaseCommand


class TestBaseCommandToDict:
    """Test suite for BaseCommand.to_dict method"""

    def test_converts_namespace_to_dict(self):
        """Test that to_dict converts Namespace to dictionary"""
        args = Namespace(scene_file='/test.duf', merge=False)
        result = BaseCommand.to_dict(args)

        assert isinstance(result, dict)
        assert result['scene_file'] == '/test.duf'
        assert result['merge'] == False

    def test_excludes_command_field(self):
        """Test that 'command' field is excluded from result"""
        args = Namespace(command='load-scene', scene_file='/test.duf')
        result = BaseCommand.to_dict(args)

        assert 'command' not in result
        assert 'scene_file' in result

    def test_excludes_class_to_run_field(self):
        """Test that 'class_to_run' field is excluded from result"""
        args = Namespace(class_to_run='SomeClass', scene_file='/test.duf')
        result = BaseCommand.to_dict(args)

        assert 'class_to_run' not in result
        assert 'scene_file' in result

    def test_excludes_custom_fields(self):
        """Test that custom exclude set works"""
        args = Namespace(scene_file='/test.duf', internal_field='value', merge=False)
        result = BaseCommand.to_dict(args, exclude={'internal_field'})

        assert 'internal_field' not in result
        assert 'scene_file' in result
        assert 'merge' in result

    def test_preserves_all_value_types(self):
        """Test that different value types are preserved"""
        args = Namespace(
            string_val='test',
            int_val=42,
            float_val=3.14,
            bool_val=True,
            none_val=None
        )
        result = BaseCommand.to_dict(args)

        assert result['string_val'] == 'test'
        assert result['int_val'] == 42
        assert result['float_val'] == 3.14
        assert result['bool_val'] == True
        assert result['none_val'] == None


class TestBaseCommandExecRemoteScript:
    """Test suite for BaseCommand.exec_remote_script method"""

    @mock.patch('subprocess.Popen')
    def test_constructs_command_line_with_daz_root(self, mock_popen, temp_env):
        """Test that exec_remote_script includes DAZ_ROOT in command"""
        BaseCommand.exec_remote_script(
            script_name='TestScript.dsa',
            script_vars={'arg': 'value'},
            daz_command_line=None
        )

        assert mock_popen.called
        call_args = mock_popen.call_args[0][0]
        assert '/mock/daz/studio' in call_args

    @mock.patch('subprocess.Popen')
    def test_constructs_command_line_with_daz_args(self, mock_popen, temp_env):
        """Test that exec_remote_script includes DAZ_ARGS in command"""
        BaseCommand.exec_remote_script(
            script_name='TestScript.dsa',
            script_vars={'arg': 'value'},
            daz_command_line=None
        )

        assert mock_popen.called
        call_args = mock_popen.call_args[0][0]
        assert '--headless --test' in call_args

    @mock.patch('subprocess.Popen')
    def test_includes_script_path(self, mock_popen, temp_env):
        """Test that exec_remote_script includes script path"""
        BaseCommand.exec_remote_script(
            script_name='TestScript.dsa',
            script_vars={'arg': 'value'},
            daz_command_line=None
        )

        assert mock_popen.called
        call_args = mock_popen.call_args[0][0]
        assert 'TestScript.dsa' in call_args

    @mock.patch('subprocess.Popen')
    def test_serializes_script_vars_to_json(self, mock_popen, temp_env):
        """Test that script_vars are serialized to JSON"""
        script_vars = {'scene_file': '/test.duf', 'merge': False, 'count': 42}

        BaseCommand.exec_remote_script(
            script_name='TestScript.dsa',
            script_vars=script_vars,
            daz_command_line=None
        )

        assert mock_popen.called
        call_args = mock_popen.call_args[0][0]

        # Verify JSON is in the command line
        json_str = json.dumps(script_vars)
        assert json_str in call_args

    @mock.patch('subprocess.Popen')
    def test_handles_none_script_vars(self, mock_popen, temp_env):
        """Test that None script_vars is handled gracefully"""
        BaseCommand.exec_remote_script(
            script_name='TestScript.dsa',
            script_vars=None,
            daz_command_line=None
        )

        assert mock_popen.called

    @mock.patch('subprocess.Popen')
    def test_handles_none_daz_args_env(self, mock_popen):
        """Test handling when DAZ_ARGS is not set"""
        with mock.patch.dict(os.environ, {'DAZ_ROOT': '/mock/daz'}, clear=True):
            BaseCommand.exec_remote_script(
                script_name='TestScript.dsa',
                script_vars={'arg': 'value'},
                daz_command_line=None
            )

            assert mock_popen.called

    @mock.patch('subprocess.Popen')
    def test_handles_custom_command_line(self, mock_popen, temp_env):
        """Test that custom command line arguments are included"""
        BaseCommand.exec_remote_script(
            script_name='TestScript.dsa',
            script_vars={'arg': 'value'},
            daz_command_line='--custom-flag'
        )

        assert mock_popen.called
        call_args = mock_popen.call_args[0][0]
        assert '--custom-flag' in call_args

    @mock.patch('subprocess.Popen')
    def test_handles_command_line_as_list(self, mock_popen, temp_env):
        """Test that command line can be provided as a list"""
        BaseCommand.exec_remote_script(
            script_name='TestScript.dsa',
            script_vars={'arg': 'value'},
            daz_command_line=['--flag1', '--flag2']
        )

        assert mock_popen.called
        call_args = mock_popen.call_args[0][0]
        assert '--flag1 --flag2' in call_args


class TestBaseCommandProcess:
    """Test suite for BaseCommand.process method"""

    def test_process_requires_parser(self):
        """Test that process raises error when parser is not set"""
        cmd = BaseCommand(parser=None, config={})
        args = Namespace(test='value')

        with pytest.raises(ValueError, match="Parser is not set"):
            cmd.process(args)

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_default_script')
    def test_process_calls_exec_default_script(self, mock_exec):
        """Test that process calls exec_default_script"""
        from argparse import ArgumentParser

        parser = ArgumentParser()
        cmd = BaseCommand(parser=parser, config={})
        args = Namespace(scene_file='/test.duf', merge=False)

        cmd.process(args)

        assert mock_exec.called
        call_args = mock_exec.call_args[0][0]
        assert call_args['scene_file'] == '/test.duf'


class TestBaseCommandExecDefaultScript:
    """Test suite for BaseCommand.exec_default_script method"""

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_exec_default_script_uses_class_name(self, mock_exec):
        """Test that exec_default_script uses the class name for script"""
        from argparse import ArgumentParser

        parser = ArgumentParser()

        # Create a concrete subclass for testing
        class TestCommandSU(BaseCommand):
            pass

        cmd = TestCommandSU(parser=parser, config={})
        args_dict = {'test': 'value'}

        cmd.exec_default_script(args_dict)

        assert mock_exec.called
        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_name'] == 'TestCommandSU.dsa'
