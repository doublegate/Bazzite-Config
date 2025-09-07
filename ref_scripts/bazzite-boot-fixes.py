#!/usr/bin/env python3
"""
Bazzite Gaming Optimizer v4.1 - Boot Configuration Fixes
Complete resolution of kernel parameter duplicates and boot errors
"""

import os
import re
import subprocess
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional, Set

class KernelBootOptimizer:
    """Handles kernel parameters and boot configuration with duplicate prevention"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.grub_config = "/etc/default/grub"
        self.grub_backup = "/etc/default/grub.bazzite-backup"
        self.existing_params: Set[str] = set()
        
    def backup_grub_config(self) -> bool:
        """Create backup of GRUB configuration"""
        try:
            if not self.dry_run and os.path.exists(self.grub_config):
                # Create timestamped backup
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                backup_path = f"{self.grub_backup}.{timestamp}"
                shutil.copy2(self.grub_config, backup_path)
                print(f"✓ GRUB config backed up to {backup_path}")
                
                # Also create a "latest" backup
                shutil.copy2(self.grub_config, self.grub_backup)
            return True
        except Exception as e:
            print(f"✗ Failed to backup GRUB config: {e}")
            return False
    
    def parse_kernel_params(self, cmdline: str) -> Dict[str, List[str]]:
        """Parse kernel parameters and detect duplicates"""
        params = {}
        # Split by spaces but handle quoted strings
        tokens = re.findall(r'(?:[^\s"]|"(?:\\.|[^"])*")+', cmdline)
        
        for token in tokens:
            if '=' in token:
                key, value = token.split('=', 1)
                if key not in params:
                    params[key] = []
                params[key].append(value)
            else:
                if token not in params:
                    params[token] = []
                params[token].append('')
        
        return params
    
    def clean_kernel_params(self, cmdline: str) -> str:
        """Remove duplicate kernel parameters, keeping last occurrence"""
        # Parse existing parameters
        params = self.parse_kernel_params(cmdline)
        
        # Parameters that should be preserved from ostree/bazzite
        preserve_params = {
            'BOOT_IMAGE', 'root', 'rootflags', 'ostree', 'rhgb', 'quiet', 'splash'
        }
        
        # Parameters we manage (will be removed and re-added cleanly)
        managed_params = {
            'mitigations', 'processor.max_cstate', 'intel_idle.max_cstate',
            'intel_pstate', 'transparent_hugepage', 'nvme_core.default_ps_max_latency_us',
            'pcie_aspm', 'intel_iommu', 'iommu', 'threadirqs', 'preempt',
            'nvidia-drm.modeset', 'nvidia-drm.fbdev', 'amdgpu.ppfeaturemask',
            'bluetooth.disable_ertm', 'pci', 'nohz_full', 'rcu_nocbs', 'isolcpus',
            'tsc', 'clocksource', 'intel_pstate', 'nmi_watchdog'
        }
        
        # Build cleaned parameter list
        cleaned = []
        seen_managed = set()
        
        for key, values in params.items():
            # Skip if it's a managed parameter (we'll add it cleanly later)
            base_key = key.split('.')[0] if '.' in key else key
            if base_key in managed_params or key in managed_params:
                continue
                
            # Keep preserved parameters as-is
            if key in preserve_params:
                if values and values[0]:
                    cleaned.append(f"{key}={values[0]}")
                else:
                    cleaned.append(key)
            # For other parameters, keep only the last occurrence
            elif values:
                if values[-1]:
                    cleaned.append(f"{key}={values[-1]}")
                else:
                    cleaned.append(key)
        
        return ' '.join(cleaned)
    
    def get_optimized_kernel_params(self, profile: str) -> Dict[str, str]:
        """Get optimized kernel parameters based on profile"""
        
        # Base parameters for all profiles
        base_params = {
            'transparent_hugepage': 'madvise',
            'nvme_core.default_ps_max_latency_us': '0',
            'intel_iommu': 'on',
            'iommu': 'pt',
            'threadirqs': '',
            'preempt': 'full',
            'nvidia-drm.modeset': '1',
            'nvidia-drm.fbdev': '1',
            'amdgpu.ppfeaturemask': '0xffffffff',
            'bluetooth.disable_ertm': '1',
            'pci': 'realloc',  # Fix PCI resource allocation issues
            'tsc': 'reliable',  # More stable TSC
            'clocksource': 'tsc',
            'nmi_watchdog': '0'  # Disable for lower latency
        }
        
        # Profile-specific parameters
        profile_params = {
            'balanced': {
                'mitigations': 'auto',
                'processor.max_cstate': '3',
                'intel_idle.max_cstate': '3',
                'intel_pstate': 'active',
                'pcie_aspm': 'default'
            },
            'performance': {
                'mitigations': 'off',
                'processor.max_cstate': '1',
                'intel_idle.max_cstate': '1',
                'intel_pstate': 'active',
                'pcie_aspm': 'off'
            },
            'competitive': {
                'mitigations': 'off',
                'processor.max_cstate': '0',
                'intel_idle.max_cstate': '0',
                'intel_pstate': 'active',
                'pcie_aspm': 'off',
                'nohz_full': '4-19',  # Isolate cores 4-19 for gaming
                'rcu_nocbs': '4-19',
                'isolcpus': 'nohz,domain,4-19'
            },
            'streaming': {
                'mitigations': 'auto',
                'processor.max_cstate': '2',
                'intel_idle.max_cstate': '2',
                'intel_pstate': 'active',
                'pcie_aspm': 'default'
            }
        }
        
        # Merge base and profile parameters
        params = base_params.copy()
        params.update(profile_params.get(profile, profile_params['balanced']))
        
        return params
    
    def update_grub_config(self, profile: str) -> bool:
        """Update GRUB configuration with optimized parameters"""
        try:
            if not os.path.exists(self.grub_config):
                print(f"✗ GRUB config not found at {self.grub_config}")
                return False
            
            # Read current config
            with open(self.grub_config, 'r') as f:
                lines = f.readlines()
            
            # Get optimized parameters
            new_params = self.get_optimized_kernel_params(profile)
            
            # Process each line
            updated_lines = []
            cmdline_updated = False
            
            for line in lines:
                if line.startswith('GRUB_CMDLINE_LINUX='):
                    # Extract current cmdline
                    match = re.match(r'GRUB_CMDLINE_LINUX="([^"]*)"', line)
                    if match:
                        current_cmdline = match.group(1)
                        
                        # Clean existing parameters
                        cleaned_cmdline = self.clean_kernel_params(current_cmdline)
                        
                        # Add new optimized parameters
                        param_strings = []
                        for key, value in new_params.items():
                            if value:
                                param_strings.append(f"{key}={value}")
                            else:
                                param_strings.append(key)
                        
                        # Combine cleaned and new parameters
                        final_cmdline = f"{cleaned_cmdline} {' '.join(param_strings)}"
                        
                        # Remove any double spaces
                        final_cmdline = re.sub(r'\s+', ' ', final_cmdline).strip()
                        
                        # Update the line
                        updated_lines.append(f'GRUB_CMDLINE_LINUX="{final_cmdline}"\n')
                        cmdline_updated = True
                        
                        print(f"✓ Updated kernel parameters for {profile} profile")
                        print(f"  Removed {len(self.parse_kernel_params(current_cmdline)) - len(self.parse_kernel_params(cleaned_cmdline))} duplicate parameters")
                    else:
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)
            
            # Write updated config
            if not self.dry_run and cmdline_updated:
                with open(self.grub_config, 'w') as f:
                    f.writelines(updated_lines)
                print(f"✓ GRUB configuration updated")
                
                # Regenerate GRUB config
                return self.regenerate_grub()
            
            return cmdline_updated
            
        except Exception as e:
            print(f"✗ Failed to update GRUB config: {e}")
            return False
    
    def regenerate_grub(self) -> bool:
        """Regenerate GRUB configuration"""
        try:
            if self.dry_run:
                print("  [DRY RUN] Would regenerate GRUB configuration")
                return True
            
            # Detect the correct command for the system
            grub_commands = [
                ['grub2-mkconfig', '-o', '/boot/grub2/grub.cfg'],
                ['grub2-mkconfig', '-o', '/boot/efi/EFI/fedora/grub.cfg'],
                ['update-grub'],
                ['grub-mkconfig', '-o', '/boot/grub/grub.cfg']
            ]
            
            for cmd in grub_commands:
                if shutil.which(cmd[0]):
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"✓ GRUB configuration regenerated")
                        return True
                    else:
                        print(f"  Warning: {cmd[0]} returned non-zero: {result.stderr}")
            
            print("✗ Could not regenerate GRUB configuration")
            return False
            
        except Exception as e:
            print(f"✗ Failed to regenerate GRUB: {e}")
            return False
    
    def validate_boot_config(self) -> Dict[str, bool]:
        """Validate boot configuration and check for issues"""
        results = {}
        
        # Check for duplicate parameters in current cmdline
        try:
            with open('/proc/cmdline', 'r') as f:
                current_cmdline = f.read().strip()
            
            params = self.parse_kernel_params(current_cmdline)
            duplicates = {k: v for k, v in params.items() if len(v) > 1}
            
            if duplicates:
                print("\n⚠ Found duplicate kernel parameters:")
                for param, values in duplicates.items():
                    print(f"  - {param}: appears {len(values)} times")
                results['duplicates'] = False
            else:
                print("✓ No duplicate kernel parameters found")
                results['duplicates'] = True
                
        except Exception as e:
            print(f"✗ Could not check current kernel parameters: {e}")
            results['duplicates'] = False
        
        # Check if PCI realloc is set (fixes resource allocation)
        if 'pci=realloc' in current_cmdline:
            print("✓ PCI reallocation enabled")
            results['pci_realloc'] = True
        else:
            print("⚠ PCI reallocation not enabled (may cause resource issues)")
            results['pci_realloc'] = False
        
        return results


class ModuleOptimizer:
    """Handles kernel module configuration and fixes"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.modprobe_dir = "/etc/modprobe.d"
        
    def fix_module_issues(self) -> bool:
        """Fix kernel module loading issues"""
        success = True
        
        # Remove NCT6687 module if it's not compatible with this system
        nct6687_conf = f"{self.modprobe_dir}/nct6687.conf"
        if os.path.exists(nct6687_conf):
            try:
                if not self.dry_run:
                    os.remove(nct6687_conf)
                print("✓ Removed incompatible NCT6687 module configuration")
            except Exception as e:
                print(f"✗ Failed to remove NCT6687 config: {e}")
                success = False
        
        # Fix nvidia_peermem module (not available with open kernel modules)
        nvidia_conf = f"{self.modprobe_dir}/nvidia-gaming.conf"
        if os.path.exists(nvidia_conf):
            try:
                with open(nvidia_conf, 'r') as f:
                    content = f.read()
                
                # Remove nvidia_peermem references (incompatible with open driver)
                content = re.sub(r'^.*nvidia_peermem.*\n', '', content, flags=re.MULTILINE)
                
                if not self.dry_run:
                    with open(nvidia_conf, 'w') as f:
                        f.write(content)
                print("✓ Fixed NVIDIA module configuration")
                
            except Exception as e:
                print(f"✗ Failed to fix NVIDIA config: {e}")
                success = False
        
        # Create blacklist for problematic modules
        blacklist_conf = f"{self.modprobe_dir}/bazzite-blacklist.conf"
        blacklist_content = """# Blacklist problematic modules
# NCT6687 Super I/O chip - not present on this motherboard
blacklist nct6687

# NVIDIA peermem - not compatible with open kernel modules
blacklist nvidia_peermem

# Disable PC speaker beep
blacklist pcspkr

# Disable Intel MEI if not needed
# blacklist mei_me
# blacklist mei
"""
        
        try:
            if not self.dry_run:
                with open(blacklist_conf, 'w') as f:
                    f.write(blacklist_content)
                os.chmod(blacklist_conf, 0o644)
            print("✓ Created module blacklist")
        except Exception as e:
            print(f"✗ Failed to create blacklist: {e}")
            success = False
        
        return success
    
    def fix_systemd_modules(self) -> bool:
        """Fix systemd module loading configuration"""
        modules_load_dir = "/etc/modules-load.d"
        gaming_modules = f"{modules_load_dir}/gaming-optimizations.conf"
        
        # Correct module list (remove incompatible ones)
        correct_modules = """# Gaming optimization modules
i2c_dev
fuse
# msr - built-in, no need to load
gcadapter_oc
kvmfr
pkcs8_key_parser
uhid
ntsync
# nvidia modules loaded automatically
# nct6687 - not compatible with this motherboard
"""
        
        try:
            if not self.dry_run:
                with open(gaming_modules, 'w') as f:
                    f.write(correct_modules)
                os.chmod(gaming_modules, 0o644)
            print("✓ Fixed systemd module loading configuration")
            return True
        except Exception as e:
            print(f"✗ Failed to fix module loading: {e}")
            return False


