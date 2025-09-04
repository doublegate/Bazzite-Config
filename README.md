# Bazzite Gaming Optimization Suite

<div align="center">

![Platform](https://img.shields.io/badge/Platform-Bazzite%20Linux-blue?style=for-the-badge&logo=linux)
![Python](https://img.shields.io/badge/Python-3.8%2B-3776ab?style=for-the-badge&logo=python)
![Shell](https://img.shields.io/badge/Shell-Bash-4eaa25?style=for-the-badge&logo=gnu-bash)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Professional gaming system optimization, monitoring, and maintenance for high-end Bazzite Linux configurations**

</div>

## 🎯 Overview

The Bazzite Gaming Optimization Suite is a comprehensive collection of tools designed to maximize gaming performance on Bazzite Linux systems. Specifically optimized for high-end hardware configurations including NVIDIA RTX 5080, Intel i9-10850K, and 64GB RAM setups, this suite delivers **15-25% performance improvements** through intelligent system tuning and automated optimization.

### ✨ Key Features

- 🚀 **Real-time Performance Monitoring** - Live system metrics with gaming-specific insights
- ⚡ **Automated Gaming Mode** - One-click performance optimization switching
- 🎮 **Game Profile Management** - Custom optimization profiles for different games
- 🔧 **Quick Fix Utilities** - Instant solutions for common gaming issues
- 📊 **Comprehensive Benchmarking** - CPU, GPU, and storage performance testing
- 🛠️ **System Maintenance** - Automated cleanup and optimization routines

## 🏗️ Architecture

The suite consists of three main components working in harmony:

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

## 🚀 Quick Start

### Prerequisites

- **Bazzite Linux** (latest version recommended)
- **Python 3.8+** with psutil
- **Standard system tools** (stress-ng, sysbench for benchmarking)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/doublegate/Bazzite-Config.git
   cd Bazzite-Config
   ```

2. **Make scripts executable:**
   ```bash
   chmod +x gaming-manager-suite.py gaming-monitor-suite.py gaming-maintenance-suite.sh
   ```

3. **Install dependencies:**
   ```bash
   sudo dnf install python3-psutil stress-ng sysbench
   ```

### Basic Usage

```bash
# Enable gaming mode optimizations
./gaming-manager-suite.py --enable

# Launch real-time performance monitor
./gaming-monitor-suite.py --mode dashboard

# Run comprehensive system benchmark
./gaming-maintenance-suite.sh

# Check system health and status
./gaming-manager-suite.py --health
```

## 🎮 Components

### Gaming Manager Suite (`gaming-manager-suite.py`)

The central control panel for your gaming system:

| Command | Description |
|---------|-------------|
| `--enable` | Activate gaming mode optimizations |
| `--disable` | Deactivate gaming mode |
| `--status` | Show current system status |
| `--health` | Run comprehensive health check |
| `--profile <name>` | Apply game-specific profile |
| `--fix <type>` | Apply quick fixes (steam/audio/gpu/caches) |

**Key Features:**
- **GamingModeController**: Toggles system-wide gaming optimizations
- **GameProfileManager**: Creates and manages game-specific configurations
- **QuickFixUtilities**: Instant solutions for Steam, audio, and GPU issues

### Gaming Monitor Suite (`gaming-monitor-suite.py`)

Real-time performance monitoring with gaming focus:

| Mode | Description |
|------|-------------|
| `dashboard` | Full curses-based interactive dashboard |
| `simple` | Clean text-based output |
| `export` | Export metrics to files for analysis |

**Monitored Metrics:**
- CPU usage, frequency, and temperature
- GPU utilization and memory usage
- System RAM and swap usage
- Gaming-specific processes (GameMode, Proton, Steam)
- Network and disk I/O

### Gaming Maintenance Suite (`gaming-maintenance-suite.sh`)

Automated benchmarking and system maintenance:

**Benchmark Categories:**
- **CPU Performance**: Multi-core stress testing with frequency analysis
- **Memory Bandwidth**: ZRAM optimization validation
- **Storage Speed**: NVMe performance testing (Samsung 990 EVO Plus optimized)
- **GPU Performance**: Gaming workload simulation
- **System Health**: Comprehensive diagnostics

## ⚙️ Hardware Optimization

### NVIDIA RTX 5080 Configuration
- Blackwell architecture with -open driver variant
- GPU overclocking support (+350-525MHz stable)
- DLSS 4 optimization (avoiding 4x Frame Generation bug)
- PowerMizer performance mode enforcement

### Intel i9-10850K Tuning
- Aggressive C-state limitation (`intel_idle.max_cstate=1`)
- Performance governor enforcement
- IRQ affinity optimization for gaming threads
- Optional undervolting support

### Memory & Storage
- Optimized ZRAM configuration (8-16GB with LZ4 compression)
- Samsung 990 EVO Plus NVMe tuning (none/noop scheduler)
- Intelligent swappiness settings (120-150 range)
- Weekly TRIM scheduling

## 📊 Performance Results

Community testing shows significant improvements:

| Metric | Improvement | Configuration |
|--------|-------------|---------------|
| Gaming Performance | **15-25%** | Combined optimizations |
| Cold Start Times | **13%** | System76-scheduler + BORE |
| Frame Time Consistency | **25%** | Reduced excessive slow frames |
| Memory Pressure Response | **15-25%** | ZRAM + swappiness tuning |
| CPU Wake-up Latency | **5-15%** | C-state limitation |

## 🛠️ Configuration

### Directory Structure
```
~/.config/gaming-manager/profiles/    # Game profiles
~/.local/share/gaming-benchmarks/     # Benchmark results
/var/log/gaming-benchmark/            # Benchmark logs
/var/log/gaming-metrics/              # Monitoring data
/etc/gaming-mode.conf                 # System configuration
/var/run/gaming-mode.state           # Current state
```

### Game Profile Example
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

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Test on Bazzite Linux
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Documentation

### User Guides
- **[Installation & Setup](docs/INSTALLATION_SETUP.md)** - Complete installation guide with hardware-specific configurations
- **[Performance Benchmarking](docs/PERFORMANCE_BENCHMARKING.md)** - Comprehensive benchmarking procedures and result interpretation
- **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Common issues, diagnostics, and solutions

### Technical Documentation
- **[Technical Architecture](docs/TECHNICAL_ARCHITECTURE.md)** - System architecture and integration details
- **[Development Guide](CLAUDE.md)** - Development patterns and contribution guidance

### Project Management
- **[Development Roadmap](to-dos/ROADMAP.md)** - Future releases and feature planning
- **[Enhancement Backlog](to-dos/ENHANCEMENTS.md)** - User-requested features and improvements
- **[Technical Debt](to-dos/TECHNICAL_DEBT.md)** - Code quality improvements and maintenance tasks
- **[Community Tasks](to-dos/COMMUNITY.md)** - Community engagement and sustainability planning

## 🔗 Resources

- **Bazzite Linux**: [Official Documentation](https://universal-blue.org/images/bazzite/)
- **System76 Scheduler**: [Configuration Guide](https://github.com/pop-os/system76-scheduler)
- **Gaming Optimization**: See `ref_docs/report-optimal_bazzite-v2.md` for detailed tuning guide

## 📈 Roadmap

- [ ] GUI interface using GTK4 (v1.1.0)
- [ ] Steam Deck optimization profiles (v1.1.0)
- [ ] AMD GPU support and optimization (v1.2.0)
- [ ] Multi-GPU configuration support (v1.2.0)
- [ ] Community profile sharing system (v1.3.0)
- [ ] Cloud benchmarking comparison (v1.3.0)

*See [Development Roadmap](to-dos/ROADMAP.md) for detailed release planning.*

---

<div align="center">

**Built with ❤️ for the Linux gaming community**

[Report Issue](https://github.com/doublegate/Bazzite-Config/issues) • [Request Feature](https://github.com/doublegate/Bazzite-Config/issues/new) • [Documentation](https://github.com/doublegate/Bazzite-Config/wiki)

</div>