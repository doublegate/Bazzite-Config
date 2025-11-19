#!/usr/bin/env python3
"""
Steam Deck Optimizer for Bazzite Gaming Optimization Suite
Provides handheld-specific optimizations, TDP management, and battery optimization
Supports Steam Deck LCD and OLED models on Bazzite/SteamOS
"""

import os
import subprocess
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# Steam Deck Detection and Information
# ============================================================================

class SteamDeckModel(Enum):
    """Steam Deck hardware models"""
    LCD_64GB = "LCD 64GB"
    LCD_256GB = "LCD 256GB"
    LCD_512GB = "LCD 512GB"
    OLED_512GB = "OLED 512GB"
    OLED_1TB = "OLED 1TB"
    UNKNOWN = "Unknown"


@dataclass
class SteamDeckInfo:
    """Steam Deck hardware information"""
    model: SteamDeckModel = SteamDeckModel.UNKNOWN
    cpu: str = "AMD Custom APU 0405"
    gpu: str = "AMD RDNA2 (Van Gogh)"
    ram: str = "16GB LPDDR5"
    display: str = ""
    battery_capacity: int = 40  # Wh (default LCD)
    tdp_min: int = 4    # Watts
    tdp_max: int = 25   # Watts (OLED can go to 30W)
    current_tdp: int = 15
    battery_percent: int = 0
    battery_status: str = "Unknown"
    on_battery: bool = True
    cpu_temp: float = 0.0
    gpu_temp: float = 0.0
    fan_rpm: int = 0