class NetworkOptimizer:
    """Handles network configuration fixes"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        
    def fix_tcp_bbr(self) -> bool:
        """Fix TCP BBR congestion control configuration"""
        sysctl_dir = "/etc/sysctl.d"
        gaming_sysctl = f"{sysctl_dir}/99-gaming-network.conf"
        
        try:
            # Check if BBR is available
            tcp_cc_path = "/proc/sys/net/ipv4/tcp_available_congestion_control"
            bbr_available = False
            
            if os.path.exists(tcp_cc_path):
                with open(tcp_cc_path, 'r') as f:
                    available_cc = f.read().strip()
                    if 'bbr' in available_cc:
                        bbr_available = True
            
            # Read current sysctl config
            if os.path.exists(gaming_sysctl):
                with open(gaming_sysctl, 'r') as f:
                    content = f.read()
            else:
                content = ""
            
            if bbr_available:
                # BBR is available, ensure it's properly configured
                if 'tcp_congestion_control' not in content:
                    content += "\n# TCP BBR congestion control\n"
                    content += "net.ipv4.tcp_congestion_control=bbr\n"
                    content += "net.core.default_qdisc=fq\n"
                print("✓ TCP BBR congestion control available and configured")
            else:
                # BBR not available, use cubic instead
                content = re.sub(r'^net\.ipv4\.tcp_congestion_control=bbr.*\n', 
                                'net.ipv4.tcp_congestion_control=cubic\n', 
                                content, flags=re.MULTILINE)
                print("✓ TCP BBR not available, using cubic instead")
                
                # Try to load BBR module
                if not self.dry_run:
                    subprocess.run(['modprobe', 'tcp_bbr'], 
                                 capture_output=True, check=False)
            
            # Write updated config
            if not self.dry_run and content:
                with open(gaming_sysctl, 'w') as f:
                    f.write(content)
                
                # Apply sysctl settings
                subprocess.run(['sysctl', '--system'], 
                             capture_output=True, check=False)
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to fix TCP congestion control: {e}")
            return False


class USBFixes:
    """Handle USB device issues"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        
    def fix_ite_usb_device(self) -> bool:
        """Fix ITE USB device disconnect issues"""
        udev_rules = "/etc/udev/rules.d/99-ite-usb-fix.rules"
        
        # Create udev rule to handle the problematic ITE device
        rule_content = """# Fix for ITE Device (048d:5702) disconnect issues
# This device appears to be an RGB controller that doesn't properly enumerate

# Ignore the device to prevent constant reconnection attempts
SUBSYSTEM=="usb", ATTRS{idVendor}=="048d", ATTRS{idProduct}=="5702", ATTR{authorized}="0"

# Alternative: Add a delay before initialization
# SUBSYSTEM=="usb", ATTRS{idVendor}=="048d", ATTRS{idProduct}=="5702", RUN+="/bin/sh -c 'sleep 1'"

# If you need this device for RGB control, comment the first rule and uncomment this:
# SUBSYSTEM=="usb", ATTRS{idVendor}=="048d", ATTRS{idProduct}=="5702", ATTR{quirks}="0x00000002"
"""
        
        try:
            if not self.dry_run:
                with open(udev_rules, 'w') as f:
                    f.write(rule_content)
                os.chmod(udev_rules, 0o644)
                
                # Reload udev rules
                subprocess.run(['udevadm', 'control', '--reload-rules'], 
                             capture_output=True, check=False)
                subprocess.run(['udevadm', 'trigger'], 
                             capture_output=True, check=False)
                
            print("✓ Created USB device fix for ITE RGB controller")
            return True
            
        except Exception as e:
            print(f"✗ Failed to fix USB device issues: {e}")
            return False


