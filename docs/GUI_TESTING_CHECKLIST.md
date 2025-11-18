# Bazzite Optimizer GUI - Testing Checklist v1.1.0

## Pre-Testing Requirements

### System Requirements
- ✓ Bazzite Linux (latest version)
- ✓ Python 3.8 or newer
- ✓ GTK4 4.6 or newer
- ✓ Active display server (X11 or Wayland)
- ✓ 4GB+ free RAM
- ✓ Graphics: NVIDIA RTX 5080 (or any NVIDIA GPU for testing)

### Installation

```bash
cd /path/to/Bazzite-Config

# Install dependencies
sudo dnf install python3-gobject gtk4
pip3 install --user psutil

# Install GUI
./install-gui.sh

# Or for system-wide
sudo ./install-gui.sh --system
```

---

## Testing Phase 1: Installation Validation

### Test 1.1: Dependency Check
```bash
# Verify Python version
python3 --version
# Expected: Python 3.8 or newer

# Verify GTK4
python3 -c "import gi; gi.require_version('Gtk', '4.0'); from gi.repository import Gtk; print(f'GTK {Gtk.MAJOR_VERSION}.{Gtk.MINOR_VERSION}')"
# Expected: GTK 4.6 or newer

# Verify psutil (optional but recommended)
python3 -c "import psutil; print(psutil.__version__)"
# Expected: Version number (any)
```

**Result:** [ ] PASS / [ ] FAIL
**Notes:** _______________________________________________

### Test 1.2: Installation Success
```bash
# Check binary installed
which bazzite-optimizer-gui
# Expected: /home/user/.local/bin/bazzite-optimizer-gui (user install)
#       or: /usr/local/bin/bazzite-optimizer-gui (system install)

# Check desktop file
ls ~/.local/share/applications/bazzite-optimizer-gui.desktop
# Expected: File exists

# Check GUI modules
ls ~/.local/share/bazzite-optimizer/gui
# Expected: Directory with Python modules
```

**Result:** [ ] PASS / [ ] FAIL
**Notes:** _______________________________________________

---

## Testing Phase 2: Application Launch

### Test 2.1: Command-Line Launch
```bash
bazzite-optimizer-gui
```

**Expected Behavior:**
- Window opens within 2-3 seconds
- No error messages in terminal
- Window title: "Bazzite Gaming Optimizer"
- 5 tabs visible: Dashboard, Profiles, Monitoring, Quick Fixes, Settings

**Result:** [ ] PASS / [ ] FAIL
**Terminal Output:** _______________________________________________
**Screenshot:** capture_2.1_launch.png

### Test 2.2: Application Menu Launch
**Steps:**
1. Open application menu (Super key or click Activities)
2. Search for "Bazzite"
3. Click "Bazzite Gaming Optimizer"

**Expected Behavior:**
- Application appears in search results
- Icon displays correctly (if icon available)
- Application launches successfully

**Result:** [ ] PASS / [ ] FAIL
**Notes:** _______________________________________________

### Test 2.3: Error Handling - Backend Not Found
```bash
# Temporarily move backend script
mv bazzite-optimizer.py bazzite-optimizer.py.bak

# Launch GUI
bazzite-optimizer-gui
```

**Expected Behavior:**
- Error dialog appears
- Message: "Backend Not Found" or similar
- GUI remains usable in read-only mode

**Cleanup:**
```bash
mv bazzite-optimizer.py.bak bazzite-optimizer.py
```

**Result:** [ ] PASS / [ ] FAIL
**Notes:** _______________________________________________

---

## Testing Phase 3: Dashboard Tab

### Test 3.1: Hardware Detection
**Steps:**
1. Launch GUI
2. View Dashboard tab (default)
3. Check hardware information cards

**Expected Data:**
- **CPU Card:**
  - Model name displayed (e.g., "Intel Core i9-10850K")
  - Core count shown (e.g., "10 cores")
- **GPU Card:**
  - Model name displayed (e.g., "NVIDIA GeForce RTX 5080")
  - VRAM amount shown (e.g., "16 GB")
- **Memory Card:**
  - Total RAM shown (e.g., "64 GB")
  - ZRAM size shown (e.g., "8 GB" or "Not configured")

**Result:** [ ] PASS / [ ] FAIL
**Actual Values:**
- CPU: _______________________________________________
- GPU: _______________________________________________
- RAM: _______________________________________________
**Screenshot:** capture_3.1_hardware.png

### Test 3.2: Current Configuration Display
**Expected Display:**
- Current profile shown (default: "None")
- Gaming mode switch (default: off/unchecked)
- System health percentage (0-100%)
- Last optimized timestamp
- Kernel version displayed

