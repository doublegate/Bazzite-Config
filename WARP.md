# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository Overview

The Bazzite Gaming Optimization Suite is a comprehensive three-component gaming system management toolset specifically designed for Bazzite Linux systems with high-end hardware configurations (NVIDIA RTX 5080, Intel i9-10850K, 64GB RAM). The suite delivers 15-25% performance improvements through intelligent system tuning and automated optimization.

**Repository URL**: https://github.com/doublegate/Bazzite-Config  
**Primary Platform**: Bazzite Linux (Fedora-based immutable gaming OS)  
**License**: MIT  
**Current Version**: 1.0.1

## Essential Commands

### Prerequisites Installation
```bash
# On Bazzite Linux (primary target platform)
sudo dnf install python3-psutil python3-configparser stress-ng sysbench

# Development tools (optional)
sudo dnf install python3-pip python3-devel pylint
pip3 install --user black isort mypy
```

### Making Scripts Executable
```bash
chmod +x gaming-manager-suite.py gaming-monitor-suite.py gaming-maintenance-suite.sh
```

### Running the Components

#### Gaming Manager Suite (System Control)
```bash
# Enable gaming mode optimizations
./gaming-manager-suite.py --enable

# Disable gaming mode
./gaming-manager-suite.py --disable

# Check system status
./gaming-manager-suite.py --status

# Run comprehensive health check
./gaming-manager-suite.py --health

# Apply game-specific profile
./gaming-manager-suite.py --profile "Cyberpunk 2077"

# Apply quick fixes (steam/audio/gpu/caches)
./gaming-manager-suite.py --fix steam
```

#### Gaming Monitor Suite (Real-time Monitoring)
```bash
# Launch interactive curses dashboard
./gaming-monitor-suite.py --mode dashboard

# Simple text-based output
./gaming-monitor-suite.py --mode simple

# Export metrics to files for analysis
./gaming-monitor-suite.py --mode export

# Set custom update interval (default 2 seconds)
./gaming-monitor-suite.py --interval 5
```

#### Gaming Maintenance Suite (Benchmarking & Maintenance)
```bash
# Interactive menu for all operations
./gaming-maintenance-suite.sh

# Direct command execution
./gaming-maintenance-suite.sh --help
```

### Development Commands
```bash
# Code formatting and linting
python3 -m black gaming-manager-suite.py gaming-monitor-suite.py
python3 -m pylint gaming-manager-suite.py gaming-monitor-suite.py

# Shell script checking
shellcheck gaming-maintenance-suite.sh

# Test script execution
python3 -c "import sys; sys.path.append('.'); from gaming_manager_suite import GamingModeController; print('Import successful')"
```

## Architecture Overview

