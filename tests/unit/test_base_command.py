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
        assert '--headless' in call_args
        assert '--test' in call_args

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
        # Check that any item in the command list contains TestScript.dsa
        assert any('TestScript.dsa' in arg for arg in call_args)

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
        assert '--flag1' in call_args
        assert '--flag2' in call_args


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


class TestBaseCommandExecRemoteScriptServer:
    """Test suite for exec_remote_script when DAZ_SCRIPT_SERVER_ENABLED is set"""

    def _make_mock_response(self, body: str = '{"status": "ok"}'):
        """Return a context-manager mock that simulates urlopen's response."""
        mock_resp = mock.MagicMock()
        mock_resp.read.return_value = body.encode("utf-8")
        mock_resp.__enter__ = mock.Mock(return_value=mock_resp)
        mock_resp.__exit__ = mock.Mock(return_value=False)
        return mock_resp

    @mock.patch('urllib.request.urlopen')
    @mock.patch('urllib.request.Request')
    def test_server_mode_calls_urlopen_not_popen(self, mock_request, mock_urlopen):
        """When server mode is enabled, urlopen is used instead of Popen"""
        mock_urlopen.return_value = self._make_mock_response()

        with mock.patch.dict(os.environ, {'DAZ_SCRIPT_SERVER_ENABLED': 'true'}, clear=False):
            with mock.patch('subprocess.Popen') as mock_popen:
                BaseCommand.exec_remote_script(
                    script_name='TestScript.dsa',
                    script_vars={'arg': 'value'},
                )

        mock_urlopen.assert_called_once()
        mock_popen.assert_not_called()

    @mock.patch('urllib.request.urlopen')
    @mock.patch('urllib.request.Request')
    def test_server_mode_default_host_and_port(self, mock_request, mock_urlopen):
        """Server mode defaults to 127.0.0.1:18811"""
        mock_urlopen.return_value = self._make_mock_response()

        env = {'DAZ_SCRIPT_SERVER_ENABLED': 'true'}
        with mock.patch.dict(os.environ, env, clear=False):
            # Remove host/port overrides if present so defaults apply
            os.environ.pop('DAZ_SCRIPT_SERVER_HOST', None)
            os.environ.pop('DAZ_SCRIPT_SERVER_PORT', None)
            BaseCommand.exec_remote_script(script_name='TestScript.dsa', script_vars={})

        call_args = mock_request.call_args
        url = call_args[0][0]
        assert url == 'http://127.0.0.1:18811/execute'

    @mock.patch('urllib.request.urlopen')
    @mock.patch('urllib.request.Request')
    def test_server_mode_custom_host_and_port(self, mock_request, mock_urlopen):
        """Server mode uses DAZ_SCRIPT_SERVER_HOST and DAZ_SCRIPT_SERVER_PORT"""
        mock_urlopen.return_value = self._make_mock_response()

        env = {
            'DAZ_SCRIPT_SERVER_ENABLED': 'true',
            'DAZ_SCRIPT_SERVER_HOST': '192.168.1.50',
            'DAZ_SCRIPT_SERVER_PORT': '9000',
        }
        with mock.patch.dict(os.environ, env, clear=False):
            BaseCommand.exec_remote_script(script_name='TestScript.dsa', script_vars={})

        call_args = mock_request.call_args
        url = call_args[0][0]
        assert url == 'http://192.168.1.50:9000/execute'

    @mock.patch('urllib.request.urlopen')
    @mock.patch('urllib.request.Request')
    def test_server_mode_payload_contains_script_file(self, mock_request, mock_urlopen):
        """POST payload contains scriptFile key with the resolved script path"""
        mock_urlopen.return_value = self._make_mock_response()

        with mock.patch.dict(os.environ, {'DAZ_SCRIPT_SERVER_ENABLED': 'true'}, clear=False):
            BaseCommand.exec_remote_script(script_name='MyCommand.dsa', script_vars={})

        call_kwargs = mock_request.call_args[1]
        payload = json.loads(call_kwargs['data'].decode('utf-8'))
        assert 'scriptFile' in payload
        assert payload['scriptFile'].endswith('MyCommand.dsa')

    @mock.patch('urllib.request.urlopen')
    @mock.patch('urllib.request.Request')
    def test_server_mode_payload_contains_args_as_json(self, mock_request, mock_urlopen):
        """POST payload args field is JSON-serialized script_vars"""
        mock_urlopen.return_value = self._make_mock_response()

        script_vars = {'scene_file': '/test.duf', 'merge': False, 'count': 42}

        with mock.patch.dict(os.environ, {'DAZ_SCRIPT_SERVER_ENABLED': 'true'}, clear=False):
            BaseCommand.exec_remote_script(script_name='TestScript.dsa', script_vars=script_vars)

        call_kwargs = mock_request.call_args[1]
        payload = json.loads(call_kwargs['data'].decode('utf-8'))
        assert payload['args'] == script_vars

    @mock.patch('urllib.request.urlopen')
    @mock.patch('urllib.request.Request')
    def test_server_mode_payload_none_vars_sends_empty_dict(self, mock_request, mock_urlopen):
        """POST payload args is empty dict when script_vars is None"""
        mock_urlopen.return_value = self._make_mock_response()

        with mock.patch.dict(os.environ, {'DAZ_SCRIPT_SERVER_ENABLED': 'true'}, clear=False):
            BaseCommand.exec_remote_script(script_name='TestScript.dsa', script_vars=None)

        call_kwargs = mock_request.call_args[1]
        payload = json.loads(call_kwargs['data'].decode('utf-8'))
        assert payload['args'] == {}

    @mock.patch('urllib.request.urlopen')
    @mock.patch('urllib.request.Request')
    def test_server_mode_enabled_flag_variants(self, mock_request, mock_urlopen):
        """DAZ_SCRIPT_SERVER_ENABLED accepts true, 1, and yes"""
        mock_urlopen.return_value = self._make_mock_response()

        for value in ('true', 'True', 'TRUE', '1', 'yes'):
            mock_urlopen.reset_mock()
            with mock.patch.dict(os.environ, {'DAZ_SCRIPT_SERVER_ENABLED': value}, clear=False):
                BaseCommand.exec_remote_script(script_name='TestScript.dsa', script_vars={})
            assert mock_urlopen.called, f"Expected server mode for DAZ_SCRIPT_SERVER_ENABLED={value!r}"

    @mock.patch('subprocess.Popen')
    def test_server_mode_disabled_by_default(self, mock_popen, temp_env):
        """Without DAZ_SCRIPT_SERVER_ENABLED, subprocess path is used"""
        env = dict(os.environ)
        env.pop('DAZ_SCRIPT_SERVER_ENABLED', None)

        with mock.patch.dict(os.environ, env, clear=True):
            BaseCommand.exec_remote_script(script_name='TestScript.dsa', script_vars={})

        mock_popen.assert_called_once()

    @mock.patch('urllib.request.urlopen')
    @mock.patch('urllib.request.Request')
    def test_server_mode_uses_post_method(self, mock_request, mock_urlopen):
        """Request is constructed with POST method"""
        mock_urlopen.return_value = self._make_mock_response()

        with mock.patch.dict(os.environ, {'DAZ_SCRIPT_SERVER_ENABLED': 'true'}, clear=False):
            BaseCommand.exec_remote_script(script_name='TestScript.dsa', script_vars={})

        call_kwargs = mock_request.call_args[1]
        assert call_kwargs['method'] == 'POST'

    @mock.patch('urllib.request.urlopen')
    @mock.patch('urllib.request.Request')
    def test_server_mode_sets_content_type_header(self, mock_request, mock_urlopen):
        """Request includes Content-Type: application/json header"""
        mock_urlopen.return_value = self._make_mock_response()

        with mock.patch.dict(os.environ, {'DAZ_SCRIPT_SERVER_ENABLED': 'true'}, clear=False):
            BaseCommand.exec_remote_script(script_name='TestScript.dsa', script_vars={})

        call_kwargs = mock_request.call_args[1]
        assert call_kwargs['headers']['Content-Type'] == 'application/json'


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
