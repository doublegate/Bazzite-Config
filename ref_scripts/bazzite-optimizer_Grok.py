#!/usr/bin/env python3
"""
Bazzite DX Gaming Optimization Master Script
For RTX 5080, Intel i9-10850K, 64GB RAM, Samsung 990 EVO Plus SSDs
Version: 1.0.0
Author: System Optimization Framework
License: MIT
"""

import os
import sys
import subprocess
import logging
import json
import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import argparse
import hashlib

# ============================================================================
# CONFIGURATION AND CONSTANTS
# ============================================================================

SCRIPT_VERSION = "1.0.0"
LOG_DIR = Path("/var/log/bazzite-optimizer")
CONFIG_BACKUP_DIR = Path("/var/backups/bazzite-optimizer")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ============================================================================
# OPTIMIZATION CONFIGURATIONS
# ============================================================================

NVIDIA_MODULE_CONFIG = """# RTX 5080 Gaming Optimizations
options nvidia-drm modeset=1 fbdev=1
options nvidia NVreg_PreserveVideoMemoryAllocations=1
options nvidia NVreg_RegistryDwords="PowerMizerEnable=0x1;PerfLevelSrc=0x2222"
options nvidia NVreg_EnableGpuFirmware=1
options nvidia NVreg_RegistryDwords="PerfLevelSrc=0x2222;PowerMizerDefaultAC=0x1"
"""

NVIDIA_OPTIMIZATION_SCRIPT = """#!/bin/bash
# RTX 5080 Gaming Optimization Script

# Enable maximum performance mode
nvidia-settings -a '[gpu:0]/GPUPowerMizerMode=1'

# Conservative overclocking for Gigabyte RTX 5080
nvidia-settings -a '[gpu:0]/GPUGraphicsClockOffset[3]=150'
nvidia-settings -a '[gpu:0]/GPUMemoryTransferRateOffset[3]=800'

# Fan control for cooling
nvidia-settings -a '[gpu:0]/GPUFanControlState=1'
nvidia-settings -a '[gpu:0]/GPUTargetFanSpeed=75'

# Enable G-SYNC/VRR
nvidia-settings -a '[gpu:0]/AllowGSYNC=1'
nvidia-settings -a '[gpu:0]/AllowGSYNCCompatible=1'

# Threading optimizations
export __GL_THREADED_OPTIMIZATIONS=1
export __GL_SHADER_DISK_CACHE=1
export __GL_SHADER_DISK_CACHE_SIZE=2147483648

# VRAM optimization for 16GB
export DXVK_MEMORY_LIMIT=14000
export VKD3D_MEMORY_LIMIT=14000

echo "RTX 5080 optimizations applied!"
"""

CPU_OPTIMIZATION_SCRIPT = """#!/bin/bash
# i9-10850K Gaming Optimization

# Enable MSR module
modprobe msr

# Set performance governor
cpupower frequency-set -g performance

# Configure frequency scaling
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/; do
    echo 3600000 > $cpu/scaling_min_freq 2>/dev/null
    echo 5200000 > $cpu/scaling_max_freq 2>/dev/null
done

# Intel P-state optimizations
echo 1 > /sys/devices/system/cpu/intel_pstate/hwp_dynamic_boost 2>/dev/null

# Disable CPU idle states for lower latency
echo 100 > /sys/devices/system/cpu/intel_pstate/min_perf_pct 2>/dev/null
echo 0 > /dev/cpu_dma_latency 2>/dev/null

echo "Intel i9-10850K optimized for gaming!"
"""

SYSCTL_CONFIG = """# 64GB RAM Gaming Optimizations
vm.swappiness=1
vm.vfs_cache_pressure=50
vm.dirty_background_ratio=5
vm.dirty_ratio=10
vm.dirty_writeback_centisecs=1500
vm.dirty_expire_centisecs=3000

# Transparent Huge Pages
vm.nr_hugepages=0

# Network optimizations
net.core.rmem_default=262144
net.core.rmem_max=134217728
net.core.wmem_default=262144
net.core.wmem_max=134217728
net.core.netdev_max_backlog=30000
net.ipv4.tcp_congestion_control=bbr
net.core.default_qdisc=fq
"""

