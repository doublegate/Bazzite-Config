# TEAM_005: Unit tests for PlatformServices factory
"""Tests for the platforms.services module."""

import pytest
from unittest.mock import patch, MagicMock

from platforms import PlatformType, PlatformInfo, PlatformServices, UnsupportedPlatformError


def make_platform_info(platform_type, pkg_mgr, boot_method):
    """Helper to create PlatformInfo for tests."""
    return PlatformInfo(
        platform_type=platform_type,
        distro_name="Test Distro",
        distro_version="1.0",
        is_immutable=platform_type in (PlatformType.BAZZITE, PlatformType.FEDORA_OSTREE),
        has_ujust=platform_type == PlatformType.BAZZITE,
        package_manager=pkg_mgr,
        boot_method=boot_method
    )


class TestPlatformServices:
    """Tests for PlatformServices factory."""
    
    def test_fedora_traditional_returns_dnf(self):
        """Test that Fedora traditional gets DnfPackageManager."""
        info = make_platform_info(PlatformType.FEDORA_TRADITIONAL, "dnf", "grub")
        services = PlatformServices(info)
        
        assert "Dnf" in type(services.package_manager).__name__
    
    def test_fedora_traditional_returns_grub(self):
        """Test that Fedora traditional gets GrubKernelParams."""
        info = make_platform_info(PlatformType.FEDORA_TRADITIONAL, "dnf", "grub")
        services = PlatformServices(info)
        
        assert "Grub" in type(services.kernel_params).__name__
    
    def test_bazzite_returns_rpm_ostree_package_manager(self):
        """Test that Bazzite gets RpmOstreePackageManager."""
        info = make_platform_info(PlatformType.BAZZITE, "rpm-ostree", "rpm-ostree-kargs")
        services = PlatformServices(info)
        
        assert "RpmOstree" in type(services.package_manager).__name__
    
    def test_bazzite_returns_rpm_ostree_kernel_params(self):
        """Test that Bazzite gets RpmOstreeKernelParams."""
        info = make_platform_info(PlatformType.BAZZITE, "rpm-ostree", "rpm-ostree-kargs")
        services = PlatformServices(info)
        
        assert "RpmOstree" in type(services.kernel_params).__name__
    
    def test_silverblue_returns_rpm_ostree(self):
        """Test that Silverblue gets rpm-ostree implementations."""
        info = make_platform_info(PlatformType.FEDORA_OSTREE, "rpm-ostree", "rpm-ostree-kargs")
        services = PlatformServices(info)
        
        assert "RpmOstree" in type(services.package_manager).__name__
        assert "RpmOstree" in type(services.kernel_params).__name__
    
    def test_unsupported_package_manager_raises(self):
        """Test that unsupported package manager raises error."""
        info = make_platform_info(PlatformType.DEBIAN_BASED, "apt", "grub")
        services = PlatformServices(info)
        
        with pytest.raises(UnsupportedPlatformError):
            _ = services.package_manager
    
    def test_unsupported_boot_method_raises(self):
        """Test that unsupported boot method raises error."""
        info = make_platform_info(PlatformType.UNKNOWN, "dnf", "systemd-boot")
        services = PlatformServices(info)
        
        with pytest.raises(UnsupportedPlatformError):
            _ = services.kernel_params
    
    def test_lazy_loading(self):
        """Test that implementations are lazily loaded."""
        info = make_platform_info(PlatformType.FEDORA_TRADITIONAL, "dnf", "grub")
        services = PlatformServices(info)
        
        # Before access, should be None
        assert services._package_manager is None
        assert services._kernel_params is None
        
        # After access, should be cached
        _ = services.package_manager
        _ = services.kernel_params
        
        assert services._package_manager is not None
        assert services._kernel_params is not None
    
    def test_is_immutable_property(self):
        """Test is_immutable property."""
        info_immutable = make_platform_info(PlatformType.BAZZITE, "rpm-ostree", "rpm-ostree-kargs")
        info_traditional = make_platform_info(PlatformType.FEDORA_TRADITIONAL, "dnf", "grub")
        
        assert PlatformServices(info_immutable).is_immutable is True
        assert PlatformServices(info_traditional).is_immutable is False
    
    def test_has_ujust_property(self):
        """Test has_ujust property."""
        info_bazzite = make_platform_info(PlatformType.BAZZITE, "rpm-ostree", "rpm-ostree-kargs")
        info_silverblue = make_platform_info(PlatformType.FEDORA_OSTREE, "rpm-ostree", "rpm-ostree-kargs")
        
        assert PlatformServices(info_bazzite).has_ujust is True
        assert PlatformServices(info_silverblue).has_ujust is False
    
    def test_platform_type_property(self):
        """Test platform_type property."""
        info = make_platform_info(PlatformType.FEDORA_TRADITIONAL, "dnf", "grub")
        services = PlatformServices(info)
        
        assert services.platform_type == PlatformType.FEDORA_TRADITIONAL
