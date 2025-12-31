# TEAM_005: Unit tests for DnfPackageManager
"""Tests for the platforms.traditional.rpm module."""

import pytest
from unittest.mock import patch, MagicMock

from platforms.traditional.rpm import DnfPackageManager


class TestDnfPackageManager:
    """Tests for DnfPackageManager class."""
    
    def test_is_installed_true(self):
        """Test checking an installed package."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            dnf = DnfPackageManager()
            result = dnf.is_installed("python3")
        
        assert result is True
        mock_run.assert_called_once()
        assert "rpm" in mock_run.call_args[0][0]
        assert "-q" in mock_run.call_args[0][0]
    
    def test_is_installed_false(self):
        """Test checking a non-installed package."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            dnf = DnfPackageManager()
            result = dnf.is_installed("nonexistent-package-12345")
        
        assert result is False
    
    def test_install_success(self):
        """Test successful package installation."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            dnf = DnfPackageManager()
            result = dnf.install(["htop", "neofetch"])
        
        assert result is True
        cmd = mock_run.call_args[0][0]
        assert "dnf" in cmd
        assert "install" in cmd
        assert "-y" in cmd
        assert "htop" in cmd
        assert "neofetch" in cmd
    
    def test_install_failure(self):
        """Test failed package installation."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr=b"Error: No package found")
            dnf = DnfPackageManager()
            result = dnf.install(["nonexistent-package"])
        
        assert result is False
    
    def test_install_empty_list(self):
        """Test installing empty package list."""
        dnf = DnfPackageManager()
        result = dnf.install([])
        assert result is True
    
    def test_remove_success(self):
        """Test successful package removal."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            dnf = DnfPackageManager()
            result = dnf.remove(["htop"])
        
        assert result is True
        cmd = mock_run.call_args[0][0]
        assert "dnf" in cmd
        assert "remove" in cmd
    
    def test_update_success(self):
        """Test successful cache update."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            dnf = DnfPackageManager()
            result = dnf.update()
        
        assert result is True
        cmd = mock_run.call_args[0][0]
        assert "dnf" in cmd
        assert "makecache" in cmd
