"""
Tests for SceneRollerSU command (inc-scene)

Tests incremental scene file saving with numeric suffixes.
"""
import pytest
from argparse import Namespace
from unittest import mock
from vangard.commands.SceneRollerSU import SceneRollerSU


class TestSceneRollerSU:
    """Test suite for SceneRollerSU command"""

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_increment_without_options(self, mock_exec):
        """Test basic increment without specifying number or increment"""
        args = Namespace(
            number=None,
            increment=1
        )

        cmd = SceneRollerSU(parser=mock.Mock(), config={})
        cmd.process(args)

        # Verify exec_remote_script was called
        mock_exec.assert_called_once()

        # Verify correct arguments
        call_kwargs = mock_exec.call_args.kwargs

        assert call_kwargs['script_name'] == "SceneRollerSU.dsa"
        assert call_kwargs['script_vars']['number'] is None
        assert call_kwargs['script_vars']['increment'] == 1

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_set_specific_number(self, mock_exec):
        """Test setting a specific number suffix"""
        args = Namespace(
            number=42,
            increment=1
        )

        cmd = SceneRollerSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['number'] == 42

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_custom_increment_value(self, mock_exec):
        """Test using a custom increment value"""
        args = Namespace(
            number=None,
            increment=5
        )

        cmd = SceneRollerSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['increment'] == 5

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_number_and_increment_together(self, mock_exec):
        """Test setting both number and increment"""
        args = Namespace(
            number=100,
            increment=10
        )

        cmd = SceneRollerSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['number'] == 100
        assert call_kwargs['script_vars']['increment'] == 10

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_increment_by_zero(self, mock_exec):
        """Test increment value of zero"""
        args = Namespace(
            number=None,
            increment=0
        )

        cmd = SceneRollerSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['increment'] == 0

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_negative_increment(self, mock_exec):
        """Test negative increment value (decrement)"""
        args = Namespace(
            number=None,
            increment=-1
        )

        cmd = SceneRollerSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['increment'] == -1

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_large_number_value(self, mock_exec):
        """Test large number values"""
        args = Namespace(
            number=9999,
            increment=1
        )

        cmd = SceneRollerSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['number'] == 9999
