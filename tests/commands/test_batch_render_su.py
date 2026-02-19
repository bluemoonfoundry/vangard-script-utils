"""
Tests for BatchRenderSU command (batch-render)

Tests batch rendering with complex argument combinations.
"""
import pytest
from argparse import Namespace
from unittest import mock
from vangard.commands.BatchRenderSU import BatchRenderSU


class TestBatchRenderSU:
    """Test suite for BatchRenderSU command"""

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_batch_render_minimal(self, mock_exec):
        """Test batch render with minimal arguments"""
        args = Namespace(
            scene_files='/path/to/scenes/*.duf',
            output_path=None,
            target='direct-file',
            resolution=None,
            cameras=None,
            job_name_pattern=None,
            frames=None,
            iray_server='127.0.0.1',
            iray_protocol='http',
            iray_port='9090',
            iray_user=None,
            iray_password=None,
            iray_config_file=None
        )

        cmd = BatchRenderSU(parser=mock.Mock(), config={})
        cmd.process(args)

        # Verify exec_remote_script was called
        mock_exec.assert_called_once()

        # Verify correct arguments
        call_kwargs = mock_exec.call_args.kwargs

        assert call_kwargs['script_name'] == "BatchRenderSU.dsa"
        # BatchRenderSU converts scene_files to a dict with glob results
        assert isinstance(call_kwargs['script_vars']['scene_files'], dict)
        assert 'scene_files' in call_kwargs['script_vars']['scene_files']
        assert call_kwargs['script_vars']['target'] == 'direct-file'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_batch_render_with_output_path(self, mock_exec):
        """Test batch render with custom output path"""
        args = Namespace(
            scene_files='/scenes/*.duf',
            output_path='/renders/output',
            target='direct-file',
            resolution=None,
            cameras=None,
            job_name_pattern=None,
            frames=None,
            iray_server='127.0.0.1',
            iray_protocol='http',
            iray_port='9090',
            iray_user=None,
            iray_password=None,
            iray_config_file=None
        )

        cmd = BatchRenderSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['output_path'] == '/renders/output'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_batch_render_with_resolution(self, mock_exec):
        """Test batch render with custom resolution"""
        args = Namespace(
            scene_files='*.duf',
            output_path=None,
            target='direct-file',
            resolution='1920x1080',
            cameras=None,
            job_name_pattern=None,
            frames=None,
            iray_server='127.0.0.1',
            iray_protocol='http',
            iray_port='9090',
            iray_user=None,
            iray_password=None,
            iray_config_file=None
        )

        cmd = BatchRenderSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['resolution'] == '1920x1080'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_batch_render_all_visible_cameras(self, mock_exec):
        """Test batch render with all visible cameras"""
        args = Namespace(
            scene_files='*.duf',
            output_path=None,
            target='direct-file',
            resolution=None,
            cameras='all_visible',
            job_name_pattern=None,
            frames=None,
            iray_server='127.0.0.1',
            iray_protocol='http',
            iray_port='9090',
            iray_user=None,
            iray_password=None,
            iray_config_file=None
        )

        cmd = BatchRenderSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['cameras'] == 'all_visible'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_batch_render_with_job_pattern(self, mock_exec):
        """Test batch render with job name pattern"""
        args = Namespace(
            scene_files='*.duf',
            output_path=None,
            target='direct-file',
            resolution=None,
            cameras=None,
            job_name_pattern='%s_%c_%f',
            frames=None,
            iray_server='127.0.0.1',
            iray_protocol='http',
            iray_port='9090',
            iray_user=None,
            iray_password=None,
            iray_config_file=None
        )

        cmd = BatchRenderSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['job_name_pattern'] == '%s_%c_%f'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_batch_render_with_frames(self, mock_exec):
        """Test batch render with frame specification"""
        args = Namespace(
            scene_files='*.duf',
            output_path=None,
            target='direct-file',
            resolution=None,
            cameras=None,
            job_name_pattern=None,
            frames='1,5,10-20',
            iray_server='127.0.0.1',
            iray_protocol='http',
            iray_port='9090',
            iray_user=None,
            iray_password=None,
            iray_config_file=None
        )

        cmd = BatchRenderSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['frames'] == '1,5,10-20'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_batch_render_iray_server_mode(self, mock_exec):
        """Test batch render with iRay server configuration"""
        args = Namespace(
            scene_files='*.duf',
            output_path=None,
            target='iray-server-bridge',
            resolution=None,
            cameras=None,
            job_name_pattern=None,
            frames=None,
            iray_server='192.168.1.100',
            iray_protocol='https',
            iray_port='9091',
            iray_user='admin',
            iray_password='password123',
            iray_config_file=None
        )

        cmd = BatchRenderSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['target'] == 'iray-server-bridge'
        assert call_kwargs['script_vars']['iray_server'] == '192.168.1.100'
        assert call_kwargs['script_vars']['iray_protocol'] == 'https'
        assert call_kwargs['script_vars']['iray_port'] == '9091'
        assert call_kwargs['script_vars']['iray_user'] == 'admin'
        assert call_kwargs['script_vars']['iray_password'] == 'password123'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_batch_render_with_config_file(self, mock_exec):
        """Test batch render with iRay config file"""
        args = Namespace(
            scene_files='*.duf',
            output_path=None,
            target='iray-server-bridge',
            resolution=None,
            cameras=None,
            job_name_pattern=None,
            frames=None,
            iray_server='127.0.0.1',
            iray_protocol='http',
            iray_port='9090',
            iray_user=None,
            iray_password=None,
            iray_config_file='/path/to/iray_config.yaml'
        )

        cmd = BatchRenderSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['script_vars']['iray_config_file'] == '/path/to/iray_config.yaml'

    @mock.patch('vangard.commands.BaseCommand.BaseCommand.exec_remote_script')
    def test_batch_render_full_configuration(self, mock_exec):
        """Test batch render with all arguments specified"""
        args = Namespace(
            scene_files='/scenes/**/*.duf',
            output_path='/renders',
            target='direct-file',
            resolution='3840x2160',
            cameras='Camera*',
            job_name_pattern='render_%s_%c',
            frames='1-100',
            iray_server='192.168.1.100',
            iray_protocol='https',
            iray_port='9091',
            iray_user='render_user',
            iray_password='secure_pass',
            iray_config_file='/config/iray.yaml'
        )

        cmd = BatchRenderSU(parser=mock.Mock(), config={})
        cmd.process(args)

        call_kwargs = mock_exec.call_args.kwargs

        # Verify all arguments are passed correctly
        # BatchRenderSU converts scene_files to a dict with glob results
        assert isinstance(call_kwargs['script_vars']['scene_files'], dict)
        assert 'scene_files' in call_kwargs['script_vars']['scene_files']
        assert call_kwargs['script_vars']['output_path'] == '/renders'
        assert call_kwargs['script_vars']['target'] == 'direct-file'
        assert call_kwargs['script_vars']['resolution'] == '3840x2160'
        assert call_kwargs['script_vars']['cameras'] == 'Camera*'
        assert call_kwargs['script_vars']['job_name_pattern'] == 'render_%s_%c'
        assert call_kwargs['script_vars']['frames'] == '1-100'
        assert call_kwargs['script_vars']['iray_server'] == '192.168.1.100'
        assert call_kwargs['script_vars']['iray_protocol'] == 'https'
        assert call_kwargs['script_vars']['iray_port'] == '9091'
        assert call_kwargs['script_vars']['iray_user'] == 'render_user'
        assert call_kwargs['script_vars']['iray_password'] == 'secure_pass'
        assert call_kwargs['script_vars']['iray_config_file'] == '/config/iray.yaml'