NVME_UDEV_RULES = """# Samsung 990 EVO Plus Optimizations
ACTION=="add|change", KERNEL=="nvme[0-9]n[0-9]", ATTR{queue/scheduler}="none"
ACTION=="add|change", KERNEL=="nvme[0-9]n[0-9]", ATTR{queue/nr_requests}="16"
ACTION=="add|change", KERNEL=="nvme[0-9]n[0-9]", ATTR{queue/read_ahead_kb}="128"
ACTION=="add|change", KERNEL=="nvme[0-9]n[0-9]", ATTR{queue/max_sectors_kb}="1024"
"""

PIPEWIRE_CONFIG = """context.properties = {
    default.clock.rate = 48000
    default.clock.quantum = 32
    default.clock.min-quantum = 32
    default.clock.max-quantum = 32
}"""

WIREPLUMBER_CONFIG = """alsa_monitor.rules = {
  {
    matches = {{ "node.name", "matches", "alsa_output.*Creative*" }},
    apply_properties = {
      ["audio.format"] = "S32LE",
      ["audio.rate"] = "48000",
      ["api.alsa.period-size"] = 32,
      ["api.alsa.periods"] = 2,
      ["api.alsa.disable-batch"] = true,
    },
  },
}"""

IGC_MODULE_CONFIG = """# Intel I225-V Gaming Optimizations
options igc InterruptThrottleRate=1,1,1,1 TxIntDelay=8,8,8,8 RxIntDelay=8,8,8,8
options igc TxDescriptors=4096,4096,4096,4096 RxDescriptors=4096,4096,4096,4096
options igc FlowControl=0,0,0,0 EEE=0,0,0,0 DMAC=0,0,0,0
"""

ETHERNET_OPTIMIZE_SCRIPT = """#!/bin/bash
# Find ethernet interface name
ETH=$(ip link | grep -E '^[0-9]+: e' | cut -d: -f2 | tr -d ' ' | head -1)

if [ -n "$ETH" ]; then
    # Disable interrupt coalescing for lowest latency
    ethtool -C $ETH adaptive-rx off adaptive-tx off 2>/dev/null
    ethtool -C $ETH rx-usecs 1 tx-usecs 1 rx-frames 0 tx-frames 0 2>/dev/null

    # Set ring buffer sizes
    ethtool -G $ETH rx 4096 tx 4096 2>/dev/null

    echo "Ethernet optimized for gaming!"
else
    echo "No ethernet interface found"
fi
"""

GAMEMODE_CONFIG = """[general]
renice=10
softrealtime=auto
ioprio=0

[cpu]
park_cores=no
pin_cores=yes

[custom]
start=/usr/local/bin/nvidia-gaming-optimize.sh
start=/usr/local/bin/cpu-gaming-optimize.sh
start=/usr/local/bin/ethernet-optimize.sh
end=notify-send "GameMode" "Optimizations deactivated"

[gpu]
apply_gpu_optimisations=accept-responsibility
gpu_device=0
amd_performance_level=high
"""

MANGOHUD_CONFIG = """gpu_stats
gpu_temp
gpu_power
vram
cpu_stats
cpu_temp
ram
fps
frametime
frame_timing
gamemode
position=top-left
background_alpha=0.4
font_size=20
"""

MASTER_GAMING_SCRIPT = """#!/bin/bash
# Bazzite DX Complete Gaming Optimization

echo "Activating Gaming Mode..."

# CPU Optimizations
echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null
echo 0 > /dev/cpu_dma_latency 2>/dev/null

# GPU Optimizations (NVIDIA)
nvidia-settings -a '[gpu:0]/GPUPowerMizerMode=1' 2>/dev/null
nvidia-settings -a '[gpu:0]/GPUGraphicsClockOffset[3]=150' 2>/dev/null
nvidia-settings -a '[gpu:0]/GPUMemoryTransferRateOffset[3]=800' 2>/dev/null

# Network Optimizations
ETH=$(ip link | grep -E '^[0-9]+: e' | cut -d: -f2 | tr -d ' ' | head -1)
if [ -n "$ETH" ]; then
    ethtool -C $ETH adaptive-rx off adaptive-tx off rx-usecs 1 tx-usecs 1 2>/dev/null
fi

# Power Profile
powerprofilesctl set performance 2>/dev/null

# Memory management
echo 1 > /proc/sys/vm/swappiness 2>/dev/null
sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null

notify-send "Gaming Mode" "All optimizations activated!" 2>/dev/null
echo "Gaming optimizations applied successfully!"
"""

