# Performance Benchmarking Guide

## Overview

The Gaming Maintenance Suite provides comprehensive benchmarking capabilities to validate system performance and optimization effectiveness. This guide covers benchmarking procedures, interpretation of results, and performance optimization validation.

## Benchmark Categories

### 1. CPU Performance Testing

#### Multi-Core Stress Testing
```bash
# Quick CPU benchmark (5 minutes)
./gaming-maintenance-suite.sh --cpu-bench --duration 300

# Comprehensive CPU test (30 minutes)
./gaming-maintenance-suite.sh --cpu-bench --duration 1800 --intensive
```

**Tests Performed:**
- **Stress-ng**: Multi-core CPU stress with various workloads
- **Sysbench**: Memory bandwidth and CPU computation tests
- **Frequency Scaling**: Real-time CPU frequency monitoring
- **Temperature Monitoring**: Thermal behavior under load
- **C-state Analysis**: Power state transition efficiency

**Expected Results (Intel i9-10850K):**
```
CPU Performance Metrics:
├─ Multi-core Score: 18,000-22,000 (stress-ng)
├─ Single-core Score: 1,800-2,200
├─ Memory Bandwidth: 45-55 GB/s
├─ CPU Frequency: 4.8-5.2 GHz (boost)
├─ Temperature Range: 65-85°C (under load)
└─ C-state Latency: <50μs (C1), <200μs (C3)
```

#### CPU Optimization Validation
```bash
# Test with default settings
./gaming-manager-suite.py --disable
./gaming-maintenance-suite.sh --cpu-bench

# Test with gaming optimizations
./gaming-manager-suite.py --enable  
./gaming-maintenance-suite.sh --cpu-bench

# Compare results
./gaming-maintenance-suite.sh --compare-results
```

### 2. GPU Performance Testing

#### GPU Workload Simulation
```bash
# GPU stress test
./gaming-maintenance-suite.sh --gpu-bench

# Gaming workload simulation
./gaming-maintenance-suite.sh --gpu-bench --gaming-workload

# Overclocking validation
./gaming-maintenance-suite.sh --gpu-bench --validate-oc
```

**Tests Performed:**
- **GPU Utilization**: Maximum throughput testing
- **Memory Bandwidth**: VRAM performance validation
- **Temperature Monitoring**: Thermal throttling detection
- **Power Draw**: TGP compliance verification
- **Clock Stability**: Overclock stability testing

**Expected Results (NVIDIA RTX 5080):**
```
GPU Performance Metrics:
├─ GPU Utilization: 95-99% (under load)
├─ Memory Usage: 14-16 GB (full workload)
├─ GPU Clock: 2800-3100 MHz (boosted)
├─ Memory Clock: 1750-2250 MHz (effective)
├─ Temperature: 65-83°C (gaming load)
├─ Power Draw: 320-400W (TGP)
└─ DLSS Performance: 2-3x improvement (quality mode)
```

#### GPU Driver Optimization Testing
```bash
# Test different PowerMizer modes
nvidia-settings -a [gpu:0]/GpuPowerMizerMode=0  # Adaptive
./gaming-maintenance-suite.sh --gpu-bench --quick

nvidia-settings -a [gpu:0]/GpuPowerMizerMode=1  # Max Performance
./gaming-maintenance-suite.sh --gpu-bench --quick

# Validate optimization impact
./gaming-maintenance-suite.sh --gpu-compare
```

### 3. Memory Performance Testing

#### System Memory Bandwidth
```bash
# Memory bandwidth test
./gaming-maintenance-suite.sh --memory-bench

# ZRAM optimization validation
./gaming-maintenance-suite.sh --memory-bench --zram-test

# Memory stress test
./gaming-maintenance-suite.sh --memory-bench --stress-test
```

**Tests Performed:**
- **Sequential Access**: Large block memory operations
- **Random Access**: Small block random memory patterns
- **Memory Latency**: Access time measurements
- **ZRAM Performance**: Compression ratio and speed
- **Swap Performance**: Virtual memory efficiency

**Expected Results (64GB DDR4-3200):**
```
Memory Performance Metrics:
├─ Sequential Read: 45-50 GB/s
├─ Sequential Write: 40-45 GB/s
├─ Random Read: 35-40 GB/s
├─ Random Write: 30-35 GB/s
├─ Memory Latency: 60-80ns
├─ ZRAM Compression: 2.5-3.5x ratio
└─ ZRAM Throughput: 8-12 GB/s
```

