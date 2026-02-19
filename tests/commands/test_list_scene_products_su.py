"""
Tests for ListSceneProductsSU command (product-list)

Tests listing product information for scene objects.
"""
import pytest
from argparse import Namespace
from unittest import mock
from vangard.commands.ListSceneProductsSU import ListSceneProductsSU


class TestListSceneProductsSU:
    """Test suite for ListSceneProductsSU command"""

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    @mock.patch('vangard.commands.ListSceneProductsSU.ListSceneProductsSU.process_product_list')
    @mock.patch('vangard.commands.ListSceneProductsSU.ListSceneProductsSU.process_product_list_reset')
    def test_product_list_defaults(self, mock_reset, mock_process_list, mock_exec):
        """Test product list with default arguments"""
        args = Namespace(
            target_file='C:/Temp/products.json',
            node_context=False,
            selected_only=False
        )

        cmd = ListSceneProductsSU(parser=mock.Mock(), config={})
        cmd.process(args)

        # Verify exec_remote_script was called
        mock_exec.assert_called_once()

        # Verify correct arguments
        call_kwargs = mock_exec.call_args.kwargs

        assert call_kwargs['script_name'] == "ListSceneProductsSU.dsa"
        assert call_kwargs['script_vars']['target_file'] == 'C:/Temp/products.json'
        assert call_kwargs['script_vars']['node_context'] == False
        assert call_kwargs['script_vars']['selected_only'] == False

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    @mock.patch('vangard.commands.ListSceneProductsSU.ListSceneProductsSU.process_product_list')
    @mock.patch('vangard.commands.ListSceneProductsSU.ListSceneProductsSU.process_product_list_reset')
    def test_product_list_with_custom_file(self, mock_reset, mock_process_list, mock_exec):
        """Test product list with custom output file"""
        args = Namespace(
            target_file='/custom/path/products.json',
            node_context=False,
            selected_only=False
        )

        cmd = ListSceneProductsSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['target_file'] == '/custom/path/products.json'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    @mock.patch('vangard.commands.ListSceneProductsSU.ListSceneProductsSU.process_product_list')
    @mock.patch('vangard.commands.ListSceneProductsSU.ListSceneProductsSU.process_product_list_reset')
    def test_product_list_node_context(self, mock_reset, mock_process_list, mock_exec):
        """Test product list with node context enabled"""
        args = Namespace(
            target_file='C:/Temp/products.json',
            node_context=True,
            selected_only=False
        )

        cmd = ListSceneProductsSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['node_context'] == True

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    @mock.patch('vangard.commands.ListSceneProductsSU.ListSceneProductsSU.process_product_list')
    @mock.patch('vangard.commands.ListSceneProductsSU.ListSceneProductsSU.process_product_list_reset')
    def test_product_list_selected_only(self, mock_reset, mock_process_list, mock_exec):
        """Test product list for selected nodes only"""
        args = Namespace(
            target_file='C:/Temp/products.json',
            node_context=False,
            selected_only=True
        )

        cmd = ListSceneProductsSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['selected_only'] == True

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    @mock.patch('vangard.commands.ListSceneProductsSU.ListSceneProductsSU.process_product_list')
    @mock.patch('vangard.commands.ListSceneProductsSU.ListSceneProductsSU.process_product_list_reset')
    def test_product_list_all_flags(self, mock_reset, mock_process_list, mock_exec):
        """Test product list with all flags enabled"""
        args = Namespace(
            target_file='/output/scene_products.json',
            node_context=True,
            selected_only=True
        )

        cmd = ListSceneProductsSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['target_file'] == '/output/scene_products.json'
        assert call_kwargs['script_vars']['node_context'] == True
        assert call_kwargs['script_vars']['selected_only'] == True

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    @mock.patch('vangard.commands.ListSceneProductsSU.ListSceneProductsSU.process_product_list')
    @mock.patch('vangard.commands.ListSceneProductsSU.ListSceneProductsSU.process_product_list_reset')
    def test_product_list_unix_path(self, mock_reset, mock_process_list, mock_exec):
        """Test product list with Unix-style path"""
        args = Namespace(
            target_file='/var/tmp/products.json',
            node_context=False,
            selected_only=False
        )

        cmd = ListSceneProductsSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['target_file'] == '/var/tmp/products.json'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    @mock.patch('vangard.commands.ListSceneProductsSU.ListSceneProductsSU.process_product_list')
    @mock.patch('vangard.commands.ListSceneProductsSU.ListSceneProductsSU.process_product_list_reset')
    def test_product_list_path_with_spaces(self, mock_reset, mock_process_list, mock_exec):
        """Test product list with path containing spaces"""
        args = Namespace(
            target_file='/path with spaces/my products.json',
            node_context=False,
            selected_only=False
        )

        cmd = ListSceneProductsSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['target_file'] == '/path with spaces/my products.json'
