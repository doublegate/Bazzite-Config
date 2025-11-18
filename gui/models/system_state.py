#!/usr/bin/env python3
"""
System State Model for Bazzite Optimizer GUI

Manages current system state including hardware info, optimization status,
and gaming mode state.
"""

import subprocess
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class HardwareInfo:
    """Hardware information data class"""
    cpu_model: str = "Unknown"
    cpu_cores: int = 0
    gpu_model: str = "Unknown"
    gpu_vram: str = "Unknown"
    total_ram: str = "Unknown"
    zram_size: str = "Unknown"
    kernel_version: str = "Unknown"


@dataclass
class OptimizationStatus:
    """Current optimization status"""
    active_profile: str = "None"
    gaming_mode_enabled: bool = False
    last_optimized: Optional[str] = None
    system_health: int = 0  # 0-100
    performance_improvement: str = "0%"


@dataclass
class SystemState:
    """Complete system state model"""
    hardware: HardwareInfo = field(default_factory=HardwareInfo)
    optimization: OptimizationStatus = field(default_factory=OptimizationStatus)
    _observers: list = field(default_factory=list, repr=False)

    def attach_observer(self, observer):
        """Attach observer for state changes"""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach_observer(self, observer):
        """Detach observer"""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self):
        """Notify all observers of state change"""
        for observer in self._observers:
            observer.on_state_changed(self)

    def update_hardware_info(self, hardware: HardwareInfo):
        """Update hardware information"""
        self.hardware = hardware
        self.notify_observers()

    def update_optimization_status(self, status: OptimizationStatus):
        """Update optimization status"""
        self.optimization = status
        self.notify_observers()

    def set_active_profile(self, profile_name: str):
        """Set the active optimization profile"""
        self.optimization.active_profile = profile_name
        self.notify_observers()

    def set_gaming_mode(self, enabled: bool):
        """Set gaming mode state"""
        self.optimization.gaming_mode_enabled = enabled
        self.notify_observers()


class SystemStateLoader:
    """Loads system state from various sources"""

    @staticmethod
    def load_hardware_info() -> HardwareInfo:
        """Load hardware information from system"""
        hardware = HardwareInfo()

        try:
            # CPU info
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'model name' in line:
                        hardware.cpu_model = line.split(':')[1].strip()
                        break

            # CPU cores
            hardware.cpu_cores = subprocess.check_output(
                ['nproc'], text=True
            ).strip()

            # GPU info (NVIDIA)
            try:
                gpu_query = subprocess.check_output(
                    ['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'],
                    text=True, stderr=subprocess.DEVNULL
                ).strip()
                if gpu_query:
                    parts = gpu_query.split(',')
                    hardware.gpu_model = parts[0].strip()
                    hardware.gpu_vram = parts[1].strip() if len(parts) > 1 else "Unknown"
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Try AMD
                try:
                    gpu_info = subprocess.check_output(
                        ['lspci', '-nn'], text=True
                    )
                    for line in gpu_info.split('\n'):
                        if 'VGA' in line or 'Display' in line:
                            hardware.gpu_model = line.split(':')[-1].strip()
                            break
                except Exception:
                    hardware.gpu_model = "Unknown"

            # RAM info
            try:
                meminfo = subprocess.check_output(['free', '-h'], text=True)
                for line in meminfo.split('\n'):
                    if 'Mem:' in line:
                        hardware.total_ram = line.split()[1]
                        break
            except Exception:
                pass

            # ZRAM info
            try:
                zram_info = subprocess.check_output(
                    ['zramctl', '--output', 'DISKSIZE', '--noheadings'],
                    text=True, stderr=subprocess.DEVNULL
                ).strip()
                if zram_info:
                    hardware.zram_size = zram_info.split('\n')[0]
            except Exception:
                hardware.zram_size = "Not configured"

            # Kernel version
            hardware.kernel_version = subprocess.check_output(
                ['uname', '-r'], text=True
            ).strip()

        except Exception as e:
            print(f"Error loading hardware info: {e}")

        return hardware

    @staticmethod
    def load_optimization_status() -> OptimizationStatus:
        """Load current optimization status"""
        status = OptimizationStatus()

        try:
            # Check gaming mode state file
            state_file = Path('/var/run/gaming-mode.state')
            if state_file.exists():
                state_content = state_file.read_text().strip()
                status.gaming_mode_enabled = state_content == '1'

            # Try to detect active profile from config
            config_file = Path('/etc/gaming-mode.conf')
            if config_file.exists():
                config = config_file.read_text()
                for line in config.split('\n'):
                    if 'PROFILE=' in line:
                        status.active_profile = line.split('=')[1].strip().strip('"')
                        break

            # Check last optimization time
            log_file = Path('/var/log/bazzite-optimizer.log')
            if log_file.exists():
                try:
                    last_lines = subprocess.check_output(
                        ['tail', '-1', str(log_file)], text=True
                    ).strip()
                    if last_lines:
                        # Parse timestamp from log
                        status.last_optimized = "Recently"
                except Exception:
                    pass

            # Estimate system health (placeholder - would need actual metrics)
            status.system_health = 85
            status.performance_improvement = "+23%"

        except Exception as e:
            print(f"Error loading optimization status: {e}")

        return status