#### Memory Optimization Validation
```bash
# Test default swappiness
echo 60 | sudo tee /proc/sys/vm/swappiness
./gaming-maintenance-suite.sh --memory-bench --gaming-workload

# Test optimized swappiness  
echo 120 | sudo tee /proc/sys/vm/swappiness
./gaming-maintenance-suite.sh --memory-bench --gaming-workload

# Compare memory efficiency
./gaming-maintenance-suite.sh --memory-compare
```

### 4. Storage Performance Testing

#### NVMe SSD Benchmarking
```bash
# Sequential I/O performance
./gaming-maintenance-suite.sh --disk-bench --sequential

# Random I/O performance
./gaming-maintenance-suite.sh --disk-bench --random

# Gaming load simulation
./gaming-maintenance-suite.sh --disk-bench --gaming-load
```

**Tests Performed:**
- **Sequential Read/Write**: Large file transfers
- **Random 4K**: Small file operations
- **Queue Depth Scaling**: I/O parallelism testing
- **Game Loading**: Asset streaming simulation
- **Sustained Performance**: Thermal throttling detection

**Expected Results (Samsung 990 EVO Plus 2TB):**
```
Storage Performance Metrics:
├─ Sequential Read: 7,000-7,450 MB/s
├─ Sequential Write: 6,500-6,900 MB/s
├─ Random 4K Read: 450-650K IOPS
├─ Random 4K Write: 500-750K IOPS
├─ Game Loading: 2-4 GB/s (asset streaming)
└─ Sustained Write: 2,000+ MB/s (10+ minutes)
```

#### Storage Optimization Testing
```bash
# Test different I/O schedulers
echo mq-deadline | sudo tee /sys/block/nvme0n1/queue/scheduler
./gaming-maintenance-suite.sh --disk-bench --quick

echo none | sudo tee /sys/block/nvme0n1/queue/scheduler  
./gaming-maintenance-suite.sh --disk-bench --quick

# Compare scheduler performance
./gaming-maintenance-suite.sh --disk-compare
```

### 5. System Integration Testing

#### Gaming Performance Simulation
```bash
# Comprehensive gaming workload
./gaming-maintenance-suite.sh --gaming-bench

# Multi-component stress test
./gaming-maintenance-suite.sh --full-system-bench

# Optimization effectiveness test
./gaming-maintenance-suite.sh --optimization-validation
```

**Combined Workload Testing:**
- **CPU + GPU**: Gaming scenario simulation
- **Memory + Storage**: Asset loading patterns
- **Network + Disk**: Multiplayer game simulation
- **Thermal Management**: Sustained performance validation

## Benchmark Interpretation

### Performance Baselines

#### High-End Configuration Targets
```
Component          | Baseline    | Optimized   | Improvement
-------------------|-------------|-------------|-------------
CPU Multi-core     | 18,000      | 22,000      | +22%
GPU Gaming         | 95 FPS      | 115 FPS     | +21%
Memory Bandwidth   | 45 GB/s     | 52 GB/s     | +16%
Storage Sequential | 7,000 MB/s  | 7,400 MB/s  | +6%
Game Loading       | 8.5 sec     | 6.2 sec     | +27%
```

#### Performance Regression Detection
```bash
# Establish baseline
./gaming-maintenance-suite.sh --establish-baseline

# Regular performance monitoring
./gaming-maintenance-suite.sh --regression-test

# Performance trend analysis
./gaming-maintenance-suite.sh --analyze-trends
```

### Result Analysis

#### CPU Performance Analysis
```bash
# Detailed CPU analysis
./gaming-maintenance-suite.sh --analyze-cpu

# Check for throttling
grep -i throttle /var/log/gaming-benchmark/cpu_*.log

# Frequency scaling analysis
./gaming-maintenance-suite.sh --frequency-analysis
```

**Key Metrics to Monitor:**
- **Base Clock Stability**: Should maintain boost clocks under load
- **Temperature Control**: Should stay below 85°C for sustained performance
- **C-state Effectiveness**: Lower latency with `intel_idle.max_cstate=1`
- **Performance Scaling**: Linear scaling with core count

#### GPU Performance Analysis
```bash
# GPU utilization analysis
./gaming-maintenance-suite.sh --analyze-gpu

# Thermal analysis
./gaming-maintenance-suite.sh --gpu-thermal-analysis

# Power efficiency analysis
./gaming-maintenance-suite.sh --gpu-power-analysis
```

