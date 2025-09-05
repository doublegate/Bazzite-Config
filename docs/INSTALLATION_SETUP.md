# Installation & Setup Guide

## Master Script Installation

The Bazzite Gaming Optimization Suite centers around the **bazzite-optimizer.py master script** (4,649 lines, 165KB) - your complete gaming optimization solution with 16 specialized optimizer classes, 4 gaming profiles, and advanced safety systems.

## Master Script Overview (v1.0.4)

**bazzite-optimizer.py** is the **primary, comprehensive optimization tool** featuring:
- **Complete Implementation**: 4,649 lines of production-ready code
- **Bazzite Compatibility**: Critical bug fixes for composefs/immutable filesystem support
- **Kernel Parsing**: Regex-based version detection for modern Linux kernels (6.16.4-104.bazzite.fc42.x86_64)
- **Smart Disk Detection**: Priority-based mount point analysis (/var/home, /sysroot, /var, /)
- **16 Specialized Optimizers**: CPU, GPU, Memory, Network, Audio, Kernel, and more
- **4 Gaming Profiles**: Competitive, Balanced, Streaming, Creative configurations
- **Advanced Safety Systems**: StabilityTester, ThermalManager, BackupManager with SHA256 integrity
- **Integrated Benchmarking**: Built-in BenchmarkRunner with statistical analysis
- **Signal Handling**: Graceful shutdown with SIGINT/SIGTERM support
- **Atomic Operations**: Secure file operations using Python's tempfile module

The **supporting scripts** (gaming-manager-suite.py, gaming-monitor-suite.py, gaming-maintenance-suite.sh) provide **auxiliary functionality** for quick access utilities, real-time monitoring, and manual benchmarking.

## Prerequisites

### System Requirements

**Operating System**
- Bazzite Linux (latest stable release recommended)
- Fedora-based immutable distribution with rpm-ostree
- fsync kernel with gaming optimizations

**Optimized Hardware Configuration**
- **CPU**: Intel i9-10850K Comet Lake (optimized configuration)
- **GPU**: NVIDIA RTX 5080 Blackwell architecture (optimized configuration)
- **RAM**: 64GB DDR4 (optimized configuration)
- **Storage**: Samsung 990 EVO Plus NVMe SSD (optimized configuration)

**Software Dependencies**
- Python 3.8+ with psutil and threading support
- NVIDIA 570.86.16 beta or newer 580.xx series drivers
- System76-scheduler and GameMode integration

### Hardware-Specific Notes

#### NVIDIA GPU Configuration
- **Driver Requirement**: NVIDIA 570.86.16 beta or newer 580.xx series
- **Driver Variant**: Use `-open` driver variant for RTX 5080 Blackwell architecture
- **Kernel Parameters**: Required for optimal performance
```bash
nvidia-drm.modeset=1 nvidia-drm.fbdev=1
```

#### Intel CPU Requirements
- **Architecture**: 10th gen or newer recommended
- **Features**: Intel SpeedStep, C-states control
- **Cooling**: Adequate cooling for sustained performance mode

## Quick Installation

### Master Script Setup (Recommended)

1. **Clone the repository:**
   ```bash
   cd ~/Code  # or your preferred directory
   git clone https://github.com/doublegate/Bazzite-Config.git
   cd Bazzite-Config
   ```

2. **Make master script executable:**
   ```bash
   chmod +x bazzite-optimizer.py
   ```

3. **Install system dependencies:**
   ```bash
   # Essential Python packages
   sudo dnf install python3-psutil python3-configparser python3-threading
   
   # Benchmarking and testing tools
   sudo dnf install stress-ng sysbench
   
   # NVIDIA tools for RTX 5080
   sudo dnf install nvidia-settings nvidia-ml
   ```

4. **Verify master script installation:**
   ```bash
   ./bazzite-optimizer.py --validate
   ```

### Supporting Tools Setup (Optional)

If you want the additional monitoring and quick-fix utilities:

```bash
# Make supporting scripts executable
chmod +x gaming-manager-suite.py gaming-monitor-suite.py gaming-maintenance-suite.sh

# Test supporting tools
./gaming-manager-suite.py --health
```

### Method 2: Development Setup

For contributors or developers who want to modify the suite:

1. **Fork the repository** on GitHub
2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/Bazzite-Config.git
   cd Bazzite-Config
   ```

3. **Set up development environment:**
   ```bash
   # Install development tools
   sudo dnf install python3-devel python3-pip
   pip3 install --user pylint black isort mypy
   
   # Set up git hooks (optional)
   git config core.hooksPath .githooks
   ```

## Detailed Installation

### Step 1: System Preparation

**Update your Bazzite system:**
```bash
rpm-ostree upgrade
systemctl reboot
```

**Verify Bazzite version:**
```bash
rpm-ostree status
```

**Check kernel version:**
```bash
uname -r
```
Expected: 6.x kernel with fsync patches

### Step 2: Hardware Detection

**Check CPU information:**
```bash
lscpu | grep "Model name"
cat /proc/cpuinfo | grep "model name" | head -1
```

**Check GPU information:**
```bash
# For NVIDIA GPUs
nvidia-smi

# For AMD GPUs  
lspci | grep VGA
```

**Check memory configuration:**
```bash
free -h
cat /proc/meminfo | grep MemTotal
```

**Check storage devices:**
```bash
lsblk -d -o NAME,SIZE,MODEL
```

### Step 3: Dependency Installation

#### Core Python Dependencies
```bash
# Essential packages
sudo dnf install python3-psutil python3-configparser python3-curses

# Optional but recommended
sudo dnf install python3-devel python3-pip
```

#### Benchmarking Tools
```bash
# CPU benchmarking
sudo dnf install stress-ng sysbench

# Storage benchmarking
sudo dnf install fio hdparm

# Network benchmarking (optional)
sudo dnf install iperf3 netperf
```

#### System Monitoring Tools
```bash
# Performance monitoring
sudo dnf install htop iotop nethogs

# Hardware monitoring
sudo dnf install lm_sensors smartmontools
```

#### NVIDIA-Specific Tools (if applicable)
```bash
# NVIDIA utilities
sudo dnf install nvidia-settings nvidia-ml

# For overclocking support
sudo nvidia-xconfig --cool-bits=28
```

### Step 4: Configuration Setup

#### Create Configuration Directories
```bash
# User configuration
mkdir -p ~/.config/gaming-manager/profiles
mkdir -p ~/.local/share/gaming-benchmarks

# System directories (requires sudo)
sudo mkdir -p /var/log/gaming-benchmark
sudo mkdir -p /var/log/gaming-metrics
sudo chown $USER:$USER /var/log/gaming-benchmark /var/log/gaming-metrics
```

#### Initial Configuration
```bash
# Run initial health check
./gaming-manager-suite.py --health

# Create default game profiles
./gaming-manager-suite.py --create-defaults
```

### Step 5: System Integration

#### Enable GameMode (if not already enabled)
```bash
ujust setup-gamemode
```

#### Configure System76 Scheduler
```bash
# Check if already running
systemctl status system76-scheduler

# Enable if not active
sudo systemctl enable --now system76-scheduler
```

#### Set up ZRAM (for memory optimization)
```bash
# Check current ZRAM configuration
zramctl

# Configure optimal ZRAM settings
sudo tee /etc/systemd/zram-generator.conf << EOF
[zram0]
zram-size = min(ram / 8, 8192)
compression-algorithm = lz4
EOF
```

## Verification & Testing

### Master Script Testing
```bash
# List available gaming profiles
./bazzite-optimizer.py --list-profiles

# System validation and health check
./bazzite-optimizer.py --validate

# Apply balanced profile optimization (default)
sudo ./bazzite-optimizer.py --profile balanced

# Apply competitive gaming profile
sudo ./bazzite-optimizer.py --profile competitive

# Run with integrated benchmarking
sudo ./bazzite-optimizer.py --benchmark

# Verification commands only (dry-run)
./bazzite-optimizer.py --verify

# Emergency rollback if needed
sudo ./bazzite-optimizer.py --rollback

# Check version information
./bazzite-optimizer.py --version
```

### Supporting Tools Testing (Optional)
```bash
# Test Gaming Manager
./gaming-manager-suite.py --status
./gaming-manager-suite.py --health

# Test Gaming Monitor (simple mode)
./gaming-monitor-suite.py --mode simple --interval 2

