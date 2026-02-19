"""
Tests for CopyTransformObjectSU command (transform-copy)

Tests copying transforms (translate/rotate/scale) between objects.
"""
import pytest
from argparse import Namespace
from unittest import mock
from vangard.commands.CopyTransformObjectSU import CopyTransformObjectSU


class TestCopyTransformObjectSU:
    """Test suite for CopyTransformObjectSU command"""

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_copy_all_transforms(self, mock_exec):
        """Test copying all transforms with --all flag"""
        args = Namespace(
            source_node='SourceObject',
            target_node='TargetObject',
            rotate=False,
            translate=False,
            scale=False,
            all=True
        )

        cmd = CopyTransformObjectSU(parser=mock.Mock(), config={})
        cmd.process(args)

        # Verify exec_remote_script was called
        mock_exec.assert_called_once()

        # Verify correct arguments
        call_kwargs = mock_exec.call_args.kwargs

        assert call_kwargs['script_name'] == "CopyTransformObjectSU.dsa"
        assert call_kwargs['script_vars']['source_node'] == 'SourceObject'
        assert call_kwargs['script_vars']['target_node'] == 'TargetObject'
        assert call_kwargs['script_vars']['all'] == True

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_copy_rotation_only(self, mock_exec):
        """Test copying only rotation"""
        args = Namespace(
            source_node='SourceObject',
            target_node='TargetObject',
            rotate=True,
            translate=False,
            scale=False,
            all=False
        )

        cmd = CopyTransformObjectSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['rotate'] == True
        assert call_kwargs['script_vars']['translate'] == False
        assert call_kwargs['script_vars']['scale'] == False
        assert call_kwargs['script_vars']['all'] == False

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_copy_translation_only(self, mock_exec):
        """Test copying only translation"""
        args = Namespace(
            source_node='SourceObject',
            target_node='TargetObject',
            rotate=False,
            translate=True,
            scale=False,
            all=False
        )

        cmd = CopyTransformObjectSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['translate'] == True
        assert call_kwargs['script_vars']['rotate'] == False

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_copy_scale_only(self, mock_exec):
        """Test copying only scale"""
        args = Namespace(
            source_node='SourceObject',
            target_node='TargetObject',
            rotate=False,
            translate=False,
            scale=True,
            all=False
        )

        cmd = CopyTransformObjectSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['scale'] == True

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_copy_rotation_and_translation(self, mock_exec):
        """Test copying rotation and translation together"""
        args = Namespace(
            source_node='SourceObject',
            target_node='TargetObject',
            rotate=True,
            translate=True,
            scale=False,
            all=False
        )

        cmd = CopyTransformObjectSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['rotate'] == True
        assert call_kwargs['script_vars']['translate'] == True
        assert call_kwargs['script_vars']['scale'] == False

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_no_transforms_selected(self, mock_exec):
        """Test when no transform flags are set"""
        args = Namespace(
            source_node='SourceObject',
            target_node='TargetObject',
            rotate=False,
            translate=False,
            scale=False,
            all=False
        )

        cmd = CopyTransformObjectSU(parser=mock.Mock(), config={})
        cmd.process(args)

        # Should still call script - validation happens in DSA
        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['rotate'] == False
        assert call_kwargs['script_vars']['translate'] == False
        assert call_kwargs['script_vars']['scale'] == False

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_nodes_with_spaces(self, mock_exec):
        """Test node names with spaces"""
        args = Namespace(
            source_node='Source Object Name',
            target_node='Target Object Name',
            rotate=True,
            translate=False,
            scale=False,
            all=False
        )

        cmd = CopyTransformObjectSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['source_node'] == 'Source Object Name'
        assert call_kwargs['script_vars']['target_node'] == 'Target Object Name'
