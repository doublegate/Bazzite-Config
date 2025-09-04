# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Bazzite Linux gaming optimization suite consisting of three main Python/Shell script components for comprehensive gaming system management, monitoring, and maintenance. The tools are designed for high-end gaming setups with NVIDIA RTX 5080, Intel i9-10850K, and 64GB RAM configurations.

## Core Components

### Gaming Manager Suite (`gaming-manager-suite.py`)
Central control panel for gaming system optimization:
- **GamingModeController**: Toggle gaming optimizations on/off
- **GameProfileManager**: Create, load, and apply game-specific profiles  
- **QuickFixUtilities**: Common fixes for Steam, audio, GPU issues

### Gaming Monitor Suite (`gaming-monitor-suite.py`)
Real-time performance monitoring with gaming-specific metrics:
- **MetricsCollector**: Collects CPU, GPU, memory, disk, network metrics
- **TerminalDashboard**: Curses-based real-time monitoring interface
- Tracks gaming-specific data like GameMode status, Proton processes, compositor state

### Gaming Maintenance Suite (`gaming-maintenance-suite.sh`)
Automated benchmarking and system maintenance:
- CPU benchmarking with stress-ng and sysbench
- Disk performance testing (optimized for Samsung 990 EVO Plus)
- GPU benchmarking and optimization verification
- Automated system cleanup and maintenance tasks

## Common Development Commands

### Running the Tools

```bash
# Gaming Manager - System control and optimization
./gaming-manager-suite.py --enable          # Enable gaming mode
./gaming-manager-suite.py --disable         # Disable gaming mode  
./gaming-manager-suite.py --status          # Show system status
./gaming-manager-suite.py --health          # Run health check
./gaming-manager-suite.py --profile <name>  # Apply game profile
./gaming-manager-suite.py --fix <type>      # Apply quick fixes (steam/audio/gpu/caches)

# Gaming Monitor - Performance monitoring
./gaming-monitor-suite.py --mode dashboard  # Real-time curses dashboard
./gaming-monitor-suite.py --mode simple     # Simple text output
./gaming-monitor-suite.py --mode export     # Export metrics to files
./gaming-monitor-suite.py --interval 5      # Update every 5 seconds

# Gaming Maintenance - Benchmarking and maintenance  
./gaming-maintenance-suite.sh               # Interactive menu
./gaming-maintenance-suite.sh --help        # Show available options
```

### Making Scripts Executable

```bash
chmod +x gaming-manager-suite.py gaming-monitor-suite.py gaming-maintenance-suite.sh
```

### Python Dependencies

```bash
# Required system packages
sudo dnf install python3-psutil python3-configparser

# Additional tools for benchmarking
sudo dnf install stress-ng sysbench
```

## Architecture Overview

### Configuration Management
- Gaming mode state: `/var/run/gaming-mode.state`
- Configuration files: `/etc/gaming-mode.conf`
- Game profiles: `~/.config/gaming-manager/profiles/`
- Log directories: `/var/log/gaming-benchmark`, `/var/log/gaming-metrics`
- Results storage: `~/.local/share/gaming-benchmarks`

### Key Design Patterns
- **Color-coded terminal output**: Consistent Colors class across all tools
- **Modular architecture**: Separate classes for different functional areas
- **Configuration-driven**: JSON-based profiles and settings
- **System integration**: Direct interaction with Bazzite's ujust commands and System76-scheduler
- **Safety-first**: Validation and rollback capabilities for system changes

### Hardware-Specific Optimizations
The suite is optimized for:
- **NVIDIA RTX 5080**: Blackwell architecture with -open driver variant
- **Intel i9-10850K**: 10-core Comet Lake with aggressive C-state tuning
- **64GB RAM**: Optimized ZRAM configuration (8-16GB with LZ4)
- **Samsung 990 EVO Plus**: NVMe with none/noop I/O scheduler
- **Bazzite Linux**: fsync kernel with System76-scheduler integration

## Reference Documentation

- `ref_docs/report-optimal_bazzite-v2.md`: Comprehensive optimization guide with community-tested configurations
- `ref_docs/device-info.txt`: Hardware specifications and system information
- `ref_scripts/`: Multiple versions of optimization scripts from different AI models for reference

## Development Notes

### Code Style
- Python scripts use type hints and comprehensive error handling
- Shell scripts follow POSIX compatibility where possible
- Consistent color coding and logging patterns across all tools
- Modular class-based architecture for Python components

### System Integration
The tools integrate with Bazzite-specific features:
- ujust commands for system configuration
- System76-scheduler for process prioritization  
- GameMode integration for automatic performance switching
- fsync kernel optimizations
- Immutable filesystem considerations (rpm-ostree)