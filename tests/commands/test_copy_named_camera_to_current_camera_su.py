"""
Tests for CopyNamedCameraToCurrentCameraSU command (copy-camera)

Tests copying camera settings between cameras.
"""
import pytest
from argparse import Namespace
from unittest import mock
from vangard.commands.CopyNamedCameraToCurrentCameraSU import CopyNamedCameraToCurrentCameraSU


class TestCopyNamedCameraToCurrentCameraSU:
    """Test suite for CopyNamedCameraToCurrentCameraSU command"""

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_copy_camera_both_specified(self, mock_exec):
        """Test copying from source camera to target camera"""
        args = Namespace(
            source_camera='Camera1',
            target_camera='Camera2'
        )

        cmd = CopyNamedCameraToCurrentCameraSU(parser=mock.Mock(), config={})
        cmd.process(args)

        # Verify exec_remote_script was called
        mock_exec.assert_called_once()

        # Verify correct arguments
        call_kwargs = mock_exec.call_args.kwargs

        assert call_kwargs['script_name'] == "CopyNamedCameraToCurrentCameraSU.dsa"
        assert call_kwargs['script_vars']['source_camera'] == 'Camera1'
        assert call_kwargs['script_vars']['target_camera'] == 'Camera2'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_copy_camera_to_viewport(self, mock_exec):
        """Test copying to viewport (target not specified)"""
        args = Namespace(
            source_camera='Camera1',
            target_camera=None
        )

        cmd = CopyNamedCameraToCurrentCameraSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['source_camera'] == 'Camera1'
        assert call_kwargs['script_vars']['target_camera'] is None

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_copy_camera_source_only(self, mock_exec):
        """Test specifying only source camera"""
        args = Namespace(
            source_camera='MainCamera',
            target_camera=None
        )

        cmd = CopyNamedCameraToCurrentCameraSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['source_camera'] == 'MainCamera'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_copy_camera_with_spaces(self, mock_exec):
        """Test camera names with spaces"""
        args = Namespace(
            source_camera='Camera Main View',
            target_camera='Camera Close Up'
        )

        cmd = CopyNamedCameraToCurrentCameraSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['source_camera'] == 'Camera Main View'
        assert call_kwargs['script_vars']['target_camera'] == 'Camera Close Up'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_copy_camera_with_numeric_names(self, mock_exec):
        """Test cameras with numeric names"""
        args = Namespace(
            source_camera='Camera 1',
            target_camera='Camera 2'
        )

        cmd = CopyNamedCameraToCurrentCameraSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['source_camera'] == 'Camera 1'
        assert call_kwargs['script_vars']['target_camera'] == 'Camera 2'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_copy_camera_with_special_characters(self, mock_exec):
        """Test camera names with special characters"""
        args = Namespace(
            source_camera='Camera_01-Main',
            target_camera='Camera_02-Alt'
        )

        cmd = CopyNamedCameraToCurrentCameraSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['source_camera'] == 'Camera_01-Main'
        assert call_kwargs['script_vars']['target_camera'] == 'Camera_02-Alt'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_both_cameras_none(self, mock_exec):
        """Test when both cameras are None"""
        args = Namespace(
            source_camera=None,
            target_camera=None
        )

        cmd = CopyNamedCameraToCurrentCameraSU(parser=mock.Mock(), config={})
        cmd.process(args)

        # Should still call script - validation happens in DSA
        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['source_camera'] is None
        assert call_kwargs['script_vars']['target_camera'] is None
