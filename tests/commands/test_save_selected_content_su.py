"""
Tests for SaveSelectedContentSU command (save-content-item)

Tests saving selected content items to target location.
"""
import pytest
from argparse import Namespace
from unittest import mock
from vangard.commands.SaveSelectedContentSU import SaveSelectedContentSU


class TestSaveSelectedContentSU:
    """Test suite for SaveSelectedContentSU command"""

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_save_content_basic(self, mock_exec):
        """Test basic content save"""
        args = Namespace(
            target_dir='/content/library'
        )

        cmd = SaveSelectedContentSU(parser=mock.Mock(), config={})
        cmd.process(args)

        # Verify exec_remote_script was called
        mock_exec.assert_called_once()

        # Verify correct arguments (using keyword args)
        call_kwargs = mock_exec.call_args.kwargs

        assert call_kwargs['script_name'] == "SaveSelectedContentSU.dsa"
        assert call_kwargs['script_vars']['target_dir'] == '/content/library'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_save_content_unix_path(self, mock_exec):
        """Test content save with Unix path"""
        args = Namespace(
            target_dir='/var/daz/content'
        )

        cmd = SaveSelectedContentSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['target_dir'] == '/var/daz/content'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_save_content_windows_path(self, mock_exec):
        """Test content save with Windows path"""
        args = Namespace(
            target_dir='C:/DAZ/Content/Library'
        )

        cmd = SaveSelectedContentSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['target_dir'] == 'C:/DAZ/Content/Library'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_save_content_path_with_spaces(self, mock_exec):
        """Test content save with path containing spaces"""
        args = Namespace(
            target_dir='/path with spaces/Content Library'
        )

        cmd = SaveSelectedContentSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['target_dir'] == '/path with spaces/Content Library'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_save_content_relative_path(self, mock_exec):
        """Test content save with relative path"""
        args = Namespace(
            target_dir='../content/custom'
        )

        cmd = SaveSelectedContentSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['target_dir'] == '../content/custom'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_save_content_nested_path(self, mock_exec):
        """Test content save with deeply nested path"""
        args = Namespace(
            target_dir='/content/library/props/furniture/modern/chairs'
        )

        cmd = SaveSelectedContentSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['target_dir'] == '/content/library/props/furniture/modern/chairs'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_save_content_special_characters(self, mock_exec):
        """Test content save with special characters in path"""
        args = Namespace(
            target_dir='/content/custom_content-v2.0'
        )

        cmd = SaveSelectedContentSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['target_dir'] == '/content/custom_content-v2.0'