SYSTEMD_SERVICE = """[Unit]
Description=Gaming Performance Optimizations
After=graphical-session.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/gaming-mode-activate.sh
RemainAfterExit=yes

[Install]
WantedBy=default.target
"""

GRUB_CMDLINE_ADDITIONS = "mitigations=off preempt=full threadirqs processor.max_cstate=1 intel_idle.max_cstate=0 elevator=kyber transparent_hugepage=madvise nvme_core.default_ps_max_latency_us=0 pcie_aspm=off intel_pstate=active"

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    """Configure logging system"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    log_file = LOG_DIR / f"optimization_{TIMESTAMP}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def print_colored(message: str, color: str = Colors.ENDC):
    """Print colored message to terminal"""
    print(f"{color}{message}{Colors.ENDC}")

def run_command(command: str, shell: bool = True, check: bool = True) -> Tuple[int, str, str]:
    """Execute shell command and return result"""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            check=check
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr
    except Exception as e:
        return -1, "", str(e)

def backup_file(filepath: Path):
    """Create backup of existing file"""
    if filepath.exists():
        CONFIG_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        backup_path = CONFIG_BACKUP_DIR / f"{filepath.name}.{TIMESTAMP}"
        shutil.copy2(filepath, backup_path)
        logging.info(f"Backed up {filepath} to {backup_path}")
        return backup_path
    return None

def write_config_file(filepath: Path, content: str, executable: bool = False):
    """Write configuration file with proper permissions"""
    backup_file(filepath)

    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content)

    if executable:
        filepath.chmod(0o755)
    else:
        filepath.chmod(0o644)

    logging.info(f"Created configuration file: {filepath}")

def check_hardware_compatibility() -> Dict[str, bool]:
    """Check if hardware matches expected configuration"""
    checks = {
        "nvidia_gpu": False,
        "intel_cpu": False,
        "sufficient_ram": False,
        "nvme_storage": False,
        "creative_audio": False,
        "intel_network": False
    }

    # Check NVIDIA GPU
    returncode, stdout, _ = run_command("lspci | grep -i nvidia", check=False)
    if returncode == 0 and "RTX 5080" in stdout or "10de:2c02" in stdout:
        checks["nvidia_gpu"] = True

    # Check Intel CPU
    returncode, stdout, _ = run_command("grep -m1 'model name' /proc/cpuinfo", check=False)
    if returncode == 0 and ("i9-10850K" in stdout or "Intel" in stdout):
        checks["intel_cpu"] = True

    # Check RAM
    returncode, stdout, _ = run_command("free -g | grep Mem | awk '{print $2}'", check=False)
    if returncode == 0:
        try:
            ram_gb = int(stdout.strip())
            if ram_gb >= 60:  # Close to 64GB
                checks["sufficient_ram"] = True
        except:
            pass

    # Check NVMe storage
    returncode, stdout, _ = run_command("ls /dev/nvme* 2>/dev/null", check=False)
    if returncode == 0 and "nvme" in stdout:
        checks["nvme_storage"] = True

    # Check Creative audio
    returncode, stdout, _ = run_command("lspci | grep -i creative", check=False)
    if returncode == 0:
        checks["creative_audio"] = True

    # Check Intel network
    returncode, stdout, _ = run_command("lspci | grep -i 'Intel.*Ethernet'", check=False)
    if returncode == 0:
        checks["intel_network"] = True

    return checks

def check_bazzite_version() -> bool:
    """Verify Bazzite installation"""
    returncode, stdout, _ = run_command("rpm-ostree status | grep -i bazzite", check=False)
    if returncode == 0 and "bazzite" in stdout.lower():
        logging.info("Bazzite detected")
        return True
    return False

# ============================================================================
# OPTIMIZATION MODULES
# ============================================================================

class NvidiaOptimizer:
    """NVIDIA RTX 5080 optimization module"""

    def __init__(self, logger):
        self.logger = logger

    def install_drivers(self):
        """Ensure NVIDIA drivers are installed"""
        self.logger.info("Checking NVIDIA drivers...")

        returncode, stdout, _ = run_command("nvidia-smi", check=False)
        if returncode != 0:
            self.logger.info("Installing NVIDIA drivers...")
            run_command("sudo rpm-ostree install akmod-nvidia xorg-x11-drv-nvidia", check=False)
            return True  # Needs reboot

        self.logger.info("NVIDIA drivers already installed")
        return False

    def apply_optimizations(self):
        """Apply NVIDIA optimizations"""
        self.logger.info("Applying NVIDIA optimizations...")

        # Write module configuration
        write_config_file(
            Path("/etc/modprobe.d/nvidia-gaming.conf"),
            NVIDIA_MODULE_CONFIG
        )

        # Write optimization script
        write_config_file(
            Path("/usr/local/bin/nvidia-gaming-optimize.sh"),
            NVIDIA_OPTIMIZATION_SCRIPT,
            executable=True
        )

        # Regenerate initramfs
        run_command("sudo dracut -f", check=False)

        self.logger.info("NVIDIA optimizations applied")

class CPUOptimizer:
    """Intel CPU optimization module"""

    def __init__(self, logger):
        self.logger = logger

    def install_tools(self):
        """Install CPU management tools"""
        self.logger.info("Installing CPU tools...")
        run_command("sudo dnf install -y kernel-tools msr-tools", check=False)

    def apply_optimizations(self):
        """Apply CPU optimizations"""
        self.logger.info("Applying CPU optimizations...")

        # Write CPU optimization script
        write_config_file(
            Path("/usr/local/bin/cpu-gaming-optimize.sh"),
            CPU_OPTIMIZATION_SCRIPT,
            executable=True
        )

        # Apply immediately
        run_command("/usr/local/bin/cpu-gaming-optimize.sh", check=False)

        self.logger.info("CPU optimizations applied")

class MemoryStorageOptimizer:
    """Memory and storage optimization module"""

    def __init__(self, logger):
        self.logger = logger

    def apply_optimizations(self):
        """Apply memory and storage optimizations"""
        self.logger.info("Applying memory and storage optimizations...")

        # Write sysctl configuration
        write_config_file(
            Path("/etc/sysctl.d/99-gaming-memory.conf"),
            SYSCTL_CONFIG
        )

        # Write NVMe udev rules
        write_config_file(
            Path("/etc/udev/rules.d/60-nvme-gaming.rules"),
            NVME_UDEV_RULES
        )

        # Apply sysctl settings
        run_command("sudo sysctl -p /etc/sysctl.d/99-gaming-memory.conf", check=False)

        # Reload udev rules
        run_command("sudo udevadm control --reload-rules", check=False)
        run_command("sudo udevadm trigger", check=False)

        self.logger.info("Memory and storage optimizations applied")

class AudioOptimizer:
    """Audio system optimization module"""

    def __init__(self, logger):
        self.logger = logger
        self.user = os.environ.get('SUDO_USER', os.environ.get('USER'))

    def apply_optimizations(self):
        """Apply audio optimizations"""
        self.logger.info("Applying audio optimizations...")

        # Create PipeWire config directory for user
        pipewire_dir = Path(f"/home/{self.user}/.config/pipewire/pipewire.conf.d")
        pipewire_dir.mkdir(parents=True, exist_ok=True)

        # Write PipeWire configuration
        pipewire_config_path = pipewire_dir / "99-gaming.conf"
        pipewire_config_path.write_text(PIPEWIRE_CONFIG)

        # Create WirePlumber config directory
        wireplumber_dir = Path(f"/home/{self.user}/.config/wireplumber/main.lua.d")
        wireplumber_dir.mkdir(parents=True, exist_ok=True)

        # Write WirePlumber configuration
        wireplumber_config_path = wireplumber_dir / "99-alsa-gaming.conf"
        wireplumber_config_path.write_text(WIREPLUMBER_CONFIG)

        # Fix ownership
        run_command(f"chown -R {self.user}:{self.user} /home/{self.user}/.config/pipewire", check=False)
        run_command(f"chown -R {self.user}:{self.user} /home/{self.user}/.config/wireplumber", check=False)

        self.logger.info("Audio optimizations applied")

class NetworkOptimizer:
    """Network optimization module"""

    def __init__(self, logger):
        self.logger = logger

    def apply_optimizations(self):
        """Apply network optimizations"""
        self.logger.info("Applying network optimizations...")

        # Write Intel ethernet module configuration
        write_config_file(
            Path("/etc/modprobe.d/igc-gaming.conf"),
            IGC_MODULE_CONFIG
        )

        # Write ethernet optimization script
        write_config_file(
            Path("/usr/local/bin/ethernet-optimize.sh"),
            ETHERNET_OPTIMIZE_SCRIPT,
            executable=True
        )

        # Apply immediately
        run_command("/usr/local/bin/ethernet-optimize.sh", check=False)

        # Disable WiFi power saving
        wifi_config = "[connection]\nwifi.powersave = 2"
        write_config_file(
            Path("/etc/NetworkManager/conf.d/wifi-powersave-off.conf"),
            wifi_config
        )

        run_command("sudo systemctl restart NetworkManager", check=False)

        self.logger.info("Network optimizations applied")

class GamingToolsOptimizer:
    """Gaming-specific tools and configurations"""

    def __init__(self, logger):
        self.logger = logger
        self.user = os.environ.get('SUDO_USER', os.environ.get('USER'))

    def install_tools(self):
        """Install gaming tools"""
        self.logger.info("Installing gaming tools...")

        # Install system packages
        packages = [
            "gamemode",
            "mangohud",
            "gamescope",
            "steam-devices",
            "nvtop",
            "btop"
        ]

        for package in packages:
            self.logger.info(f"Installing {package}...")
            run_command(f"sudo dnf install -y {package}", check=False)

        # Install Flatpak applications
        flatpak_apps = [
            "com.leinardi.gwe",  # GreenWithEnvy
            "net.davidotek.pupgui2",  # ProtonUp-Qt
            "com.github.tchx84.Flatseal"  # Flatseal
        ]

        for app in flatpak_apps:
            self.logger.info(f"Installing {app}...")
            run_command(f"flatpak install -y flathub {app}", check=False)

    def configure_gamemode(self):
        """Configure GameMode"""
        self.logger.info("Configuring GameMode...")

        write_config_file(
            Path("/etc/gamemode.ini"),
            GAMEMODE_CONFIG
        )

        self.logger.info("GameMode configured")

    def configure_mangohud(self):
        """Configure MangoHud"""
        self.logger.info("Configuring MangoHud...")

        mangohud_dir = Path(f"/home/{self.user}/.config/MangoHud")
        mangohud_dir.mkdir(parents=True, exist_ok=True)

        mangohud_config_path = mangohud_dir / "MangoHud.conf"
        mangohud_config_path.write_text(MANGOHUD_CONFIG)

        run_command(f"chown -R {self.user}:{self.user} {mangohud_dir}", check=False)

        self.logger.info("MangoHud configured")

class KernelOptimizer:
    """Kernel and boot parameter optimization"""

    def __init__(self, logger):
        self.logger = logger

    def apply_grub_optimizations(self):
        """Update GRUB configuration"""
        self.logger.info("Updating GRUB configuration...")

        # Backup GRUB config
        grub_config = Path("/etc/default/grub")
        backup_file(grub_config)

        # Read current configuration
        with open(grub_config, 'r') as f:
            lines = f.readlines()

        # Update GRUB_CMDLINE_LINUX_DEFAULT
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("GRUB_CMDLINE_LINUX_DEFAULT="):
                # Extract current value
                current_value = line.split('=', 1)[1].strip().strip('"')

                # Add our optimizations if not already present
                for param in GRUB_CMDLINE_ADDITIONS.split():
                    if param not in current_value:
                        current_value += f" {param}"

                lines[i] = f'GRUB_CMDLINE_LINUX_DEFAULT="{current_value}"\n'
                updated = True
                break

        if updated:
            # Write updated configuration
            with open(grub_config, 'w') as f:
                f.writelines(lines)

            # Update GRUB
            run_command("sudo grub2-mkconfig -o /boot/grub2/grub.cfg", check=False)
            self.logger.info("GRUB configuration updated")
        else:
            self.logger.warning("Could not update GRUB configuration")

class SystemdServiceOptimizer:
    """Systemd service configuration"""

    def __init__(self, logger):
        self.logger = logger

    def create_gaming_service(self):
        """Create systemd service for gaming optimizations"""
        self.logger.info("Creating gaming optimization service...")

        # Write master gaming script
        write_config_file(
            Path("/usr/local/bin/gaming-mode-activate.sh"),
            MASTER_GAMING_SCRIPT,
            executable=True
        )

        # Write systemd service
        write_config_file(
            Path("/etc/systemd/system/gaming-optimizations.service"),
            SYSTEMD_SERVICE
        )

        # Enable service
        run_command("sudo systemctl daemon-reload", check=False)
        run_command("sudo systemctl enable gaming-optimizations.service", check=False)

        self.logger.info("Gaming optimization service created and enabled")

class PlasmaOptimizer:
    """KDE Plasma optimization module"""

    def __init__(self, logger):
        self.logger = logger
        self.user = os.environ.get('SUDO_USER', os.environ.get('USER'))

    def apply_optimizations(self):
        """Apply KDE Plasma optimizations"""
        self.logger.info("Applying KDE Plasma optimizations...")

        kwin_commands = [
            "kwriteconfig6 --file ~/.config/kwinrc --group Compositing --key LatencyPolicy Low",
            "kwriteconfig6 --file ~/.config/kwinrc --group TabBox --key DelayTime 0",
            "kwriteconfig6 --file ~/.config/kwinrc --group Compositing --key VariableRefreshRate true",
            "kwriteconfig6 --file ~/.config/kwinrc --group Plugins --key blurEnabled false",
            "kwriteconfig6 --file ~/.config/kwinrc --group Plugins --key minimizeanimationEnabled false"
        ]

        for cmd in kwin_commands:
            run_command(f"sudo -u {self.user} {cmd}", check=False)

        # Apply changes
        run_command(f"sudo -u {self.user} qdbus org.kde.KWin /KWin reconfigure", check=False)

        self.logger.info("KDE Plasma optimizations applied")

# ============================================================================
# MAIN OPTIMIZER CLASS
# ============================================================================

class BazziteGamingOptimizer:
    """Main optimizer orchestrator"""

    def __init__(self):
        self.logger = setup_logging()
        self.optimizers = []
        self.needs_reboot = False

    def print_banner(self):
        """Display welcome banner"""
        print_colored("=" * 70, Colors.HEADER)
        print_colored("       BAZZITE DX GAMING OPTIMIZER v" + SCRIPT_VERSION, Colors.HEADER + Colors.BOLD)
        print_colored("  RTX 5080 | i9-10850K | 64GB RAM | Samsung 990 EVO Plus", Colors.OKCYAN)
        print_colored("=" * 70, Colors.HEADER)
        print()

    def check_prerequisites(self) -> bool:
        """Check system prerequisites"""
        print_colored("Checking system prerequisites...", Colors.OKBLUE)

        # Check if running as root
        if os.geteuid() != 0:
            print_colored("ERROR: This script must be run as root (use sudo)", Colors.FAIL)
            return False

        # Check Bazzite
        if not check_bazzite_version():
            print_colored("WARNING: Bazzite not detected. Continue anyway? (y/n): ", Colors.WARNING, end="")
            if input().lower() != 'y':
                return False

        # Check hardware
        hardware = check_hardware_compatibility()

        print("\nHardware Detection:")
        for component, detected in hardware.items():
            status = "✓" if detected else "✗"
            color = Colors.OKGREEN if detected else Colors.WARNING
            print_colored(f"  {status} {component.replace('_', ' ').title()}", color)

        # Warn if hardware doesn't match
        if not all(hardware.values()):
            print_colored("\nWARNING: Some hardware components were not detected.", Colors.WARNING)
            print_colored("The optimizations are specifically designed for your hardware.", Colors.WARNING)
            print_colored("Continue anyway? (y/n): ", Colors.WARNING, end="")
            if input().lower() != 'y':
                return False

        return True

    def initialize_optimizers(self):
        """Initialize all optimizer modules"""
        self.optimizers = [
            NvidiaOptimizer(self.logger),
            CPUOptimizer(self.logger),
            MemoryStorageOptimizer(self.logger),
            AudioOptimizer(self.logger),
            NetworkOptimizer(self.logger),
            GamingToolsOptimizer(self.logger),
            KernelOptimizer(self.logger),
            SystemdServiceOptimizer(self.logger),
            PlasmaOptimizer(self.logger)
        ]

    def apply_optimizations(self, skip_packages: bool = False):
        """Apply all optimizations"""
        print_colored("\nStarting optimization process...", Colors.HEADER)

        try:
            # NVIDIA optimizations
            print_colored("\n[1/9] NVIDIA RTX 5080 Optimizations", Colors.OKCYAN)
            nvidia = self.optimizers[0]
            if not skip_packages:
                if nvidia.install_drivers():
                    self.needs_reboot = True
            nvidia.apply_optimizations()

            # CPU optimizations
            print_colored("\n[2/9] Intel i9-10850K CPU Optimizations", Colors.OKCYAN)
            cpu = self.optimizers[1]
            if not skip_packages:
                cpu.install_tools()
            cpu.apply_optimizations()

            # Memory and Storage
            print_colored("\n[3/9] Memory & Storage Optimizations", Colors.OKCYAN)
            self.optimizers[2].apply_optimizations()

            # Audio
            print_colored("\n[4/9] Audio System Optimizations", Colors.OKCYAN)
            self.optimizers[3].apply_optimizations()

            # Network
            print_colored("\n[5/9] Network Optimizations", Colors.OKCYAN)
            self.optimizers[4].apply_optimizations()

            # Gaming tools
            print_colored("\n[6/9] Gaming Tools Installation", Colors.OKCYAN)
            gaming_tools = self.optimizers[5]
            if not skip_packages:
                gaming_tools.install_tools()
            gaming_tools.configure_gamemode()
            gaming_tools.configure_mangohud()

            # Kernel
            print_colored("\n[7/9] Kernel & Boot Parameters", Colors.OKCYAN)
            self.optimizers[6].apply_grub_optimizations()
            self.needs_reboot = True

            # Systemd service
            print_colored("\n[8/9] Systemd Service Configuration", Colors.OKCYAN)
            self.optimizers[7].create_gaming_service()

            # KDE Plasma
            print_colored("\n[9/9] KDE Plasma Optimizations", Colors.OKCYAN)
            self.optimizers[8].apply_optimizations()

            print_colored("\n✓ All optimizations applied successfully!", Colors.OKGREEN + Colors.BOLD)

        except Exception as e:
            print_colored(f"\n✗ Error during optimization: {str(e)}", Colors.FAIL)
            self.logger.error(f"Optimization failed: {str(e)}", exc_info=True)
            return False

        return True

    def create_rollback_script(self):
        """Create script to rollback changes"""
        rollback_script = f"""#!/bin/bash
