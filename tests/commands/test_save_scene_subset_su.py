"""
Tests for SaveSceneSubsetSU command (save-subset)

Tests saving scene subsets with optional directory and category.
"""
import pytest
from argparse import Namespace
from unittest import mock
from vangard.commands.SaveSceneSubsetSU import SaveSceneSubsetSU


class TestSaveSceneSubsetSU:
    """Test suite for SaveSceneSubsetSU command"""

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_save_subset_basic(self, mock_exec):
        """Test basic subset save"""
        args = Namespace(
            subset_file='MySubset',
            directory=None,
            category=''
        )

        cmd = SaveSceneSubsetSU(parser=mock.Mock(), config={})
        cmd.process(args)

        # Verify exec_remote_script was called
        mock_exec.assert_called_once()

        # Verify correct arguments
        call_kwargs = mock_exec.call_args.kwargs

        assert call_kwargs['script_name'] == "SaveSceneSubsetSU.dsa"
        assert call_kwargs['script_vars']['subset_file'] == 'MySubset'
        assert call_kwargs['script_vars']['directory'] is None
        assert call_kwargs['script_vars']['category'] == ''

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_save_subset_with_directory(self, mock_exec):
        """Test subset save with custom directory"""
        args = Namespace(
            subset_file='CharacterPreset',
            directory='/custom/presets/directory',
            category=''
        )

        cmd = SaveSceneSubsetSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['directory'] == '/custom/presets/directory'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_save_subset_with_category(self, mock_exec):
        """Test subset save with category"""
        args = Namespace(
            subset_file='Outfit',
            directory=None,
            category='Clothing/Female'
        )

        cmd = SaveSceneSubsetSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['category'] == 'Clothing/Female'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_save_subset_full_specification(self, mock_exec):
        """Test subset save with all arguments"""
        args = Namespace(
            subset_file='FullCharacter',
            directory='/presets/characters',
            category='Characters/Heroes'
        )

        cmd = SaveSceneSubsetSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['subset_file'] == 'FullCharacter'
        assert call_kwargs['script_vars']['directory'] == '/presets/characters'
        assert call_kwargs['script_vars']['category'] == 'Characters/Heroes'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_save_subset_with_spaces(self, mock_exec):
        """Test subset save with spaces in names"""
        args = Namespace(
            subset_file='My Character Preset',
            directory='/path with spaces/presets',
            category='My Category'
        )

        cmd = SaveSceneSubsetSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['subset_file'] == 'My Character Preset'
        assert call_kwargs['script_vars']['directory'] == '/path with spaces/presets'
        assert call_kwargs['script_vars']['category'] == 'My Category'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_save_subset_hierarchical_category(self, mock_exec):
        """Test subset save with hierarchical category"""
        args = Namespace(
            subset_file='Subset',
            directory=None,
            category='Props/Furniture/Modern/Chairs'
        )

        cmd = SaveSceneSubsetSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['category'] == 'Props/Furniture/Modern/Chairs'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_save_subset_windows_path(self, mock_exec):
        """Test subset save with Windows-style path"""
        args = Namespace(
            subset_file='Preset',
            directory='C:/DAZ/Presets/Custom',
            category='Custom'
        )

        cmd = SaveSceneSubsetSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['directory'] == 'C:/DAZ/Presets/Custom'
