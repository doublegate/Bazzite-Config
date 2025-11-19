"""
Shared pytest fixtures and configuration for Bazzite Gaming Optimization Suite
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Dict, Any
from unittest.mock import Mock, MagicMock, patch
import pytest

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================================
# Session-level Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return project root directory"""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def test_data_dir(project_root: Path) -> Path:
    """Return test data directory"""
    return project_root / "tests" / "fixtures"


# =============================================================================
# Function-level Fixtures - Temporary Directories
# =============================================================================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for test"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_etc_dir(temp_dir: Path) -> Path:
    """Create mock /etc directory structure"""
    etc_dir = temp_dir / "etc"
    etc_dir.mkdir(parents=True)

    # Create common subdirectories
    (etc_dir / "bazzite-optimizer").mkdir()
    (etc_dir / "bazzite-optimizer" / "profiles").mkdir()
    (etc_dir / "systemd" / "system").mkdir(parents=True)
    (etc_dir / "modprobe.d").mkdir()
    (etc_dir / "sysctl.d").mkdir()

    return etc_dir


@pytest.fixture
def mock_var_dir(temp_dir: Path) -> Path:
    """Create mock /var directory structure"""
    var_dir = temp_dir / "var"
    var_dir.mkdir(parents=True)

    # Create common subdirectories
    (var_dir / "run").mkdir()
    (var_dir / "log").mkdir()
    (var_dir / "lib").mkdir()

    return var_dir


# =============================================================================
# Hardware Detection Mocks
# =============================================================================

@pytest.fixture
def mock_nvidia_gpu() -> Dict[str, Any]:
    """Mock NVIDIA RTX 5080 GPU data"""
    return {
        "vendor": "NVIDIA",
        "model": "RTX 5080",
        "driver": "nvidia-open",
        "driver_version": "560.35.03",
        "cuda_version": "12.6",
        "vram": "16GB",
        "pci_id": "10de:2860",
        "architecture": "Blackwell"
    }


@pytest.fixture
def mock_amd_gpu() -> Dict[str, Any]:
    """Mock AMD RX 7900 XTX GPU data"""
    return {
        "vendor": "AMD",
        "model": "RX 7900 XTX",
        "driver": "amdgpu",
        "driver_version": "6.0.0",
        "rocm_version": "5.7.0",
        "vram": "24GB",
        "pci_id": "1002:744c",
        "architecture": "RDNA3"
    }


@pytest.fixture
def mock_intel_cpu() -> Dict[str, Any]:
    """Mock Intel i9-10850K CPU data"""
    return {
        "vendor": "Intel",
        "model": "i9-10850K",
        "architecture": "Comet Lake",
        "cores": 10,
        "threads": 20,
        "base_freq": 3.6,
        "turbo_freq": 5.2,
        "tdp": 125,
        "features": ["AVX2", "AVX512", "TSX"]
    }


@pytest.fixture
def mock_amd_cpu() -> Dict[str, Any]:
    """Mock AMD Ryzen 9 7950X CPU data"""
    return {
        "vendor": "AMD",
        "model": "Ryzen 9 7950X",
        "architecture": "Zen 4",
        "cores": 16,
        "threads": 32,
        "base_freq": 4.5,
        "turbo_freq": 5.7,
        "tdp": 170,
        "features": ["AVX2", "AVX512", "SMT"]
    }


# =============================================================================
# System State Mocks
# =============================================================================

@pytest.fixture
def mock_system_info() -> Dict[str, Any]:
    """Mock complete system information"""
    return {
        "os": "Bazzite Linux",
        "kernel": "6.11.3-200.fsync.fc41.x86_64",
        "desktop": "GNOME 47",
        "ram_total": 68719476736,  # 64GB
        "ram_available": 60129542144,  # ~56GB
        "swap_total": 8589934592,  # 8GB
        "swap_available": 8589934592,
        "disk_total": 2000398934016,  # ~2TB
        "disk_available": 1500299200512,  # ~1.5TB
    }


@pytest.fixture
def mock_gaming_profiles() -> Dict[str, Dict[str, Any]]:
    """Mock gaming profile configurations"""
    return {
        "competitive": {
            "name": "Competitive",
            "cpu_governor": "performance",
            "gpu_power_mode": 1,
            "max_cstate": 1,
            "core_isolation": True,
            "mitigations": "off"
        },
        "balanced": {
            "name": "Balanced",
            "cpu_governor": "schedutil",
            "gpu_power_mode": 0,
            "max_cstate": 3,
            "core_isolation": False,
            "mitigations": "off"
        },
        "streaming": {
            "name": "Streaming",
            "cpu_governor": "schedutil",
            "gpu_power_mode": 0,
            "max_cstate": 3,
            "core_isolation": False,
            "mitigations": "auto"
        },
        "creative": {
            "name": "Creative",
            "cpu_governor": "performance",
            "gpu_power_mode": 0,
            "max_cstate": 1,
            "core_isolation": False,
            "mitigations": "auto"
        }
    }