### Three-Component Architecture
```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│  Gaming Manager     │    │  Gaming Monitor     │    │ Gaming Maintenance  │
│  (Control Panel)    │    │  (Live Metrics)     │    │  (Benchmarks)       │
├─────────────────────┤    ├─────────────────────┤    ├─────────────────────┤
│ • Gaming Mode       │    │ • CPU/GPU Metrics   │    │ • Performance Tests │
│ • Game Profiles     │    │ • Memory Usage      │    │ • System Cleanup    │
│ • Quick Fixes       │    │ • Gaming Processes  │    │ • Maintenance Tasks │
│ • System Health     │    │ • Real-time Display │    │ • Automated Reports │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

### Component Responsibilities

#### Gaming Manager Suite (`gaming-manager-suite.py`)
**Primary Function**: Central control panel for gaming system optimization

**Key Classes**:
- `GamingModeController`: Toggles system-wide gaming optimizations
- `GameProfileManager`: Creates and manages game-specific configurations  
- `QuickFixUtilities`: Instant solutions for Steam, audio, and GPU issues
- `SystemHealthChecker`: Comprehensive system diagnostics

**System Integration**:
- CPU governor control (`performance`/`schedutil`)
- NVIDIA GPU power management and overclocking
- KWin compositor suspension for better performance
- GameMode service integration
- System memory cache clearing and swappiness tuning

#### Gaming Monitor Suite (`gaming-monitor-suite.py`)
**Primary Function**: Real-time performance monitoring with gaming-specific insights

**Key Classes**:
- `MetricsCollector`: Comprehensive system metrics collection
- `TerminalDashboard`: Curses-based real-time monitoring interface

**Monitored Metrics**:
- CPU: Usage per core, frequency, temperature, load average
- GPU: Utilization, memory usage, temperature, power draw, clocks
- Memory: RAM usage, swap, ZRAM compression status
- Gaming: Steam processes, GameMode status, Proton games, compositor state
- Network & Disk: I/O rates, bandwidth, latency

#### Gaming Maintenance Suite (`gaming-maintenance-suite.sh`)
**Primary Function**: Automated benchmarking and system maintenance

**Benchmark Categories**:
- CPU performance testing with stress-ng and sysbench
- GPU performance testing with NVIDIA utilities and OpenGL/Vulkan
- Memory bandwidth validation for ZRAM optimization
- NVMe storage performance testing (Samsung 990 EVO Plus optimized)
- System health diagnostics

## Configuration Management

### Directory Structure
```
~/.config/gaming-manager/profiles/    # Game profiles (JSON format)
~/.local/share/gaming-benchmarks/     # Benchmark results
/var/log/gaming-benchmark/            # Benchmark logs  
/var/log/gaming-metrics/              # Monitoring data
/etc/gaming-mode.conf                 # System configuration
/var/run/gaming-mode.state           # Runtime state file
```

### Game Profile Example
Game profiles are stored as JSON files in `~/.config/gaming-manager/profiles/`:

```json
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
```

## Hardware-Specific Optimizations

### NVIDIA RTX 5080 Configuration
- Blackwell architecture with `-open` driver variant support
- GPU overclocking: +350-525MHz core stable range
- Memory overclocking with proper cooling validation
- DLSS 4 optimization (avoids 4x Frame Generation bug)
- PowerMizer performance mode enforcement

### Intel i9-10850K Tuning  
- Aggressive C-state limitation (`intel_idle.max_cstate=1`)
- Performance governor enforcement
- IRQ affinity optimization for gaming threads
- Optional undervolting support for thermal management

### Memory & Storage (64GB RAM + Samsung 990 EVO Plus)
- Optimized ZRAM configuration (8-16GB with LZ4 compression)
- NVMe tuning with `none`/`noop` I/O scheduler
- Intelligent swappiness settings (120-150 range for high-memory systems)
- Weekly TRIM scheduling via systemd timer

## System Integration with Bazzite

### Bazzite-Specific Integration
The suite integrates with Bazzite's unique features:

- **ujust commands**: Leverages Bazzite's just-based system management
- **System76-scheduler**: Integration for process prioritization
- **GameMode**: Automatic performance switching integration
- **fsync kernel**: Optimized for Bazzite's gaming-focused kernel
- **rpm-ostree**: Considerations for immutable filesystem

### Service Integration
The components work with these system services:
- `gamemoded.service`: GameMode daemon
- `system76-scheduler.service`: Process scheduling optimization
- Power management via `power-profiles-daemon`

### Verification Commands
```bash
# Check gaming mode status
systemctl --user status gamemoded

# Verify system optimizations
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

# Check NVIDIA GPU state
nvidia-smi --query-gpu=name,clocks.gr,clocks.mem --format=csv

# Monitor system logs
journalctl -f --since "1 hour ago" | grep -i gaming
```

## Development Workflow

### Code Style Requirements
- **Python**: Follow PEP 8 with type hints for all functions
- **Shell Scripts**: Use bash with strict mode (`set -euo pipefail`)
- **Error Handling**: Comprehensive exception handling with user-friendly messages
- **Color Consistency**: Use the standardized `Colors` class across all components
- **Logging**: Consistent logging patterns with appropriate levels

### Git Workflow
- **Branching**: Feature branches from `main`
- **Commits**: Conventional commit format (`feat:`, `fix:`, `docs:`, etc.)
- **Pull Requests**: Include tests, documentation updates, and CHANGELOG.md entries
- **Review**: All changes require review for system integration safety

### Key Development Patterns
- **Modular Architecture**: Separate classes for different functional areas
- **Configuration-Driven**: JSON-based profiles and settings
- **Safety-First**: Validation and rollback capabilities for system changes
- **Hardware Abstraction**: Detection and fallback for different hardware configurations

## Testing and Validation

### Manual Testing Requirements
Before submitting changes:
1. Test all command-line options for affected components
2. Verify system integration on Bazzite Linux
3. Check privilege escalation and sudo prompts
4. Validate error conditions and recovery paths
5. Test with different hardware configurations when possible

### Hardware Validation Matrix
Test combinations:
- **GPUs**: NVIDIA RTX (primary), AMD (future), Intel (basic)
- **CPUs**: Intel (primary), AMD (compatibility)
- **Sessions**: X11, Wayland, Gamescope
- **Storage**: NVMe (optimized), SATA SSD, traditional HDD

### Smoke Tests
```bash
# Component startup tests
./gaming-manager-suite.py --status
./gaming-monitor-suite.py --mode simple --interval 1 &
timeout 5s ./gaming-maintenance-suite.sh --help

