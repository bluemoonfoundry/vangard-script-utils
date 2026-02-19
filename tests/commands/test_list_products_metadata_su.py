"""
Tests for ListProductsMetadataSU command (listproducts)

Tests dumping product metadata to output file.
"""
import pytest
from argparse import Namespace
from unittest import mock
from vangard.commands.ListProductsMetadataSU import ListProductsMetadataSU


class TestListProductsMetadataSU:
    """Test suite for ListProductsMetadataSU command"""

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_list_products_basic(self, mock_exec):
        """Test basic product metadata listing"""
        args = Namespace(
            output_file='/output/products.json'
        )

        cmd = ListProductsMetadataSU(parser=mock.Mock(), config={})
        cmd.process(args)

        # Verify exec_remote_script was called
        mock_exec.assert_called_once()

        # Verify correct arguments
        call_kwargs = mock_exec.call_args.kwargs

        assert call_kwargs['script_name'] == "ListProductsMetadataSU.dsa"
        assert call_kwargs['script_vars']['output_file'] == '/output/products.json'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_list_products_unix_path(self, mock_exec):
        """Test product listing with Unix path"""
        args = Namespace(
            output_file='/var/tmp/daz_products.json'
        )

        cmd = ListProductsMetadataSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['output_file'] == '/var/tmp/daz_products.json'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_list_products_windows_path(self, mock_exec):
        """Test product listing with Windows path"""
        args = Namespace(
            output_file='C:/Temp/products.json'
        )

        cmd = ListProductsMetadataSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['output_file'] == 'C:/Temp/products.json'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_list_products_path_with_spaces(self, mock_exec):
        """Test product listing with path containing spaces"""
        args = Namespace(
            output_file='/path with spaces/product data.json'
        )

        cmd = ListProductsMetadataSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['output_file'] == '/path with spaces/product data.json'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_list_products_different_extensions(self, mock_exec):
        """Test product listing with different file extensions"""
        extensions = ['.json', '.txt', '.csv', '.xml']

        for ext in extensions:
            args = Namespace(
                output_file=f'/output/products{ext}'
            )

            cmd = ListProductsMetadataSU(parser=mock.Mock(), config={})
            cmd.process(args)

            call_kwargs = mock_exec.call_args.kwargs
            assert call_kwargs['script_vars']['output_file'] == f'/output/products{ext}'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_list_products_relative_path(self, mock_exec):
        """Test product listing with relative path"""
        args = Namespace(
            output_file='../data/products.json'
        )

        cmd = ListProductsMetadataSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['output_file'] == '../data/products.json'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_list_products_nested_directory(self, mock_exec):
        """Test product listing with deeply nested directory"""
        args = Namespace(
            output_file='/data/exports/daz/metadata/products/all_products.json'
        )

        cmd = ListProductsMetadataSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['output_file'] == '/data/exports/daz/metadata/products/all_products.json'
