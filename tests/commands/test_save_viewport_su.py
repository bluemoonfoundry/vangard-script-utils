"""
Tests for SaveViewportSU command (save-viewport)

Tests viewport image capture with optional camera, format, and frame range.
"""
import pytest
from argparse import Namespace
from unittest import mock
from vangard.commands.SaveViewportSU import SaveViewportSU


class TestSaveViewportSU:
    """Test suite for SaveViewportSU command"""

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_save_viewport_minimal(self, mock_exec):
        """Test basic viewport save with only the required argument"""
        args = Namespace(
            save_file='C:/output/frame',
            view_camera=None,
            image_format='png',
            frame_start=None,
            frame_end=None,
        )

        cmd = SaveViewportSU(parser=mock.Mock(), config={})
        cmd.process(args)

        mock_exec.assert_called_once()
        call_kwargs = mock_exec.call_args.kwargs

        assert call_kwargs['script_name'] == "SaveViewportSU.dsa"
        assert call_kwargs['script_vars']['save_file'] == 'C:/output/frame'
        assert call_kwargs['script_vars']['view_camera'] is None
        assert call_kwargs['script_vars']['image_format'] == 'png'
        assert call_kwargs['script_vars']['frame_start'] is None
        assert call_kwargs['script_vars']['frame_end'] is None

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_save_viewport_with_camera(self, mock_exec):
        """Test viewport save with a named camera"""
        args = Namespace(
            save_file='C:/output/frame',
            view_camera='FrontCamera',
            image_format='png',
            frame_start=None,
            frame_end=None,
        )

        cmd = SaveViewportSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['view_camera'] == 'FrontCamera'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_save_viewport_jpg_format(self, mock_exec):
        """Test viewport save with jpg image format"""
        args = Namespace(
            save_file='C:/output/frame',
            view_camera=None,
            image_format='jpg',
            frame_start=None,
            frame_end=None,
        )

        cmd = SaveViewportSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['image_format'] == 'jpg'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_save_viewport_single_frame(self, mock_exec):
        """Test viewport save for a single explicit frame"""
        args = Namespace(
            save_file='C:/output/frame',
            view_camera=None,
            image_format='png',
            frame_start=10,
            frame_end=11,
        )

        cmd = SaveViewportSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['frame_start'] == 10
        assert call_kwargs['script_vars']['frame_end'] == 11

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_save_viewport_frame_range(self, mock_exec):
        """Test viewport save over a multi-frame range"""
        args = Namespace(
            save_file='C:/output/frame',
            view_camera=None,
            image_format='png',
            frame_start=0,
            frame_end=30,
        )

        cmd = SaveViewportSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['frame_start'] == 0
        assert call_kwargs['script_vars']['frame_end'] == 30

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_save_viewport_full_specification(self, mock_exec):
        """Test viewport save with all arguments provided"""
        args = Namespace(
            save_file='Y:/renders/viewport/shot',
            view_camera='OrbitCam',
            image_format='jpg',
            frame_start=5,
            frame_end=15,
        )

        cmd = SaveViewportSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_name'] == "SaveViewportSU.dsa"
        assert call_kwargs['script_vars']['save_file'] == 'Y:/renders/viewport/shot'
        assert call_kwargs['script_vars']['view_camera'] == 'OrbitCam'
        assert call_kwargs['script_vars']['image_format'] == 'jpg'
        assert call_kwargs['script_vars']['frame_start'] == 5
        assert call_kwargs['script_vars']['frame_end'] == 15

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_save_viewport_path_with_spaces(self, mock_exec):
        """Test viewport save with spaces in the output path"""
        args = Namespace(
            save_file='C:/My Renders/Viewport Capture/frame',
            view_camera=None,
            image_format='png',
            frame_start=None,
            frame_end=None,
        )

        cmd = SaveViewportSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['save_file'] == 'C:/My Renders/Viewport Capture/frame'
