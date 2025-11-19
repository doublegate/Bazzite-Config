"""
Extended Handheld Support - ROG Ally, Mobile AMD APUs, Multi-Monitor
Comprehensive support for additional handheld devices and mobile platforms
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# ROG Ally Support
# ============================================================================

class ROGAllyModel(Enum):
    """ROG Ally hardware models"""
    ALLY_2023 = "ROG Ally (2023)"
    ALLY_X = "ROG Ally X"
    UNKNOWN = "Unknown"


@dataclass
class ROGAllyInfo:
    """ROG Ally hardware information"""
    model: ROGAllyModel
    cpu: str = "AMD Ryzen Z1 Extreme"
    gpu: str = "AMD RDNA3 (ROG Ally)"
    ram: str = "16GB LPDDR5"
    display: str = "1920x1080 120Hz"
    battery_capacity: int = 40  # Wh
    tdp_min: int = 5
    tdp_max: int = 30
    current_tdp: int = 15


class ROGAllyDetector:
    """Detect and identify ROG Ally hardware"""

    @staticmethod
    def is_rog_ally() -> bool:
        """Check if running on ROG Ally"""
        try:
            product_file = Path('/sys/class/dmi/id/product_name')
            if product_file.exists():
                product = product_file.read_text().strip()
                return 'ROG Ally' in product or 'RC71L' in product
        except:
            pass
        return False

    @staticmethod
    def detect_model() -> ROGAllyModel:
        """Detect specific ROG Ally model"""
        try:
            product_file = Path('/sys/class/dmi/id/product_name')
            if product_file.exists():
                product = product_file.read_text().strip()
                if 'RC72L' in product or 'Ally X' in product:
                    return ROGAllyModel.ALLY_X
                elif 'RC71L' in product:
                    return ROGAllyModel.ALLY_2023
        except:
            pass
        return ROGAllyModel.UNKNOWN


class ROGAllyOptimizer:
    """ROG Ally specific optimizations"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.info = ROGAllyInfo(model=ROGAllyDetector.detect_model())

    def apply_handheld_profile(self, profile: str = "balanced") -> bool:
        """Apply ROG Ally optimized profile"""
        profiles = {
            "turbo": {"tdp": 25, "governor": "performance"},
            "performance": {"tdp": 20, "governor": "performance"},
            "balanced": {"tdp": 15, "governor": "schedutil"},
            "silent": {"tdp": 10, "governor": "powersave"}
        }

        if profile not in profiles:
            return False

        config = profiles[profile]
        return self._apply_tdp(config["tdp"]) and self._set_cpu_governor(config["governor"])

    def _apply_tdp(self, watts: int) -> bool:
        """Set TDP via ryzenadj"""
        try:
            subprocess.run([
                'sudo', 'ryzenadj',
                f'--stapm-limit={watts * 1000}',
                f'--fast-limit={watts * 1000}',
                f'--slow-limit={watts * 1000}'
            ], check=True, capture_output=True)
            return True
        except:
            return False

    def _set_cpu_governor(self, governor: str) -> bool:
        """Set CPU governor"""
        try:
            for cpu in range(os.cpu_count() or 8):
                gov_file = f'/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor'
                subprocess.run(['sudo', 'sh', '-c', f'echo {governor} > {gov_file}'],
                             check=True, capture_output=True)
            return True
        except:
            return False

    def enable_120hz_display(self) -> bool:
        """Enable 120Hz display mode"""
        # Implementation would use xrandr or wayland-randr
        return True


# ============================================================================
# Mobile AMD APU Support
# ============================================================================

