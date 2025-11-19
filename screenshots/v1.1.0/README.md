# Bazzite Gaming Optimizer v1.1.0 Screenshots

This directory contains screenshots for the v1.1.0 GUI release.

## Required Screenshots

The following screenshots are needed for the official v1.1.0 release:

### 1. Dashboard Tab (`01-dashboard.png`)
**Capture**: Main dashboard showing system overview
- Hardware detection cards (CPU, GPU, RAM)
- Current optimization profile display
- Gaming mode status indicator
- System health metrics
- Profile application button

**Requirements**:
- Show actual hardware detection (RTX 5080, i9-10850K, 64GB RAM)
- Display current profile status
- Demonstrate clean, professional UI

---

### 2. Profiles Tab (`02-profiles.png`)
**Capture**: All 4 gaming profile cards visible
- ⚡ Competitive profile card
- ⚖️ Balanced profile card
- 📹 Streaming profile card
- 🎨 Creative profile card

**Requirements**:
- All 4 profile cards should be visible
- Show profile descriptions and features
- Display selection/application controls
- Demonstrate visual hierarchy

---

### 3. Monitoring Tab - Active (`03-monitoring-active.png`)
**Capture**: Real-time monitoring with live metrics
- CPU usage, frequency, temperature graphs
- GPU usage, VRAM, temperature displays
- Memory (RAM/Swap) usage indicators
- Real-time statistics and averages
- Start/Stop controls (in "active" state)

**Requirements**:
- Show actual real-time data (not zeros)
- Demonstrate 1-second update intervals
- Display temperature readings
- Show monitoring controls

---

### 4. Quick Fixes Tab (`04-quickfix.png`)
**Capture**: Quick fix solutions grid
- All 5 fix cards visible:
  - 🎮 Fix Steam
  - 🔊 Fix Audio
  - 🎨 Reset GPU
  - 🧹 Clear Caches
  - 🔄 Restart Gaming Services
- Recent fixes log section

**Requirements**:
- Show all fix cards with descriptions
- Display recent fixes log (can be empty or with sample entries)
- Demonstrate one-click solution interface

---

### 5. Settings Tab (`05-settings.png`)
**Capture**: Application configuration options
- General settings (auto-start, notifications, tray)
- Optimization settings (default profile, auto-switching)
- Advanced options (logs, backup, restore, export)
- About section (version info, links)

**Requirements**:
- Show all settings sections
- Display version information (v1.1.0)
- Demonstrate configuration options

---

## Screenshot Guidelines

### Technical Requirements
- **Format**: PNG (lossless)
- **Resolution**: Native resolution (1920x1080 or higher preferred)
- **File Size**: Keep under 2MB per screenshot (use PNG compression if needed)
- **Naming**: Use exact filenames listed above (01-dashboard.png, etc.)

### Content Requirements
- **Window State**: Maximized or large enough to show all UI elements clearly
- **Theme**: Use default GTK theme (or clean, professional theme)
- **Data**: Show real data where possible (not placeholder text)
- **Focus**: Ensure the relevant tab is active and fully visible

### Quality Standards
- **Clarity**: No blur, artifacts, or compression issues
- **Completeness**: All UI elements visible (no cutoff text/buttons)
- **Professionalism**: Clean desktop background, no distracting elements
- **Consistency**: Use same window size/theme across all screenshots

---

## How to Capture Screenshots

### On Bazzite/Fedora Linux

**Method 1: Using GNOME Screenshot Tool**
```bash
# Full window screenshot
gnome-screenshot -w

# Interactive selection
gnome-screenshot -i
```

**Method 2: Using Flameshot (Recommended)**
```bash
# Install flameshot
flatpak install flameshot

# Launch interactive screenshot
flameshot gui
```

**Method 3: Using Print Screen Key**
- Press `PrtScn` for full screen
- Press `Alt+PrtScn` for active window
- Press `Shift+PrtScn` for area selection

### After Capturing

1. Save screenshots to this directory: `screenshots/v1.1.0/`
2. Use exact filenames: `01-dashboard.png`, `02-profiles.png`, etc.
3. Verify all 5 screenshots are present
4. Check image quality and clarity
5. Commit to repository:
   ```bash
   git add screenshots/v1.1.0/*.png
   git commit -m "docs: Add v1.1.0 GUI screenshots"
   ```

---

## Usage in Documentation

These screenshots will be used in:

1. **RELEASE_NOTES_v1.1.0_GUI.md** - Official release announcement
2. **docs/GUI_USER_GUIDE.md** - User documentation
3. **README.md** - Project homepage
4. **GitHub Release** - v1.1.0 release page

---

## Screenshot Checklist

Before finalizing release, verify:

- [ ] `01-dashboard.png` - Dashboard tab with hardware detection
- [ ] `02-profiles.png` - All 4 gaming profile cards visible
- [ ] `03-monitoring-active.png` - Real-time monitoring with live data
- [ ] `04-quickfix.png` - Quick fixes grid with all 5 fixes
- [ ] `05-settings.png` - Settings and configuration options
- [ ] All images are PNG format
- [ ] All images are clear and professional quality
- [ ] All filenames match exactly
- [ ] All screenshots show v1.1.0 version
- [ ] Screenshots committed to repository

---

## Notes

- Screenshots should be captured on an actual Bazzite system after completing GUI testing
- Ensure the GUI application is fully functional before capturing screenshots
- Use real system data to demonstrate actual functionality
- Maintain consistent visual style across all screenshots

**Status**: ⏳ Awaiting capture on Bazzite system during testing phase
