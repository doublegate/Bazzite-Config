# Bazzite Optimizer GUI - User Guide

## Introduction

The Bazzite Gaming Optimizer GUI provides an intuitive graphical interface to all the powerful optimization features of the Bazzite Gaming Optimization Suite. No command-line knowledge required!

## Installation

### Prerequisites

- **Bazzite Linux** (latest version)
- **Python 3.8+**
- **GTK4** and Python GObject bindings
- **psutil** (optional but recommended for monitoring)

### Quick Install

**User Installation (Recommended):**
```bash
cd /path/to/Bazzite-Config
./install-gui.sh
```

**System-wide Installation:**
```bash
cd /path/to/Bazzite-Config
sudo ./install-gui.sh --system
```

### Manual Installation

If you prefer manual installation:

```bash
# Install dependencies
sudo dnf install python3-gobject gtk4
pip3 install --user psutil

# Copy GUI script
cp bazzite-optimizer-gui.py ~/.local/bin/
chmod +x ~/.local/bin/bazzite-optimizer-gui.py

# Install desktop entry
cp bazzite-optimizer-gui.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications/
```

## Launching the GUI

### From Application Menu
1. Open your application menu (usually Super/Windows key)
2. Search for "Bazzite Gaming Optimizer"
3. Click to launch

### From Command Line
```bash
bazzite-optimizer-gui
```

Or if installed to user directory:
```bash
~/.local/bin/bazzite-optimizer-gui
```

## Interface Overview

The GUI consists of 5 main tabs:

1. **Dashboard** - System overview and quick status
2. **Profiles** - Gaming profile selection and management
3. **Monitoring** - Real-time performance metrics
4. **Quick Fixes** - One-click solutions for common issues
5. **Settings** - Application configuration

## Dashboard Tab

### Overview

The Dashboard provides an at-a-glance view of your system's current state.

### Features

**Hardware Information Cards:**
- **CPU**: Model, core count
- **GPU**: Model, VRAM amount
- **Memory**: Total RAM, ZRAM configuration

**Current Configuration:**
- Active optimization profile
- Gaming mode status (toggle on/off)
- Quick apply/disable buttons

**System Health:**
- Overall system health percentage
- Last optimization timestamp
- Performance improvement metric
- Kernel version

### Actions

**Apply Current Profile:**
- Applies the currently selected optimization profile
- Requires root privileges (will prompt for password)
- Shows progress during application

**Disable Optimizations:**
- Rolls back all optimizations to system defaults
- Requires confirmation
- Creates backup before rollback

**Gaming Mode Toggle:**
- Quickly enable/disable gaming mode
- Affects process prioritization and system scheduling

## Profiles Tab

### Overview

Select from 4 pre-configured gaming profiles optimized for different use cases.

### Available Profiles

#### ⚡ Competitive Profile
**Best for:** FPS games, Esports, Competitive multiplayer

**Features:**
- No C-states (maximum CPU responsiveness)
- Maximum CPU/GPU clocks
- Core isolation for gaming threads
- Disabled mitigations for peak performance
- Minimum latency network tuning
- Compositor disabled

**Performance:** Maximum gaming performance, may increase power consumption

#### ⚖️ Balanced Profile (Recommended)
**Best for:** Single player games, General gaming, Daily use

**Features:**
- Moderate C-state tuning (C-state 3)
- Balanced power management
- Auto-tuned clocks
- Some mitigations enabled
- Optimized network settings
- Adaptive compositor

**Performance:** Best balance between performance and system responsiveness

#### 📹 Streaming Profile
**Best for:** Twitch streaming, YouTube streaming, Content creation

**Features:**
- Power-efficient settings
- NVENC/VAAPI encoding optimization
- Reduced system impact
- Network upload optimization
- Multi-threaded encoding support
- Background task management

**Performance:** Optimized for simultaneous gaming and streaming

#### 🎨 Creative Profile
**Best for:** Video editing, 3D rendering, Game development

**Features:**
- Multi-core optimization
- High memory bandwidth
- Storage performance focus
- GPU compute optimization
- Rendering acceleration
- Background task support

**Performance:** Optimized for content creation workflows