class SteamDeckDetector:
    """Steam Deck hardware detection"""

    @staticmethod
    def is_steam_deck() -> bool:
        """Check if running on Steam Deck"""
        try:
            # Check DMI product name
            product_file = Path('/sys/class/dmi/id/product_name')
            if product_file.exists():
                product = product_file.read_text().strip()
                if 'Jupiter' in product or 'Galileo' in product:
                    return True

            # Check for Steam Deck specific files
            if Path('/sys/class/hwmon/hwmon0/name').exists():
                hwmon_name = Path('/sys/class/hwmon/hwmon0/name').read_text().strip()
                if 'jupiter' in hwmon_name.lower():
                    return True

            return False

        except Exception:
            return False

    @staticmethod
    def detect_model() -> SteamDeckModel:
        """Detect specific Steam Deck model"""
        try:
            product_file = Path('/sys/class/dmi/id/product_name')
            if not product_file.exists():
                return SteamDeckModel.UNKNOWN

            product = product_file.read_text().strip()

            # Jupiter = LCD models
            # Galileo = OLED models
            if 'Galileo' in product:
                # OLED models - detect based on storage or other identifiers
                return SteamDeckModel.OLED_512GB  # Default, could be refined
            elif 'Jupiter' in product:
                # LCD models - could check storage size
                return SteamDeckModel.LCD_512GB  # Default, could be refined

            return SteamDeckModel.UNKNOWN

        except Exception:
            return SteamDeckModel.UNKNOWN

    @staticmethod
    def gather_info() -> Optional[SteamDeckInfo]:
        """Gather comprehensive Steam Deck information"""
        if not SteamDeckDetector.is_steam_deck():
            return None

        info = SteamDeckInfo()
        info.model = SteamDeckDetector.detect_model()

        # Set model-specific parameters
        if info.model in [SteamDeckModel.OLED_512GB, SteamDeckModel.OLED_1TB]:
            info.display = "1280x800 HDR OLED"
            info.battery_capacity = 50  # Wh
            info.tdp_max = 30  # OLED can do 30W
        else:
            info.display = "1280x800 LCD"
            info.battery_capacity = 40  # Wh
            info.tdp_max = 25  # LCD max 25W

        # Get current TDP
        info.current_tdp = SteamDeckDetector._get_current_tdp()

        # Get battery information
        battery_info = SteamDeckDetector._get_battery_info()
        info.battery_percent = battery_info.get('percent', 0)
        info.battery_status = battery_info.get('status', 'Unknown')
        info.on_battery = battery_info.get('on_battery', True)

        # Get temperatures
        temps = SteamDeckDetector._get_temperatures()
        info.cpu_temp = temps.get('cpu', 0.0)
        info.gpu_temp = temps.get('gpu', 0.0)
        info.fan_rpm = temps.get('fan_rpm', 0)

        return info

    @staticmethod
    def _get_current_tdp() -> int:
        """Get current TDP setting"""
        try:
            # Steam Deck TDP is controlled via ryzenadj or custom kernel interface
            # Simplified implementation
            tdp_file = Path('/sys/class/hwmon/hwmon0/power1_cap')
            if tdp_file.exists():
                power_microwatts = int(tdp_file.read_text().strip())
                return power_microwatts // 1000000  # Convert to Watts

            return 15  # Default

        except Exception:
            return 15

    @staticmethod
    def _get_battery_info() -> Dict[str, any]:
        """Get battery information"""
        battery_info = {
            'percent': 0,
            'status': 'Unknown',
            'on_battery': True
        }

        try:
            battery_path = Path('/sys/class/power_supply/BAT1')
            if not battery_path.exists():
                battery_path = Path('/sys/class/power_supply/BAT0')

            if battery_path.exists():
                # Battery percentage
                capacity_file = battery_path / 'capacity'
                if capacity_file.exists():
                    battery_info['percent'] = int(capacity_file.read_text().strip())

                # Battery status
                status_file = battery_path / 'status'
                if status_file.exists():
                    battery_info['status'] = status_file.read_text().strip()

                # Check if on AC power
                battery_info['on_battery'] = battery_info['status'] != 'Charging'

        except Exception:
            pass

        return battery_info

    @staticmethod
    def _get_temperatures() -> Dict[str, float]:
        """Get CPU/GPU temperatures and fan RPM"""
        temps = {
            'cpu': 0.0,
            'gpu': 0.0,
            'fan_rpm': 0
        }

        try:
            hwmon_path = Path('/sys/class/hwmon/hwmon0')
            if hwmon_path.exists():
                # CPU temp
                cpu_temp_file = hwmon_path / 'temp1_input'
                if cpu_temp_file.exists():
                    temp_millicelsius = int(cpu_temp_file.read_text().strip())
                    temps['cpu'] = temp_millicelsius / 1000.0

                # GPU temp (same as CPU on APU)
                temps['gpu'] = temps['cpu']

                # Fan RPM
                fan_rpm_file = hwmon_path / 'fan1_input'
                if fan_rpm_file.exists():
                    temps['fan_rpm'] = int(fan_rpm_file.read_text().strip())

        except Exception:
            pass

        return temps


# ============================================================================
# Steam Deck Optimizer
# ============================================================================