# Rollback script created on {TIMESTAMP}

echo "Rolling back optimizations..."

# Restore backed up files
for backup in {CONFIG_BACKUP_DIR}/*.{TIMESTAMP}; do
    original=$(basename $backup .{TIMESTAMP})
    target_paths=(
        "/etc/modprobe.d/$original"
        "/etc/sysctl.d/$original"
        "/etc/udev/rules.d/$original"
        "/etc/$original"
    )

    for target in "${{target_paths[@]}}"; do
        if [ -f "$target" ]; then
            cp "$backup" "$target"
            echo "Restored $target"
            break
        fi
    done
done

# Remove optimization scripts
rm -f /usr/local/bin/nvidia-gaming-optimize.sh
rm -f /usr/local/bin/cpu-gaming-optimize.sh
rm -f /usr/local/bin/ethernet-optimize.sh
rm -f /usr/local/bin/gaming-mode-activate.sh

# Disable gaming service
systemctl disable gaming-optimizations.service
rm -f /etc/systemd/system/gaming-optimizations.service

# Reset CPU governor
echo powersave | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

echo "Rollback complete. Please reboot your system."
"""

        rollback_path = Path("/usr/local/bin/rollback-gaming-optimizations.sh")
        write_config_file(rollback_path, rollback_script, executable=True)

        print_colored(f"\nRollback script created: {rollback_path}", Colors.OKBLUE)

    def print_verification_commands(self):
        """Print commands to verify optimizations"""
        print_colored("\n" + "=" * 70, Colors.HEADER)
        print_colored("VERIFICATION COMMANDS", Colors.HEADER + Colors.BOLD)
        print_colored("=" * 70, Colors.HEADER)

        commands = [
            ("CPU Governor", "cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor | head -1"),
            ("GPU Performance Mode", "nvidia-settings -q GPUPowerMizerMode"),
            ("Memory Swappiness", "sysctl vm.swappiness"),
            ("Network Congestion Control", "sysctl net.ipv4.tcp_congestion_control"),
            ("GameMode Status", "systemctl status gamemoded"),
            ("Gaming Service", "systemctl status gaming-optimizations.service")
        ]

        print("\nRun these commands to verify optimizations:")
        for name, cmd in commands:
            print(f"\n{Colors.OKCYAN}{name}:{Colors.ENDC}")
            print(f"  {cmd}")

    def print_usage_instructions(self):
        """Print usage instructions"""
        print_colored("\n" + "=" * 70, Colors.HEADER)
        print_colored("USAGE INSTRUCTIONS", Colors.HEADER + Colors.BOLD)
        print_colored("=" * 70, Colors.HEADER)

        print(f"""
{Colors.OKGREEN}Gaming Mode Activation:{Colors.ENDC}
  Manual:     sudo /usr/local/bin/gaming-mode-activate.sh
  Automatic:  Enabled on boot via systemd service

{Colors.OKGREEN}Steam Launch Options:{Colors.ENDC}
  Default:    MANGOHUD=1 gamemoderun %command%
  DLSS:       PROTON_ENABLE_NVAPI=1 %command%
  Ray Tracing: DXVK_ENABLE_NVAPI=1 VKD3D_CONFIG=dxr11,dxr %command%

{Colors.OKGREEN}Monitor Performance:{Colors.ENDC}
  System:     btop
  GPU:        nvtop
  In-Game:    MangoHud (automatically enabled)

{Colors.OKGREEN}Rollback Changes:{Colors.ENDC}
  sudo /usr/local/bin/rollback-gaming-optimizations.sh

{Colors.OKGREEN}Update System:{Colors.ENDC}
  ujust update
""")

    def run(self):
        """Main execution flow"""
        self.print_banner()

        # Check prerequisites
        if not self.check_prerequisites():
            return 1

        # Initialize optimizers
        self.initialize_optimizers()

        # Parse arguments
        parser = argparse.ArgumentParser(description='Bazzite Gaming Optimizer')
        parser.add_argument('--skip-packages', action='store_true',
                          help='Skip package installation')
        parser.add_argument('--rollback', action='store_true',
                          help='Rollback optimizations')
        args = parser.parse_args()

        # Handle rollback
        if args.rollback:
            rollback_script = Path("/usr/local/bin/rollback-gaming-optimizations.sh")
            if rollback_script.exists():
                print_colored("\nExecuting rollback...", Colors.WARNING)
                run_command(str(rollback_script))
                return 0
            else:
                print_colored("No rollback script found", Colors.FAIL)
                return 1

        # Apply optimizations
        if not self.apply_optimizations(args.skip_packages):
            return 1

        # Create rollback script
        self.create_rollback_script()

        # Print verification commands
        self.print_verification_commands()

        # Print usage instructions
        self.print_usage_instructions()

        # Check if reboot needed
        if self.needs_reboot:
            print_colored("\n" + "!" * 70, Colors.WARNING)
            print_colored("REBOOT REQUIRED", Colors.WARNING + Colors.BOLD)
            print_colored("Some optimizations require a system reboot to take effect.", Colors.WARNING)
            print_colored("Please reboot your system when convenient.", Colors.WARNING)
            print_colored("!" * 70, Colors.WARNING)

        print_colored("\n✓ Optimization complete! Happy gaming! 🎮", Colors.OKGREEN + Colors.BOLD)

        return 0

# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    try:
        optimizer = BazziteGamingOptimizer()
        return optimizer.run()
    except KeyboardInterrupt:
        print_colored("\n\nOperation cancelled by user", Colors.WARNING)
        return 130
    except Exception as e:
        print_colored(f"\nFatal error: {str(e)}", Colors.FAIL)
        logging.error(f"Fatal error: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
