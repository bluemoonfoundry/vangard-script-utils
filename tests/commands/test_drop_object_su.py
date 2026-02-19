"""
Tests for DropObjectSU command (drop-object)

Tests object dropping with bounding box collision.
"""
import pytest
from argparse import Namespace
from unittest import mock
from vangard.commands.DropObjectSU import DropObjectSU


class TestDropObjectSU:
    """Test suite for DropObjectSU command"""

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_drop_object_basic(self, mock_exec):
        """Test basic object dropping"""
        args = Namespace(
            source_node='Apple',
            target_node='Table'
        )

        cmd = DropObjectSU(parser=mock.Mock(), config={})
        cmd.process(args)

        # Verify exec_remote_script was called
        mock_exec.assert_called_once()

        # Verify correct arguments
        call_kwargs = mock_exec.call_args.kwargs

        assert call_kwargs['script_name'] == "DropObjectSU.dsa"
        assert call_kwargs['script_vars']['source_node'] == 'Apple'
        assert call_kwargs['script_vars']['target_node'] == 'Table'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_drop_with_node_paths(self, mock_exec):
        """Test dropping objects with hierarchical node paths"""
        args = Namespace(
            source_node='Scene/Props/Apple',
            target_node='Scene/Furniture/Table'
        )

        cmd = DropObjectSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['source_node'] == 'Scene/Props/Apple'
        assert call_kwargs['script_vars']['target_node'] == 'Scene/Furniture/Table'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_drop_with_spaces_in_names(self, mock_exec):
        """Test node names with spaces"""
        args = Namespace(
            source_node='Small Apple',
            target_node='Wooden Table'
        )

        cmd = DropObjectSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['source_node'] == 'Small Apple'
        assert call_kwargs['script_vars']['target_node'] == 'Wooden Table'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_drop_with_special_characters(self, mock_exec):
        """Test node names with special characters"""
        args = Namespace(
            source_node='Object_01-v2',
            target_node='Surface_A-flat'
        )

        cmd = DropObjectSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['source_node'] == 'Object_01-v2'
        assert call_kwargs['script_vars']['target_node'] == 'Surface_A-flat'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_drop_character_onto_prop(self, mock_exec):
        """Test dropping a character onto a prop"""
        args = Namespace(
            source_node='Genesis 8 Female',
            target_node='Chair'
        )

        cmd = DropObjectSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['source_node'] == 'Genesis 8 Female'
        assert call_kwargs['script_vars']['target_node'] == 'Chair'