class SteamDeckOptimizer:
    """Steam Deck handheld-specific optimizations"""

    def __init__(self, deck_info: SteamDeckInfo):
        self.deck_info = deck_info
        self.logger = logging.getLogger(__name__)

    def apply_handheld_profile(self, profile: str = "balanced") -> bool:
        """Apply handheld-optimized gaming profile"""
        try:
            if profile == "performance":
                return self._apply_performance_profile()
            elif profile == "balanced":
                return self._apply_balanced_profile()
            elif profile == "battery_saver":
                return self._apply_battery_saver_profile()
            elif profile == "silent":
                return self._apply_silent_profile()
            else:
                self.logger.error(f"Unknown handheld profile: {profile}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to apply handheld profile: {e}")
            return False

    def _apply_performance_profile(self) -> bool:
        """Performance profile (15-25W TDP, max fan)"""
        self.logger.info("Applying Steam Deck performance profile")

        # Set high TDP (20-25W depending on model)
        target_tdp = 22 if self.deck_info.model in [SteamDeckModel.OLED_512GB, SteamDeckModel.OLED_1TB] else 20

        if not self.set_tdp(target_tdp):
            return False

        # Set CPU governor to performance
        if not self._set_cpu_governor("performance"):
            return False

        # Set GPU to high performance mode
        if not self._set_gpu_performance_level("high"):
            return False

        self.logger.info(f"Performance profile applied (TDP: {target_tdp}W)")
        return True

    def _apply_balanced_profile(self) -> bool:
        """Balanced profile (12-15W TDP, balanced settings)"""
        self.logger.info("Applying Steam Deck balanced profile")

        # Set moderate TDP
        if not self.set_tdp(15):
            return False

        # Set CPU governor to schedutil
        if not self._set_cpu_governor("schedutil"):
            return False

        # Set GPU to auto performance
        if not self._set_gpu_performance_level("auto"):
            return False

        self.logger.info("Balanced profile applied (TDP: 15W)")
        return True

    def _apply_battery_saver_profile(self) -> bool:
        """Battery saver profile (7-10W TDP, efficiency focus)"""
        self.logger.info("Applying Steam Deck battery saver profile")

        # Set low TDP
        if not self.set_tdp(8):
            return False

        # Set CPU governor to powersave
        if not self._set_cpu_governor("powersave"):
            return False

        # Set GPU to low performance
        if not self._set_gpu_performance_level("low"):
            return False

        # Reduce screen brightness
        if self.deck_info.on_battery:
            self._set_screen_brightness(50)

        self.logger.info("Battery saver profile applied (TDP: 8W)")
        return True

    def _apply_silent_profile(self) -> bool:
        """Silent profile (10-12W TDP, quiet fan)"""
        self.logger.info("Applying Steam Deck silent profile")

        # Set moderate-low TDP for quiet operation
        if not self.set_tdp(11):
            return False

        # Set CPU governor to schedutil
        if not self._set_cpu_governor("schedutil"):
            return False

        # Set GPU to auto
        if not self._set_gpu_performance_level("auto"):
            return False

        self.logger.info("Silent profile applied (TDP: 11W)")
        return True

    def set_tdp(self, watts: int) -> bool:
        """Set TDP (Thermal Design Power) in Watts"""
        # Clamp to safe limits
        watts = max(self.deck_info.tdp_min, min(self.deck_info.tdp_max, watts))

        try:
            # Try ryzenadj first (if available)
            result = subprocess.run(
                ['ryzenadj', f'--stapm-limit={watts * 1000}',
                 f'--fast-limit={watts * 1000}',
                 f'--slow-limit={watts * 1000}'],
                capture_output=True,
                check=False
            )

            if result.returncode == 0:
                self.logger.info(f"TDP set to {watts}W via ryzenadj")
                self.deck_info.current_tdp = watts
                return True

            # Fallback to sysfs
            tdp_file = Path('/sys/class/hwmon/hwmon0/power1_cap')
            if tdp_file.exists():
                power_microwatts = watts * 1000000
                with open(tdp_file, 'w') as f:
                    f.write(str(power_microwatts))
                self.logger.info(f"TDP set to {watts}W via sysfs")
                self.deck_info.current_tdp = watts
                return True

            self.logger.warning("Could not set TDP - no method available")
            return False

        except Exception as e:
            self.logger.error(f"Failed to set TDP: {e}")
            return False

    def _set_cpu_governor(self, governor: str) -> bool:
        """Set CPU frequency governor"""
        try:
            cpu_count = os.cpu_count() or 8
            for cpu in range(cpu_count):
                governor_file = Path(f'/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor')
                if governor_file.exists():
                    with open(governor_file, 'w') as f:
                        f.write(governor)

            self.logger.info(f"CPU governor set to: {governor}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to set CPU governor: {e}")
            return False

    def _set_gpu_performance_level(self, level: str) -> bool:
        """Set GPU performance level"""
        try:
            gpu_perf_file = Path('/sys/class/drm/card0/device/power_dpm_force_performance_level')
            if not gpu_perf_file.exists():
                return False

            with open(gpu_perf_file, 'w') as f:
                f.write(level)

            self.logger.info(f"GPU performance level set to: {level}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to set GPU performance: {e}")
            return False

    def _set_screen_brightness(self, percent: int) -> bool:
        """Set screen brightness percentage"""
        try:
            brightness_file = Path('/sys/class/backlight/amdgpu_bl0/brightness')
            max_brightness_file = Path('/sys/class/backlight/amdgpu_bl0/max_brightness')

            if not brightness_file.exists() or not max_brightness_file.exists():
                return False

            max_brightness = int(max_brightness_file.read_text().strip())
            target_brightness = int((percent / 100.0) * max_brightness)

            with open(brightness_file, 'w') as f:
                f.write(str(target_brightness))

            self.logger.info(f"Screen brightness set to: {percent}%")
            return True

        except Exception as e:
            self.logger.error(f"Failed to set brightness: {e}")
            return False

    def apply_gaming_optimizations(self) -> bool:
        """Apply Steam Deck specific gaming optimizations"""
        self.logger.info("Applying Steam Deck gaming optimizations")

        try:
            # Enable memory compaction
            compaction_file = Path('/proc/sys/vm/compact_memory')
            if compaction_file.exists():
                with open(compaction_file, 'w') as f:
                    f.write('1')

            # Set swappiness for handheld (lower than desktop)
            swappiness_file = Path('/proc/sys/vm/swappiness')
            if swappiness_file.exists():
                with open(swappiness_file, 'w') as f:
                    f.write('10')  # Low swappiness for responsive gaming

            # Disable watchdogs for performance
            subprocess.run(
                ['sysctl', '-w', 'kernel.nmi_watchdog=0'],
                check=False,
                capture_output=True
            )

            self.logger.info("Gaming optimizations applied")
            return True

        except Exception as e:
            self.logger.error(f"Failed to apply gaming optimizations: {e}")
            return False

    def estimate_battery_life(self, tdp: int) -> float:
        """Estimate battery life in hours at given TDP"""
        # Simple estimation: battery_capacity (Wh) / power_draw (W)
        # Add 20% overhead for display, WiFi, etc.
        total_power = tdp + (tdp * 0.2)
        estimated_hours = self.deck_info.battery_capacity / total_power
        return estimated_hours

    def get_recommended_tdp_for_target_fps(self, target_fps: int) -> int:
        """Recommend TDP for target FPS (rough heuristic)"""
        # Rough heuristics for Steam Deck
        if target_fps >= 60:
            return 20  # High TDP for 60 FPS
        elif target_fps >= 40:
            return 15  # Medium TDP for 40 FPS
        elif target_fps >= 30:
            return 11  # Low TDP for 30 FPS
        else:
            return 8   # Battery saver for <30 FPS