**Result:** [ ] PASS / [ ] FAIL
**Notes:** _______________________________________________

### Test 3.3: Gaming Mode Toggle
**Steps:**
1. Click gaming mode switch to ON
2. Observe status bar
3. Toggle back to OFF

**Expected Behavior:**
- Switch toggles smoothly
- Status bar updates: "Gaming Mode: ● Enabled" / "Gaming Mode: ○ Disabled"
- No errors in terminal

**Result:** [ ] PASS / [ ] FAIL
**Notes:** _______________________________________________

---

## Testing Phase 4: Profiles Tab

### Test 4.1: Profile Display
**Steps:**
1. Switch to Profiles tab
2. Verify all 4 profiles visible

**Expected Profiles:**
- [ ] ⚡ Competitive (top-left)
- [ ] ⚖️ Balanced (top-right)
- [ ] 📹 Streaming (bottom-left)
- [ ] 🎨 Creative (bottom-right)

Each profile should show:
- Icon/emoji
- Name and tagline
- Description
- 3+ features listed
- "Select" button

**Result:** [ ] PASS / [ ] FAIL
**Screenshot:** capture_4.1_profiles.png

### Test 4.2: Profile Selection
**Steps:**
1. Click "Select" on Balanced profile
2. Review details section

**Expected Behavior:**
- Details panel updates with profile information
- Features list expands
- "Recommended for" section shows
- "Apply Selected Profile" button becomes enabled

**Result:** [ ] PASS / [ ] FAIL
**Notes:** _______________________________________________

### Test 4.3: Profile Application (REQUIRES ROOT)
**Steps:**
1. Select Balanced profile
2. Click "Apply Selected Profile"
3. Confirm in dialog
4. Wait for completion

**Expected Behavior:**
- Confirmation dialog appears
- After confirming, progress dialog shows
- Progress bar pulses during application
- Success dialog appears on completion (or error dialog if failed)
- Operation takes 30-60 seconds

**Result:** [ ] PASS / [ ] FAIL
**Duration:** _____ seconds
**Terminal Output:** _______________________________________________
**Screenshot:** capture_4.3_apply.png

### Test 4.4: Benchmark Execution
**Steps:**
1. Click "Run Benchmark" button
2. Confirm in dialog
3. Wait for completion (5-10 minutes)

**Expected Behavior:**
- Confirmation dialog appears
- Benchmark runs in background
- Results dialog appears when complete
- Results include performance metrics

**Result:** [ ] PASS / [ ] FAIL / [ ] SKIPPED
**Notes:** _______________________________________________

---

## Testing Phase 5: Monitoring Tab

### Test 5.1: Start Monitoring
**Steps:**
1. Switch to Monitoring tab
2. Click "▶ Start Monitoring"
3. Observe metrics for 60 seconds

**Expected Behavior:**
- "Start Monitoring" button becomes disabled
- "Stop Monitoring" button becomes enabled
- Metrics update every 1 second
- Progress bars animate smoothly
- No lag or freezing

**Metrics to Verify:**
- [ ] CPU percentage (0-100%)
- [ ] CPU frequency (MHz)
- [ ] CPU temperature (°C) - if available
- [ ] GPU percentage (0-100%)
- [ ] GPU VRAM usage (MB)
- [ ] GPU temperature (°C) - if available
- [ ] RAM usage (GB)
- [ ] Swap usage (GB)

**Result:** [ ] PASS / [ ] FAIL
**Notes:** _______________________________________________
**Screenshot:** capture_5.1_monitoring.png

### Test 5.2: Monitoring Statistics
**Steps:**
1. Continue monitoring for 60 seconds
2. Observe statistics panel

**Expected Data:**
- CPU average calculated correctly
- GPU average calculated correctly
- Monitoring uptime counting (seconds)

**Result:** [ ] PASS / [ ] FAIL
**Notes:** _______________________________________________

### Test 5.3: Stop Monitoring
**Steps:**
1. Click "◼ Stop Monitoring"

**Expected Behavior:**
- Updates stop immediately
- "Start Monitoring" button becomes enabled
- "Stop Monitoring" button becomes disabled
- Last metrics remain visible

**Result:** [ ] PASS / [ ] FAIL
**Notes:** _______________________________________________

### Test 5.4: Monitoring Without psutil
**Setup:**
```bash
# Temporarily uninstall psutil
pip3 uninstall -y psutil

# Restart GUI
```

**Expected Behavior:**
- Monitoring still works (falls back to /proc parsing)
- Some metrics may show placeholder values
- No crashes or errors

**Cleanup:**
```bash
pip3 install --user psutil
```

