"""
Tests for CopyCurrentSceneFileSU command (saveas)

Tests saving scene file to a new location.
"""
import pytest
from argparse import Namespace
from unittest import mock
from vangard.commands.CopyCurerentSceneFileSU import CopyCurrentSceneFileSU


class TestCopyCurrentSceneFileSU:
    """Test suite for CopyCurrentSceneFileSU command"""

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_saveas_basic(self, mock_exec):
        """Test basic save as functionality"""
        args = Namespace(
            save_file='/path/to/new_scene.duf'
        )

        cmd = CopyCurrentSceneFileSU(parser=mock.Mock(), config={})
        cmd.process(args)

        # Verify exec_remote_script was called
        mock_exec.assert_called_once()

        # Verify correct arguments
        call_kwargs = mock_exec.call_args.kwargs

        assert call_kwargs['script_name'] == "CopyCurrentSceneFileSU.dsa"
        assert call_kwargs['script_vars']['save_file'] == '/path/to/new_scene.duf'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_saveas_with_spaces_in_path(self, mock_exec):
        """Test save as with spaces in file path"""
        args = Namespace(
            save_file='/path with spaces/my scene file.duf'
        )

        cmd = CopyCurrentSceneFileSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['save_file'] == '/path with spaces/my scene file.duf'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_saveas_windows_path(self, mock_exec):
        """Test save as with Windows-style path"""
        args = Namespace(
            save_file='C:/Users/Test/Documents/Scenes/new_scene.duf'
        )

        cmd = CopyCurrentSceneFileSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['save_file'] == 'C:/Users/Test/Documents/Scenes/new_scene.duf'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_saveas_with_version_number(self, mock_exec):
        """Test save as with version numbers in filename"""
        args = Namespace(
            save_file='/path/to/scene_v1.2.3_final.duf'
        )

        cmd = CopyCurrentSceneFileSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['save_file'] == '/path/to/scene_v1.2.3_final.duf'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_saveas_different_file_extensions(self, mock_exec):
        """Test save as with different file extensions"""
        extensions = ['.duf', '.daz', '.dsf']

        for ext in extensions:
            args = Namespace(
                save_file=f'/path/to/scene{ext}'
            )

            cmd = CopyCurrentSceneFileSU(parser=mock.Mock(), config={})
            cmd.process(args)

            call_kwargs = mock_exec.call_args.kwargs
            assert call_kwargs['script_vars']['save_file'] == f'/path/to/scene{ext}'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_saveas_relative_path(self, mock_exec):
        """Test save as with relative path"""
        args = Namespace(
            save_file='../backup/scene.duf'
        )

        cmd = CopyCurrentSceneFileSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['save_file'] == '../backup/scene.duf'
