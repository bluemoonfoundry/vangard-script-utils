"""
Pytest configuration and shared fixtures for vangard-script-utils tests.
"""
import pytest
import os
from unittest import mock
from core.framework import load_config


@pytest.fixture
def sample_config():
    """Returns the actual configuration for testing."""
    return load_config('config.yaml')


@pytest.fixture
def mock_daz_execution():
    """
    Mocks BaseCommand.exec_remote_script to prevent DAZ execution.

    Usage:
        def test_something(mock_daz_execution):
            # Your test code
            mock_daz_execution.assert_called_once()
            script_name, script_vars, _ = mock_daz_execution.call_args[0]
    """
    with mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script') as mock_exec:
        yield mock_exec


@pytest.fixture
def mock_subprocess():
    """
    Mocks subprocess.Popen to prevent any subprocess execution.

    Usage:
        def test_something(mock_subprocess):
            # Your test code
            assert mock_subprocess.called
    """
    with mock.patch('subprocess.Popen') as mock_popen:
        mock_popen.return_value.returncode = 0
        yield mock_popen


@pytest.fixture
def temp_env():
    """
    Provides temporary environment variables for testing.

    Usage:
        def test_something(temp_env):
            # DAZ_ROOT and DAZ_ARGS are available
            assert os.getenv('DAZ_ROOT') == '/mock/daz/studio'
    """
    with mock.patch.dict(os.environ, {
        'DAZ_ROOT': '/mock/daz/studio',
        'DAZ_ARGS': '--headless --test'
    }):
        yield


@pytest.fixture
def clean_env():
    """
    Provides a clean environment without DAZ environment variables.
    Useful for testing error handling when DAZ is not configured.
    """
    env_copy = os.environ.copy()
    os.environ.pop('DAZ_ROOT', None)
    os.environ.pop('DAZ_ARGS', None)
    yield
    os.environ.clear()
    os.environ.update(env_copy)


@pytest.fixture
def mock_parser():
    """
    Provides a mock ArgumentParser for commands that need it.

    Usage:
        def test_something(mock_parser):
            cmd = MyCommand(parser=mock_parser, config={})
    """
    from unittest import mock
    parser = mock.Mock()
    return parser
