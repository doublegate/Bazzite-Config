#!/usr/bin/env python3
"""
Bazzite Gaming System Manager & Control Panel
Comprehensive management utilities for optimized gaming system
Version: 1.0.0
"""

import os
import sys
import json
import subprocess
import argparse
import configparser
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import time
import shutil

# ============================================================================
# COLOR CODES
# ============================================================================

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# ============================================================================
# GAMING MODE CONTROLLER
# ============================================================================

class GamingModeController:
    """Control gaming optimizations on/off"""
    
    def __init__(self):
        self.config_file = Path("/etc/gaming-mode.conf")
        self.state_file = Path("/var/run/gaming-mode.state")
    
    def get_status(self) -> Dict:
        """Get current gaming mode status"""
        status = {
            'enabled': False,
            'cpu_governor': 'unknown',
            'gpu_mode': 'unknown',
            'gamemode': False,
            'compositor': True,
            'services': {}
        }
        
        # Check if gaming mode is enabled
        if self.state_file.exists():
            status['enabled'] = True
        
        # Check CPU governor
        try:
            with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor', 'r') as f:
                status['cpu_governor'] = f.read().strip()
        except:
            pass
        
        # Check GPU performance mode
        try:
            result = subprocess.run("nvidia-settings -q GPUPowerMizerMode -t", 
                                  shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                mode = result.stdout.strip()
                status['gpu_mode'] = 'maximum' if '1' in mode else 'adaptive'
        except:
            pass
        
        # Check GameMode
        try:
            result = subprocess.run("systemctl is-active gamemoded", 
                                  shell=True, capture_output=True, text=True)
            status['gamemode'] = 'active' in result.stdout
        except:
            pass
        
        # Check compositor
        try:
            result = subprocess.run("qdbus org.kde.KWin /Compositor active", 
                                  shell=True, capture_output=True, text=True)
            status['compositor'] = 'true' in result.stdout.lower()
        except:
            pass
        
        # Check services
        services = ['gaming-optimizations.service', 'gamemoded.service']
        for service in services:
            try:
                result = subprocess.run(f"systemctl is-active {service}", 
                                      shell=True, capture_output=True, text=True)
                status['services'][service] = 'active' in result.stdout
            except:
                status['services'][service] = False
        
        return status
    
    def enable_gaming_mode(self) -> bool:
        """Enable full gaming mode"""
        print(f"{Colors.OKGREEN}Enabling Gaming Mode...{Colors.ENDC}")
        
        commands = [
            # CPU performance mode
            "echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor",
            
            # GPU maximum performance
            "nvidia-settings -a '[gpu:0]/GPUPowerMizerMode=1'",
            "nvidia-settings -a '[gpu:0]/GPUGraphicsClockOffset[3]=150'",
            "nvidia-settings -a '[gpu:0]/GPUMemoryTransferRateOffset[3]=800'",
            
            # Disable compositor
            "qdbus org.kde.KWin /Compositor suspend",
            
            # Start GameMode
            "systemctl --user start gamemoded",
            
            # Network optimization
            "sudo /usr/local/bin/ethernet-optimize.sh",
            
            # Clear memory caches
            "sudo sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'",
            
            # Set swappiness
            "sudo sysctl vm.swappiness=1"
        ]
        
        success = True
        for cmd in commands:
            result = subprocess.run(cmd, shell=True, capture_output=True)
            if result.returncode != 0:
                print(f"{Colors.WARNING}Warning: Command failed: {cmd[:50]}...{Colors.ENDC}")
                success = False
        
        # Mark as enabled
        self.state_file.touch()
        
        print(f"{Colors.OKGREEN}✓ Gaming Mode Enabled{Colors.ENDC}")
        return success
    
    def disable_gaming_mode(self) -> bool:
        """Disable gaming mode and restore defaults"""
        print(f"{Colors.WARNING}Disabling Gaming Mode...{Colors.ENDC}")
        
        commands = [
            # CPU balanced mode
            "echo schedutil | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor",
            
            # GPU adaptive performance
            "nvidia-settings -a '[gpu:0]/GPUPowerMizerMode=0'",
            "nvidia-settings -a '[gpu:0]/GPUGraphicsClockOffset[3]=0'",
            "nvidia-settings -a '[gpu:0]/GPUMemoryTransferRateOffset[3]=0'",
            
            # Enable compositor
            "qdbus org.kde.KWin /Compositor resume",
            
            # Stop GameMode if not needed
            "systemctl --user stop gamemoded",
            
            # Reset swappiness
            "sudo sysctl vm.swappiness=10"
        ]
        
        success = True
        for cmd in commands:
            result = subprocess.run(cmd, shell=True, capture_output=True)
            if result.returncode != 0:
                print(f"{Colors.WARNING}Warning: Command failed: {cmd[:50]}...{Colors.ENDC}")
                success = False
        
        # Remove state file
        if self.state_file.exists():
            self.state_file.unlink()
        
        print(f"{Colors.OKGREEN}✓ Gaming Mode Disabled{Colors.ENDC}")
        return success
    
    def toggle_compositor(self) -> bool:
        """Toggle KWin compositor"""
        try:
            result = subprocess.run("qdbus org.kde.KWin /Compositor active", 
                                  shell=True, capture_output=True, text=True)
            is_active = 'true' in result.stdout.lower()
            
            if is_active:
                subprocess.run("qdbus org.kde.KWin /Compositor suspend", shell=True)
                print(f"{Colors.OKGREEN}Compositor disabled (better for gaming){Colors.ENDC}")
            else:
                subprocess.run("qdbus org.kde.KWin /Compositor resume", shell=True)
                print(f"{Colors.WARNING}Compositor enabled{Colors.ENDC}")
            
            return True
        except Exception as e:
            print(f"{Colors.FAIL}Failed to toggle compositor: {e}{Colors.ENDC}")
            return False

# ============================================================================
# GAME PROFILE MANAGER
# ============================================================================

class GameProfileManager:
    """Manage per-game optimization profiles"""
    
    def __init__(self):
        self.profiles_dir = Path.home() / ".config/gaming-profiles"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.active_profile = None
    
    def create_profile(self, name: str, config: Dict) -> bool:
        """Create a new game profile"""
        profile_file = self.profiles_dir / f"{name}.json"
        
        default_config = {
            'name': name,
            'created': datetime.now().isoformat(),
            'steam_launch_options': '',
            'cpu_governor': 'performance',
            'gpu_overclock': True,
            'gpu_clock_offset': 150,
            'gpu_memory_offset': 800,
            'disable_compositor': True,
            'gamemode': True,
            'mangohud': True,
            'vsync': False,
            'fps_limit': 0,
            'resolution': 'native',
            'proton_version': 'experimental',
            'dxvk_settings': {
                'DXVK_ASYNC': '1',
                'DXVK_MEMORY_LIMIT': '14000'
            },
            'env_variables': {}
        }
        
        # Merge with provided config
        default_config.update(config)
        
        # Save profile
        with open(profile_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        print(f"{Colors.OKGREEN}Profile '{name}' created{Colors.ENDC}")
        return True
    
    def load_profile(self, name: str) -> Optional[Dict]:
        """Load a game profile"""
        profile_file = self.profiles_dir / f"{name}.json"
        
        if not profile_file.exists():
            print(f"{Colors.FAIL}Profile '{name}' not found{Colors.ENDC}")
            return None
        
        with open(profile_file, 'r') as f:
            return json.load(f)
    
    def apply_profile(self, name: str) -> bool:
        """Apply a game profile"""
        profile = self.load_profile(name)
        if not profile:
            return False
        
        print(f"{Colors.OKBLUE}Applying profile: {name}{Colors.ENDC}")
        
        # Apply CPU governor
        if profile.get('cpu_governor'):
            subprocess.run(f"echo {profile['cpu_governor']} | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor", 
                         shell=True, capture_output=True)
        
        # Apply GPU settings
        if profile.get('gpu_overclock'):
            subprocess.run(f"nvidia-settings -a '[gpu:0]/GPUGraphicsClockOffset[3]={profile.get('gpu_clock_offset', 0)}'", 
                         shell=True, capture_output=True)
            subprocess.run(f"nvidia-settings -a '[gpu:0]/GPUMemoryTransferRateOffset[3]={profile.get('gpu_memory_offset', 0)}'", 
                         shell=True, capture_output=True)
        
        # Toggle compositor
        if profile.get('disable_compositor'):
            subprocess.run("qdbus org.kde.KWin /Compositor suspend", shell=True, capture_output=True)
        
        # Set environment variables
        env_vars = profile.get('env_variables', {})
        env_vars.update(profile.get('dxvk_settings', {}))
        
        for key, value in env_vars.items():
            os.environ[key] = str(value)
        
        # Generate launch command
        launch_cmd = self._generate_launch_command(profile)
        
        print(f"{Colors.OKGREEN}✓ Profile applied{Colors.ENDC}")
        print(f"{Colors.OKCYAN}Launch command: {launch_cmd}{Colors.ENDC}")
        
        self.active_profile = name
        return True
    
    def _generate_launch_command(self, profile: Dict) -> str:
        """Generate Steam launch command from profile"""
        parts = []
        
        # Add MangoHud
        if profile.get('mangohud'):
            parts.append('MANGOHUD=1')
        
        # Add GameMode
        if profile.get('gamemode'):
            parts.append('gamemoderun')
        
        # Add DXVK settings
        for key, value in profile.get('dxvk_settings', {}).items():
            parts.append(f"{key}={value}")
        
        # Add environment variables
        for key, value in profile.get('env_variables', {}).items():
            parts.append(f"{key}={value}")
        
        # Add %command% placeholder
        parts.append('%command%')
        
        # Add custom options
        if profile.get('steam_launch_options'):
            parts.append(profile['steam_launch_options'])
        
        return ' '.join(parts)
    
    def list_profiles(self) -> List[str]:
        """List all available profiles"""
        profiles = []
        for profile_file in self.profiles_dir.glob("*.json"):
            profiles.append(profile_file.stem)
        return sorted(profiles)
    
    def delete_profile(self, name: str) -> bool:
        """Delete a profile"""
        profile_file = self.profiles_dir / f"{name}.json"
        if profile_file.exists():
            profile_file.unlink()
            print(f"{Colors.OKGREEN}Profile '{name}' deleted{Colors.ENDC}")
            return True
        return False
    
    def create_preset_profiles(self):
        """Create preset profiles for common scenarios"""
        
        presets = {
            'competitive_fps': {
                'description': 'Competitive FPS games (CS2, Valorant, etc)',
                'gpu_overclock': True,
                'gpu_clock_offset': 200,
                'gpu_memory_offset': 1000,
                'disable_compositor': True,
                'vsync': False,
                'fps_limit': 0,
                'mangohud': False,  # Disable for lowest latency
                'dxvk_settings': {
                    'DXVK_ASYNC': '0',  # Disable async for consistency
                    'DXVK_MEMORY_LIMIT': '8000'
                }
            },
            'single_player_quality': {
                'description': 'Single player with max quality',
                'gpu_overclock': True,
                'gpu_clock_offset': 150,
                'gpu_memory_offset': 800,
                'disable_compositor': True,
                'vsync': True,
                'fps_limit': 144,
                'mangohud': True,
                'dxvk_settings': {
                    'DXVK_ASYNC': '1',
                    'DXVK_MEMORY_LIMIT': '14000'
                },
                'env_variables': {
                    'PROTON_ENABLE_NVAPI': '1',
                    'VKD3D_CONFIG': 'dxr11,dxr'  # Ray tracing
                }
            },
            'battery_saving': {
                'description': 'Power saving mode',
                'cpu_governor': 'powersave',
                'gpu_overclock': False,
                'disable_compositor': False,
                'fps_limit': 60,
                'mangohud': True
            },
            'streaming': {
                'description': 'Optimized for streaming/recording',
                'gpu_overclock': True,
                'gpu_clock_offset': 100,
                'disable_compositor': False,  # Keep compositor for OBS
                'fps_limit': 60,
                'mangohud': True,
                'env_variables': {
                    'OBS_VKCAPTURE': '1'
                }
            }
        }
        
        for name, config in presets.items():
            self.create_profile(name, config)
        
        print(f"{Colors.OKGREEN}Created {len(presets)} preset profiles{Colors.ENDC}")

# ============================================================================
# QUICK FIX UTILITIES
# ============================================================================

class QuickFixUtilities:
    """Common fixes for gaming issues"""
    
    @staticmethod
    def fix_steam_issues():
        """Fix common Steam issues"""
        print(f"{Colors.OKBLUE}Fixing Steam issues...{Colors.ENDC}")
        
        commands = [
            # Clear Steam shader cache
            "rm -rf ~/.cache/mesa_shader_cache",
            "rm -rf ~/.cache/nvidia",
            "rm -rf ~/.local/share/Steam/steamapps/shadercache/*",
            
            # Reset Steam runtime
            "rm -rf ~/.local/share/Steam/ubuntu12_32/steam-runtime",
            
            # Fix Steam library permissions
            "find ~/.local/share/Steam/steamapps -type d -exec chmod 755 {} \;",
            "find ~/.local/share/Steam/steamapps -type f -exec chmod 644 {} \;"
        ]
        
        for cmd in commands:
            subprocess.run(cmd, shell=True, capture_output=True)
        
        print(f"{Colors.OKGREEN}✓ Steam fixes applied{Colors.ENDC}")
        print("Please restart Steam")
    
    @staticmethod
    def fix_audio_crackling():
        """Fix audio crackling issues"""
        print(f"{Colors.OKBLUE}Fixing audio issues...{Colors.ENDC}")
        
        commands = [
            # Restart audio services
            "systemctl --user restart pipewire pipewire-pulse wireplumber",
            
            # Clear audio cache
            "rm -rf ~/.cache/pipewire",
            
            # Reset audio settings
            "pactl unload-module module-suspend-on-idle"
        ]
        
        for cmd in commands:
            subprocess.run(cmd, shell=True, capture_output=True)
        
        print(f"{Colors.OKGREEN}✓ Audio fixes applied{Colors.ENDC}")
    
    @staticmethod
    def fix_gpu_driver():
        """Reload GPU driver"""
        print(f"{Colors.OKBLUE}Reloading GPU driver...{Colors.ENDC}")
        
        commands = [
            # Reload NVIDIA modules
            "sudo rmmod nvidia_uvm",
            "sudo rmmod nvidia_modeset",
            "sudo rmmod nvidia",
            "sudo modprobe nvidia",
            "sudo modprobe nvidia_modeset",
            "sudo modprobe nvidia_uvm"
        ]
        
        print(f"{Colors.WARNING}WARNING: This will reset your GPU. Save all work first!{Colors.ENDC}")
        print("Continue? (y/n): ", end="")
        if input().lower() != 'y':
            return
        
        for cmd in commands:
            subprocess.run(cmd, shell=True, capture_output=True)
        
        print(f"{Colors.OKGREEN}✓ GPU driver reloaded{Colors.ENDC}")
    
    @staticmethod
    def clear_caches():
        """Clear all gaming-related caches"""
        print(f"{Colors.OKBLUE}Clearing caches...{Colors.ENDC}")
        
        cache_dirs = [
            "~/.cache/mesa_shader_cache",
            "~/.cache/nvidia",
            "~/.cache/wine",
            "~/.local/share/Steam/steamapps/shadercache",
            "~/.cache/dxvk",
            "~/.cache/vkd3d",
            "~/.cache/lutris"
        ]
        
        for cache_dir in cache_dirs:
            cache_path = Path(cache_dir).expanduser()
            if cache_path.exists():
                shutil.rmtree(cache_path, ignore_errors=True)
                print(f"  Cleared: {cache_dir}")
        
        # Clear system caches
        subprocess.run("sudo sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'", 
                      shell=True, capture_output=True)
        
        print(f"{Colors.OKGREEN}✓ All caches cleared{Colors.ENDC}")
    
    @staticmethod
    def optimize_game_files(game_path: str):
        """Optimize game files for better loading"""
        print(f"{Colors.OKBLUE}Optimizing game files...{Colors.ENDC}")
        
        game_path = Path(game_path)
        if not game_path.exists():
            print(f"{Colors.FAIL}Game path not found{Colors.ENDC}")
            return
        
        # Defragment if on BTRFS
        subprocess.run(f"sudo btrfs filesystem defragment -r {game_path}", 
                      shell=True, capture_output=True)
        
        # Preload game files into cache
        subprocess.run(f"find {game_path} -type f -exec cat {{}} > /dev/null \;", 
                      shell=True, capture_output=True)
        
        print(f"{Colors.OKGREEN}✓ Game files optimized{Colors.ENDC}")

# ============================================================================
# SYSTEM HEALTH CHECKER
# ============================================================================

class SystemHealthChecker:
    """Check system health and optimization status"""
    
    def __init__(self):
        self.checks = []
    
    def run_all_checks(self) -> Dict:
        """Run all health checks"""
        print(f"{Colors.HEADER}Running System Health Checks...{Colors.ENDC}\n")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        # Check NVIDIA driver
        results['checks']['nvidia_driver'] = self._check_nvidia_driver()
        
        # Check CPU performance
        results['checks']['cpu_performance'] = self._check_cpu_performance()
        
        # Check memory
        results['checks']['memory'] = self._check_memory()
        
        # Check disk performance
        results['checks']['disk_performance'] = self._check_disk_performance()
        
        # Check thermals
        results['checks']['thermals'] = self._check_thermals()
        
        # Check services
        results['checks']['services'] = self._check_services()
        
        # Check kernel parameters
        results['checks']['kernel'] = self._check_kernel_parameters()
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    def _check_nvidia_driver(self) -> Dict:
        """Check NVIDIA driver status"""
        result = {'status': 'unknown', 'version': 'unknown', 'issues': []}
        
        try:
            # Check driver version
            output = subprocess.run("nvidia-smi --query-gpu=driver_version --format=csv,noheader", 
                                  shell=True, capture_output=True, text=True)
            if output.returncode == 0:
                version = output.stdout.strip()
                result['version'] = version
                result['status'] = 'ok'
                
                # Check if version is optimal for RTX 5080
                if not version.startswith('580'):
                    result['issues'].append("Driver may not be optimal for RTX 5080")
                    result['status'] = 'warning'
        except:
            result['status'] = 'error'
            result['issues'].append("Cannot query NVIDIA driver")
        
        self._print_check("NVIDIA Driver", result['status'], f"Version: {result['version']}")
        return result
    
    def _check_cpu_performance(self) -> Dict:
        """Check CPU performance settings"""
        result = {'status': 'ok', 'governor': 'unknown', 'issues': []}
        
        try:
            with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor', 'r') as f:
                governor = f.read().strip()
                result['governor'] = governor
                
                if governor != 'performance':
                    result['status'] = 'warning'
                    result['issues'].append(f"CPU governor is '{governor}', not 'performance'")
        except:
            result['status'] = 'error'
            result['issues'].append("Cannot read CPU governor")
        
        self._print_check("CPU Performance", result['status'], f"Governor: {result['governor']}")
        return result
    
    def _check_memory(self) -> Dict:
        """Check memory configuration"""
        result = {'status': 'ok', 'total_gb': 0, 'available_gb': 0, 'issues': []}
        
        try:
            import psutil
            mem = psutil.virtual_memory()
            result['total_gb'] = mem.total / (1024**3)
            result['available_gb'] = mem.available / (1024**3)
            
            if result['total_gb'] < 60:  # Less than expected 64GB
                result['status'] = 'warning'
                result['issues'].append(f"Only {result['total_gb']:.1f}GB RAM detected")
            
            if mem.percent > 80:
                result['status'] = 'warning'
                result['issues'].append(f"High memory usage: {mem.percent:.1f}%")
        except:
            result['status'] = 'error'
        
        self._print_check("Memory", result['status'], 
                         f"Total: {result['total_gb']:.1f}GB, Available: {result['available_gb']:.1f}GB")
        return result
    
    def _check_disk_performance(self) -> Dict:
        """Check disk I/O performance"""
        result = {'status': 'ok', 'scheduler': 'unknown', 'issues': []}
        
        try:
            # Check NVMe scheduler
            nvme_devices = Path('/sys/block').glob('nvme*')
            for device in nvme_devices:
                sched_file = device / 'queue/scheduler'
                if sched_file.exists():
                    with open(sched_file, 'r') as f:
                        scheduler = f.read().strip()
                        if 'none' not in scheduler and 'kyber' not in scheduler:
                            result['status'] = 'warning'
                            result['issues'].append(f"{device.name} not using optimal scheduler")
        except:
            result['status'] = 'error'
        
        self._print_check("Disk Performance", result['status'], "NVMe optimization check")
        return result
    
    def _check_thermals(self) -> Dict:
        """Check system thermals"""
        result = {'status': 'ok', 'cpu_temp': 0, 'gpu_temp': 0, 'issues': []}
        
        try:
            # Check GPU temp
            output = subprocess.run("nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader", 
                                  shell=True, capture_output=True, text=True)
            if output.returncode == 0:
                gpu_temp = float(output.stdout.strip())
                result['gpu_temp'] = gpu_temp
                
                if gpu_temp > 85:
                    result['status'] = 'warning'
                    result['issues'].append(f"GPU temperature high: {gpu_temp}°C")
        except:
            pass
        
        self._print_check("Thermals", result['status'], 
                         f"GPU: {result['gpu_temp']}°C")
        return result
    
    def _check_services(self) -> Dict:
        """Check gaming-related services"""
        result = {'status': 'ok', 'services': {}, 'issues': []}
        
        services_to_check = [
            'gaming-optimizations.service',
            'gamemoded.service',
            'nvidia-persistenced.service'
        ]
        
        for service in services_to_check:
            try:
                output = subprocess.run(f"systemctl is-active {service}", 
                                      shell=True, capture_output=True, text=True)
                is_active = 'active' in output.stdout
                result['services'][service] = is_active
                
                if not is_active and 'gaming-optimizations' in service:
                    result['status'] = 'warning'
                    result['issues'].append(f"{service} is not active")
            except:
                pass
        
        active_count = sum(1 for v in result['services'].values() if v)
        self._print_check("Services", result['status'], 
                         f"{active_count}/{len(services_to_check)} services active")
        return result
    
    def _check_kernel_parameters(self) -> Dict:
        """Check kernel boot parameters"""
        result = {'status': 'ok', 'parameters': [], 'issues': []}
        
        try:
            with open('/proc/cmdline', 'r') as f:
                cmdline = f.read().strip()
                result['parameters'] = cmdline.split()
                
                # Check for gaming optimizations
                important_params = ['mitigations=off', 'threadirqs', 'preempt=full']
                for param in important_params:
                    if param not in cmdline:
                        result['status'] = 'info'
                        result['issues'].append(f"Missing optimization: {param}")
        except:
            result['status'] = 'error'
        
        self._print_check("Kernel Parameters", result['status'], "Boot optimizations check")
        return result
    
    def _print_check(self, name: str, status: str, details: str):
        """Print a health check result"""
        if status == 'ok':
            symbol = f"{Colors.OKGREEN}✓{Colors.ENDC}"
        elif status == 'warning':
            symbol = f"{Colors.WARNING}⚠{Colors.ENDC}"
        elif status == 'error':
            symbol = f"{Colors.FAIL}✗{Colors.ENDC}"
        else:
            symbol = f"{Colors.OKBLUE}ℹ{Colors.ENDC}"
        
        print(f"{symbol} {name}: {details}")
    
    def _print_summary(self, results: Dict):
        """Print health check summary"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}HEALTH CHECK SUMMARY{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        total_checks = len(results['checks'])
        ok_count = sum(1 for c in results['checks'].values() if c['status'] == 'ok')
        warning_count = sum(1 for c in results['checks'].values() if c['status'] == 'warning')
        error_count = sum(1 for c in results['checks'].values() if c['status'] == 'error')
        
        print(f"Total Checks: {total_checks}")
        print(f"{Colors.OKGREEN}Passed: {ok_count}{Colors.ENDC}")
        print(f"{Colors.WARNING}Warnings: {warning_count}{Colors.ENDC}")
        print(f"{Colors.FAIL}Errors: {error_count}{Colors.ENDC}")
        
        # Print recommendations
        if warning_count > 0 or error_count > 0:
            print(f"\n{Colors.OKBLUE}Recommendations:{Colors.ENDC}")
            for check_name, check_data in results['checks'].items():
                for issue in check_data.get('issues', []):
                    print(f"  • {issue}")

# ============================================================================
# MAIN MANAGER CLASS
# ============================================================================

class GamingSystemManager:
    """Main gaming system manager"""
    
    def __init__(self):
        self.mode_controller = GamingModeController()
        self.profile_manager = GameProfileManager()
        self.health_checker = SystemHealthChecker()
    
    def interactive_menu(self):
        """Interactive management menu"""
        while True:
            print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
            print(f"{Colors.HEADER}BAZZITE GAMING SYSTEM MANAGER{Colors.ENDC}")
            print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
            
            # Show current status
            status = self.mode_controller.get_status()
            status_color = Colors.OKGREEN if status['enabled'] else Colors.WARNING
            print(f"Gaming Mode: {status_color}{'ENABLED' if status['enabled'] else 'DISABLED'}{Colors.ENDC}")
            print(f"CPU Governor: {status['cpu_governor']}")
            print(f"GPU Mode: {status['gpu_mode']}")
            
            print(f"\n{Colors.OKBLUE}Options:{Colors.ENDC}")
            print("1. Toggle Gaming Mode")
            print("2. Toggle Compositor")
            print("3. Manage Game Profiles")
            print("4. Quick Fixes")
            print("5. System Health Check")
            print("6. Clear All Caches")
            print("7. Create Preset Profiles")
            print("0. Exit")
            
            choice = input(f"\n{Colors.OKCYAN}Select option: {Colors.ENDC}")
            
            if choice == '1':
                if status['enabled']:
                    self.mode_controller.disable_gaming_mode()
                else:
                    self.mode_controller.enable_gaming_mode()
            
            elif choice == '2':
                self.mode_controller.toggle_compositor()
            
            elif choice == '3':
                self._manage_profiles_menu()
            
            elif choice == '4':
                self._quick_fixes_menu()
            
            elif choice == '5':
                self.health_checker.run_all_checks()
                input("\nPress Enter to continue...")
            
            elif choice == '6':
                QuickFixUtilities.clear_caches()
                input("\nPress Enter to continue...")
            
            elif choice == '7':
                self.profile_manager.create_preset_profiles()
                input("\nPress Enter to continue...")
            
            elif choice == '0':
                break
    
    def _manage_profiles_menu(self):
        """Profile management submenu"""
        while True:
            print(f"\n{Colors.OKBLUE}Game Profile Management:{Colors.ENDC}")
            
            profiles = self.profile_manager.list_profiles()
            if profiles:
                print("Available profiles:")
                for i, profile in enumerate(profiles, 1):
                    print(f"  {i}. {profile}")
            
            print("\nOptions:")
            print("1. Apply Profile")
            print("2. Create New Profile")
            print("3. Delete Profile")
            print("0. Back")
            
            choice = input(f"\n{Colors.OKCYAN}Select option: {Colors.ENDC}")
            
            if choice == '1' and profiles:
                profile_num = input("Enter profile number: ")
                try:
                    profile_idx = int(profile_num) - 1
                    if 0 <= profile_idx < len(profiles):
                        self.profile_manager.apply_profile(profiles[profile_idx])
                except:
                    print(f"{Colors.FAIL}Invalid selection{Colors.ENDC}")
            
            elif choice == '2':
                name = input("Profile name: ")
                self.profile_manager.create_profile(name, {})
            
            elif choice == '3' and profiles:
                profile_num = input("Enter profile number to delete: ")
                try:
                    profile_idx = int(profile_num) - 1
                    if 0 <= profile_idx < len(profiles):
                        self.profile_manager.delete_profile(profiles[profile_idx])
                except:
                    print(f"{Colors.FAIL}Invalid selection{Colors.ENDC}")
            
            elif choice == '0':
                break
    
    def _quick_fixes_menu(self):
        """Quick fixes submenu"""
        while True:
            print(f"\n{Colors.OKBLUE}Quick Fixes:{Colors.ENDC}")
            print("1. Fix Steam Issues")
            print("2. Fix Audio Crackling")
            print("3. Reload GPU Driver")
            print("4. Clear Shader Caches")
            print("5. Optimize Game Files")
            print("0. Back")
            
            choice = input(f"\n{Colors.OKCYAN}Select option: {Colors.ENDC}")
            
            if choice == '1':
                QuickFixUtilities.fix_steam_issues()
            elif choice == '2':
                QuickFixUtilities.fix_audio_crackling()
            elif choice == '3':
                QuickFixUtilities.fix_gpu_driver()
            elif choice == '4':
                QuickFixUtilities.clear_caches()
            elif choice == '5':
                path = input("Enter game path: ")
                QuickFixUtilities.optimize_game_files(path)
            elif choice == '0':
                break
            
            if choice in ['1', '2', '3', '4', '5']:
                input("\nPress Enter to continue...")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Gaming System Manager')
    parser.add_argument('--enable', action='store_true', help='Enable gaming mode')
    parser.add_argument('--disable', action='store_true', help='Disable gaming mode')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--health', action='store_true', help='Run health check')
    parser.add_argument('--profile', type=str, help='Apply game profile')
    parser.add_argument('--fix', choices=['steam', 'audio', 'gpu', 'caches'], 
                       help='Apply quick fix')
    
    args = parser.parse_args()
    
    # Check if running with proper privileges
    if os.geteuid() != 0 and not args.status:
        print(f"{Colors.WARNING}Note: Some features require root privileges (use sudo){Colors.ENDC}")
    
    controller = GamingModeController()
    
    # Handle command line arguments
    if args.enable:
        controller.enable_gaming_mode()
    elif args.disable:
        controller.disable_gaming_mode()
    elif args.status:
        status = controller.get_status()
        print(json.dumps(status, indent=2))
    elif args.health:
        checker = SystemHealthChecker()
        checker.run_all_checks()
    elif args.profile:
        manager = GameProfileManager()
        manager.apply_profile(args.profile)
    elif args.fix:
        if args.fix == 'steam':
            QuickFixUtilities.fix_steam_issues()
        elif args.fix == 'audio':
            QuickFixUtilities.fix_audio_crackling()
        elif args.fix == 'gpu':
            QuickFixUtilities.fix_gpu_driver()
        elif args.fix == 'caches':
            QuickFixUtilities.clear_caches()
    else:
        # Interactive mode
        manager = GamingSystemManager()
        try:
            manager.interactive_menu()
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Exiting...{Colors.ENDC}")

if __name__ == "__main__":
    sys.exit(main())
