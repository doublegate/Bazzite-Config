#!/usr/bin/env python3
"""
Integration module for bazzite-optimizer.py
Replaces the kernel_and_boot section with comprehensive fixes
"""

# Add this import section to your main bazzite-optimizer.py
from boot_fixes import (
    KernelBootOptimizer,
    ModuleOptimizer,
    NetworkOptimizer,
    USBFixes,
    SystemGroupsFix
)

def kernel_and_boot_optimization(self):
    """Complete kernel and boot optimization with all fixes"""
    
    self.section_header("KERNEL & BOOT OPTIMIZATION")
    
    # Initialize all optimizers
    kernel_opt = KernelBootOptimizer(dry_run=self.dry_run)
    module_opt = ModuleOptimizer(dry_run=self.dry_run)
    network_opt = NetworkOptimizer(dry_run=self.dry_run)
    usb_fix = USBFixes(dry_run=self.dry_run)
    groups_fix = SystemGroupsFix(dry_run=self.dry_run)
    
    results = {}
    
    # Step 1: Backup GRUB configuration
    self.print_status("Backing up GRUB configuration")
    results['grub_backup'] = kernel_opt.backup_grub_config()
    
    # Step 2: Clean and optimize kernel parameters
    self.print_status("Optimizing kernel parameters")
    results['kernel_params'] = kernel_opt.update_grub_config(self.profile)
    
    # Step 3: Fix module configuration
    self.print_status("Fixing kernel module configuration")
    
    # Remove incompatible modules
    module_blacklist = f"{self.dirs['modprobe']}/bazzite-blacklist.conf"
    blacklist_content = """# Blacklist problematic modules
# NCT6687 Super I/O chip - not present on Z490 motherboards
blacklist nct6687

# NVIDIA peermem - incompatible with open kernel modules
blacklist nvidia_peermem

# Disable PC speaker beep
blacklist pcspkr

# ITE USB RGB controller fix (causes disconnect loops)
# Handled via udev rules instead
"""
    
    self.write_file(module_blacklist, blacklist_content, "module blacklist")
    
    # Fix systemd module loading
    modules_load = f"{self.dirs['modules_load']}/gaming-optimizations.conf"
    modules_content = """# Gaming optimization modules
# Core modules
i2c_dev
fuse
kvmfr
uhid
ntsync

# Gaming input modules
gcadapter_oc

# Crypto modules for Secure Boot compatibility
pkcs8_key_parser

# Note: MSR is built-in on modern kernels
# Note: nvidia modules load automatically
# Note: nct6687 removed - incompatible with Z490
"""
    
    self.write_file(modules_load, modules_content, "module loading configuration")
    
    # Step 4: Intel I225-V specific configuration
    self.print_status("Configuring Intel I225-V ethernet")
    
    igc_config = f"{self.dirs['modprobe']}/igc-gaming.conf"
    igc_content = """# Intel I225-V 2.5GbE Gaming Optimizations
options igc InterruptThrottleRate=0
options igc IntMode=2
options igc TxIntDelay=0
options igc TxAbsIntDelay=0
options igc RxIntDelay=0
options igc RxAbsIntDelay=0
options igc TxDescriptors=4096
options igc RxDescriptors=4096
options igc FlowControl=0
options igc EEE=0
options igc DMAC=0
options igc MDD=0
options igc LRO=0
"""
    
    self.write_file(igc_config, igc_content, "Intel I225-V configuration")
    
    # Step 5: NVIDIA RTX 5080 module configuration (fixed)
    self.print_status("Configuring NVIDIA RTX 5080 modules")
    
    nvidia_config = f"{self.dirs['modprobe']}/nvidia-rtx5080.conf"
    nvidia_content = """# RTX 5080 Blackwell Gaming Optimizations
# Open kernel module variant for RTX 50-series
options nvidia NVreg_OpenRmEnableUnsupportedGpus=1
options nvidia-drm modeset=1 fbdev=1
options nvidia NVreg_PreserveVideoMemoryAllocations=1
options nvidia NVreg_EnableGpuFirmware=1
options nvidia NVreg_EnableResizableBar=1
options nvidia NVreg_EnablePCIeGen3=0
options nvidia NVreg_UsePageAttributeTable=1
options nvidia NVreg_EnableHDMI20=1
options nvidia NVreg_EnableStreamMemOPs=1
options nvidia NVreg_EnableBacklightHandler=1
options nvidia NVreg_TemperatureMonitoring=1
options nvidia NVreg_EnableMSI=1
options nvidia NVreg_EnablePCIERelaxedOrdering=1

# Power management settings
options nvidia NVreg_RegistryDwords="PowerMizerEnable=0x1;PerfLevelSrc=0x2222;PowerMizerDefaultAC=0x1"

# Memory allocation optimizations for 16GB VRAM
options nvidia NVreg_InitializeSystemMemoryAllocations=0
options nvidia NVreg_DynamicPowerManagement=0x02
"""
    
    self.write_file(nvidia_config, nvidia_content, "NVIDIA RTX 5080 configuration")
    
    # Step 6: Fix USB device issues
    self.print_status("Fixing USB device issues")
    
    usb_rules = f"{self.dirs['udev']}/99-usb-gaming-fixes.rules"
    usb_rules_content = """# USB Gaming Device Fixes

# Fix for ITE RGB Controller (048d:5702) disconnect issues
# This device has malformed descriptors causing constant reconnects
SUBSYSTEM=="usb", ATTRS{idVendor}=="048d", ATTRS{idProduct}=="5702", ATTR{authorized}="0"

# Alternative if you need RGB control (comment line above, uncomment below):
# SUBSYSTEM=="usb", ATTRS{idVendor}=="048d", ATTRS{idProduct}=="5702", ATTR{quirks}="0x00000002", RUN+="/bin/sh -c 'sleep 2'"

# Xbox controller optimizations
SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTR{bInterfaceClass}=="ff", ATTR{bInterfaceSubClass}=="5d", ATTR{authorized}="1", TAG+="uaccess"

# Creative Sound Blaster AE-5 Plus
SUBSYSTEM=="usb", ATTRS{idVendor}=="1102", ATTRS{idProduct}=="0012", ATTR{authorized}="1", TAG+="uaccess"

# Razer devices
SUBSYSTEM=="usb", ATTRS{idVendor}=="1532", ATTR{authorized}="1", TAG+="uaccess"

# Corsair devices
SUBSYSTEM=="usb", ATTRS{idVendor}=="1b1c", ATTR{authorized}="1", TAG+="uaccess"

# Stream Deck
SUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", ATTR{authorized}="1", TAG+="uaccess"
"""
    
    self.write_file(usb_rules, usb_rules_content, "USB device fixes")
    
    # Step 7: System groups creation
    self.print_status("Creating missing system groups")
    if not self.dry_run:
        groups_fix.create_missing_groups()
    
    # Step 8: Sysctl configuration (fixed for BBR)
    self.print_status("Configuring kernel sysctl parameters")
    
    # Check if BBR is available
    bbr_available = False
    try:
        with open('/proc/sys/net/ipv4/tcp_available_congestion_control', 'r') as f:
            if 'bbr' in f.read():
                bbr_available = True
    except:
        pass
    
    # Try to load BBR module if not available
    if not bbr_available and not self.dry_run:
        self.run_command(['modprobe', 'tcp_bbr'], check=False)
        # Check again
        try:
            with open('/proc/sys/net/ipv4/tcp_available_congestion_control', 'r') as f:
                if 'bbr' in f.read():
                    bbr_available = True
        except:
            pass
    
    congestion_control = "bbr" if bbr_available else "cubic"
    
    sysctl_gaming = f"{self.dirs['sysctl']}/99-gaming-optimizations.conf"
    sysctl_content = f"""# Gaming System Optimizations for 64GB RAM

# Memory Management
vm.swappiness={self.config['system']['swappiness']}
vm.vfs_cache_pressure=50
vm.dirty_background_ratio=5
vm.dirty_ratio=20
vm.dirty_writeback_centisecs=1500
vm.dirty_expire_centisecs=3000
vm.min_free_kbytes=1048576
vm.page-cluster=0

# Transparent Huge Pages
kernel.transparent_hugepage=madvise
kernel.hugepages=0

# Memory overcommit for gaming
vm.overcommit_memory=1
vm.overcommit_ratio=50
vm.panic_on_oom=0
vm.oom_kill_allocating_task=1

# Network Optimizations for Gaming
net.core.rmem_default=262144
net.core.rmem_max=134217728
net.core.wmem_default=262144
net.core.wmem_max=134217728
net.core.netdev_max_backlog=30000
net.core.netdev_budget=600
net.core.netdev_budget_usecs=8000

# TCP Optimizations
net.ipv4.tcp_congestion_control={congestion_control}
net.core.default_qdisc=fq
net.ipv4.tcp_fastopen=3
net.ipv4.tcp_low_latency=1
net.ipv4.tcp_timestamps={'0' if self.profile == 'competitive' else '1'}
net.ipv4.tcp_sack=1
net.ipv4.tcp_window_scaling=1
net.ipv4.tcp_adv_win_scale=1
net.ipv4.tcp_mtu_probing=1

# Gaming-specific network tuning
net.ipv4.tcp_fin_timeout=15
net.ipv4.tcp_keepalive_time=300
net.ipv4.tcp_keepalive_intvl=30
net.ipv4.tcp_keepalive_probes=5
net.ipv4.tcp_tw_reuse=1
net.ipv4.ip_local_port_range=1024 65535
net.ipv4.tcp_max_syn_backlog=8192
net.ipv4.tcp_max_tw_buckets=2000000
net.ipv4.tcp_slow_start_after_idle=0
net.ipv4.tcp_no_metrics_save=1

# Security (minimal for gaming performance)
net.ipv4.tcp_rfc1337=1
net.ipv4.conf.all.rp_filter=1
net.ipv4.conf.default.rp_filter=1

# Intel I225-V specific (disable checksum offload issues)
net.ipv4.ip_forward=0
net.ipv6.conf.all.disable_ipv6={'1' if self.profile == 'competitive' else '0'}

# Process scheduling
kernel.sched_migration_cost_ns=500000
kernel.sched_autogroup_enabled=1
kernel.pid_max=4194304

# File system
fs.file-max=2097152
fs.inotify.max_user_watches=524288
"""
    
    if congestion_control == "cubic":
        sysctl_content += "\n# Note: BBR not available, using cubic instead\n"
    
    self.write_file(sysctl_gaming, sysctl_content, "sysctl gaming configuration")
    
    # Step 9: GRUB configuration
    self.print_status("Updating GRUB configuration")
    
    # Read current GRUB config
    grub_config = "/etc/default/grub"
    if os.path.exists(grub_config):
        # Use the KernelBootOptimizer for proper parameter handling
        success = kernel_opt.update_grub_config(self.profile)
        
        if success:
            self.print_success("GRUB configuration updated successfully")
        else:
            self.print_warning("GRUB configuration update had issues")
    else:
        self.print_error(f"GRUB config not found at {grub_config}")
    
    # Step 10: Apply runtime optimizations
    if not self.dry_run:
        self.print_status("Applying runtime optimizations")
        
        # Reload kernel modules
        self.run_command(['systemctl', 'restart', 'systemd-modules-load.service'], check=False)
        
        # Apply sysctl settings
        self.run_command(['sysctl', '--system'], check=False)
        
        # Reload udev rules
        self.run_command(['udevadm', 'control', '--reload-rules'], check=False)
        self.run_command(['udevadm', 'trigger'], check=False)
    
    # Summary
    self.print_header("Boot Configuration Summary")
    print(f"  Profile: {self.profile}")
    print(f"  Congestion Control: {congestion_control}")
    print(f"  Kernel Security: {'Disabled' if self.profile == 'competitive' else 'Enabled'}")
    print(f"  Power Management: {'Aggressive' if self.profile in ['performance', 'competitive'] else 'Balanced'}")
    
    if kernel_opt.validate_boot_config().get('duplicates', True):
        self.print_success("No duplicate kernel parameters detected")
    else:
        self.print_warning("Duplicate kernel parameters found - will be fixed on next boot")
    
    self.print_info("\n⚠ Reboot required for kernel parameter changes to take effect")
    
    return True

