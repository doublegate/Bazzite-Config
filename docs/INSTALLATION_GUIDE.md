# Installation Guide

## Bazzite Gaming Optimizer - Complete Installation

**Version:** 1.6.0
**Platform Support:** Bazzite, Fedora, Ubuntu, Debian, Arch

---

## Quick Install (Bazzite)

```bash
# Clone repository
git clone https://github.com/yourusername/Bazzite-Config
cd Bazzite-Config

# Make scripts executable
chmod +x gaming-manager-suite.py gaming-monitor-suite.py gaming-maintenance-suite.sh

# Install Python dependencies
pip install --user -r requirements.txt

# Test installation
./gaming-manager-suite.py --status
```

---

## Prerequisites

### System Requirements

- **OS**: Bazzite Linux (recommended), Fedora 38+, Ubuntu 22.04+, Debian 12+, Arch
- **Python**: 3.10 or higher
- **Hardware**:
  - NVIDIA RTX series (5080, 4090, 4080, etc.)
  - AMD RDNA2/RDNA3 (RX 6000/7000 series)
  - Intel Arc GPUs
- **RAM**: 4GB minimum, 8GB recommended for ML features
- **Storage**: 500MB free space

### Required Packages

**Bazzite/Fedora**:
```bash
sudo dnf install python3-pip python3-psutil python3-configparser \
                 stress-ng sysbench lm_sensors git
```

**Ubuntu/Debian**:
```bash
sudo apt install python3-pip python3-psutil python3-yaml \
                 stress-ng sysbench lm-sensors git
```

**Arch**:
```bash
sudo pacman -S python-pip python-psutil python-yaml \
               stress sysbench lm_sensors git
```

---

## Step-by-Step Installation

### 1. Clone Repository

```bash
cd ~
git clone https://github.com/yourusername/Bazzite-Config
cd Bazzite-Config
```

### 2. Install Python Dependencies

```bash
pip install --user -r requirements.txt
```

**Dependencies include**:
- psutil (system monitoring)
- numpy (numerical operations)
- scikit-learn (machine learning)
- torch (deep learning, optional)
- fastapi + uvicorn (cloud API, optional)
- websockets (mobile API, optional)

### 3. Make Scripts Executable

```bash
chmod +x gaming-manager-suite.py
chmod +x gaming-monitor-suite.py
chmod +x gaming-maintenance-suite.sh
```

### 4. Verify Installation

```bash
./gaming-manager-suite.py --status
```

Expected output:
```
Gaming Mode Status: Disabled
Current Profile: None
System Health: ✓ All checks passed
```

---

## Optional Components

### ML/AI Features

**Install PyTorch** (for deep learning models):
```bash
pip install --user torch torchvision torchaudio
```

**Train initial models** (optional, models included):
```bash
python ml_engine/models/profile_optimizer.py
python ai_engine/game_detection/detector.py
```

### GUI Application

**Install Qt dependencies**:
```bash
# Bazzite/Fedora
sudo dnf install python3-qt6 python3-matplotlib

# Ubuntu/Debian
sudo apt install python3-pyqt6 python3-matplotlib

# Then launch GUI
python bazzite-optimizer-gui.py
```

### Cloud API

**Start FastAPI server**:
```bash
uvicorn ml_engine.cloud_api.api_server:app --host 0.0.0.0 --port 8080
```

Access at: `http://localhost:8080/docs`

### Mobile Companion App

**Start WebSocket server**:
```bash
python mobile_api/websocket_server.py
```

**Install mobile app**:
- Download APK (Android) or TestFlight (iOS)
- Scan QR code to pair

---

## Docker Installation

### Using Docker Compose (Recommended)

```bash
cd deployment
docker-compose up -d
```

**Services started**:
- ML/Cloud API on port 8080
- Mobile WebSocket on port 8081
- Nginx reverse proxy on ports 80/443

### Using Docker

```bash
docker build -t bazzite-optimizer:latest -f deployment/Dockerfile .
docker run -p 8080:8080 -p 8081:8081 bazzite-optimizer:latest
```

### Kubernetes Deployment

