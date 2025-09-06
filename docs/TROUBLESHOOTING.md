# Troubleshooting Guide

**Last Updated**: September 6, 2025

## Master Script Built-in Diagnostics

The **bazzite-optimizer.py master script** includes comprehensive built-in diagnostics, validation systems, and recovery mechanisms for all 16 optimizer classes and gaming profiles.

### Primary Diagnostic Commands
```bash
# Complete system validation and health check
./bazzite-optimizer.py --validate

# Check version and available options
./bazzite-optimizer.py --version
./bazzite-optimizer.py --list-profiles

# Dry-run to see what would be done
./bazzite-optimizer.py --verify

# Emergency rollback if issues occur  
sudo ./bazzite-optimizer.py --rollback

# Apply safer balanced profile for testing
sudo ./bazzite-optimizer.py --profile balanced
```

### Component-Specific Diagnostics
The master script's 16 optimizer classes include built-in validation:

```bash
# System hardware detection and validation
./bazzite-optimizer.py --validate

# Test specific profiles to isolate issues  
sudo ./bazzite-optimizer.py --profile competitive  # Maximum performance
sudo ./bazzite-optimizer.py --profile balanced     # Safe default
sudo ./bazzite-optimizer.py --profile streaming    # Background processes
sudo ./bazzite-optimizer.py --profile creative     # Content creation

# Verification mode shows exactly what each profile does
./bazzite-optimizer.py --verify --profile competitive
```

### Supporting Tools Diagnostics (Optional)
```bash
# Quick health check with supporting tools
./gaming-manager-suite.py --health
./gaming-monitor-suite.py --test
./gaming-maintenance-suite.sh --health-check
```

## Master Script Issue Resolution (v1.0.4)

### 1. Critical Compatibility Issues - RESOLVED in v1.0.4

#### Problem: Script fails with "invalid literal for int() with base 10" error
**Status: ✅ RESOLVED in v1.0.4**

```bash
# Previously failed on modern Linux kernels
ValueError: invalid literal for int() with base 10: '4-104'
```

**Root Cause**: Modern Linux kernels like "6.16.4-104.bazzite.fc42.x86_64" contain hyphens that broke simple dot-splitting logic.

**Solution**: v1.0.4 implements regex-based kernel version parsing:
```python
# Old method (failed): tuple(map(int, platform.release().split('.')[:3]))
# New method (works): re.match(r'^(\d+)\.(\d+)\.(\d+)', platform.release()).groups()
```

#### Problem: Script reports "Free Disk: 0 GB" and fails prerequisite checks
**Status: ✅ RESOLVED in v1.0.4**

**Root Cause**: Bazzite's composefs architecture creates read-only overlays at root (/) with 0 bytes free by design.

**Solution**: v1.0.4 implements smart disk space detection with priority mount points:
1. `/var/home` (user data) - Primary check
2. `/sysroot` (system root) - Secondary check 
3. `/var` (system data) - Tertiary check
4. `/` (fallback) - Final check

Filters out small overlays (< 100GB) to focus on actual storage devices.

### 2. Master Script Optimization Failures

#### Problem: Profile application fails
```bash
# Check system compatibility
./bazzite-optimizer.py --validate

# Try safer balanced profile instead of competitive
sudo ./bazzite-optimizer.py --profile balanced

# Use verification mode to see what would be applied
./bazzite-optimizer.py --verify --profile balanced
```

**Solution Steps:**
1. **Hardware Validation**: Ensure RTX 5080 + i9-10850K + 64GB RAM configuration
2. **Driver Check**: Verify NVIDIA 570.86.16+ or 580.xx series drivers
3. **System Compatibility**: Check Bazzite Linux version and fsync kernel
4. **Safety Fallback**: Use balanced profile for initial testing

#### Problem: System instability after optimization
```bash
# Emergency rollback to previous stable state
sudo ./bazzite-optimizer.py --rollback

# Validate current system state
./bazzite-optimizer.py --validate

# Apply less aggressive profile
sudo ./bazzite-optimizer.py --profile balanced
```

