# Bazzite Optimizer GUI Architecture - v1.1.0

## Overview

GTK4-based graphical interface for the Bazzite Gaming Optimization Suite, providing intuitive access to all optimization features through a modern, responsive UI.

## Architecture Design

### Technology Stack

- **GUI Framework**: GTK4 (via PyGObject/gi)
- **Language**: Python 3.8+
- **Backend Integration**: Direct integration with bazzite-optimizer.py
- **Graphics**: Cairo for performance graphs
- **Threading**: GLib.idle_add for async operations
- **Styling**: CSS for consistent theme

### Design Principles

1. **User-First Design**: Maximum of 3 clicks to any major function
2. **Visual Feedback**: Clear status indicators and progress bars
3. **Safety**: Confirmation dialogs for destructive operations
4. **Performance**: Non-blocking UI with threaded operations
5. **Accessibility**: Keyboard navigation, high contrast support

## Application Structure

```
bazzite-optimizer-gui/
├── gui/
│   ├── ui/                      # UI component files
│   │   ├── main_window.py       # Main application window
│   │   ├── dashboard_tab.py     # System overview dashboard
│   │   ├── profiles_tab.py      # Profile management
│   │   ├── monitoring_tab.py    # Real-time monitoring
│   │   ├── quickfix_tab.py      # Quick fixes panel
│   │   └── settings_tab.py      # Configuration settings
│   ├── controllers/             # Business logic controllers
│   │   ├── optimizer_backend.py # Backend integration
│   │   ├── monitor_controller.py# Monitoring data controller
│   │   └── profile_controller.py# Profile management logic
│   ├── models/                  # Data models
│   │   ├── system_state.py      # System state model
│   │   ├── profile_model.py     # Profile data model
│   │   └── metrics_model.py     # Performance metrics model
│   └── resources/               # UI resources
│       ├── style.css            # Application stylesheet
│       ├── icons/               # Application icons
│       └── ui_templates/        # Glade UI templates (if used)
├── bazzite-optimizer-gui.py     # Main application entry point
└── bazzite-optimizer-gui.desktop # Desktop file
```

## User Interface Layout

### Main Window

```
┌─────────────────────────────────────────────────────────────┐
│ Bazzite Gaming Optimizer                          [−][□][×] │
├─────────────────────────────────────────────────────────────┤
│ [Dashboard] [Profiles] [Monitoring] [Quick Fixes] [Settings]│
├─────────────────────────────────────────────────────────────┤
│                                                               │
│                    TAB CONTENT AREA                          │
│                                                               │
│                                                               │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│ Status: Ready                    Gaming Mode: ● Enabled      │
└─────────────────────────────────────────────────────────────┘
```

## Tab Specifications

### 1. Dashboard Tab

**Purpose**: System overview and quick status check

**Components**:
- System information panel (CPU, GPU, RAM, Kernel)
- Current optimization profile indicator
- Gaming mode status toggle
- Performance summary cards
- Recent optimization history
- System health indicators

**Layout**:
```
┌─────────────────────────────────────────────────────┐
│ System Information                                  │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐  │
│ │   CPU       │ │    GPU      │ │   Memory    │  │
│ │ i9-10850K   │ │  RTX 5080   │ │   64 GB     │  │
│ │ 10 cores    │ │ 16GB VRAM   │ │ 8GB ZRAM    │  │
│ └─────────────┘ └─────────────┘ └─────────────┘  │
├─────────────────────────────────────────────────────┤
│ Current Profile: Competitive                        │
│ Gaming Mode: [●] Enabled    [Apply] [Disable]      │
├─────────────────────────────────────────────────────┤
│ System Health:  ████████████████░░ 85%             │
│ Last Optimized: 2 hours ago                        │
│ Performance:    +23% vs baseline                   │
└─────────────────────────────────────────────────────┘
```

### 2. Profiles Tab

**Purpose**: Gaming profile selection and management

**Components**:
- Visual profile cards (Competitive, Balanced, Streaming, Creative)
- Profile details and optimization summary
- One-click apply button
- Profile comparison view
- Custom profile creation wizard

