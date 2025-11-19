# Bazzite Gaming Optimizer - User Guide

## 📘 Complete Guide to Gaming Optimization

**Version:** 1.6.0
**Last Updated:** 2025-11-18

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Gaming Profiles](#gaming-profiles)
3. [GUI Application](#gui-application)
4. [ML/AI Features](#mlai-features)
5. [Mobile Companion App](#mobile-companion-app)
6. [Command-Line Usage](#command-line-usage)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### What is Bazzite Optimizer?

Bazzite Gaming Optimizer is an enterprise-grade gaming optimization suite featuring:
- 🎮 **Automated Gaming Optimization**: 16 specialized optimizer classes
- 🤖 **Machine Learning**: AI-powered profile recommendations
- 📊 **Real-Time Monitoring**: Live performance metrics and graphs
- 📱 **Mobile App**: Remote monitoring and control
- ☁️ **Cloud API**: Community benchmarking and data sharing

### System Requirements

- **OS**: Bazzite Linux, Fedora, Ubuntu, Debian, Arch
- **Hardware**: NVIDIA RTX / AMD RDNA2+ / Intel GPUs
- **Python**: 3.10 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 500MB for installation

---

## Gaming Profiles

The optimizer includes 4 built-in gaming profiles optimized for different use cases:

### 🏆 Competitive Profile
**Best for**: Competitive FPS gaming (CS2, Valorant, Apex)

**Optimizations**:
- Maximum CPU performance (C-state=1, no power saving)
- Core isolation for gaming threads
- Network priority and low latency
- GPU maximum performance mode
- Compositor disabled for minimum input lag

**Expected Results**:
- 15-25% FPS improvement
- Reduced input lag
- Consistent frame times
- Higher power consumption (280-350W)

**Usage**:
```bash
./gaming-manager-suite.py --profile competitive
```

### ⚖️ Balanced Profile
**Best for**: General gaming, AAA titles, casual play

**Optimizations**:
- Moderate CPU performance (C-state=3)
- Balanced power management
- Normal compositor settings
- Moderate GPU clocks

**Expected Results**:
- 8-15% FPS improvement
- Good power efficiency
- Balanced temps (60-75°C)
- Moderate power consumption (200-280W)

**Usage**:
```bash
./gaming-manager-suite.py --profile balanced
```

### 🎥 Streaming Profile
**Best for**: Streaming to Twitch/YouTube with OBS

**Optimizations**:
- CPU encoding optimization
- Network upload priority
- Background process management
- Moderate GPU settings

**Expected Results**:
- Stable streaming performance
- Good encode quality
- Lower power consumption (180-250W)
- CPU reserved for encoding

**Usage**:
```bash
./gaming-manager-suite.py --profile streaming
```

### 🛡️ Safe Defaults
**Best for**: Troubleshooting, stability testing

**Optimizations**:
- Conservative settings
- All safety features enabled
- Default system behavior
- No aggressive tuning

**Usage**:
```bash
./gaming-manager-suite.py --profile safe_defaults
```

---

## GUI Application

### Launching the GUI

```bash
python bazzite-optimizer-gui.py
```

### Dashboard Tab

**Real-Time Metrics**:
- CPU/GPU usage and temps
- FPS counter (if available)
- RAM usage
- Power consumption
- 5-minute historical graphs

**Quick Actions**:
- Profile switcher dropdown
- Apply/Revert buttons
- Health check
- Emergency safe mode

### Profiles Tab

**Profile Management**:
1. **Select Profile**: Choose from built-in or custom profiles
2. **View Details**: See what optimizations will be applied
3. **Apply**: Click "Apply Profile" button
4. **Verify**: Check metrics to confirm improvements

**Custom Profile Creation**:
1. Click "Create Custom Profile"
2. Set profile name and description
3. Configure individual optimizations:
   - CPU governor and C-states
   - GPU power mode and clocks
   - Network priority
   - Compositor settings
4. Save profile

### Monitoring Tab

**Performance Graphs**:
- CPU usage over time
- GPU usage over time
- Temperature trends
- FPS history (if available)

**Export Data**:
- CSV export for analysis
- Screenshot graphs
- Benchmark reports

---

## ML/AI Features

### AI Profile Recommendations

The ML engine analyzes your hardware and usage patterns to recommend optimal profiles.

**Usage**:
1. **Collect Data**: Run benchmarks to gather performance data
2. **Get Recommendation**:
   ```bash
   python -c "
   from ml_engine.models.profile_optimizer import ProfileOptimizer, HardwareProfile, UsagePattern

   optimizer = ProfileOptimizer()

   # Your hardware
   hw = HardwareProfile(
       cpu_cores=10,
       cpu_frequency_mhz=5100,
       ram_gb=64,
       gpu_vendor='nvidia',
       gpu_vram_gb=16,
       gpu_compute_units=10752,
       storage_type='nvme',
       has_dedicated_gpu=True
   )

   # Your usage
   usage = UsagePattern(
       primary_use='competitive_gaming',
       games_played=['CS2', 'Valorant'],
       avg_session_hours=4.0,
       target_fps=240
   )

   rec = optimizer.recommend_profile(hw, usage)
   print(f'Recommended: {rec.profile_name} ({rec.confidence:.0%} confidence)')
   "
   ```

3. **Apply Recommendation**: Use suggested profile

### Performance Prediction

Predict FPS before applying profile:

```bash
python ml_engine/models/performance_predictor.py
```

### Game Auto-Detection

CNN automatically detects running games:

```python
from ai_engine.game_detection.detector import GameDetector

detector = GameDetector()
detections = detector.detect_from_system()

for game in detections:
    print(f"Detected: {game.game_name} ({game.confidence:.0%})")
    print(f"  Recommended profile: {game.recommended_profile}")
```

---

## Mobile Companion App

### Setup

1. **Start WebSocket Server**:
   ```bash
   python mobile_api/websocket_server.py
   ```

2. **Install Mobile App**:
   - Android: Install from APK
   - iOS: Install via TestFlight

3. **Pair Device**:
   - In desktop browser: `http://localhost:8081/pair/generate`
   - Get QR code
   - Scan with mobile app

### Features

**Real-Time Dashboard**:
- Live FPS counter
- CPU/GPU temps and usage
- Power consumption
- Connection status

**Remote Control**:
- Switch gaming profiles
- View system status
- Receive alerts

**Push Notifications**:
- Thermal warnings (>85°C)
- Performance drops
- Profile switches

---

## Command-Line Usage

### Gaming Manager

```bash
# Enable gaming mode with competitive profile
./gaming-manager-suite.py --enable --profile competitive

# Check system status
./gaming-manager-suite.py --status

# Run health check
./gaming-manager-suite.py --health

# Apply quick fixes
./gaming-manager-suite.py --fix steam    # Fix Steam issues
./gaming-manager-suite.py --fix audio    # Fix audio problems
./gaming-manager-suite.py --fix gpu      # Reset GPU to defaults

# Disable gaming mode (revert all changes)
./gaming-manager-suite.py --disable
```

### Gaming Monitor

```bash
# Real-time dashboard (curses interface)
./gaming-monitor-suite.py --mode dashboard

# Simple text output
./gaming-monitor-suite.py --mode simple

# Export metrics to files
./gaming-monitor-suite.py --mode export --interval 5

# Monitor specific metrics
./gaming-monitor-suite.py --mode dashboard --cpu --gpu --fps
```

### Benchmarking

```bash
# Run full benchmark suite
./gaming-maintenance-suite.sh

# CPU benchmark only
./gaming-maintenance-suite.sh --cpu

# GPU benchmark
./gaming-maintenance-suite.sh --gpu

# Disk performance
./gaming-maintenance-suite.sh --disk
```

---

## Advanced Features

### Cloud API

**Start FastAPI Server**:
```bash
uvicorn ml_engine.cloud_api.api_server:app --host 0.0.0.0 --port 8080
```

**API Endpoints**:
- `GET /api/v1/health` - Health check
- `POST /api/v1/profile/recommend` - Get ML recommendation
- `POST /api/v1/performance/predict` - Predict FPS
- `POST /api/v1/community/submit` - Submit benchmark
- `GET /api/v1/community/stats` - View stats

**Example**:
```bash
curl -X GET http://localhost:8080/api/v1/health
```

### Real Data Collection

Collect actual gaming performance data:

```bash
python ml_engine/data_collection/benchmark_collector.py \
    --duration 300 \
    --profile competitive \
    --game "CS2" \
    --resolution 1440p
```

### Hyperparameter Tuning

Optimize ML models:

```python
from ml_engine.evaluation.model_optimizer import ModelOptimizer

optimizer = ModelOptimizer()
results = optimizer.optimize_profile_classifier(X_train, y_train, method='grid')
print(f"Best params: {results['best_params']}")
```

### Docker Deployment

```bash
cd deployment
docker-compose up -d
```

Access API at `http://localhost:8080`

---

## Troubleshooting

### Common Issues

**1. Gaming mode won't enable**
- Check logs: `journalctl -u gaming-mode`
- Verify permissions: `sudo usermod -aG input $USER`
- Reboot and try again

**2. FPS not improving**
- Verify profile applied: `./gaming-manager-suite.py --status`
- Check GPU power mode: `nvidia-smi -q | grep "Power Management"`
- Review validation: `./gaming-manager-suite.py --health`

**3. System overheating**
- Switch to balanced profile
- Check fan curves: `sensors`
- Clean dust from cooling system

**4. ML models not loading**
- Install dependencies: `pip install -r requirements.txt`
- Train models first: See ML_TRAINING_GUIDE.md

**5. Mobile app won't connect**
- Check WebSocket server running on port 8081
- Verify firewall allows connections
- Use correct IP address in app settings

### Getting Help

- **Documentation**: See `docs/` directory
- **FAQ**: See `docs/FAQ.md`
- **Logs**: Check `~/.local/share/bazzite-optimizer/logs/`
- **GitHub Issues**: Report bugs with system info

---

## Best Practices

### 1. Start with Balanced Profile
Don't jump straight to competitive. Test balanced first.

### 2. Monitor Temperatures
Keep CPU <85°C, GPU <85°C for longevity.

### 3. Collect Benchmarks
More data = better ML recommendations.

### 4. Regular Updates
Keep the optimizer and drivers updated.

### 5. Backup Settings
Save custom profiles before major changes.

---

## Next Steps

- Read [Installation Guide](INSTALLATION_GUIDE.md)
- Check [API Documentation](API_DOCUMENTATION.md)
- Review [ML Training Guide](ML_TRAINING_GUIDE.md)
- See [FAQ](FAQ.md) for common questions

**Happy Gaming! 🎮**