**Built-in Safety Features (v1.0.3 Enhanced):**
- **Automatic Rollback**: StabilityTester triggers rollback on <95% stability
- **Thermal Protection**: Emergency throttling at 90°C GPU / 100°C CPU
- **Backup Manager**: Automatic configuration backups with SHA256 integrity validation
- **Validation Systems**: Hardware compatibility and safety checks
- **Signal Handling**: Graceful shutdown with SIGINT/SIGTERM support for safe interruption
- **Atomic Operations**: Secure file operations using tempfile to prevent corruption
- **Statistical Validation**: Confidence intervals for benchmark results and stability testing

## D-Bus Session Issues (v1.0.6)

### 1. D-Bus Connection Failures - RESOLVED in v1.0.6

#### Problem: "Failed to connect to the user's systemd instance via D-Bus" errors
**Status: ✅ RESOLVED in v1.0.6**

```bash
# Previously failed with D-Bus connection errors
systemctl --user status
Failed to connect to the user's systemd instance via D-Bus: Connection refused
```

**Root Cause**: Single-stage D-Bus validation was insufficient for Bazzite's complex user session architecture.

**Solution**: v1.0.6 implements 3-stage progressive D-Bus validation (Lines 3544-3576):

```python
# Stage 1: Basic systemd accessibility test
systemctl --user status

# Stage 2: D-Bus connectivity verification  
systemctl --user list-units --type=service --no-pager

# Stage 3: Manual session bus validation (comprehensive fallback)
systemd --user --test
```

#### Problem: Audio system health scores artificially low (25%)
**Status: ✅ RESOLVED in v1.0.6**

**Root Cause**: Unrealistic thresholds for Bazzite's PipeWire ecosystem (21+ processes normal).

**Solution**: Calibrated thresholds for realistic scoring:
- **Process Count**: 20→30 threshold (Line 3922) 
- **Health Score**: 60%→50% requirement (Line 3934)
- **Expected Results**: Health scores >70% vs previous 25%

#### Problem: PipeWire service restart cascades and "Host is down" errors
**Status: ✅ RESOLVED in v1.0.6**

**Solution**: Sequenced service restart with dependency management (Lines 3587-3647):

```bash
# Dependency-aware stop sequence
systemctl --user stop wireplumber
sleep 1
systemctl --user stop pipewire-pulse  
sleep 1
systemctl --user stop pipewire

# Socket cleanup
rm -f /run/user/1000/pulse/native
rm -f /run/user/1000/pipewire-0*

# Dependency-aware start sequence (reverse order)
systemctl --user start pipewire
sleep 2
systemctl --user start pipewire-pulse
sleep 2  
systemctl --user start wireplumber
sleep 3  # Final stabilization
```

### 2. D-Bus Session Debugging Procedures

#### Manual D-Bus Session Validation
```bash
# Test all three validation stages manually
systemctl --user status
systemctl --user list-units --type=service --no-pager
systemd --user --test

# Check D-Bus environment variables
echo $DBUS_SESSION_BUS_ADDRESS
echo $XDG_RUNTIME_DIR

# Validate user session persistence
loginctl show-user $USER
loginctl list-sessions
```

#### Audio System Health Debugging  
```bash
# Check realistic process counts (21+ processes normal on Bazzite)
ps aux | grep -E "(pipewire|pulse|wire)" | wc -l

# Comprehensive audio device enumeration
wpctl status
pw-cli info all
pactl list sources
pactl list sinks

# Socket status verification
ls -la /run/user/1000/pulse/
ls -la /run/user/1000/pipewire*
```