# ============================================================================
# Main Entry Point for Testing
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("Steam Deck Optimizer - Detection and Testing")
    print("=" * 60)

    # Detect Steam Deck
    if SteamDeckDetector.is_steam_deck():
        print("\n✓ Steam Deck Detected!")

        deck_info = SteamDeckDetector.gather_info()
        if deck_info:
            print(f"\nHardware Information:")
            print(f"  Model: {deck_info.model.value}")
            print(f"  CPU: {deck_info.cpu}")
            print(f"  GPU: {deck_info.gpu}")
            print(f"  RAM: {deck_info.ram}")
            print(f"  Display: {deck_info.display}")
            print(f"  Battery: {deck_info.battery_capacity}Wh")
            print(f"  TDP Range: {deck_info.tdp_min}-{deck_info.tdp_max}W")
            print(f"  Current TDP: {deck_info.current_tdp}W")
            print(f"  Battery: {deck_info.battery_percent}% ({deck_info.battery_status})")
            print(f"  CPU Temp: {deck_info.cpu_temp}°C")
            print(f"  Fan RPM: {deck_info.fan_rpm}")

            # Test optimizer
            print("\nTesting optimizer...")
            optimizer = SteamDeckOptimizer(deck_info)

            # Battery life estimates
            print("\nBattery Life Estimates:")
            for tdp in [8, 11, 15, 20]:
                hours = optimizer.estimate_battery_life(tdp)
                print(f"  {tdp}W TDP: ~{hours:.1f} hours")

    else:
        print("\n✗ Not running on Steam Deck")