```bash
kubectl apply -f deployment/kubernetes/deployment.yaml
```

---

## Configuration

### Default Locations

- **Profiles**: `~/.config/gaming-manager/profiles/`
- **Logs**: `/var/log/gaming-benchmark/` or `~/.local/share/bazzite-optimizer/logs/`
- **ML Models**: `~/.local/share/bazzite-optimizer/ml-models/`
- **Benchmarks**: `~/.local/share/bazzite-optimizer/real-benchmarks/`
- **Configuration**: `/etc/gaming-mode.conf`

### Custom Configuration

Edit `/etc/gaming-mode.conf`:

```ini
[gaming-mode]
default_profile = competitive
auto_apply = false
monitor_interval = 1
log_level = INFO

[hardware]
gpu_vendor = nvidia
cpu_cores = 10
ram_gb = 64
```

---

## Systemd Service (Optional)

Create systemd service for auto-start:

```bash
sudo tee /etc/systemd/system/bazzite-optimizer.service <<EOF
[Unit]
Description=Bazzite Gaming Optimizer
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/bin/python3 $HOME/Bazzite-Config/gaming-manager-suite.py --enable --profile balanced
ExecStop=/usr/bin/python3 $HOME/Bazzite-Config/gaming-manager-suite.py --disable
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl enable bazzite-optimizer
sudo systemctl start bazzite-optimizer
```

---

## Post-Installation

### 1. Test Gaming Profile

```bash
./gaming-manager-suite.py --profile balanced --enable
./gaming-manager-suite.py --status
./gaming-manager-suite.py --health
```

### 2. Run Benchmark

```bash
./gaming-maintenance-suite.sh
```

### 3. Collect Real Data

```bash
python ml_engine/data_collection/benchmark_collector.py \
    --duration 300 --profile balanced --game "CS2"
```

### 4. Launch GUI

```bash
python bazzite-optimizer-gui.py
```

---

## Troubleshooting Installation

### Python Module Not Found

```bash
# Install missing module
pip install --user <module-name>

# Or reinstall all
pip install --user -r requirements.txt --force-reinstall
```

### Permission Denied

```bash
# Make scripts executable
chmod +x *.py *.sh

# Add user to required groups
sudo usermod -aG input,video $USER
newgrp input
```

### systemd Service Won't Start

```bash
# Check logs
sudo journalctl -u bazzite-optimizer -n 50

# Verify paths in service file
systemctl cat bazzite-optimizer

# Test command manually
python3 gaming-manager-suite.py --status
```

### GPU Not Detected

**NVIDIA**:
```bash
# Verify driver
nvidia-smi

# Install if missing
sudo dnf install nvidia-driver  # Fedora/Bazzite
```

**AMD**:
```bash
# Verify
lspci | grep VGA
radeontop  # Install if needed
```

---

## Upgrading

### From v1.5.0 to v1.6.0

```bash
cd Bazzite-Config
git pull origin main

# Install new dependencies
pip install --user -r requirements.txt

# Retrain ML models (optional)
python ml_engine/models/model_trainer.py
```

### Preserving Custom Profiles

Custom profiles are saved in `~/.config/gaming-manager/profiles/` and will not be affected by upgrades.

---

## Uninstallation

### Remove Optimizer

```bash
cd Bazzite-Config

# Disable gaming mode
./gaming-manager-suite.py --disable

# Remove systemd service (if installed)
sudo systemctl stop bazzite-optimizer
sudo systemctl disable bazzite-optimizer
sudo rm /etc/systemd/system/bazzite-optimizer.service

# Remove files
cd ..
rm -rf Bazzite-Config
```

### Remove Python Packages

```bash
pip uninstall -y -r requirements.txt
```

### Reset to System Defaults

```bash
# If reset script available
./reset-bazzite-defaults.sh
```

---

## Next Steps

- Read [User Guide](USER_GUIDE.md) for usage instructions
- Check [API Documentation](API_DOCUMENTATION.md) for cloud features
- Review [FAQ](FAQ.md) for common questions

**Installation Complete! 🎉**