#### Emergency Recovery Procedures
```bash
# Emergency rollback for critical D-Bus failures (Lines 3649-3668)
sudo ./bazzite-optimizer.py --emergency-rollback

# Manual emergency recovery if script unavailable
systemctl --user stop wireplumber pipewire-pulse pipewire pulseaudio
sudo systemctl restart systemd-user-sessions
systemctl --user daemon-reload
systemctl --user start pipewire pipewire-pulse wireplumber
```
**Symptoms:**
- `./gaming-manager-suite.py --enable` reports errors
- System performance doesn't improve during gaming
- GameMode not detected by monitoring tools

**Diagnostic Steps:**
```bash
# Check GameMode installation
rpm -qa | grep gamemode
which gamemode

# Check GameMode configuration
cat ~/.config/gamemode.ini
ls -la /usr/share/gamemode/

# Test GameMode manually
gamemoderun echo "GameMode test"
```

**Solutions:**

**Missing GameMode:**
```bash
# Install GameMode
sudo dnf install gamemode gamemode-devel

# Enable user access
sudo usermod -aG gamemode $USER
newgrp gamemode
```

**Permission Issues:**
```bash
# Fix GameMode permissions
sudo chmod +s /usr/bin/gamemode*
sudo systemctl restart gamemode

# Verify group membership
groups $USER | grep gamemode
```

**Configuration Issues:**
```bash
# Create user GameMode configuration
mkdir -p ~/.config
cat << EOF > ~/.config/gamemode.ini
[general]
reaper_freq=5
desiredgov=performance
defaultgov=powersave

[filter]
whitelist=steam
whitelist=lutris
whitelist=wine

[gpu]
apply_gpu_optimisations=accept_responsibility
amd_performance_level=high
EOF
```

### 2. NVIDIA Driver Problems

#### Problem: NVIDIA GPU not detected or underperforming
**Symptoms:**
- `nvidia-smi` command fails or shows errors
- Poor gaming performance despite high-end GPU
- Temperature and power readings unavailable

**Diagnostic Steps:**
```bash
# Check NVIDIA driver installation
nvidia-smi
lspci | grep -i nvidia
lsmod | grep nvidia

# Check driver version compatibility
cat /proc/driver/nvidia/version
rpm -qa | grep nvidia

# Verify kernel module loading
dmesg | grep -i nvidia
modinfo nvidia
```

**Solutions:**

**Driver Installation Issues:**
```bash
# Remove conflicting drivers
sudo dnf remove xorg-x11-drv-nouveau

# Install NVIDIA drivers
sudo dnf install akmod-nvidia xorg-x11-drv-nvidia-cuda

# For RTX 5080 (Blackwell), ensure -open variant
sudo dnf install nvidia-driver-open

# Rebuild initramfs
sudo dracut --force

# Reboot and verify
sudo reboot
nvidia-smi
```

**DRM Modeset Issues:**
```bash
# Add kernel parameters for proper DRM support
sudo grubby --update-kernel=ALL --args="nvidia-drm.modeset=1 nvidia-drm.fbdev=1"

# Verify parameters after reboot
cat /proc/cmdline | grep nvidia-drm

# Check DRM status
cat /sys/module/nvidia_drm/parameters/modeset
```

**Power Management Issues:**
```bash
# Set maximum performance mode
nvidia-settings -a [gpu:0]/GpuPowerMizerMode=1

# Make persistent
nvidia-settings -a [gpu:0]/GPUPowerMizerMode=1
nvidia-settings --store-rc-file ~/.nvidia-settings-rc

# Verify power mode
nvidia-smi -q -d POWER
```

### 3. CPU Performance Issues

#### Problem: CPU not reaching boost clocks or poor performance
**Symptoms:**
- CPU frequency stuck at base clocks during gaming
- High CPU usage with poor performance
- Thermal throttling occurring prematurely

**Diagnostic Steps:**
```bash
# Check CPU frequency scaling
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq
cpupower frequency-info

# Check CPU governor
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
cpupower frequency-info -o proc

# Monitor CPU behavior during load
watch -n 1 'cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq | head -10'
```

**Solutions:**

**Governor Issues:**
```bash
# Set performance governor
sudo cpupower frequency-set -g performance

# Make persistent
echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpupower

# Enable cpupower service
sudo systemctl enable --now cpupower.service
```