**Result:** [ ] PASS / [ ] FAIL / [ ] SKIPPED
**Notes:** _______________________________________________

---

## Testing Phase 6: Quick Fixes Tab

### Test 6.1: Fix Display
**Steps:**
1. Switch to Quick Fixes tab
2. Verify all fixes visible

**Expected Fixes:**
- [ ] 🎮 Fix Steam
- [ ] 🔊 Fix Audio
- [ ] 🎨 Reset GPU
- [ ] 🧹 Clear Caches
- [ ] 🔄 Restart Gaming Services

**Result:** [ ] PASS / [ ] FAIL
**Screenshot:** capture_6.1_quickfixes.png

### Test 6.2: Audio Fix (SAFE TEST)
**Steps:**
1. Click "Apply Fix" on Audio fix
2. Wait for completion
3. Check log output

**Expected Behavior:**
- Progress dialog shows
- Fix completes in 5-30 seconds
- Success dialog appears
- Log shows timestamp and success message
- Audio continues working normally

**Result:** [ ] PASS / [ ] FAIL
**Log Output:** _______________________________________________

### Test 6.3: Fix Logging
**Steps:**
1. Apply any fix
2. Observe "Recent Fixes" log

**Expected Behavior:**
- Timestamp appears in log
- Fix name and status shown
- Log scrolls to bottom automatically
- Multiple fixes accumulate in log

**Result:** [ ] PASS / [ ] FAIL
**Notes:** _______________________________________________

### Test 6.4: Cache Clear Confirmation
**Steps:**
1. Click "Apply Fix" on Clear Caches
2. Observe confirmation dialog

**Expected Behavior:**
- Confirmation dialog appears first
- Warning message displayed
- Yes/No buttons
- Only proceeds if "Yes" clicked

**Result:** [ ] PASS / [ ] FAIL
**Notes:** _______________________________________________

---

## Testing Phase 7: Settings Tab

### Test 7.1: Settings Display
**Steps:**
1. Switch to Settings tab
2. Verify all sections visible

**Expected Sections:**
- [ ] General (auto-start, notifications, tray)
- [ ] Optimization (startup profile, auto-switching)
- [ ] Advanced (logs, backup, export, reset)
- [ ] About (version, links)

**Result:** [ ] PASS / [ ] FAIL
**Screenshot:** capture_7.1_settings.png

### Test 7.2: Toggle Switches
**Steps:**
1. Toggle each switch on and off
2. Verify visual feedback

**Switches to Test:**
- [ ] Start optimizer GUI on login
- [ ] Show notifications
- [ ] Minimize to system tray
- [ ] Apply profile on startup
- [ ] Enable automatic profile switching

**Expected Behavior:**
- All switches toggle smoothly
- Visual state changes clearly
- No errors

**Result:** [ ] PASS / [ ] FAIL
**Notes:** _______________________________________________

### Test 7.3: Default Profile Selection
**Steps:**
1. Click default profile dropdown
2. Select each option

**Expected Options:**
- [ ] Competitive
- [ ] Balanced
- [ ] Streaming
- [ ] Creative

**Result:** [ ] PASS / [ ] FAIL
**Notes:** _______________________________________________

### Test 7.4: Advanced Buttons
**Steps:**
1. Click each advanced button
2. Verify dialog appears

**Buttons:**
- [ ] View Logs → Dialog with message
- [ ] Backup Config → Dialog with message
- [ ] Restore Config → Dialog with message
- [ ] Export System Info → Dialog with message

**Result:** [ ] PASS / [ ] FAIL
**Notes:** _______________________________________________

### Test 7.5: Reset to Defaults
**Steps:**
1. Click "Reset to Defaults"
2. Confirm action

**Expected Behavior:**
- Confirmation dialog appears
- Warning message clear
- Only proceeds if confirmed
- Success message on completion

**Result:** [ ] PASS / [ ] FAIL
**Notes:** _______________________________________________

---

## Testing Phase 8: Integration Testing

### Test 8.1: Tab Switching
**Steps:**
1. Rapidly switch between all tabs
2. Return to each tab multiple times

**Expected Behavior:**
- No lag or freezing
- Content loads correctly each time
- No memory leaks (check with `top` or `htop`)

**Result:** [ ] PASS / [ ] FAIL
**Memory Usage:** _____MB
**Notes:** _______________________________________________

### Test 8.2: Window Resize
**Steps:**
1. Resize window to minimum size
2. Resize to maximum size
3. Resize to various intermediate sizes

**Expected Behavior:**
- Content scales appropriately
- No visual glitches
- All text remains readable
- Buttons remain accessible

**Result:** [ ] PASS / [ ] FAIL
**Notes:** _______________________________________________

