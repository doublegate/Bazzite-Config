# TEAM_005: Unit tests for platform detection
"""Tests for the platforms.detection module."""

import pytest
from unittest.mock import patch, mock_open, MagicMock

from platforms.detection import (
    PlatformType,
    PlatformInfo,
    detect_platform,
    _parse_os_release,
    _check_rpm_ostree_deployment,
    _detect_boot_method,
)


class TestParseOsRelease:
    """Tests for _parse_os_release()."""
    
    def test_parse_fedora(self):
        os_release = '''NAME="Fedora Linux"
VERSION_ID="40"
ID=fedora
VARIANT_ID=workstation
'''
        with patch("builtins.open", mock_open(read_data=os_release)):
            with patch("pathlib.Path.exists", return_value=True):
                result = _parse_os_release()
        
        assert result["NAME"] == "Fedora Linux"
        assert result["VERSION_ID"] == "40"
        assert result["ID"] == "fedora"
        assert result["VARIANT_ID"] == "workstation"
    
    def test_parse_ultramarine(self):
        os_release = '''NAME="Ultramarine Linux"
VERSION_ID="40"
ID=ultramarine
'''
        with patch("builtins.open", mock_open(read_data=os_release)):
            with patch("pathlib.Path.exists", return_value=True):
                result = _parse_os_release()
        
        assert result["NAME"] == "Ultramarine Linux"
        assert result["ID"] == "ultramarine"
    
    def test_parse_bazzite(self):
        os_release = '''NAME="Bazzite"
VERSION_ID="40"
ID=bazzite
VARIANT_ID=bazzite
'''
        with patch("builtins.open", mock_open(read_data=os_release)):
            with patch("pathlib.Path.exists", return_value=True):
                result = _parse_os_release()
        
        assert result["ID"] == "bazzite"
    
    def test_missing_file(self):
        with patch("pathlib.Path.exists", return_value=False):
            result = _parse_os_release()
        assert result == {}


class TestCheckRpmOstreeDeployment:
    """Tests for _check_rpm_ostree_deployment()."""
    
    def test_rpm_ostree_present(self):
        with patch("shutil.which", return_value="/usr/bin/rpm-ostree"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout=b'{"deployments": []}'
                )
                result = _check_rpm_ostree_deployment()
        assert result is True
    
    def test_rpm_ostree_not_installed(self):
        with patch("shutil.which", return_value=None):
            result = _check_rpm_ostree_deployment()
        assert result is False
    
    def test_rpm_ostree_no_deployment(self):
        with patch("shutil.which", return_value="/usr/bin/rpm-ostree"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=1,
                    stdout=b''
                )
                result = _check_rpm_ostree_deployment()
        assert result is False


class TestDetectBootMethod:
    """Tests for _detect_boot_method()."""
    
    def test_immutable_system(self):
        result = _detect_boot_method(is_immutable=True)
        assert result == "rpm-ostree-kargs"
    
    def test_grub_system(self):
        with patch("pathlib.Path.exists", return_value=True):
            result = _detect_boot_method(is_immutable=False)
        assert result == "grub"


class TestDetectPlatform:
    """Tests for detect_platform()."""
    
    def test_detect_fedora_traditional(self):
        os_release = '''NAME="Fedora Linux"
VERSION_ID="40"
ID=fedora
'''
        with patch("platforms.detection._parse_os_release") as mock_parse:
            mock_parse.return_value = {
                "NAME": "Fedora Linux",
                "VERSION_ID": "40",
                "ID": "fedora",
            }
            with patch("platforms.detection._check_rpm_ostree_deployment", return_value=False):
                with patch("shutil.which", return_value=None):  # No ujust
                    with patch("pathlib.Path.exists", return_value=True):  # Has grub
                        info = detect_platform()
        
        assert info.platform_type == PlatformType.FEDORA_TRADITIONAL
        assert info.distro_name == "Fedora Linux"
        assert info.is_immutable is False
        assert info.package_manager == "dnf"
        assert info.boot_method == "grub"
    
    def test_detect_ultramarine(self):
        with patch("platforms.detection._parse_os_release") as mock_parse:
            mock_parse.return_value = {
                "NAME": "Ultramarine Linux",
                "VERSION_ID": "40",
                "ID": "ultramarine",
            }
            with patch("platforms.detection._check_rpm_ostree_deployment", return_value=False):
                with patch("shutil.which", return_value=None):
                    with patch("pathlib.Path.exists", return_value=True):
                        info = detect_platform()
        
        assert info.platform_type == PlatformType.FEDORA_TRADITIONAL
        assert info.distro_name == "Ultramarine Linux"
        assert info.package_manager == "dnf"
    
    def test_detect_bazzite(self):
        with patch("platforms.detection._parse_os_release") as mock_parse:
            mock_parse.return_value = {
                "NAME": "Bazzite",
                "VERSION_ID": "40",
                "ID": "bazzite",
                "VARIANT_ID": "bazzite",
            }
            with patch("platforms.detection._check_rpm_ostree_deployment", return_value=True):
                with patch("shutil.which", return_value="/usr/bin/ujust"):  # Has ujust
                    info = detect_platform()
        
        assert info.platform_type == PlatformType.BAZZITE
        assert info.is_immutable is True
        assert info.has_ujust is True
        assert info.package_manager == "rpm-ostree"
        assert info.boot_method == "rpm-ostree-kargs"
    
    def test_detect_silverblue(self):
        with patch("platforms.detection._parse_os_release") as mock_parse:
            mock_parse.return_value = {
                "NAME": "Fedora Linux",
                "VERSION_ID": "40",
                "ID": "fedora",
                "VARIANT_ID": "silverblue",
            }
            with patch("platforms.detection._check_rpm_ostree_deployment", return_value=True):
                with patch("shutil.which", return_value=None):  # No ujust
                    info = detect_platform()
        
        assert info.platform_type == PlatformType.FEDORA_OSTREE
        assert info.is_immutable is True
        assert info.has_ujust is False
        assert info.package_manager == "rpm-ostree"