**C-state Optimization:**
```bash
# Add C-state limitation for gaming
sudo grubby --update-kernel=ALL --args="intel_idle.max_cstate=1"

# Verify after reboot
cat /proc/cmdline | grep intel_idle

# Check current C-state limits
cat /sys/devices/system/cpu/cpu*/cpuidle/state*/disable
```

**Thermal Throttling:**
```bash
# Check temperature sensors
sensors
sudo sensors-detect

# Monitor thermal throttling
dmesg | grep -i thermal
journalctl -k | grep -i throttl

# Check CPU thermal limits
cat /sys/class/thermal/thermal_zone*/temp
cat /sys/class/thermal/thermal_zone*/type
```

### 4. Memory and ZRAM Issues

#### Problem: High memory usage or ZRAM not working optimally
**Symptoms:**
- System running out of memory during gaming
- ZRAM not compressing effectively
- Excessive swap usage

**Diagnostic Steps:**
```bash
# Check memory usage
free -h
cat /proc/meminfo

# Check ZRAM status
zramctl
cat /proc/swaps

# Monitor memory pressure
vmstat 1 5
sar -r 1 5
```

**Solutions:**

**ZRAM Configuration Issues:**
```bash
# Check current ZRAM setup
zramctl -f

# Reconfigure ZRAM with optimal settings
sudo tee /etc/systemd/zram-generator.conf << EOF
[zram0]
zram-size = min(ram / 8, 8192)
compression-algorithm = lz4
options = discard
EOF

# Restart ZRAM
sudo systemctl restart systemd-zram-setup@zram0.service

# Verify new configuration
zramctl
```

**Swappiness Optimization:**
```bash
# Check current swappiness
cat /proc/sys/vm/swappiness

# Set optimal swappiness for gaming
echo 'vm.swappiness = 120' | sudo tee -a /etc/sysctl.conf
echo 'vm.page-cluster = 0' | sudo tee -a /etc/sysctl.conf

# Apply immediately
sudo sysctl -p

# Verify settings
sysctl vm.swappiness vm.page-cluster
```

**Memory Leak Detection:**
```bash
# Monitor memory usage over time
while true; do
    echo "$(date): $(free -h | grep '^Mem')"
    sleep 300
done > memory-usage.log

# Find memory-hungry processes
ps aux --sort=-%mem | head -20
pmap -d $(pgrep steam)
```

### 5. Storage Performance Issues

#### Problem: Slow game loading or poor I/O performance
**Symptoms:**
- Long game loading times
- Stuttering during asset streaming
- Poor benchmark results for storage

**Diagnostic Steps:**
```bash
# Check I/O scheduler
cat /sys/block/nvme*/queue/scheduler

# Monitor I/O activity
iostat -x 1 5
iotop -d 1

# Check storage health
sudo smartctl -a /dev/nvme0n1
```

**Solutions:**

**I/O Scheduler Optimization:**
```bash
# Set optimal scheduler for NVMe (none/noop for performance)
echo none | sudo tee /sys/block/nvme0n1/queue/scheduler

# Make persistent via udev rule
sudo tee /etc/udev/rules.d/60-nvme-scheduler.rules << EOF
ACTION=="add|change", KERNEL=="nvme[0-9]*", ATTR{queue/scheduler}="none"
EOF

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

**Mount Options Optimization:**
```bash
# Check current mount options
mount | grep nvme

# Add optimal mount options to /etc/fstab
# Example line (adjust UUID accordingly):
# UUID=your-uuid / btrfs subvol=root,noatime,discard=async,commit=60 0 0

# Remount with new options (if safe to do so)
sudo mount -o remount,noatime,discard=async /
```

**TRIM and Maintenance:**
```bash
# Enable periodic TRIM
sudo systemctl enable --now fstrim.timer

# Manual TRIM
sudo fstrim -av

