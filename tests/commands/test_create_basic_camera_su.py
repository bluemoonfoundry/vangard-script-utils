"""
Tests for CreateBasicCameraSU command (create-cam)

Tests camera creation with various configurations.
"""
import pytest
from argparse import Namespace
from unittest import mock
from vangard.commands.CreateBasicCameraSU import CreateBasicCameraSU


class TestCreateBasicCameraSU:
    """Test suite for CreateBasicCameraSU command"""

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_create_camera_basic(self, mock_exec):
        """Test creating a basic camera without focus"""
        args = Namespace(
            cam_name='TestCamera',
            cam_class='PerspectiveCamera',
            focus=False
        )

        cmd = CreateBasicCameraSU(parser=mock.Mock(), config={})
        cmd.process(args)

        # Verify exec_remote_script was called
        mock_exec.assert_called_once()

        # Verify correct arguments
        call_kwargs = mock_exec.call_args.kwargs

        assert call_kwargs['script_name'] == "CreateBasicCameraSU.dsa"
        assert call_kwargs['script_vars']['cam_name'] == 'TestCamera'
        assert call_kwargs['script_vars']['cam_class'] == 'PerspectiveCamera'
        assert call_kwargs['script_vars']['focus'] == False

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_create_camera_with_focus(self, mock_exec):
        """Test creating a camera with focus/DOF enabled"""
        args = Namespace(
            cam_name='FocusCamera',
            cam_class='PerspectiveCamera',
            focus=True
        )

        cmd = CreateBasicCameraSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['focus'] == True

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_camera_name_with_spaces(self, mock_exec):
        """Test camera names with spaces are handled"""
        args = Namespace(
            cam_name='My Test Camera',
            cam_class='PerspectiveCamera',
            focus=False
        )

        cmd = CreateBasicCameraSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['cam_name'] == 'My Test Camera'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_different_camera_classes(self, mock_exec):
        """Test different camera class types"""
        camera_classes = [
            'PerspectiveCamera',
            'OrthographicCamera',
            'CustomCamera'
        ]

        for cam_class in camera_classes:
            args = Namespace(
                cam_name='TestCam',
                cam_class=cam_class,
                focus=False
            )

            cmd = CreateBasicCameraSU(parser=mock.Mock(), config={})
            cmd.process(args)

            call_kwargs = mock_exec.call_args.kwargs
            assert call_kwargs['script_vars']['cam_class'] == cam_class

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_camera_name_with_special_characters(self, mock_exec):
        """Test camera names with special characters"""
        args = Namespace(
            cam_name='Camera_01-Close-Up',
            cam_class='PerspectiveCamera',
            focus=False
        )

        cmd = CreateBasicCameraSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['cam_name'] == 'Camera_01-Close-Up'