### Using Profiles

1. **Select a Profile:** Click "Select" on any profile card
2. **View Details:** Profile details appear below the cards
3. **Apply Profile:** Click "Apply Selected Profile"
4. **Confirm:** Confirm the operation in the dialog
5. **Wait:** Profile application takes 30-60 seconds
6. **Verify:** Check Dashboard for confirmation

### Benchmarking

Click "Run Benchmark" to test system performance:
- Runs comprehensive system tests
- Takes 5-10 minutes
- Results shown in dialog
- Useful for comparing before/after optimization

## Monitoring Tab

### Overview

Real-time performance monitoring with 1-second updates.

### Monitored Metrics

**CPU:**
- Usage percentage (0-100%)
- Current frequency (MHz)
- Temperature (°C)

**GPU:**
- Usage percentage (0-100%)
- VRAM usage (MB used / total MB)
- Temperature (°C)

**Memory:**
- RAM usage (GB used / total GB)
- Swap usage (GB used / total GB)

**Statistics:**
- CPU average usage
- GPU average usage
- Monitoring uptime

### Using Monitoring

1. **Start Monitoring:** Click "▶ Start Monitoring"
2. **View Metrics:** Watch real-time updates (1Hz)
3. **Stop Monitoring:** Click "◼ Stop Monitoring" when done

**Note:** Monitoring uses minimal system resources (~0.5% CPU)

### Tips

- Start monitoring before launching a game
- Watch GPU usage to identify bottlenecks
- High CPU temp (>80°C) may indicate thermal throttling
- Monitor during gameplay to verify optimizations

## Quick Fixes Tab

### Overview

One-click solutions for common gaming issues on Bazzite.

### Available Fixes

#### 🎮 Fix Steam
**Fixes:** Steam client freezing, login issues, download problems

**Actions:**
- Restarts Steam client
- Clears Steam cache

**When to Use:** Steam not launching, library not loading, downloads stuck

#### 🔊 Fix Audio
**Fixes:** Audio crackling, no sound issues, device detection problems

**Actions:**
- Restarts PipeWire service
- Restarts PulseAudio compatibility layer
- Restarts WirePlumber session manager

**When to Use:** No audio in games, crackling sounds, wrong audio device

#### 🎨 Reset GPU
**Fixes:** Display issues, resolution problems, overclocking instability

**Actions:**
- Resets GPU settings to defaults
- Restores factory clock speeds

**When to Use:** Screen artifacts, crashes after overclocking, display glitches

#### 🧹 Clear Caches
**Fixes:** Disk space issues, stale cache data

**Actions:**
- Clears user cache directories
- Frees up disk space

**When to Use:** Low disk space, after major system updates

**Warning:** May require re-login to some applications

#### 🔄 Restart Gaming Services
**Fixes:** Game prioritization issues, system responsiveness problems

**Actions:**
- Restarts system76-scheduler
- Resets process priorities

**When to Use:** Games not getting priority, system feels sluggish

### Using Quick Fixes

1. **Identify Issue:** Determine which fix matches your problem
2. **Click Fix Button:** Click "Apply Fix" on the appropriate card
3. **Wait:** Fix applies in 5-30 seconds
4. **Verify:** Check if issue is resolved
5. **View Log:** Recent fixes shown in log at bottom

**Tip:** Most fixes are safe to apply multiple times

## Settings Tab

### Overview

Configure application behavior and preferences.

### General Settings

**Start optimizer GUI on login:**
- Auto-launch GUI when you log in
- Convenient for always-on optimization

**Show notifications for optimization events:**
- Get notified when profiles are applied
- Alerts for system health changes

**Minimize to system tray:**
- Keep GUI running in background
- Quick access from system tray

### Optimization Settings

**Apply profile on startup:**
- Automatically apply your preferred profile at boot
- Ensures optimizations always active

**Enable automatic profile switching:**
- Automatically switch profiles based on running applications
- **Note:** Requires configuration (coming soon)

**Default profile:**
- Select which profile to use at startup
- Choose from: Competitive, Balanced, Streaming, Creative

### Advanced Options

**View Logs:**
- View application and optimization logs
- Useful for troubleshooting