**Layout**:
```
┌─────────────────────────────────────────────────────┐
│ Select Gaming Profile                               │
├─────────────────────────────────────────────────────┤
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐│
│ │ Competitive  │ │  Balanced    │ │  Streaming   ││
│ │ ⚡ Max Perf  │ │ ⚖️ Optimal   │ │ 📹 Broadcast ││
│ │              │ │              │ │              ││
│ │ • No C-states│ │ • C-state 3  │ │ • Power eff. ││
│ │ • Max clocks │ │ • Balanced   │ │ • Encoding   ││
│ │ • Core isol. │ │ • Auto tune  │ │ • Low impact ││
│ │              │ │              │ │              ││
│ │  [● Active]  │ │   [Apply]    │ │   [Apply]    ││
│ └──────────────┘ └──────────────┘ └──────────────┘│
│                                                     │
│ Profile Details:                                    │
│ Competitive profile maximizes gaming performance... │
│                                                     │
│ [Apply Profile] [Benchmark] [Profile Comparison]   │
└─────────────────────────────────────────────────────┘
```

### 3. Monitoring Tab

**Purpose**: Real-time performance monitoring

**Components**:
- Live CPU usage graph
- Live GPU usage graph
- Memory usage indicators
- Temperature monitoring
- FPS counter integration (if available)
- Network latency display

**Layout**:
```
┌─────────────────────────────────────────────────────┐
│ Real-Time Performance Monitoring                    │
├─────────────────────────────────────────────────────┤
│ CPU Usage (%)        GPU Usage (%)                  │
│ ┌──────────────┐    ┌──────────────┐               │
│ │   Graph      │    │   Graph      │               │
│ │   ▁▃▅▇█      │    │   ▂▄▆█▆      │               │
│ │   45%        │    │   78%        │               │
│ └──────────────┘    └──────────────┘               │
│                                                     │
│ Temperatures         Memory                        │
│ CPU: 65°C           RAM:  24GB / 64GB              │
│ GPU: 72°C           VRAM: 8GB / 16GB               │
│                     SWAP: 2GB / 16GB               │
│                                                     │
│ [◼] Stop Monitoring  [⟳] Refresh  Interval: 1s ▼  │
└─────────────────────────────────────────────────────┘
```

### 4. Quick Fixes Tab

**Purpose**: One-click solutions for common issues

**Components**:
- Steam fix button
- Audio fix button
- GPU reset button
- Cache cleanup button
- Service restart buttons
- Fix history log

**Layout**:
```
┌─────────────────────────────────────────────────────┐
│ Quick System Fixes                                  │
├─────────────────────────────────────────────────────┤
│ Common Issues:                                      │
│                                                     │
│ [🎮 Fix Steam]        Fix Steam client issues      │
│ [🔊 Fix Audio]        Restart audio services       │
│ [🎨 Reset GPU]        Reset GPU to defaults        │
│ [🧹 Clear Caches]     Clean system caches          │
│ [🔄 Restart Services] Restart gaming services      │
│                                                     │
│ Recent Fixes:                                       │
│ ✓ Steam fixed - 2 hours ago                        │
│ ✓ Audio restarted - 1 day ago                      │
│                                                     │
│ [View Fix History] [Advanced Troubleshooting]      │
└─────────────────────────────────────────────────────┘
```

### 5. Settings Tab

**Purpose**: Application and optimization configuration

**Components**:
- Auto-start options
- Notification preferences
- Advanced optimizer settings
- Backup/restore configuration
- System information export
- About section

**Layout**:
```
┌─────────────────────────────────────────────────────┐
│ Settings & Configuration                            │
├─────────────────────────────────────────────────────┤
│ General                                             │
│ [✓] Start optimizer GUI on login                   │
│ [✓] Show notifications for optimization events     │
│ [✓] Minimize to system tray                        │
│                                                     │
│ Optimization                                        │
│ [✓] Apply profile on startup                       │
│ [ ] Enable automatic profile switching             │
│ Default profile: Balanced ▼                        │
│                                                     │
│ Advanced                                            │
│ [View Logs] [Backup Config] [Restore Config]       │
│ [Export System Info] [Reset to Defaults]           │
│                                                     │
│ About                                               │
│ Bazzite Optimizer v1.1.0                           │
│ [Check for Updates] [Documentation] [GitHub]       │
└─────────────────────────────────────────────────────┘
```

## Backend Integration

### Communication Pattern

```python
GUI Layer (gtk4)
    ↓ commands
OptimizerBackend (controller)
    ↓ subprocess/API calls
bazzite-optimizer.py (existing script)
    ↓ system calls
Bazzite System
```

### Threading Model

- **Main Thread**: GTK event loop
- **Worker Threads**: Long-running operations (optimization, monitoring)
- **GLib.idle_add**: Update UI from worker threads
- **GLib.timeout_add**: Periodic updates (monitoring)

### State Management

- **SystemState**: Current system configuration and status
- **ProfileModel**: Active profile and available profiles
- **MetricsModel**: Real-time performance metrics
- **Observable Pattern**: Controllers notify UI of state changes