# Check TRIM support
sudo hdparm -I /dev/nvme0n1 | grep TRIM
```

### 6. Network Performance Issues

#### Problem: High latency or packet loss affecting online gaming
**Symptoms:**
- High ping in online games
- Frequent network timeouts
- Inconsistent connection quality

**Diagnostic Steps:**
```bash
# Test network connectivity
ping -c 10 8.8.8.8
traceroute google.com

# Check network interface status
ip link show
ethtool eth0  # or your interface name

# Monitor network performance
iftop -i eth0
nethogs
```

**Solutions:**

**Network Interface Optimization:**
```bash
# Optimize network interface settings
sudo ethtool -G eth0 rx 4096 tx 4096  # Increase buffer sizes
sudo ethtool -K eth0 gro on gso on tso on  # Enable offloading

# Set interrupt moderation
sudo ethtool -C eth0 adaptive-rx on adaptive-tx on

# Make settings persistent
sudo tee /etc/systemd/system/network-optimize.service << EOF
[Unit]
Description=Network Interface Optimization
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/sbin/ethtool -G eth0 rx 4096 tx 4096
ExecStart=/usr/sbin/ethtool -K eth0 gro on gso on tso on
ExecStart=/usr/sbin/ethtool -C eth0 adaptive-rx on adaptive-tx on
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable network-optimize.service
```

**DNS Optimization:**
```bash
# Use fast DNS servers
sudo tee /etc/systemd/resolved.conf << EOF
[Resolve]
DNS=1.1.1.1 8.8.8.8 8.8.4.4
FallbackDNS=1.0.0.1
Cache=yes
DNSSEC=no
EOF

# Restart DNS resolver
sudo systemctl restart systemd-resolved

# Test DNS performance
dig @1.1.1.1 google.com
dig @8.8.8.8 google.com
```

### 7. Audio System Issues (v1.0.5+ D-Bus Environment Enhancement)

#### Problem: Audio devices not detected or service responsiveness failures
**Symptoms:**
- Sound card, headset, or HDMI audio not working
- PipeWire/PulseAudio conflicts and service responsiveness failures
- "Address already in use" socket errors
- D-Bus session bus connection issues with user services
- User services failing to start properly due to environment context
- Hardware devices missing from audio control panels

**Diagnostic Steps:**
```bash
# Check D-Bus environment for user services
echo "DBUS_SESSION_BUS_ADDRESS: $DBUS_SESSION_BUS_ADDRESS"
echo "XDG_RUNTIME_DIR: $XDG_RUNTIME_DIR"
dbus-send --session --dest=org.freedesktop.DBus --type=method_call --print-reply /org/freedesktop/DBus org.freedesktop.DBus.GetId

# Check user session lingering
loginctl show-user $USER
loginctl user-status $USER

# Check PipeWire/PulseAudio status with proper environment
systemctl --user status pipewire pipewire-pulse wireplumber
pw-cli info all
wpctl status

# Check for socket conflicts
ls -la /run/user/1000/pulse/
ps aux | grep -E "(pipewire|pulseaudio)"

# Audio device enumeration
lsusb | grep -i audio
lspci | grep -i audio
arecord -l && aplay -l
```

**Resolution:**
```bash
# D-Bus Environment and Audio System Recovery (Enhanced 4-strategy approach)

# Strategy 1: D-Bus Environment and User Session Setup
# Enable user session lingering for persistent services
loginctl enable-linger $USER
# Wait for linger to take effect
sleep 2

# Strategy 2: Complete environment reset with proper D-Bus context  
systemctl --user stop pipewire pipewire-pulse wireplumber
# Clean socket conflicts
rm -f /run/user/1000/pulse/native
# Restart with proper D-Bus environment
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus"
export XDG_RUNTIME_DIR="/run/user/$(id -u)"

# Strategy 3: Service restart with socket cleanup
systemctl --user start pipewire pipewire-pulse