**Performance Indicators:**
- **Consistent Utilization**: 95%+ GPU usage during testing
- **Thermal Stability**: No throttling below 83°C
- **Clock Consistency**: Minimal clock variation during load
- **Power Efficiency**: Optimal performance/watt ratio

### Optimization Effectiveness Measurement

#### Before/After Comparison
```bash
# Pre-optimization baseline
./gaming-manager-suite.py --disable
./gaming-maintenance-suite.sh --full-bench --save-baseline

# Post-optimization measurement  
./gaming-manager-suite.py --enable
./gaming-maintenance-suite.sh --full-bench --compare-baseline

# Generate improvement report
./gaming-maintenance-suite.sh --optimization-report
```

#### Specific Optimization Validation

**C-state Optimization:**
```bash
# Test default C-states
sudo grubby --update-kernel=ALL --remove-args="intel_idle.max_cstate=1"
reboot

# Benchmark with default C-states
./gaming-maintenance-suite.sh --latency-test --save-results=default

# Test optimized C-states
sudo grubby --update-kernel=ALL --args="intel_idle.max_cstate=1"
reboot

# Benchmark with optimized C-states
./gaming-maintenance-suite.sh --latency-test --compare-results=default
```

**ZRAM Optimization:**
```bash
# Disable ZRAM temporarily
sudo swapoff /dev/zram0

# Test without ZRAM
./gaming-maintenance-suite.sh --memory-pressure-test --save-results=no-zram

# Re-enable optimized ZRAM
sudo swapon /dev/zram0

# Test with optimized ZRAM
./gaming-maintenance-suite.sh --memory-pressure-test --compare-results=no-zram
```

## Automated Benchmark Scheduling

### Scheduled Performance Monitoring
```bash
# Create systemd timer for daily benchmarks
sudo tee /etc/systemd/system/gaming-bench.service << EOF
[Unit]
Description=Gaming Performance Benchmark
After=multi-user.target

[Service]
Type=oneshot
User=$USER
WorkingDirectory=/home/$USER/Bazzite-Config
ExecStart=/home/$USER/Bazzite-Config/gaming-maintenance-suite.sh --auto-bench
EOF

sudo tee /etc/systemd/system/gaming-bench.timer << EOF
[Unit]
Description=Daily Gaming Benchmark
Requires=gaming-bench.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Enable automatic benchmarking
sudo systemctl enable --now gaming-bench.timer
```

### Performance Regression Alerts
```bash
# Configure performance alerts
tee ~/.config/gaming-manager/alert-config.json << EOF
{
  "performance_thresholds": {
    "cpu_degradation": 10,
    "gpu_degradation": 15,
    "memory_degradation": 20,
    "disk_degradation": 25
  },
  "alert_methods": ["email", "desktop_notification"],
  "baseline_update_interval": "weekly"
}
EOF
```

## Best Practices

### Benchmark Environment Preparation

**System Preparation:**
```bash
# Ensure consistent environment
./gaming-manager-suite.py --health
systemctl --user stop steam # Stop unnecessary processes
killall -STOP firefox       # Pause background applications

# Thermal preparation
sensors # Check initial temperatures
sleep 300 # Allow thermal normalization
```

**Consistent Test Conditions:**
1. **Thermal State**: Allow 5-minute cooldown between tests
2. **Background Load**: Minimize active applications
3. **Power State**: Ensure AC power for laptops
4. **Storage Space**: Maintain >20% free space on test drives

### Performance Optimization Workflow

1. **Establish Baseline**: Run comprehensive benchmarks before optimization
2. **Apply Single Optimization**: Change one parameter at a time
3. **Validate Improvement**: Re-run relevant benchmarks
4. **Document Changes**: Record optimization and impact
5. **Stability Testing**: Verify long-term stability
6. **Rollback if Needed**: Revert if performance degrades

### Result Documentation

**Performance Log Format:**
```bash
# Generate comprehensive report
./gaming-maintenance-suite.sh --generate-report

# Example output location
cat /var/log/gaming-benchmark/performance-report-$(date +%Y%m%d).md
```

**Report Contents:**
- Hardware configuration summary
- Benchmark methodology and parameters
- Before/after performance comparison
- Optimization recommendations
- Stability assessment
- Environmental conditions during testing

This benchmarking framework provides the foundation for scientific performance optimization and validation of the Bazzite Gaming Optimization Suite's effectiveness.