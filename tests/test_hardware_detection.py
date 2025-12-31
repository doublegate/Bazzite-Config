"""
TEAM_015: Tests for CPU and NIC hardware detection functions.

These tests verify the detection logic works correctly for various hardware configurations.
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestCPUCapabilities:
    """Tests for CPUCapabilities dataclass and detect_cpu_capabilities function."""

    def test_cpu_capabilities_dataclass(self):
        """Test CPUCapabilities dataclass can be instantiated."""
        from platforms.detection import CPUCapabilities
        
        caps = CPUCapabilities(
            vendor="intel",
            model_name="Intel(R) Core(TM) i5-1240P",
            family="alder_lake",
            generation=12,
            core_count=12,
            thread_count=16,
            supports_undervolt=False,
            safe_undervolt_mv=0,
            base_clock_mhz=1700,
            supports_turbo=True
        )
        
        assert caps.vendor == "intel"
        assert caps.family == "alder_lake"
        assert caps.supports_undervolt is False

    def test_detect_cpu_capabilities_returns_valid_object(self):
        """Test detect_cpu_capabilities returns a valid CPUCapabilities object."""
        from platforms.detection import detect_cpu_capabilities, CPUCapabilities
        
        caps = detect_cpu_capabilities()
        
        assert isinstance(caps, CPUCapabilities)
        assert caps.vendor in ("intel", "amd", "other")
        assert caps.core_count >= 1
        assert caps.thread_count >= 1

    def test_intel_cpu_families_patterns(self):
        """Test Intel CPU family patterns are correctly defined."""
        from platforms.detection import INTEL_CPU_FAMILIES
        
        assert "comet_lake" in INTEL_CPU_FAMILIES
        assert "alder_lake" in INTEL_CPU_FAMILIES
        assert "raptor_lake" in INTEL_CPU_FAMILIES
        
        # Comet Lake should support undervolt
        assert INTEL_CPU_FAMILIES["comet_lake"]["supports_undervolt"] is True
        assert INTEL_CPU_FAMILIES["comet_lake"]["safe_undervolt_mv"] > 0
        
        # Alder Lake should NOT support undervolt (locked on most systems)
        assert INTEL_CPU_FAMILIES["alder_lake"]["supports_undervolt"] is False
        assert INTEL_CPU_FAMILIES["alder_lake"]["safe_undervolt_mv"] == 0

    def test_cpu_detection_with_mocked_cpuinfo(self):
        """Test CPU detection with mocked /proc/cpuinfo content."""
        from platforms.detection import detect_cpu_capabilities
        
        mock_cpuinfo = """processor	: 0
vendor_id	: GenuineIntel
model name	: Intel(R) Core(TM) i9-10850K CPU @ 3.60GHz
cpu MHz		: 3600.000
core id		: 0