# Strategy 2: Complete daemon restart
systemctl --user daemon-reload
systemctl --user restart pipewire pipewire-pulse pipewire-media-session

# Strategy 3: Full audio subsystem reset
pkill -f pipewire
pkill -f pulseaudio
sleep 2
systemctl --user start pipewire

# Validate recovery
pw-cli info all | head -10
wpctl status
```

**Hardware-Specific Recovery:**
- **Creative Sound Blaster X3**: Check USB connection and driver status
- **Corsair HS70 Wireless**: Verify wireless receiver and charging status  
- **NVIDIA HDMI Audio**: Ensure HDMI cable connected and display active
- **Razer Kiyo Webcam**: Check USB port and webcam integration

#### Problem: Audio optimization causing device failures
**Symptoms:**
- Audio optimization script causes hardware device loss
- Network, USB, or sound devices stop working after optimization
- System becomes unstable after audio tuning

**Diagnostic Steps:**
```bash
# Identify problematic optimization sections
# Check critical script sections (bazzite-optimizer.py):
# - IRQ affinity optimization (lines 587-590)
# - Core isolation settings (lines 3512-3513)  
# - Thermald service management (lines 2909-2910)
# - Audio optimization routines (lines 3176-3225)

# Enable debug logging for detailed analysis
# Edit bazzite-optimizer.py line 1634:
# console_handler.setLevel(logging.DEBUG)
```

**Resolution:**
```bash
# Selective rollback of audio optimizations
sudo ./bazzite-optimizer.py --rollback

# Apply safer balanced profile instead
sudo ./bazzite-optimizer.py --profile balanced

# Manual service restoration if needed
sudo systemctl restart NetworkManager
sudo systemctl --user restart pipewire
```

### 8. System76 Scheduler Issues

#### Problem: System76-scheduler not working or misconfigured
**Symptoms:**
- Gaming processes not getting priority
- System feels sluggish during gaming
- Background processes interfering with games

**Diagnostic Steps:**
```bash
# Check scheduler status
systemctl status system76-scheduler

# Check configuration
cat /etc/system76-scheduler/config.kdl

# Monitor process priorities
ps axo pid,ppid,user,comm,nice,pri,psr
```

**Solutions:**

**Service Issues:**
```bash
# Restart scheduler service
sudo systemctl restart system76-scheduler

# Check logs for errors
journalctl -u system76-scheduler -f

# Enable if not running
sudo systemctl enable --now system76-scheduler
```

**Configuration Issues:**
```bash
# Backup current config
sudo cp /etc/system76-scheduler/config.kdl /etc/system76-scheduler/config.kdl.backup

# Reset to default configuration
sudo tee /etc/system76-scheduler/config.kdl << 'EOF'
processes = {
    game = {
        nice = -10
        ioClass = 1
        ioNice = 4
    }
    
    cpu-intensive = {
        nice = 19
        ioClass = 3
    }
}

assignments = {
    "steam" = "game"
    "gamemoderun" = "game"
    "lutris" = "game"
    "wine" = "game"
    "proton" = "game"
}
EOF

# Restart service to apply changes
sudo systemctl restart system76-scheduler
```

## Advanced Troubleshooting

### Performance Profiling
```bash
# CPU profiling with perf
sudo dnf install perf
sudo perf record -a -g sleep 30
sudo perf report

# System-wide tracing
sudo dnf install trace-cmd
sudo trace-cmd record -p function_graph sleep 10
trace-cmd report
```

### Hardware Debugging
```bash
# Check hardware errors
dmesg | grep -i error
journalctl -p err -x

# Monitor hardware sensors
watch -n 1 sensors