class SystemGroupsFix:
    """Fix missing system groups that cause tmpfiles warnings"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        
    def create_missing_groups(self) -> bool:
        """Create missing system groups"""
        required_groups = {
            'audio': 63,
            'disk': 6,
            'kvm': 36,
            'lp': 7,
            'video': 39,
            'render': 105,
            'sgx': 106,
            'input': 104,
            'utmp': 22,
            'adm': 4,
            'wheel': 10
        }
        
        success = True
        for group, gid in required_groups.items():
            try:
                # Check if group exists
                result = subprocess.run(['getent', 'group', group], 
                                      capture_output=True, check=False)
                
                if result.returncode != 0:
                    # Group doesn't exist, create it
                    if not self.dry_run:
                        cmd = ['groupadd', '-g', str(gid), group]
                        result = subprocess.run(cmd, capture_output=True, check=False)
                        
                        if result.returncode == 0:
                            print(f"✓ Created missing group: {group}")
                        else:
                            # Try without specific GID if it's already taken
                            cmd = ['groupadd', group]
                            result = subprocess.run(cmd, capture_output=True, check=False)
                            if result.returncode == 0:
                                print(f"✓ Created missing group: {group}")
                            else:
                                print(f"✗ Failed to create group {group}")
                                success = False
                                
            except Exception as e:
                print(f"✗ Error checking/creating group {group}: {e}")
                success = False
        
        return success


def apply_boot_fixes(profile: str = 'balanced', dry_run: bool = False):
    """Apply all boot configuration fixes"""
    
    print("\n" + "="*60)
    print("Bazzite Gaming Optimizer - Boot Configuration Fixes v4.1")
    print("="*60)
    print(f"Profile: {profile}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print("="*60 + "\n")
    
    # Initialize components
    kernel_opt = KernelBootOptimizer(dry_run)
    module_opt = ModuleOptimizer(dry_run)
    network_opt = NetworkOptimizer(dry_run)
    usb_fix = USBFixes(dry_run)
    groups_fix = SystemGroupsFix(dry_run)
    
    results = {}
    
    # Step 1: Backup GRUB configuration
    print("\n[1/7] Backing up GRUB configuration...")
    results['grub_backup'] = kernel_opt.backup_grub_config()
    
    # Step 2: Fix kernel parameters
    print("\n[2/7] Fixing kernel parameters...")
    results['kernel_params'] = kernel_opt.update_grub_config(profile)
    
    # Step 3: Fix module issues
    print("\n[3/7] Fixing kernel module issues...")
    results['modules'] = module_opt.fix_module_issues()
    results['systemd_modules'] = module_opt.fix_systemd_modules()
    
    # Step 4: Fix network configuration
    print("\n[4/7] Fixing network configuration...")
    results['network'] = network_opt.fix_tcp_bbr()
    
    # Step 5: Fix USB device issues
    print("\n[5/7] Fixing USB device issues...")
    results['usb'] = usb_fix.fix_ite_usb_device()
    
    # Step 6: Create missing system groups
    print("\n[6/7] Creating missing system groups...")
    results['groups'] = groups_fix.create_missing_groups()
    
    # Step 7: Validate configuration
    print("\n[7/7] Validating boot configuration...")
    validation = kernel_opt.validate_boot_config()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    total = len(results)
    successful = sum(1 for v in results.values() if v)
    
    for task, result in results.items():
        status = "✓" if result else "✗"
        print(f"{status} {task.replace('_', ' ').title()}")
    
    print(f"\nCompleted: {successful}/{total} tasks successful")
    
    if not dry_run and results.get('kernel_params'):
        print("\n⚠ IMPORTANT: Reboot required for kernel parameter changes to take effect")
        print("  Run: sudo systemctl reboot")
    
    return successful == total


def main():
    """Main entry point for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fix boot configuration issues for Bazzite gaming optimization"
    )
    parser.add_argument(
        '--profile',
        choices=['balanced', 'performance', 'competitive', 'streaming'],
        default='balanced',
        help='Gaming profile to apply'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    
    args = parser.parse_args()
    
    # Check for root privileges
    if not args.dry_run and os.geteuid() != 0:
        print("✗ This script must be run as root (use sudo)")
        return 1
    
    # Apply fixes
    success = apply_boot_fixes(args.profile, args.dry_run)
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