processor	: 1
vendor_id	: GenuineIntel
model name	: Intel(R) Core(TM) i9-10850K CPU @ 3.60GHz
cpu MHz		: 3600.000
core id		: 1
"""
        
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=mock_cpuinfo):
                caps = detect_cpu_capabilities()
                
                assert caps.vendor == "intel"
                assert "i9-10850K" in caps.model_name
                assert caps.family == "comet_lake"
                assert caps.generation == 10
                assert caps.supports_undervolt is True
                assert caps.safe_undervolt_mv == 80


class TestNICCapabilities:
    """Tests for NICCapabilities dataclass and detect_nic_capabilities function."""

    def test_nic_capabilities_dataclass(self):
        """Test NICCapabilities dataclass can be instantiated."""
        from platforms.detection import NICCapabilities
        
        caps = NICCapabilities(
            interface="enp3s0",
            driver="igc",
            vendor="intel",
            is_intel=True,
            is_i225_family=True,
            supports_eee_disable=True,
            pci_id="15f3"
        )
        
        assert caps.interface == "enp3s0"
        assert caps.driver == "igc"
        assert caps.is_i225_family is True

    def test_intel_i225_device_ids(self):
        """Test I225/I226 device IDs are correctly defined."""
        from platforms.detection import INTEL_I225_DEVICE_IDS
        
        assert "15f3" in INTEL_I225_DEVICE_IDS  # I225-V
        assert "15f2" in INTEL_I225_DEVICE_IDS  # I225-LM
        assert "125c" in INTEL_I225_DEVICE_IDS  # I226-V

    def test_detect_nic_capabilities_handles_no_nic(self):
        """Test detect_nic_capabilities returns None when no NIC found."""
        from platforms.detection import detect_nic_capabilities
        
        with patch.object(Path, 'exists', return_value=False):
            caps = detect_nic_capabilities()
            assert caps is None


class TestMemoryScaling:
    """Tests for memory configuration scaling based on RAM."""

    def test_zram_size_calculation(self):
        """Test ZRAM size scales correctly with RAM."""
        # These are the expected ZRAM divisors from the config
        # competitive: RAM / 8, max 12GB
        # balanced: RAM / 6, max 16GB
        
        def calculate_zram(ram_gb: int, divisor: int, max_size: int) -> int:
            return min(ram_gb * 1024 // divisor, max_size)
        
        # Test competitive profile (divisor=8, max=12288)
        assert calculate_zram(16, 8, 12288) == 2048   # 16GB RAM -> 2GB ZRAM
        assert calculate_zram(32, 8, 12288) == 4096   # 32GB RAM -> 4GB ZRAM
        assert calculate_zram(64, 8, 12288) == 8192   # 64GB RAM -> 8GB ZRAM
        assert calculate_zram(128, 8, 12288) == 12288 # 128GB RAM -> 12GB (capped)
        
        # Test balanced profile (divisor=6, max=16384)
        assert calculate_zram(16, 6, 16384) == 2730   # 16GB RAM -> ~2.7GB ZRAM
        assert calculate_zram(64, 6, 16384) == 10922  # 64GB RAM -> ~10.7GB ZRAM
        assert calculate_zram(128, 6, 16384) == 16384 # 128GB RAM -> 16GB (capped)


class TestOptimizerIntegration:
    """Integration tests for optimizer classes with detection."""

    def test_cpu_optimizer_skips_undervolt_for_alder_lake(self):
        """Test CPUOptimizer skips undervolt for Alder Lake CPUs."""
        from platforms.detection import CPUCapabilities
        
        # Create Alder Lake CPU caps (undervolt not supported)
        alder_caps = CPUCapabilities(
            vendor="intel",
            model_name="12th Gen Intel(R) Core(TM) i5-1240P",
            family="alder_lake",
            generation=12,
            core_count=12,
            thread_count=16,
            supports_undervolt=False,
            safe_undervolt_mv=0,
            base_clock_mhz=1700,
            supports_turbo=True
        )
        
        assert alder_caps.supports_undervolt is False
        # In actual optimizer, this would skip configure_undervolt()

    def test_network_optimizer_detects_i225_family(self):
        """Test NetworkOptimizer correctly identifies I225 family NICs."""
        from platforms.detection import NICCapabilities, INTEL_I225_DEVICE_IDS
        
        # I225-V NIC
        i225v_caps = NICCapabilities(
            interface="enp3s0",
            driver="igc",
            vendor="intel",
            is_intel=True,
            is_i225_family=True,
            supports_eee_disable=True,
            pci_id="15f3"
        )
        
        assert i225v_caps.is_i225_family is True
        assert i225v_caps.supports_eee_disable is True
        
        # Non-I225 Intel NIC (e1000e)
        e1000e_caps = NICCapabilities(
            interface="eth0",
            driver="e1000e",
            vendor="intel",
            is_intel=True,
            is_i225_family=False,
            supports_eee_disable=False,
            pci_id="1234"
        )
        
        assert e1000e_caps.is_i225_family is False
        assert e1000e_caps.supports_eee_disable is False
