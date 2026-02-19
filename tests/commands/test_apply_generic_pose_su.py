"""
Tests for ApplyGenericPoseSU command (apply-pose)

Tests pose application to characters.
"""
import pytest
from argparse import Namespace
from unittest import mock
from vangard.commands.ApplyGenericPoseSU import ApplyGenericPoseSU


class TestApplyGenericPoseSU:
    """Test suite for ApplyGenericPoseSU command"""

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_apply_pose_to_selected(self, mock_exec):
        """Test applying pose to currently selected node"""
        args = Namespace(
            pose_file='/path/to/pose.duf',
            target_node=None
        )

        cmd = ApplyGenericPoseSU(parser=mock.Mock(), config={})
        cmd.process(args)

        # Verify exec_remote_script was called
        mock_exec.assert_called_once()

        # Verify correct arguments
        call_kwargs = mock_exec.call_args.kwargs

        assert call_kwargs['script_name'] == "ApplyGenericPoseSU.dsa"
        assert call_kwargs['script_vars']['pose_file'] == '/path/to/pose.duf'
        assert call_kwargs['script_vars']['target_node'] is None

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_apply_pose_to_specific_node(self, mock_exec):
        """Test applying pose to a specific target node"""
        args = Namespace(
            pose_file='/path/to/pose.duf',
            target_node='Genesis 8 Female'
        )

        cmd = ApplyGenericPoseSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['pose_file'] == '/path/to/pose.duf'
        assert call_kwargs['script_vars']['target_node'] == 'Genesis 8 Female'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_pose_file_with_spaces(self, mock_exec):
        """Test pose file paths with spaces"""
        args = Namespace(
            pose_file='/path with spaces/my pose file.duf',
            target_node=None
        )

        cmd = ApplyGenericPoseSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['pose_file'] == '/path with spaces/my pose file.duf'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_windows_pose_file_path(self, mock_exec):
        """Test Windows-style pose file paths"""
        args = Namespace(
            pose_file='C:/Users/Test/Documents/Poses/standing.duf',
            target_node='Character'
        )

        cmd = ApplyGenericPoseSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['pose_file'] == 'C:/Users/Test/Documents/Poses/standing.duf'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_target_node_with_hierarchy(self, mock_exec):
        """Test target node with hierarchical path"""
        args = Namespace(
            pose_file='/path/to/pose.duf',
            target_node='Scene/Characters/Genesis 8 Female'
        )

        cmd = ApplyGenericPoseSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['target_node'] == 'Scene/Characters/Genesis 8 Female'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_different_pose_file_formats(self, mock_exec):
        """Test different pose file formats/extensions"""
        pose_files = [
            '/path/to/pose.duf',
            '/path/to/pose.dsf',
            '/path/to/pose.daz'
        ]

        for pose_file in pose_files:
            args = Namespace(
                pose_file=pose_file,
                target_node=None
            )

            cmd = ApplyGenericPoseSU(parser=mock.Mock(), config={})
            cmd.process(args)

            call_kwargs = mock_exec.call_args.kwargs
            assert call_kwargs['script_vars']['pose_file'] == pose_file
