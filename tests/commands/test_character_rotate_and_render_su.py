"""
Tests for CharacterRotateAndRenderSU command (rotate-render, rotate-random)

Tests character rotation and rendering functionality.
"""
import pytest
from argparse import Namespace
from unittest import mock
from vangard.commands.CharacterRotateAndRenderSU import CharacterRotateAndRenderSU


class TestCharacterRotateAndRenderSU:
    """Test suite for CharacterRotateAndRenderSU command"""

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_rotate_render_basic(self, mock_exec):
        """Test basic rotate and render"""
        args = Namespace(
            object_name='Character',
            lower=0,
            upper=180,
            slices=8,
            output_file=None,
            skip_render=False
        )

        cmd = CharacterRotateAndRenderSU(parser=mock.Mock(), config={})
        cmd.process(args)

        # Verify exec_remote_script was called
        mock_exec.assert_called_once()

        # Verify correct arguments
        call_kwargs = mock_exec.call_args.kwargs

        assert call_kwargs['script_name'] == "CharacterRotateAndRenderSU.dsa"
        assert call_kwargs['script_vars']['object_name'] == 'Character'
        assert call_kwargs['script_vars']['lower'] == 0
        assert call_kwargs['script_vars']['upper'] == 180
        assert call_kwargs['script_vars']['slices'] == 8

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_rotate_render_full_rotation(self, mock_exec):
        """Test full 360 degree rotation"""
        args = Namespace(
            object_name='Character',
            lower=0,
            upper=360,
            slices=12,
            output_file='/output/rotations',
            skip_render=False
        )

        cmd = CharacterRotateAndRenderSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['lower'] == 0
        assert call_kwargs['script_vars']['upper'] == 360
        assert call_kwargs['script_vars']['slices'] == 12

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_rotate_render_with_output_path(self, mock_exec):
        """Test rotation with custom output path"""
        args = Namespace(
            object_name='Character',
            lower=0,
            upper=180,
            slices=6,
            output_file='/custom/path/renders',
            skip_render=False
        )

        cmd = CharacterRotateAndRenderSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['output_file'] == '/custom/path/renders'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_rotate_render_skip_rendering(self, mock_exec):
        """Test rotation without rendering"""
        args = Namespace(
            object_name='Character',
            lower=0,
            upper=180,
            slices=8,
            output_file=None,
            skip_render=True
        )

        cmd = CharacterRotateAndRenderSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['skip_render'] == True

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_rotate_render_object_with_spaces(self, mock_exec):
        """Test object names with spaces"""
        args = Namespace(
            object_name='Genesis 8 Female',
            lower=0,
            upper=180,
            slices=4,
            output_file=None,
            skip_render=False
        )

        cmd = CharacterRotateAndRenderSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['object_name'] == 'Genesis 8 Female'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_rotate_render_negative_angles(self, mock_exec):
        """Test rotation with negative angles"""
        args = Namespace(
            object_name='Object',
            lower=-90,
            upper=90,
            slices=6,
            output_file=None,
            skip_render=False
        )

        cmd = CharacterRotateAndRenderSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['lower'] == -90
        assert call_kwargs['script_vars']['upper'] == 90

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_rotate_render_zero_slices(self, mock_exec):
        """Test rotation with zero slices (render only)"""
        args = Namespace(
            object_name='Object',
            lower=0,
            upper=180,
            slices=0,
            output_file=None,
            skip_render=False
        )

        cmd = CharacterRotateAndRenderSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['slices'] == 0

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_rotate_render_many_slices(self, mock_exec):
        """Test rotation with many slices"""
        args = Namespace(
            object_name='Object',
            lower=0,
            upper=360,
            slices=36,
            output_file='/output',
            skip_render=False
        )

        cmd = CharacterRotateAndRenderSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['slices'] == 36

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_rotate_random_basic(self, mock_exec):
        """Test rotate-random command (minimal args)"""
        args = Namespace(
            object_name='Character',
            lower=0
        )

        cmd = CharacterRotateAndRenderSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['object_name'] == 'Character'
        assert call_kwargs['script_vars']['lower'] == 0

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_rotate_random_custom_start(self, mock_exec):
        """Test rotate-random with custom starting angle"""
        args = Namespace(
            object_name='Prop',
            lower=45
        )

        cmd = CharacterRotateAndRenderSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['lower'] == 45