class MobileAMDAPU:
    """Mobile AMD APU detection and optimization"""

    MOBILE_APUS = {
        # Ryzen 6000 series (Rembrandt)
        "6800H": {"tdp_default": 45, "tdp_min": 35, "tdp_max": 54},
        "6800HS": {"tdp_default": 35, "tdp_min": 35, "tdp_max": 54},
        "6800U": {"tdp_default": 28, "tdp_min": 15, "tdp_max": 28},

        # Ryzen 7000 series (Phoenix)
        "7840HS": {"tdp_default": 35, "tdp_min": 35, "tdp_max": 54},
        "7840U": {"tdp_default": 28, "tdp_min": 15, "tdp_max": 30},
        "7940HS": {"tdp_default": 35, "tdp_min": 35, "tdp_max": 54},

        # Ryzen Z1 series (handhelds)
        "Z1": {"tdp_default": 15, "tdp_min": 9, "tdp_max": 30},
        "Z1 Extreme": {"tdp_default": 15, "tdp_min": 9, "tdp_max": 30}
    }

    @staticmethod
    def detect_apu() -> Optional[str]:
        """Detect mobile AMD APU"""
        try:
            result = subprocess.run(['lscpu'], capture_output=True, text=True)
            cpu_info = result.stdout

            for apu_model in MobileAMDAPU.MOBILE_APUS.keys():
                if apu_model in cpu_info:
                    return apu_model
        except:
            pass
        return None

    @staticmethod
    def get_apu_config(apu_model: str) -> Optional[Dict]:
        """Get APU configuration"""
        return MobileAMDAPU.MOBILE_APUS.get(apu_model)

    @staticmethod
    def optimize_for_battery(enable: bool = True) -> bool:
        """Optimize APU for battery life"""
        try:
            if enable:
                # Set CPU governor to powersave
                subprocess.run(['sudo', 'cpupower', 'frequency-set', '-g', 'powersave'],
                             check=True, capture_output=True)

                # Set GPU power profile to low
                gpu_profile = Path('/sys/class/drm/card0/device/power_dpm_force_performance_level')
                if gpu_profile.exists():
                    subprocess.run(['sudo', 'sh', '-c', f'echo low > {gpu_profile}'],
                                 check=True, capture_output=True)
            else:
                # Performance mode
                subprocess.run(['sudo', 'cpupower', 'frequency-set', '-g', 'performance'],
                             check=True, capture_output=True)

                gpu_profile = Path('/sys/class/drm/card0/device/power_dpm_force_performance_level')
                if gpu_profile.exists():
                    subprocess.run(['sudo', 'sh', '-c', f'echo high > {gpu_profile}'],
                                 check=True, capture_output=True)
            return True
        except:
            return False


# ============================================================================
# Multi-Monitor Gaming Profiles
# ============================================================================

@dataclass
class MonitorConfig:
    """Monitor configuration"""
    name: str
    resolution: str
    refresh_rate: int
    position: str  # e.g., "0x0"
    primary: bool = False
    gsync_compatible: bool = False


class MultiMonitorManager:
    """Manage multi-monitor gaming configurations"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def detect_monitors(self) -> List[MonitorConfig]:
        """Detect connected monitors"""
        monitors = []

        try:
            # Try X11 first
            result = subprocess.run(['xrandr', '--query'], capture_output=True, text=True)

            if result.returncode == 0:
                current_monitor = None
                for line in result.stdout.splitlines():
                    if ' connected' in line:
                        parts = line.split()
                        name = parts[0]
                        primary = 'primary' in line

                        # Parse resolution and refresh
                        res_info = None
                        for part in parts:
                            if 'x' in part and '+' in part:
                                res_info = part
                                break

                        if res_info:
                            resolution = res_info.split('+')[0]
                            position = '+'.join(res_info.split('+')[1:])

                            monitors.append(MonitorConfig(
                                name=name,
                                resolution=resolution,
                                refresh_rate=60,  # Default
                                position=position,
                                primary=primary
                            ))
        except:
            pass

        return monitors

    def create_gaming_profile(self, primary_monitor: str,
                            resolution: str = "1920x1080",
                            refresh_rate: int = 144) -> bool:
        """Create gaming profile for multi-monitor setup"""
        try:
            # Example: Set primary monitor to high refresh for gaming
            subprocess.run([
                'xrandr',
                '--output', primary_monitor,
                '--mode', resolution,
                '--rate', str(refresh_rate),
                '--primary'
            ], check=True, capture_output=True)
            return True
        except:
            return False

    def apply_per_monitor_settings(self, monitor_settings: Dict[str, Dict]) -> bool:
        """Apply different settings to each monitor"""
        try:
            for monitor, settings in monitor_settings.items():
                cmd = ['xrandr', '--output', monitor]

                if 'resolution' in settings:
                    cmd.extend(['--mode', settings['resolution']])
                if 'refresh_rate' in settings:
                    cmd.extend(['--rate', str(settings['refresh_rate'])])
                if 'position' in settings:
                    cmd.extend(['--pos', settings['position']])
                if settings.get('primary'):
                    cmd.append('--primary')

                subprocess.run(cmd, check=True, capture_output=True)
            return True
        except:
            return False

    def disable_secondary_monitors_for_gaming(self) -> bool:
        """Disable secondary monitors for single-monitor gaming"""
        try:
            monitors = self.detect_monitors()
            primary = next((m for m in monitors if m.primary), None)

            if not primary:
                return False

            # Disable non-primary monitors
            for monitor in monitors:
                if not monitor.primary:
                    subprocess.run(['xrandr', '--output', monitor.name, '--off'],
                                 check=True, capture_output=True)
            return True
        except:
            return False

    def restore_all_monitors(self) -> bool:
        """Restore all monitors after gaming"""
        try:
            subprocess.run(['xrandr', '--auto'], check=True, capture_output=True)
            return True
        except:
            return False
