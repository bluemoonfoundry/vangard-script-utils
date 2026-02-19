"""
Tests for SingleSceneRendererSU command (scene-render)

Tests scene rendering with optional arguments.
"""
import pytest
from argparse import Namespace
from unittest import mock
from vangard.commands.SingleSceneRendererSU import SingleSceneRendererSU


class TestSingleSceneRendererSU:
    """Test suite for SingleSceneRendererSU command"""

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_render_current_scene(self, mock_exec):
        """Test rendering current scene without specifying scene file"""
        args = Namespace(
            scene_file=None,
            output_file=None
        )

        cmd = SingleSceneRendererSU(parser=mock.Mock(), config={})
        cmd.process(args)

        # Verify exec_remote_script was called
        mock_exec.assert_called_once()

        # Verify correct arguments
        call_kwargs = mock_exec.call_args.kwargs

        assert call_kwargs['script_name'] == "SingleSceneRendererSU.dsa"
        assert call_kwargs['script_vars']['scene_file'] is None
        assert call_kwargs['script_vars']['output_file'] is None

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_render_with_scene_file(self, mock_exec):
        """Test rendering a specific scene file"""
        args = Namespace(
            scene_file='/path/to/scene.duf',
            output_file=None
        )

        cmd = SingleSceneRendererSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['scene_file'] == '/path/to/scene.duf'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_render_with_output_file(self, mock_exec):
        """Test rendering with specific output file"""
        args = Namespace(
            scene_file=None,
            output_file='/output/render.png'
        )

        cmd = SingleSceneRendererSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['output_file'] == '/output/render.png'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_render_with_both_args(self, mock_exec):
        """Test rendering with both scene file and output file"""
        args = Namespace(
            scene_file='/path/to/scene.duf',
            output_file='/output/render.png'
        )

        cmd = SingleSceneRendererSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['scene_file'] == '/path/to/scene.duf'
        assert call_kwargs['script_vars']['output_file'] == '/output/render.png'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_render_with_spaces_in_paths(self, mock_exec):
        """Test rendering with spaces in file paths"""
        args = Namespace(
            scene_file='/path with spaces/my scene.duf',
            output_file='/output path/my render.png'
        )

        cmd = SingleSceneRendererSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['scene_file'] == '/path with spaces/my scene.duf'
        assert call_kwargs['script_vars']['output_file'] == '/output path/my render.png'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_render_different_output_formats(self, mock_exec):
        """Test rendering to different output formats"""
        formats = ['.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp', '.exr']

        for fmt in formats:
            args = Namespace(
                scene_file=None,
                output_file=f'/output/render{fmt}'
            )

            cmd = SingleSceneRendererSU(parser=mock.Mock(), config={})
            cmd.process(args)

            call_kwargs = mock_exec.call_args.kwargs
            assert call_kwargs['script_vars']['output_file'] == f'/output/render{fmt}'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_render_windows_paths(self, mock_exec):
        """Test rendering with Windows-style paths"""
        args = Namespace(
            scene_file='C:/Scenes/test.duf',
            output_file='D:/Renders/output.png'
        )

        cmd = SingleSceneRendererSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['scene_file'] == 'C:/Scenes/test.duf'
        assert call_kwargs['script_vars']['output_file'] == 'D:/Renders/output.png'