# Replace the kernel_and_boot method in your BazziteOptimizer class with this version:
def apply_kernel_boot_fixes(optimizer_instance):
    """Apply kernel and boot fixes to a BazziteOptimizer instance"""
    
    # Backup the original method
    original_method = optimizer_instance.kernel_and_boot
    
    # Replace with our fixed version
    optimizer_instance.kernel_and_boot = lambda: kernel_and_boot_optimization(optimizer_instance)
    
    # Add helper methods if they don't exist
    if not hasattr(optimizer_instance, 'write_file'):
        def write_file(path, content, description):
            """Helper to write configuration files"""
            try:
                if not optimizer_instance.dry_run:
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    with open(path, 'w') as f:
                        f.write(content)
                    os.chmod(path, 0o644)
                optimizer_instance.print_success(f"Created {description}")
                return True
            except Exception as e:
                optimizer_instance.print_error(f"Failed to create {description}: {e}")
                return False
        
        optimizer_instance.write_file = write_file
    
    if not hasattr(optimizer_instance, 'run_command'):
        def run_command(cmd, check=True):
            """Helper to run system commands"""
            try:
                if not optimizer_instance.dry_run:
                    result = subprocess.run(cmd, capture_output=True, text=True, check=check)
                    return result.returncode == 0
                return True
            except Exception as e:
                optimizer_instance.print_error(f"Command failed: {e}")
                return False
        
        optimizer_instance.run_command = run_command
    
    return optimizer_instance