# =============================================================================
# Subprocess Mocking
# =============================================================================

@pytest.fixture
def mock_subprocess():
    """Mock subprocess.run for command execution"""
    with patch('subprocess.run') as mock_run:
        # Default successful result
        mock_run.return_value = Mock(
            returncode=0,
            stdout="",
            stderr=""
        )
        yield mock_run


@pytest.fixture
def mock_subprocess_failure():
    """Mock subprocess.run for failed command execution"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="Command failed"
        )
        yield mock_run


# =============================================================================
# File System Mocking
# =============================================================================

@pytest.fixture
def mock_pathlib_exists():
    """Mock Path.exists() to return True"""
    with patch('pathlib.Path.exists', return_value=True) as mock_exists:
        yield mock_exists


@pytest.fixture
def mock_pathlib_not_exists():
    """Mock Path.exists() to return False"""
    with patch('pathlib.Path.exists', return_value=False) as mock_exists:
        yield mock_exists


# =============================================================================
# Logging Mocks
# =============================================================================

@pytest.fixture
def mock_logger():
    """Mock logger for testing log output"""
    logger = MagicMock()
    logger.debug = MagicMock()
    logger.info = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    logger.critical = MagicMock()
    return logger


# =============================================================================
# GTK Mocking (for GUI tests without display server)
# =============================================================================

@pytest.fixture
def mock_gtk():
    """Mock GTK4 for testing without display server"""
    with patch.dict('sys.modules', {
        'gi': MagicMock(),
        'gi.repository': MagicMock(),
        'gi.repository.Gtk': MagicMock(),
        'gi.repository.Gio': MagicMock(),
        'gi.repository.GLib': MagicMock()
    }):
        yield


# =============================================================================
# Permission Mocking
# =============================================================================

@pytest.fixture
def mock_root_privileges():
    """Mock root privileges (os.geteuid() returns 0)"""
    with patch('os.geteuid', return_value=0):
        yield


@pytest.fixture
def mock_user_privileges():
    """Mock user privileges (os.geteuid() returns 1000)"""
    with patch('os.geteuid', return_value=1000):
        yield


# =============================================================================
# Steam Deck Detection Mocking
# =============================================================================

@pytest.fixture
def mock_steam_deck_hardware():
    """Mock Steam Deck hardware detection"""
    return {
        "device": "Steam Deck",
        "variant": "OLED",
        "cpu": "AMD Custom APU 0405",
        "gpu": "AMD RDNA2 (Steam Deck)",
        "ram": "16GB LPDDR5",
        "display": "1280x800 HDR OLED",
        "tdp_range": (4, 25),
        "battery_capacity": 50  # Wh
    }


# =============================================================================
# Pytest Configuration Hooks
# =============================================================================

def pytest_configure(config):
    """Pytest configuration hook"""
    # Add custom markers
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for component interactions"
    )
    config.addinivalue_line(
        "markers", "gui: GUI tests requiring GTK4"
    )
    config.addinivalue_line(
        "markers", "slow: Slow-running tests (>1s)"
    )
    config.addinivalue_line(
        "markers", "requires_root: Tests requiring root privileges"
    )
    config.addinivalue_line(
        "markers", "requires_hardware: Tests requiring specific hardware"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip tests based on markers"""
    # Skip tests requiring root if not running as root
    if os.geteuid() != 0:
        skip_root = pytest.mark.skip(reason="Requires root privileges")
        for item in items:
            if "requires_root" in item.keywords:
                item.add_marker(skip_root)

    # Skip hardware-specific tests if hardware not available
    # (This would be extended with actual hardware detection)
    skip_nvidia = pytest.mark.skip(reason="Requires NVIDIA GPU")
    skip_amd = pytest.mark.skip(reason="Requires AMD GPU")
    skip_steamdeck = pytest.mark.skip(reason="Requires Steam Deck hardware")

    for item in items:
        if "requires_nvidia" in item.keywords:
            # Add logic to detect NVIDIA GPU
            item.add_marker(skip_nvidia)
        if "requires_amd" in item.keywords:
            # Add logic to detect AMD GPU
            item.add_marker(skip_amd)
        if "requires_steamdeck" in item.keywords:
            # Add logic to detect Steam Deck
            item.add_marker(skip_steamdeck)