**Backup Config:**
- Create backup of current configuration
- Safe before major changes

**Restore Config:**
- Restore from previous backup
- Rollback configuration changes

**Export System Info:**
- Export hardware and configuration details
- Useful for bug reports and support

**Reset to Defaults:**
- Reset all settings to default values
- Doesn't affect applied optimizations

### About Section

- View application version
- Check for updates
- Access documentation
- Visit GitHub repository

## Tips and Best Practices

### Getting Started

1. **Start with Balanced Profile** - Safe default for most users
2. **Monitor First** - Use Monitoring tab to understand baseline performance
3. **Apply Gradually** - Try Competitive profile only when needed
4. **Benchmark** - Run benchmarks before and after to quantify improvements

### Common Workflows

**Daily Gaming:**
```
1. Launch GUI
2. Dashboard → Check system health
3. Profiles → Apply Balanced profile
4. Launch game
```

**Competitive Gaming:**
```
1. Monitoring → Start monitoring
2. Profiles → Apply Competitive profile
3. Launch game
4. Monitor performance during gameplay
```

**Troubleshooting:**
```
1. Quick Fixes → Apply relevant fix
2. Dashboard → Verify gaming mode enabled
3. Profiles → Reapply current profile if needed
4. Settings → View logs for details
```

### Performance Expectations

**Typical Improvements:**
- **Competitive Profile:** 15-25% FPS improvement, lower latency
- **Balanced Profile:** 10-15% FPS improvement, stable performance
- **Streaming Profile:** Optimized encoding, minimal FPS loss while streaming
- **Creative Profile:** Faster renders, improved multi-core performance

**Your Results May Vary:** Performance depends on hardware, games, and system configuration.

## Troubleshooting

### GUI Won't Launch

**Check dependencies:**
```bash
python3 -c "import gi; gi.require_version('Gtk', '4.0')"
```

If error, install GTK4:
```bash
sudo dnf install python3-gobject gtk4
```

### Backend Not Found Error

Ensure `bazzite-optimizer.py` is in the same directory or installed system-wide:
```bash
ls -l bazzite-optimizer.py
```

### Profile Application Fails

**Check privileges:**
- Profile application requires root access
- Ensure `pkexec` is available:
```bash
pkexec --version
```

**Check logs:**
```bash
tail -50 /var/log/bazzite-optimizer.log
```

### Monitoring Shows No Data

**Install psutil:**
```bash
pip3 install --user psutil
```

**Check GPU tools (NVIDIA):**
```bash
nvidia-smi
```

### Desktop Entry Not Showing

**Update desktop database:**
```bash
update-desktop-database ~/.local/share/applications/
```

**Logout and login** to refresh application menu cache.

## Uninstallation

### User Installation
```bash
./install-gui.sh --uninstall
```

### System-wide Installation
```bash
sudo ./install-gui.sh --uninstall --system
```

### Manual Uninstall
```bash
rm ~/.local/bin/bazzite-optimizer-gui
rm ~/.local/share/applications/bazzite-optimizer-gui.desktop
rm -rf ~/.local/share/bazzite-optimizer
```

## Support and Feedback

### Getting Help

- **Documentation:** Check docs/ directory for detailed guides
- **GitHub Issues:** Report bugs at https://github.com/doublegate/Bazzite-Config/issues
- **Bazzite Community:** Ask in Bazzite Linux community forums

### Reporting Bugs

Include in bug reports:
1. GUI version (Settings → About)
2. System information (Settings → Export System Info)
3. Steps to reproduce
4. Relevant log excerpts
5. Screenshots if applicable

## Keyboard Shortcuts

- **Ctrl+1-5:** Switch between tabs
- **F5:** Refresh current view
- **Ctrl+Q:** Quit application
- **Ctrl+H:** Show/hide main window (when minimized to tray)

## Privacy and Data

The Bazzite Optimizer GUI:
- ✅ Runs entirely locally
- ✅ No telemetry or data collection
- ✅ No internet connection required
- ✅ Open source (MIT License)

All optimizations and monitoring happen on your system only.

---

**Version:** 1.1.0
**Last Updated:** November 18, 2025
**License:** MIT