## Key Features Implementation

### 1. Real-Time Monitoring

```python
class MonitorController:
    def start_monitoring(self, interval_ms=1000):
        """Start real-time monitoring with specified interval"""
        GLib.timeout_add(interval_ms, self._update_metrics)

    def _update_metrics(self):
        """Fetch latest metrics and notify observers"""
        metrics = self._fetch_system_metrics()
        self.notify_observers(metrics)
        return True  # Continue monitoring
```

### 2. Profile Application

```python
class ProfileController:
    def apply_profile(self, profile_name, callback):
        """Apply profile in background thread"""
        def worker():
            result = self.backend.apply_profile(profile_name)
            GLib.idle_add(callback, result)

        threading.Thread(target=worker, daemon=True).start()
```

### 3. Progress Feedback

```python
class ProgressDialog:
    def show_with_progress(self, operation_name):
        """Show progress dialog with pulsing progress bar"""
        self.dialog.show()
        GLib.timeout_add(100, self._pulse_progress)
```

## Performance Considerations

1. **Lazy Loading**: Load tab content only when tab is activated
2. **Data Caching**: Cache system info for 5 seconds to reduce syscalls
3. **Graph Optimization**: Limit data points to last 60 seconds for graphs
4. **Async Operations**: All system calls run in worker threads
5. **Resource Cleanup**: Properly dispose GTK objects to prevent memory leaks

## Security Considerations

1. **Privilege Escalation**: Use pkexec for operations requiring root
2. **Input Validation**: Sanitize all user inputs before passing to backend
3. **Confirmation Dialogs**: Require confirmation for destructive operations
4. **Audit Logging**: Log all optimization operations
5. **Safe Defaults**: Conservative defaults for all settings

## Accessibility Features

1. **Keyboard Navigation**: Full keyboard support for all functions
2. **Screen Reader**: Proper GTK accessibility attributes
3. **High Contrast**: Support for high contrast themes
4. **Font Scaling**: Respect system font size settings
5. **Keyboard Shortcuts**: Ctrl+1-5 for tab switching, F5 for refresh

## Error Handling

1. **Graceful Degradation**: UI remains functional if backend unavailable
2. **User-Friendly Messages**: Clear error messages with suggested actions
3. **Error Recovery**: Automatic retry for transient failures
4. **Logging**: Comprehensive error logging for debugging
5. **Fallback Mode**: Read-only mode if optimization unavailable

## Installation & Packaging

### Desktop Integration

```desktop
[Desktop Entry]
Name=Bazzite Optimizer
Comment=Gaming system optimization suite
Exec=bazzite-optimizer-gui
Icon=bazzite-optimizer
Terminal=false
Type=Application
Categories=System;Settings;Game;
Keywords=gaming;optimization;performance;
```

### Dependencies

```
python3 >= 3.8
python3-gi >= 3.40
gtk4 >= 4.6
libadwaita >= 1.0 (optional, for modern GNOME look)
python3-cairo
python3-psutil
```

### Installation Script

```bash
#!/bin/bash
# install-gui.sh
pip3 install --user pygobject pycairo
cp bazzite-optimizer-gui.py ~/.local/bin/
cp bazzite-optimizer-gui.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications/
```

## Testing Strategy

1. **Unit Tests**: Test controllers and models independently
2. **Integration Tests**: Test backend communication
3. **UI Tests**: Automated GTK UI testing with Dogtail
4. **Manual Testing**: Real-world usage on Bazzite system
5. **Performance Testing**: Memory and CPU usage profiling

## Future Enhancements (v1.2.0+)

1. **Custom Themes**: User-selectable color schemes
2. **Widget Customization**: Draggable dashboard widgets
3. **Notifications**: System tray notifications for events
4. **Remote Monitoring**: Web-based remote monitoring (v2.0.0)
5. **Plugin System**: Third-party plugin support

## Development Timeline

- **Week 1**: Core window and dashboard tab
- **Week 2**: Profiles tab and backend integration
- **Week 3**: Monitoring tab with graphs
- **Week 4**: Quick fixes and settings tabs, packaging

## Success Criteria

- [ ] Application launches in <2 seconds
- [ ] Profile application requires <3 clicks
- [ ] Real-time graphs update smoothly at 1Hz
- [ ] UI remains responsive during all operations
- [ ] Memory usage <100MB idle, <200MB monitoring
- [ ] Desktop integration works on KDE Plasma and GNOME

---

**Last Updated**: 2025-11-18
**Status**: Design Phase Complete - Ready for Implementation