# System integration tests  
systemctl --user is-active gamemoded || echo "GameMode not active"
nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader
```

## Troubleshooting

### Common Issues

#### Scripts Not Executable
**Symptom**: `Permission denied` when running scripts
**Solution**: `chmod +x *.py *.sh`

#### Missing Dependencies
**Symptom**: `ModuleNotFoundError: No module named 'psutil'`
**Solution**: `sudo dnf install python3-psutil`

#### NVIDIA Commands Fail
**Symptom**: `nvidia-settings: command not found`
**Solution**: Ensure NVIDIA drivers are installed via akmods or driver packages

#### GameMode Not Starting
**Symptom**: Gaming mode features don't apply
**Solution**: `systemctl --user enable --now gamemoded`

### Log Analysis
```bash
# Monitor gaming manager operations
journalctl -f | grep -i gaming

# Check service status
systemctl --user status gamemoded

# View benchmark results
ls -la ~/.local/share/gaming-benchmarks/

# Check system optimization state
cat /var/run/gaming-mode.state 2>/dev/null || echo "Gaming mode disabled"
```

## Security and Safety Considerations

### Privilege Requirements
- Most operations require sudo for system-level changes
- Scripts validate hardware before applying vendor-specific settings
- Rollback mechanisms for all system modifications
- Input validation for all user-provided parameters

### Hardware Safety
- GPU overclocking within safe ranges with temperature monitoring  
- CPU optimizations with thermal throttling protection
- Automatic fallback for unsupported hardware configurations
- Dry-run modes available for testing optimizations

## Quick Reference

### One-liner Commands
```bash
# Quick gaming mode toggle
./gaming-manager-suite.py --enable && echo "Gaming mode enabled"

# System performance snapshot
./gaming-monitor-suite.py --mode simple --interval 1 | head -20

# Emergency reset to defaults
./gaming-manager-suite.py --disable

# Health check summary  
./gaming-manager-suite.py --health | grep -E "(✓|✗|⚠)"
```

### Important File Locations
- **Scripts**: `gaming-manager-suite.py`, `gaming-monitor-suite.py`, `gaming-maintenance-suite.sh`
- **Configs**: `~/.config/gaming-manager/profiles/`
- **Logs**: `/var/log/gaming-benchmark/`, `/var/log/gaming-metrics/`
- **State**: `/var/run/gaming-mode.state`
- **Documentation**: `docs/`, `to-dos/`, `ref_docs/`

### Development Files
- **Contributing Guidelines**: `CONTRIBUTING.md`
- **AI Development Rules**: `CLAUDE.md`
- **Architecture Details**: `docs/TECHNICAL_ARCHITECTURE.md`
- **Installation Guide**: `docs/INSTALLATION_SETUP.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`

## Project Status

**Current Version**: 1.0.1 (Professional documentation release)  
**Development Stage**: Production ready with comprehensive documentation  
**Community**: Active GitHub repository with professional project management infrastructure

### Roadmap Highlights
- **v1.1.0**: GUI interface (GTK4) and Steam Deck optimization profiles
- **v1.2.0**: AMD GPU support and multi-GPU configuration management  
- **v1.3.0**: Community profile sharing system and cloud benchmarking

The suite is actively maintained with a focus on community engagement and expanding hardware support while maintaining the high performance standards established for the current NVIDIA/Intel configuration.