### Test 8.3: Multiple Operations
**Steps:**
1. Start monitoring
2. Switch to Profiles tab
3. Apply a profile (while monitoring running)
4. Return to Monitoring tab

**Expected Behavior:**
- Monitoring continues in background
- Profile application succeeds
- No conflicts or errors
- UI remains responsive

**Result:** [ ] PASS / [ ] FAIL
**Notes:** _______________________________________________

### Test 8.4: Error Recovery
**Steps:**
1. Attempt profile application without root access
2. Try to launch with backend script removed
3. Network disconnected (if applicable)

**Expected Behavior:**
- Clear error messages
- GUI doesn't crash
- User can continue using other features
- Recovery instructions provided

**Result:** [ ] PASS / [ ] FAIL
**Notes:** _______________________________________________

---

## Testing Phase 9: Performance Testing

### Test 9.1: Launch Time
**Measurement:**
```bash
time bazzite-optimizer-gui
# Close immediately after window appears
```

**Expected:** <2 seconds
**Actual:** _____ seconds
**Result:** [ ] PASS / [ ] FAIL

### Test 9.2: Memory Usage (Idle)
**Measurement:**
```bash
# After GUI launched, check process:
ps aux | grep bazzite-optimizer-gui
# Or use htop/top
```

**Expected:** <100MB
**Actual:** _____MB
**Result:** [ ] PASS / [ ] FAIL

### Test 9.3: Memory Usage (Monitoring Active)
**Measurement:**
```bash
# With monitoring running for 5 minutes
ps aux | grep bazzite-optimizer-gui
```

**Expected:** <200MB
**Actual:** _____MB
**Result:** [ ] PASS / [ ] FAIL

### Test 9.4: CPU Usage (Idle)
**Expected:** <1% CPU
**Actual:** _____%
**Result:** [ ] PASS / [ ] FAIL

### Test 9.5: CPU Usage (Monitoring Active)
**Expected:** <5% CPU
**Actual:** _____%
**Result:** [ ] PASS / [ ] FAIL

---

## Testing Phase 10: Desktop Integration

### Test 10.1: Desktop File
```bash
desktop-file-validate ~/.local/share/applications/bazzite-optimizer-gui.desktop
```

**Expected:** No errors
**Result:** [ ] PASS / [ ] FAIL
**Output:** _______________________________________________

### Test 10.2: Application Menu Categories
**Expected Location:** System → Settings or System → Utilities
**Actual Location:** _______________________________________________
**Result:** [ ] PASS / [ ] FAIL

### Test 10.3: Icon Display
(If icon implemented)

**Expected:** Icon displays in:
- [ ] Application menu
- [ ] Window title bar
- [ ] Task bar/dock

**Result:** [ ] PASS / [ ] FAIL / [ ] N/A
**Notes:** _______________________________________________

---

## Known Issues / Expected Limitations

### Current Limitations:
1. **No Cairo graphs yet** - Monitoring shows metrics but not historical graphs
2. **Some settings not functional** - Placeholders for future features
3. **Icon not included** - Generic icon or no icon
4. **Auto-start not implemented** - Setting toggle doesn't save yet
5. **Profile state persistence** - May not remember across restarts

### Environment-Specific Issues:
- **Wayland**: Potential pkexec dialog positioning issues
- **HiDPI**: May need scaling adjustments
- **AMD GPU**: Some monitoring features may not work (NVIDIA-specific)

---

## Test Summary

**Date:** _______________
**Tester:** _______________
**System:** _______________
**Bazzite Version:** _______________
**GTK Version:** _______________

**Overall Results:**
- Total Tests: 50+
- Passed: _____ / _____
- Failed: _____ / _____
- Skipped: _____ / _____

**Critical Issues Found:** _______________________________________________
_______________________________________________
_______________________________________________

**Minor Issues Found:** _______________________________________________
_______________________________________________
_______________________________________________

**Recommended for Release:** [ ] YES / [ ] NO / [ ] WITH FIXES

---

## Screenshots Required for Release

1. `dashboard.png` - Dashboard tab with hardware info
2. `profiles.png` - Profiles tab showing all 4 profiles
3. `monitoring.png` - Monitoring tab with active metrics
4. `quickfixes.png` - Quick Fixes tab
5. `settings.png` - Settings tab
6. `profile_apply.png` - Profile application in progress
7. `monitoring_active.png` - Monitoring with real-time data

**Screenshot Naming Convention:** `v1.1.0_[tab-name]_[description].png`

---

**Testing Completed:** [ ] YES / [ ] NO
**Ready for Release:** [ ] YES / [ ] NO
**Signature:** _______________
**Date:** _______________
