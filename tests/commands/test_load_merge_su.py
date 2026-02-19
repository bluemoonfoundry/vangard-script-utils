"""
Tests for LoadMergeSU command

Tests the load-scene command functionality without executing DAZ Studio.
"""
import pytest
from argparse import Namespace
from unittest import mock
from vangard.commands.LoadMergeSU import LoadMergeSU


class TestLoadMergeSU:
    """Test suite for LoadMergeSU command"""

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_basic_load_without_merge(self, mock_exec):
        """Test loading a scene without merge flag"""
        args = Namespace(
            scene_file='/path/to/scene.duf',
            merge=False,
            command='load-scene',
            class_to_run='vangard.commands.LoadMergeSU.LoadMergeSU'
        )

        cmd = LoadMergeSU(parser=mock.Mock(), config={})
        cmd.process(args)

        # Verify exec_remote_script was called
        mock_exec.assert_called_once()

        # Verify correct arguments
        call_kwargs = mock_exec.call_args.kwargs

        assert call_kwargs['script_name'] == "LoadMergeSU.dsa"
        assert call_kwargs['script_vars']['scene_file'] == '/path/to/scene.duf'
        assert call_kwargs['script_vars']['merge'] == False

        # Verify framework fields are excluded
        assert 'command' not in call_kwargs['script_vars']
        assert 'class_to_run' not in call_kwargs['script_vars']

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_load_with_merge_flag(self, mock_exec):
        """Test loading a scene with merge flag enabled"""
        args = Namespace(
            scene_file='/path/to/scene.duf',
            merge=True
        )

        cmd = LoadMergeSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['merge'] == True

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_handles_path_with_spaces(self, mock_exec):
        """Test that paths with spaces are handled correctly"""
        args = Namespace(
            scene_file='/path with spaces/my scene.duf',
            merge=False
        )

        cmd = LoadMergeSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['scene_file'] == '/path with spaces/my scene.duf'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_handles_windows_path(self, mock_exec):
        """Test that Windows paths are handled correctly"""
        args = Namespace(
            scene_file='C:/Users/Test/Documents/scene.duf',
            merge=False
        )

        cmd = LoadMergeSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['scene_file'] == 'C:/Users/Test/Documents/scene.duf'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_handles_special_characters_in_path(self, mock_exec):
        """Test that special characters in paths are handled"""
        args = Namespace(
            scene_file='/path/to/scene_v1.2-final.duf',
            merge=False
        )

        cmd = LoadMergeSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['scene_file'] == '/path/to/scene_v1.2-final.duf'