# Test Gaming Maintenance (health check only)
./gaming-maintenance-suite.sh --health-check
```

### Gaming Profile Testing
```bash
# Test all 4 gaming profiles with the master script
sudo ./bazzite-optimizer.py --profile competitive
sudo ./bazzite-optimizer.py --profile balanced
sudo ./bazzite-optimizer.py --profile streaming  
sudo ./bazzite-optimizer.py --profile creative

# Verify profile application
./bazzite-optimizer.py --validate
```

### Interactive Testing
```bash
# Launch full monitoring dashboard
./gaming-monitor-suite.py --mode dashboard

# Launch interactive maintenance menu
./gaming-maintenance-suite.sh
```

## Configuration

### Game Profile Creation

**Create a custom game profile:**
```bash
# Interactive profile creation
./gaming-manager-suite.py --create-profile

# Or manually create in ~/.config/gaming-manager/profiles/
cat << EOF > ~/.config/gaming-manager/profiles/cyberpunk2077.json
{
  "name": "Cyberpunk 2077",
  "cpu_governor": "performance",
  "gpu_mode": "max_performance",
  "compositor": "disabled",
  "nice_value": -10,
  "environment": {
    "DXVK_HUD": "fps,memory",
    "VKD3D_CONFIG": "dxr"
  }
}
EOF
```

### System Optimization Settings

**Create system configuration:**
```bash
sudo tee /etc/gaming-mode.conf << EOF
[gaming]
enabled = false
cpu_governor = performance
gpu_mode = max_performance
compositor_control = true

[monitoring]
update_interval = 2
log_metrics = true
export_format = json

[maintenance]
auto_cleanup = true
benchmark_on_startup = false
EOF
```

## Troubleshooting Installation

### Common Issues

#### Permission Errors
```bash
# Fix script permissions
chmod +x gaming-manager-suite.py gaming-monitor-suite.py gaming-maintenance-suite.sh

# Fix directory permissions
sudo chown -R $USER:$USER ~/.config/gaming-manager
sudo chown -R $USER:$USER ~/.local/share/gaming-benchmarks
```

#### Missing Dependencies
```bash
# Check for missing Python modules
python3 -c "import psutil, configparser, curses; print('All modules available')"

# Install missing tools
sudo dnf install $(cat << EOF
python3-psutil
python3-configparser
stress-ng
sysbench
nvidia-settings
EOF
)
```

#### NVIDIA Driver Issues
```bash
# Check NVIDIA driver status
nvidia-smi

# Reinstall NVIDIA drivers if needed
sudo dnf reinstall nvidia-driver

# Verify DRM modeset
cat /sys/module/nvidia_drm/parameters/modeset
```

#### System76 Scheduler Issues
```bash
# Check scheduler status
systemctl status system76-scheduler

# Restart scheduler
sudo systemctl restart system76-scheduler

# Check configuration
cat /etc/system76-scheduler/config.kdl
```

### Health Check Interpretation

**Run comprehensive health check:**
```bash
./gaming-manager-suite.py --health
```

**Expected Output Indicators:**
- ✅ System76-scheduler: Active
- ✅ GameMode: Available
- ✅ NVIDIA drivers: Loaded (if applicable)
- ✅ Python dependencies: Satisfied
- ✅ Configuration directories: Created
- ✅ Permissions: Correct

### Log File Locations

**Debug Information:**
```bash
# Gaming Manager logs
ls -la ~/.config/gaming-manager/logs/

# System benchmark logs
ls -la /var/log/gaming-benchmark/

# Monitoring logs
ls -la /var/log/gaming-metrics/

# System logs
journalctl -u system76-scheduler
journalctl -u gamemode
```

## Next Steps

After successful installation:

1. **Read the User Guide**: Familiarize yourself with available commands
2. **Create Game Profiles**: Set up optimization profiles for your games
3. **Run Benchmarks**: Establish performance baselines
4. **Monitor Performance**: Use the monitoring dashboard during gaming
5. **Join the Community**: Contribute to the project on GitHub

## Getting Help

If you encounter issues during installation:

1. **Check the logs** for error messages
2. **Run health check** to identify problems
3. **Review troubleshooting** section above
4. **Search existing issues** on GitHub
5. **Create a new issue** with detailed information

**GitHub Repository**: https://github.com/doublegate/Bazzite-Config
**Issue Template**: Use bug report template with system information

---

**Installation complete!** You're now ready to optimize your Bazzite gaming system.