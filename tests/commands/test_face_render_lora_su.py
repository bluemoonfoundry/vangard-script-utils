"""
Tests for FaceRenderLoraSU command (face-render-lora)

Tests orbital face render generation for LoRA training datasets.
"""
import pytest
from argparse import Namespace
from unittest import mock
from vangard.commands.FaceRenderLoraSU import FaceRenderLoraSU


class TestFaceRenderLoraSU:
    """Test suite for FaceRenderLoraSU command"""

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_face_render_defaults(self, mock_exec):
        """Test face render with all default values"""
        args = Namespace(
            output_dir='y:/ai/charflow/output/face_lora/',
            file_prefix='face',
            wid=768,
            height=768,
            camera_distance=80,
            face_y_offset=5,
            node_label=None,
            test_mode=False,
        )

        cmd = FaceRenderLoraSU(parser=mock.Mock(), config={})
        cmd.process(args)

        mock_exec.assert_called_once()
        call_kwargs = mock_exec.call_args.kwargs

        assert call_kwargs['script_name'] == "FaceRenderLoraSU.dsa"
        assert call_kwargs['script_vars']['output_dir'] == 'y:/ai/charflow/output/face_lora/'
        assert call_kwargs['script_vars']['file_prefix'] == 'face'
        assert call_kwargs['script_vars']['wid'] == 768
        assert call_kwargs['script_vars']['height'] == 768
        assert call_kwargs['script_vars']['camera_distance'] == 80
        assert call_kwargs['script_vars']['face_y_offset'] == 5
        assert call_kwargs['script_vars']['node_label'] is None
        assert call_kwargs['script_vars']['test_mode'] is False

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_face_render_custom_output_dir(self, mock_exec):
        """Test face render with a custom output directory"""
        args = Namespace(
            output_dir='C:/lora_output/my_character/',
            file_prefix='face',
            wid=768,
            height=768,
            camera_distance=80,
            face_y_offset=5,
            node_label=None,
            test_mode=False,
        )

        cmd = FaceRenderLoraSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['output_dir'] == 'C:/lora_output/my_character/'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_face_render_custom_resolution(self, mock_exec):
        """Test face render with non-default resolution"""
        args = Namespace(
            output_dir='y:/ai/charflow/output/face_lora/',
            file_prefix='face',
            wid=512,
            height=512,
            camera_distance=80,
            face_y_offset=5,
            node_label=None,
            test_mode=False,
        )

        cmd = FaceRenderLoraSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['wid'] == 512
        assert call_kwargs['script_vars']['height'] == 512

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_face_render_custom_camera_distance(self, mock_exec):
        """Test face render with adjusted camera distance"""
        args = Namespace(
            output_dir='y:/ai/charflow/output/face_lora/',
            file_prefix='face',
            wid=768,
            height=768,
            camera_distance=60,
            face_y_offset=5,
            node_label=None,
            test_mode=False,
        )

        cmd = FaceRenderLoraSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['camera_distance'] == 60

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_face_render_with_node_label(self, mock_exec):
        """Test face render targeting a specific scene node"""
        args = Namespace(
            output_dir='y:/ai/charflow/output/face_lora/',
            file_prefix='face',
            wid=768,
            height=768,
            camera_distance=80,
            face_y_offset=5,
            node_label='Genesis 9',
            test_mode=False,
        )

        cmd = FaceRenderLoraSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['node_label'] == 'Genesis 9'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_face_render_test_mode(self, mock_exec):
        """Test face render in test mode (shows message boxes instead of rendering)"""
        args = Namespace(
            output_dir='y:/ai/charflow/output/face_lora/',
            file_prefix='face',
            wid=768,
            height=768,
            camera_distance=80,
            face_y_offset=5,
            node_label=None,
            test_mode=True,
        )

        cmd = FaceRenderLoraSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['test_mode'] is True

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_face_render_custom_file_prefix(self, mock_exec):
        """Test face render with a custom file prefix"""
        args = Namespace(
            output_dir='y:/ai/charflow/output/face_lora/',
            file_prefix='victoria_face',
            wid=768,
            height=768,
            camera_distance=80,
            face_y_offset=5,
            node_label=None,
            test_mode=False,
        )

        cmd = FaceRenderLoraSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['file_prefix'] == 'victoria_face'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_face_render_full_specification(self, mock_exec):
        """Test face render with all arguments explicitly set"""
        args = Namespace(
            output_dir='C:/renders/lora/chars/',
            file_prefix='char01',
            wid=1024,
            height=1024,
            camera_distance=100,
            face_y_offset=8,
            node_label='My Character',
            test_mode=False,
        )

        cmd = FaceRenderLoraSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_name'] == "FaceRenderLoraSU.dsa"
        assert call_kwargs['script_vars']['output_dir'] == 'C:/renders/lora/chars/'
        assert call_kwargs['script_vars']['file_prefix'] == 'char01'
        assert call_kwargs['script_vars']['wid'] == 1024
        assert call_kwargs['script_vars']['height'] == 1024
        assert call_kwargs['script_vars']['camera_distance'] == 100
        assert call_kwargs['script_vars']['face_y_offset'] == 8
        assert call_kwargs['script_vars']['node_label'] == 'My Character'
        assert call_kwargs['script_vars']['test_mode'] is False
