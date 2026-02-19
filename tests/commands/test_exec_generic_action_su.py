"""
Tests for ExecGenericActionSU command (action)

Tests executing generic actions with optional settings.
"""
import pytest
from argparse import Namespace
from unittest import mock
from vangard.commands.ExecGenericActionSU import ExecGenericActionSU


class TestExecGenericActionSU:
    """Test suite for ExecGenericActionSU command"""

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_action_basic(self, mock_exec):
        """Test basic action execution without settings"""
        args = Namespace(
            action_class='DzFileExportAction',
            settings=None
        )

        cmd = ExecGenericActionSU(parser=mock.Mock(), config={})
        cmd.process(args)

        # Verify exec_remote_script was called
        mock_exec.assert_called_once()

        # Verify correct arguments
        call_kwargs = mock_exec.call_args.kwargs

        assert call_kwargs['script_name'] == "ExecGenericActionSU.dsa"
        assert call_kwargs['script_vars']['action_class'] == 'DzFileExportAction'
        assert call_kwargs['script_vars']['settings'] is None

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_action_with_single_setting(self, mock_exec):
        """Test action with single setting"""
        args = Namespace(
            action_class='DzRenderAction',
            settings='quality=high'
        )

        cmd = ExecGenericActionSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['settings'] == 'quality=high'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_action_with_multiple_settings(self, mock_exec):
        """Test action with multiple settings"""
        args = Namespace(
            action_class='DzExportAction',
            settings='format=obj,scale=1.0,units=meters'
        )

        cmd = ExecGenericActionSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['settings'] == 'format=obj,scale=1.0,units=meters'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_action_different_classes(self, mock_exec):
        """Test different action classes"""
        action_classes = [
            'DzFileExportAction',
            'DzRenderAction',
            'DzScriptAction',
            'DzCustomAction'
        ]

        for action_class in action_classes:
            args = Namespace(
                action_class=action_class,
                settings=None
            )

            cmd = ExecGenericActionSU(parser=mock.Mock(), config={})
            cmd.process(args)

            call_kwargs = mock_exec.call_args.kwargs
            assert call_kwargs['script_vars']['action_class'] == action_class

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_action_with_boolean_settings(self, mock_exec):
        """Test action with boolean settings"""
        args = Namespace(
            action_class='DzAction',
            settings='enabled=true,visible=false,locked=true'
        )

        cmd = ExecGenericActionSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['settings'] == 'enabled=true,visible=false,locked=true'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_action_with_numeric_settings(self, mock_exec):
        """Test action with numeric settings"""
        args = Namespace(
            action_class='DzRenderAction',
            settings='width=1920,height=1080,samples=100'
        )

        cmd = ExecGenericActionSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['settings'] == 'width=1920,height=1080,samples=100'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_action_with_path_settings(self, mock_exec):
        """Test action with file path settings"""
        args = Namespace(
            action_class='DzExportAction',
            settings='output=/path/to/file.obj,texture_path=/textures'
        )

        cmd = ExecGenericActionSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['settings'] == 'output=/path/to/file.obj,texture_path=/textures'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_action_with_empty_settings(self, mock_exec):
        """Test action with empty settings string"""
        args = Namespace(
            action_class='DzAction',
            settings=''
        )

        cmd = ExecGenericActionSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['settings'] == ''

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_action_with_special_characters(self, mock_exec):
        """Test action class names with special characters"""
        args = Namespace(
            action_class='Dz::Custom::Action_v2',
            settings='param=value'
        )

        cmd = ExecGenericActionSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['action_class'] == 'Dz::Custom::Action_v2'
