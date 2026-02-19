"""
Tests for CreateGroupNodeSU command (create-group)

Tests node grouping functionality.
"""
import pytest
from argparse import Namespace
from unittest import mock
from vangard.commands.CreateGroupNodeSU import CreateGroupNodeSU


class TestCreateGroupNodeSU:
    """Test suite for CreateGroupNodeSU command"""

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_create_basic_group(self, mock_exec):
        """Test creating a basic group"""
        args = Namespace(
            group_name='MyGroup'
        )

        cmd = CreateGroupNodeSU(parser=mock.Mock(), config={})
        cmd.process(args)

        # Verify exec_remote_script was called
        mock_exec.assert_called_once()

        # Verify correct arguments
        call_kwargs = mock_exec.call_args.kwargs

        assert call_kwargs['script_name'] == "CreateGroupNodeSU.dsa"
        assert call_kwargs['script_vars']['group_name'] == 'MyGroup'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_group_name_with_spaces(self, mock_exec):
        """Test group names with spaces"""
        args = Namespace(
            group_name='My Test Group'
        )

        cmd = CreateGroupNodeSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['group_name'] == 'My Test Group'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_group_name_with_special_characters(self, mock_exec):
        """Test group names with special characters"""
        args = Namespace(
            group_name='Group_01-Characters'
        )

        cmd = CreateGroupNodeSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['group_name'] == 'Group_01-Characters'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_hierarchical_group_name(self, mock_exec):
        """Test hierarchical group names"""
        args = Namespace(
            group_name='Characters/Heroes/MainCharacter'
        )

        cmd = CreateGroupNodeSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['group_name'] == 'Characters/Heroes/MainCharacter'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_empty_group_name(self, mock_exec):
        """Test handling of empty group name"""
        args = Namespace(
            group_name=''
        )

        cmd = CreateGroupNodeSU(parser=mock.Mock(), config={})
        cmd.process(args)

        # Should still call the script - validation happens in DSA
        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['group_name'] == ''
