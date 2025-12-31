# TEAM_005: Unit tests for GrubKernelParams
"""Tests for the platforms.traditional.grub module."""

import pytest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

from platforms.traditional.grub import GrubKernelParams


SAMPLE_GRUB = '''GRUB_TIMEOUT=5
GRUB_DISTRIBUTOR="$(sed 's, release .*$,,g' /etc/system-release)"
GRUB_DEFAULT=saved
GRUB_DISABLE_SUBMENU=true
GRUB_TERMINAL_OUTPUT="console"
GRUB_CMDLINE_LINUX="rhgb quiet"
GRUB_DISABLE_RECOVERY="true"
'''


class TestGrubKernelParams:
    """Tests for GrubKernelParams class."""
    
    def test_get_current_params(self):
        """Test reading current params from grub config."""
        with patch("builtins.open", mock_open(read_data=SAMPLE_GRUB)):
            with patch.object(Path, "exists", return_value=True):
                grub = GrubKernelParams()
                params = grub.get_current_params()
        
        assert "rhgb" in params
        assert "quiet" in params
        assert len(params) == 2
    
    def test_get_current_params_empty(self):
        """Test reading empty params."""
        grub_empty = '''GRUB_CMDLINE_LINUX=""
'''
        with patch("builtins.open", mock_open(read_data=grub_empty)):
            with patch.object(Path, "exists", return_value=True):
                grub = GrubKernelParams()
                params = grub.get_current_params()
        
        assert params == []
    
    def test_get_current_params_no_file(self):
        """Test handling missing grub config."""
        with patch.object(Path, "exists", return_value=False):
            grub = GrubKernelParams()
            params = grub.get_current_params()
        
        assert params == []
    
    def test_append_deduplicates(self):
        """Test that append deduplicates by param name."""
        with patch.object(GrubKernelParams, "get_current_params", return_value=["rhgb", "quiet", "mitigations=auto"]):
            with patch.object(GrubKernelParams, "_backup_grub_config", return_value=None):
                with patch.object(GrubKernelParams, "_write_grub_config") as mock_write:
                    with patch.object(GrubKernelParams, "_run_grub_mkconfig", return_value=True):
                        grub = GrubKernelParams()
                        result = grub.append_params(["mitigations=off"])
        
        assert result is True
        written_params = mock_write.call_args[0][0]
        assert "mitigations=off" in written_params
        assert "mitigations=auto" not in written_params
        assert "rhgb" in written_params
        assert "quiet" in written_params
    
    def test_remove_params(self):
        """Test removing params."""
        with patch.object(GrubKernelParams, "get_current_params", return_value=["rhgb", "quiet", "mitigations=off"]):
            with patch.object(GrubKernelParams, "_backup_grub_config", return_value=None):
                with patch.object(GrubKernelParams, "_write_grub_config") as mock_write:
                    with patch.object(GrubKernelParams, "_run_grub_mkconfig", return_value=True):
                        grub = GrubKernelParams()
                        result = grub.remove_params(["mitigations"])
        
        assert result is True
        written_params = mock_write.call_args[0][0]
        assert "mitigations=off" not in written_params
        assert "rhgb" in written_params
    
    def test_replace_param(self):
        """Test replacing a param."""
        with patch.object(GrubKernelParams, "get_current_params", return_value=["rhgb", "quiet", "mitigations=auto"]):
            with patch.object(GrubKernelParams, "_backup_grub_config", return_value=None):
                with patch.object(GrubKernelParams, "_write_grub_config") as mock_write:
                    with patch.object(GrubKernelParams, "_run_grub_mkconfig", return_value=True):
                        grub = GrubKernelParams()
                        result = grub.replace_param("mitigations=auto", "mitigations=off")
        
        assert result is True
        written_params = mock_write.call_args[0][0]
        assert "mitigations=off" in written_params
        assert "mitigations=auto" not in written_params
    
    def test_requires_reboot(self):
        """Test that GRUB changes always require reboot."""
        grub = GrubKernelParams()
        assert grub.requires_reboot() is True
    
    def test_get_pending_params(self):
        """Test that pending params returns None for GRUB."""
        grub = GrubKernelParams()
        assert grub.get_pending_params() is None


class TestGrubMkconfig:
    """Tests for grub-mkconfig execution."""
    
    def test_grub2_mkconfig_fedora(self):
        """Test using grub2-mkconfig on Fedora."""
        with patch("shutil.which") as mock_which:
            mock_which.side_effect = lambda x: "/usr/sbin/grub2-mkconfig" if x == "grub2-mkconfig" else None
            with patch.object(Path, "exists", return_value=True):
                with patch("subprocess.run") as mock_run:
                    mock_run.return_value = MagicMock(returncode=0)
                    grub = GrubKernelParams()
                    result = grub._run_grub_mkconfig()
        
        assert result is True
        assert "grub2-mkconfig" in mock_run.call_args[0][0]
    
    def test_update_grub_debian(self):
        """Test using update-grub on Debian."""
        with patch("shutil.which") as mock_which:
            def which_side_effect(x):
                if x == "update-grub":
                    return "/usr/sbin/update-grub"
                return None
            mock_which.side_effect = which_side_effect
            with patch.object(Path, "exists", return_value=True):
                with patch("subprocess.run") as mock_run:
                    mock_run.return_value = MagicMock(returncode=0)
                    grub = GrubKernelParams()
                    result = grub._run_grub_mkconfig()
        
        assert result is True