# Check PCIe link status
sudo lspci -vvv | grep -A 10 -i "nvidia\|vga"
```

### Log Analysis
```bash
# Gaming suite logs
tail -f /var/log/gaming-benchmark/*.log
tail -f /var/log/gaming-metrics/*.log

# System logs
journalctl -f -u gamemode -u system76-scheduler
dmesg -w | grep -i "gpu\|cpu\|memory"

# Application logs
journalctl --user -u steam
~/.local/share/Steam/logs/
```

## Getting Help

### Information to Gather
Before reporting issues, collect:

```bash
# System information
./gaming-manager-suite.py --health > system-health.txt

# Hardware information
lscpu > hardware-info.txt
lspci >> hardware-info.txt
free -h >> hardware-info.txt
lsblk >> hardware-info.txt

# Driver information
nvidia-smi >> driver-info.txt 2>/dev/null || echo "No NVIDIA GPU" >> driver-info.txt
rpm -qa | grep -E "(nvidia|gamemode|system76)" >> driver-info.txt

# Configuration files
cp ~/.config/gaming-manager/config.json config-backup.json 2>/dev/null || echo "No config found"
```

### Reporting Issues
1. **Search existing issues** on GitHub
2. **Use appropriate issue template** (bug/performance/feature)
3. **Include diagnostic information** from above
4. **Describe reproduction steps** clearly
5. **Specify expected vs actual behavior**

### Community Resources
- **GitHub Issues**: https://github.com/doublegate/Bazzite-Config/issues
- **Discussions**: https://github.com/doublegate/Bazzite-Config/discussions
- **Bazzite Community**: https://reddit.com/r/bazzite
- **Linux Gaming**: https://reddit.com/r/linux_gaming

## 6. Script Template Issues (v1.0.5 Production Ready)

### Template Generation Errors
**Problem**: Master script template generation fails with KeyError or ValueError exceptions

**Symptoms:**
- Python .format() method conflicts with bash variable syntax
- KeyError exceptions when generating optimization scripts
- ValueError during script template rendering
- Template validation failures

**Diagnostic Steps:**
```bash
# Test template generation
./bazzite-optimizer.py --test-templates

# Check template validation
python3 -c "
import bazzite_optimizer
try:
    result = bazzite_optimizer.generate_master_script()
    print('Template generation: SUCCESS')
    print(f'Generated script length: {len(result)} characters')
except Exception as e:
    print(f'Template generation FAILED: {e}')
"
```

**Solutions (v1.0.5 Production Ready Resolution):**

**Template Engine Breakthrough (COMPLETELY RESOLVED):**
- **100% Resolution**: Complete elimination of Python .format() conflicts with bash syntax
- **Systematic Escaping**: All bash variables properly escaped with double-brace {{variable}} format
- **Parameter Expansion**: Fixed `${VAR:-default}` → `${{VAR:-default}}` patterns
- **Function Definitions**: Corrected `function() {` → `function() {{` and `}` → `}}` escaping
- **AWK Commands**: Fixed `{print $1}` → `{{print $1}}` for pattern compatibility
- **MCP Debug Integration**: zen debug workflow implementation for systematic resolution

**Production Template Validation Results:**
- MASTER_GAMING_SCRIPT: 7,832 characters - ✅ PRODUCTION READY
- NVIDIA_OPTIMIZATION_SCRIPT: 3,561 characters - ✅ PRODUCTION READY  
- CPU_OPTIMIZATION_SCRIPT: 3,110 characters - ✅ PRODUCTION READY
- **Total Coverage**: 14,503+ characters validated error-free across all templates
- **Error Elimination**: 100% elimination of KeyError/ValueError exceptions in template generation

### Emergency Recovery

#### Reset Gaming Optimizations
```bash
# Disable all gaming optimizations
./gaming-manager-suite.py --disable --force

# Reset to system defaults
sudo rm -f /var/run/gaming-mode.state
sudo systemctl restart system76-scheduler gamemode
```

#### System Recovery
```bash
# Boot to previous ostree deployment
sudo rpm-ostree rollback
sudo reboot

# Reset kernel parameters
sudo grubby --update-kernel=ALL --remove-args="intel_idle.max_cstate=1 nvidia-drm.modeset=1"
sudo reboot
```

Remember: Always backup important configurations before making changes, and test optimizations in a controlled environment first.