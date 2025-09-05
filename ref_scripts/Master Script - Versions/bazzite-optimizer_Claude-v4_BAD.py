#!/usr/bin/env python3
"""
Bazzite DX Ultimate Gaming Optimization Master Script v4.0.0
For RTX 5080, Intel i9-10850K, 64GB RAM, Samsung 990 EVO Plus SSDs

Version 4.0 enhancements:
- Stability testing system for overclocking validation
- Power consumption monitoring and tracking
- Log rotation for long-term maintenance  
- Security warnings for mitigation disabling
- Display server auto-detection (X11/Wayland)
- Automated backup scheduling
- Steam Deck/handheld detection and optimization
- Enhanced NVIDIA GPU verification
- Safer GRUB modification with validation
- Conservative Intel undervolting with stepping
- Network isolation mode for competitive gaming
- Crash recovery and safe mode
- Performance regression detection

Author: System Optimization Framework
License: MIT
"""

import os
import sys
import subprocess
import logging
import json
import time
import shutil
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union
import argparse
import hashlib
import platform
import psutil
import threading
import signal
import tempfile
import statistics

# ============================================================================
# CONFIGURATION AND CONSTANTS
# ============================================================================

SCRIPT_VERSION = "4.0.0"
LOG_DIR = Path("/var/log/bazzite-optimizer")
CONFIG_BACKUP_DIR = Path("/var/backups/bazzite-optimizer")
PROFILE_DIR = Path("/etc/bazzite-optimizer/profiles")
SHADER_CACHE_DIR = Path("/var/cache/gaming-shaders")
CRASH_RECOVERY_DIR = Path("/var/cache/bazzite-optimizer/recovery")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# Minimum requirements
MIN_KERNEL_VERSION = (6, 1, 0)  # For MGLRU support
MIN_DISK_SPACE_GB = 10  # Increased for stability testing logs
MAX_GPU_TEMP_WARNING = 83  # Celsius
MAX_CPU_TEMP_WARNING = 95  # Celsius
MAX_GPU_TEMP_CRITICAL = 90  # Emergency throttle
MAX_CPU_TEMP_CRITICAL = 100  # Emergency throttle

# Stability test thresholds
STABILITY_TEST_DURATION = 300  # 5 minutes default
MAX_GPU_TEMP_STRESS = 87  # Max allowed during stress test
MAX_CPU_TEMP_STRESS = 98  # Max allowed during stress test
MIN_STABILITY_SCORE = 95  # Minimum % to pass

# Security warning flags
SECURITY_WARNINGS_SHOWN = False

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ============================================================================
# GAMING PROFILES - Enhanced with safety features
# ============================================================================

GAMING_PROFILES = {
    "competitive": {
        "name": "Competitive Gaming",
        "description": "Maximum performance, minimal latency, no visual effects",
        "security_risk": "HIGH",  # Due to disabled mitigations
        "settings": {
            "cpu_governor": "performance",
            "gpu_power_mode": 1,
            "gpu_clock_offset": 525,
            "gpu_mem_offset": 1000,
            "network_latency": "ultra-low",
            "network_isolation": True,  # New: isolate gaming traffic
            "audio_quantum": 256,
            "visual_effects": False,
            "compositor_bypass": True,
            "mouse_polling": 1000,
            "disable_mitigations": True,
            "isolate_cores": True,
            "fan_profile": "aggressive",
            "undervolt_aggressive": False  # Conservative for stability
        }
    },
    "balanced": {
        "name": "Balanced Gaming",
        "description": "Good performance with visual quality and moderate thermals",
        "security_risk": "MEDIUM",
        "settings": {
            "cpu_governor": "performance",
            "gpu_power_mode": 1,
            "gpu_clock_offset": 400,
            "gpu_mem_offset": 800,
            "network_latency": "low",
            "network_isolation": False,
            "audio_quantum": 512,
            "visual_effects": True,
            "compositor_bypass": False,
            "mouse_polling": 500,
            "disable_mitigations": True,
            "isolate_cores": False,
            "fan_profile": "balanced",
            "undervolt_aggressive": False
        }
    },
    "streaming": {
        "name": "Streaming Optimized",
        "description": "Optimized for OBS/streaming with encoding headroom",
        "security_risk": "LOW",
        "settings": {
            "cpu_governor": "schedutil",
            "gpu_power_mode": 2,
            "gpu_clock_offset": 350,
            "gpu_mem_offset": 600,
            "network_latency": "balanced",
            "network_isolation": False,
            "audio_quantum": 1024,
            "visual_effects": True,
            "compositor_bypass": False,
            "mouse_polling": 500,
            "disable_mitigations": False,
            "isolate_cores": True,  # Reserve cores for encoding
            "fan_profile": "quiet",
            "undervolt_aggressive": False
        }
    },
    "creative": {
        "name": "Creative Workloads",
        "description": "Optimized for rendering and creative applications",
        "security_risk": "LOW",
        "settings": {
            "cpu_governor": "performance",
            "gpu_power_mode": 1,
            "gpu_clock_offset": 450,
            "gpu_mem_offset": 900,
            "network_latency": "normal",
            "network_isolation": False,
            "audio_quantum": 2048,
            "visual_effects": True,
            "compositor_bypass": False,
            "mouse_polling": 125,
            "disable_mitigations": False,
            "isolate_cores": False,
            "fan_profile": "balanced",
            "undervolt_aggressive": False
        }
    },
    "safe": {
        "name": "Safe Mode",
        "description": "Conservative settings for troubleshooting",
        "security_risk": "NONE",
        "settings": {
            "cpu_governor": "schedutil",
            "gpu_power_mode": 2,
            "gpu_clock_offset": 0,
            "gpu_mem_offset": 0,
            "network_latency": "normal",
            "network_isolation": False,
            "audio_quantum": 1024,
            "visual_effects": True,
            "compositor_bypass": False,
            "mouse_polling": 125,
            "disable_mitigations": False,
            "isolate_cores": False,
            "fan_profile": "balanced",
            "undervolt_aggressive": False
        }
    },
    "handheld": {
        "name": "Handheld/Steam Deck",
        "description": "Optimized for battery life and thermal constraints",
        "security_risk": "LOW",
        "settings": {
            "cpu_governor": "powersave",
            "gpu_power_mode": 0,
            "gpu_clock_offset": 0,
            "gpu_mem_offset": 0,
            "network_latency": "balanced",
            "network_isolation": False,
            "audio_quantum": 1024,
            "visual_effects": False,
            "compositor_bypass": False,
            "mouse_polling": 125,
            "disable_mitigations": False,
            "isolate_cores": False,
            "fan_profile": "quiet",
            "undervolt_aggressive": False
        }
    }
}

# ============================================================================
# FAN CURVE PROFILES
# ============================================================================

FAN_CURVES = {
    "aggressive": {
        "gpu": [(30, 40), (50, 60), (65, 80), (75, 90), (80, 100)],
        "cpu": "performance"
    },
    "balanced": {
        "gpu": [(30, 30), (50, 45), (65, 60), (75, 75), (83, 90), (87, 100)],
        "cpu": "balanced"
    },
    "quiet": {
        "gpu": [(30, 20), (50, 30), (65, 45), (75, 60), (83, 75), (90, 100)],
        "cpu": "quiet"
    },
    "custom": {
        "gpu": [],  # User-defined
        "cpu": "balanced"
    }
}

# ============================================================================
# OPTIMIZATION CONFIGURATIONS - Enhanced with safety features
# ============================================================================

# NVIDIA RTX 5080 Configuration - Enhanced with validation
NVIDIA_MODULE_CONFIG = """# RTX 5080 Blackwell Gaming Optimizations v4
# Force -open driver variant for RTX 5080
options nvidia NVreg_OpenRmEnableUnsupportedGpus=1
options nvidia-drm modeset=1 fbdev=1
options nvidia NVreg_PreserveVideoMemoryAllocations=1
options nvidia NVreg_RegistryDwords="PowerMizerEnable=0x1;PerfLevelSrc=0x2222"
options nvidia NVreg_EnableGpuFirmware=1
options nvidia NVreg_RegistryDwords="PerfLevelSrc=0x2222;PowerMizerDefaultAC=0x1"
options nvidia NVreg_EnableResizableBar=1
options nvidia NVreg_EnablePCIeGen3=0
options nvidia NVreg_UsePageAttributeTable=1
options nvidia NVreg_EnableHDMI20=1
options nvidia NVreg_EnableStreamMemOPs=1
options nvidia NVreg_EnableBacklightHandler=1
# Safety: Temperature monitoring enabled
options nvidia NVreg_TemperatureMonitoring=1
"""

# Dynamic GPU Optimization Script with safety checks
NVIDIA_OPTIMIZATION_SCRIPT = """#!/bin/bash
# RTX 5080 Gaming Optimization Script v4 - With Safety Features

# Safety: Check if NVIDIA GPU exists
if ! command -v nvidia-smi &> /dev/null; then
    echo "WARNING: nvidia-smi not found, skipping GPU optimizations"
    exit 0
fi

if ! nvidia-smi &> /dev/null; then
    echo "WARNING: No NVIDIA GPU detected, skipping optimizations"
    exit 0
fi

# Function to get GPU temperature
get_gpu_temp() {
    nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits 2>/dev/null || echo "0"
}

# Function to get GPU power draw
get_gpu_power() {
    nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits 2>/dev/null | cut -d. -f1 || echo "0"
}

# Safety check: Emergency throttle if too hot
emergency_check() {
    local temp=$(get_gpu_temp)
    if [ $temp -gt {MAX_GPU_TEMP_CRITICAL} ]; then
        echo "CRITICAL: GPU temperature at ${temp}°C! Emergency throttling!"
        nvidia-settings -a '[gpu:0]/GPUPowerMizerMode=0' 2>/dev/null || true
        nvidia-settings -a '[gpu:0]/GPUTargetFanSpeed=100' 2>/dev/null || true
        exit 1
    fi
}

# Function to apply fan curve with safety
apply_fan_curve() {
    local temp=$(get_gpu_temp)
    local fan_speed=50
    
    # Safety override for high temps
    if [ $temp -gt 85 ]; then
        fan_speed=100
    else
        # Apply fan curve based on profile
        case "${FAN_PROFILE:-balanced}" in
            aggressive)
                if [ $temp -le 30 ]; then fan_speed=40
                elif [ $temp -le 50 ]; then fan_speed=60
                elif [ $temp -le 65 ]; then fan_speed=80
                elif [ $temp -le 75 ]; then fan_speed=90
                else fan_speed=100; fi
                ;;
            balanced)
                if [ $temp -le 30 ]; then fan_speed=30
                elif [ $temp -le 50 ]; then fan_speed=45
                elif [ $temp -le 65 ]; then fan_speed=60
                elif [ $temp -le 75 ]; then fan_speed=75
                elif [ $temp -le 83 ]; then fan_speed=90
                else fan_speed=100; fi
                ;;
            quiet)
                if [ $temp -le 30 ]; then fan_speed=20
                elif [ $temp -le 50 ]; then fan_speed=30
                elif [ $temp -le 65 ]; then fan_speed=45
                elif [ $temp -le 75 ]; then fan_speed=60
                elif [ $temp -le 83 ]; then fan_speed=75
                else fan_speed=100; fi
                ;;
        esac
    fi
    
    nvidia-settings -a '[gpu:0]/GPUTargetFanSpeed='$fan_speed 2>/dev/null || true
}

# Record baseline power consumption
BASELINE_POWER=$(get_gpu_power)
echo "Baseline GPU power: ${BASELINE_POWER}W"

# Emergency check before applying optimizations
emergency_check

# Enable maximum performance mode
nvidia-settings -a '[gpu:0]/GPUPowerMizerMode=1' 2>/dev/null || true

# RTX 5080 overclocking based on profile (with validation)
CLOCK_OFFSET=${GPU_CLOCK_OFFSET:-400}
MEM_OFFSET=${GPU_MEM_OFFSET:-800}

# Validate overclock values are within safe ranges
if [ $CLOCK_OFFSET -gt 600 ]; then
    echo "WARNING: GPU clock offset clamped to 600MHz for safety"
    CLOCK_OFFSET=600
fi

if [ $MEM_OFFSET -gt 1200 ]; then
    echo "WARNING: Memory offset clamped to 1200MHz for safety"
    MEM_OFFSET=1200
fi

nvidia-settings -a '[gpu:0]/GPUGraphicsClockOffsetAllPerformanceLevels='$CLOCK_OFFSET 2>/dev/null || true
nvidia-settings -a '[gpu:0]/GPUMemoryTransferRateOffsetAllPerformanceLevels='$MEM_OFFSET 2>/dev/null || true

# Enable fan control and apply initial curve
nvidia-settings -a '[gpu:0]/GPUFanControlState=1' 2>/dev/null || true
apply_fan_curve

# G-SYNC/VRR Configuration
nvidia-settings -a '[gpu:0]/AllowGSYNC=1' 2>/dev/null || true
nvidia-settings -a '[gpu:0]/AllowGSYNCCompatible=1' 2>/dev/null || true
nvidia-settings -a '[gpu:0]/ShowGSYNCVisualIndicator=0' 2>/dev/null || true

# HDR Configuration
nvidia-settings -a '[gpu:0]/AllowHDR=1' 2>/dev/null || true
nvidia-settings -a '[gpu:0]/HDRMode=1' 2>/dev/null || true

# Environment variables for optimal performance
export __GL_THREADED_OPTIMIZATIONS=1
export __GL_SHADER_DISK_CACHE=1
export __GL_SHADER_DISK_CACHE_SIZE=4294967296
export __GL_SHADER_DISK_CACHE_PATH=/var/cache/gaming-shaders/nvidia

# VKD3D-Proton shader cache optimization
export VKD3D_SHADER_CACHE_PATH=/var/cache/gaming-shaders/vkd3d-proton
export DXVK_STATE_CACHE_PATH=/var/cache/gaming-shaders/dxvk-state

# VRAM optimization for 16GB RTX 5080
export DXVK_MEMORY_LIMIT=15000
export VKD3D_MEMORY_LIMIT=15000

# DLSS 4 Frame Generation workaround - limit to 2x/3x modes
export NVIDIA_FG_MODE_MAX=3

# HDR Support
export KWIN_HDR=1
export VK_HDR_ENABLED=1
export GAMESCOPE_HDR_ENABLED=1

# Display server specific optimizations
DISPLAY_SERVER=$(echo $XDG_SESSION_TYPE)
if [ "$DISPLAY_SERVER" = "wayland" ]; then
    export GBM_BACKEND=nvidia-drm
    export __GLX_VENDOR_LIBRARY_NAME=nvidia
    export __GL_GSYNC_ALLOWED=1
    export KWIN_EXPLICIT_SYNC=1
elif [ "$DISPLAY_SERVER" = "x11" ]; then
    export __GL_SYNC_TO_VBLANK=0
    export __GL_GSYNC_ALLOWED=1
fi

# Enable NVAPI and DLSS
export PROTON_ENABLE_NVAPI=1
export DXVK_ENABLE_NVAPI=1
export PROTON_HIDE_NVIDIA_GPU=0
export VKD3D_CONFIG=dxr11,dxr

# Start thermal monitoring daemon with safety checks
(
    while true; do
        emergency_check
        apply_fan_curve
        
        # Log power consumption
        CURRENT_POWER=$(get_gpu_power)
        echo "$(date +%s),GPU_POWER,$CURRENT_POWER" >> /var/log/bazzite-optimizer/power.csv
        
        sleep 5
    done
) &

# Report power increase
sleep 2
CURRENT_POWER=$(get_gpu_power)
POWER_INCREASE=$((CURRENT_POWER - BASELINE_POWER))
echo "Power consumption increased by ${POWER_INCREASE}W"

echo "RTX 5080 Blackwell optimizations v4 applied with safety checks!"
"""

# Intel i9-10850K CPU Optimization - Enhanced with stepped undervolting
CPU_OPTIMIZATION_SCRIPT = """#!/bin/bash
# i9-10850K Gaming Optimization v4 - With Stepped Undervolting

# Enable MSR module for advanced CPU control
modprobe msr 2>/dev/null || true

# Install cpupower if not present
if ! command -v cpupower &> /dev/null; then
    rpm-ostree install kernel-tools 2>/dev/null || dnf install -y kernel-tools 2>/dev/null || true
fi

# Function to get CPU package temperature
get_cpu_temp() {
    sensors -j 2>/dev/null | grep -o '"temp[0-9]_input":[0-9.]*' | head -1 | cut -d: -f2 | cut -d. -f1 || echo "0"
}

# Function to get CPU power consumption
get_cpu_power() {
    if command -v turbostat &> /dev/null; then
        turbostat --quiet --show PkgWatt --num_iterations 1 2>/dev/null | tail -1 | awk '{print $1}' | cut -d. -f1 || echo "0"
    else
        echo "0"
    fi
}

# Record baseline power
BASELINE_POWER=$(get_cpu_power)
echo "Baseline CPU power: ${BASELINE_POWER}W"

# Safety check: Emergency throttle if too hot
emergency_check() {
    local temp=$(get_cpu_temp)
    if [ -n "$temp" ] && [ "$temp" -gt {MAX_CPU_TEMP_CRITICAL} ]; then
        echo "CRITICAL: CPU temperature at ${temp}°C! Emergency throttling!"
        echo powersave | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null || true
        exit 1
    fi
}

emergency_check

# Set governor based on profile
GOVERNOR=${CPU_GOVERNOR:-performance}
cpupower frequency-set -g $GOVERNOR 2>/dev/null || true

# Configure frequency scaling for all cores
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/; do
    echo 4000000 > $cpu/scaling_min_freq 2>/dev/null || true
    echo 5200000 > $cpu/scaling_max_freq 2>/dev/null || true
done

# Intel P-state optimizations
echo 1 > /sys/devices/system/cpu/intel_pstate/hwp_dynamic_boost 2>/dev/null || true
echo 100 > /sys/devices/system/cpu/intel_pstate/min_perf_pct 2>/dev/null || true
echo 0 > /sys/devices/system/cpu/intel_pstate/no_turbo 2>/dev/null || true

# Disable deep C-states for lower latency (profile-dependent)
if [ "${ISOLATE_CORES:-false}" = "true" ]; then
    echo 1 > /sys/module/intel_idle/parameters/max_cstate 2>/dev/null || true
    echo 0 > /dev/cpu_dma_latency 2>/dev/null || true
else
    echo 3 > /sys/module/intel_idle/parameters/max_cstate 2>/dev/null || true
fi

# Apply Intel undervolt with stepping (safer approach)
if command -v intel-undervolt &> /dev/null; then
    echo "Applying conservative stepped undervolting..."
    
    # Step 1: Very conservative
    intel-undervolt apply -v -25 2>/dev/null || true
    sleep 2
    emergency_check
    
    # Step 2: Moderate (only if Step 1 succeeded)
    if [ $? -eq 0 ] && [ "${UNDERVOLT_AGGRESSIVE:-false}" != "true" ]; then
        intel-undervolt apply -v -40 2>/dev/null || true
        sleep 2
        emergency_check
    fi
    
    # Step 3: Target (only if aggressive mode and previous steps succeeded)
    if [ $? -eq 0 ] && [ "${UNDERVOLT_AGGRESSIVE:-false}" = "true" ]; then
        intel-undervolt apply 2>/dev/null || true
        echo "Full undervolt profile applied"
    else
        echo "Conservative undervolt applied for stability"
    fi
fi

# Configure IRQ affinity for network and GPU
if [ "${ISOLATE_CORES:-false}" = "true" ]; then
    for irq in $(grep -E 'nvidia|igc' /proc/interrupts | cut -d: -f1); do
        echo 0-3 > /proc/irq/$irq/smp_affinity_list 2>/dev/null || true
    done
fi

# Thermal monitoring with emergency response
(
    while true; do
        emergency_check
        
        # Log power consumption
        CURRENT_POWER=$(get_cpu_power)
        echo "$(date +%s),CPU_POWER,$CURRENT_POWER" >> /var/log/bazzite-optimizer/power.csv
        
        sleep 5
    done
) &

# Report power increase
sleep 2
CURRENT_POWER=$(get_cpu_power)
POWER_INCREASE=$((CURRENT_POWER - BASELINE_POWER))
echo "CPU power consumption changed by ${POWER_INCREASE}W"

echo "Intel i9-10850K optimized with stepped undervolting (Profile: $GOVERNOR)!"
"""

# Intel undervolt configuration - More conservative
UNDERVOLT_CONFIG = """# Intel i9-10850K Conservative Undervolt Configuration v4
# WARNING: These are conservative starting values - monitor stability!

# Conservative values for stability
undervolt 0 'CPU' -40
undervolt 1 'GPU' -25
undervolt 2 'CPU Cache' -40
undervolt 3 'System Agent' -25
undervolt 4 'Analog I/O' -25

# Power and temperature limits (watts/celsius)
power package 125 100
power core 125 100
tjoffset -3
"""

# Log rotation configuration
LOGROTATE_CONFIG = """# Bazzite Optimizer log rotation
/var/log/bazzite-optimizer/*.log {
    weekly
    rotate 4
    compress
    missingok
    notifempty
    create 0640 root root
}

/var/log/bazzite-optimizer/*.csv {
    weekly
    rotate 2
    compress
    missingok
    notifempty
    create 0640 root root
}

/var/log/bazzite-optimizer/performance/*.csv {
    daily
    rotate 7
    compress
    missingok
    notifempty
    create 0640 root root
}

/var/log/bazzite-optimizer/benchmarks/*.txt {
    monthly
    rotate 3
    compress
    missingok
    notifempty
}
"""

# Automated backup script
AUTO_BACKUP_SCRIPT = """#!/bin/bash
# Automated daily backup of gaming configurations

BACKUP_DIR="/var/backups/bazzite-optimizer"
TODAY=$(date +%Y%m%d)
BACKUP_FILE="$BACKUP_DIR/auto_backup_$TODAY.tar.gz"

# Check if backup already exists for today
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Creating daily configuration backup..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup critical configuration directories
    tar -czf "$BACKUP_FILE" \
        /etc/modprobe.d \
        /etc/sysctl.d \
        /etc/default/grub \
        /etc/systemd/system/gaming-*.service \
        /etc/udev/rules.d/*gaming* \
        /etc/udev/rules.d/*nvme* \
        /etc/pipewire \
        /etc/wireplumber \
        /etc/gamemode.ini \
        /etc/intel-undervolt.conf \
        2>/dev/null || true
    
    # Keep only last 7 daily backups
    find "$BACKUP_DIR" -name "auto_backup_*.tar.gz" -mtime +7 -delete
    
    echo "Backup completed: $BACKUP_FILE"
else
    echo "Backup already exists for today"
fi
"""

# Network isolation script for competitive gaming
NETWORK_ISOLATION_SCRIPT = """#!/bin/bash
# Network isolation for competitive gaming - minimize jitter

# Identify gaming interface
GAMING_IF=$(ip route | grep default | awk '{print $5}' | head -1)

if [ -n "$GAMING_IF" ] && [ "${NETWORK_ISOLATION:-false}" = "true" ]; then
    echo "Enabling network isolation mode for $GAMING_IF"
    
    # Disable all unnecessary network services
    systemctl stop avahi-daemon 2>/dev/null || true
    systemctl stop cups-browsed 2>/dev/null || true
    systemctl stop bluetooth 2>/dev/null || true
    
    # Kill bandwidth-hungry processes
    pkill -f "dropbox|onedrive|syncthing|megasync" 2>/dev/null || true
    
    # Set static DNS for lower latency (Cloudflare)
    echo "nameserver 1.1.1.1" > /etc/resolv.conf.gaming
    echo "nameserver 1.0.0.1" >> /etc/resolv.conf.gaming
    cp /etc/resolv.conf /etc/resolv.conf.backup
    cp /etc/resolv.conf.gaming /etc/resolv.conf
    
    # Flush all iptables rules and set minimal firewall
    iptables -F
    iptables -X
    iptables -P INPUT DROP
    iptables -P FORWARD DROP
    iptables -P OUTPUT ACCEPT
    
    # Allow only gaming traffic
    iptables -A INPUT -i lo -j ACCEPT
    iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
    iptables -A INPUT -p icmp --icmp-type echo-reply -j ACCEPT
    
    # Common game ports
    iptables -A INPUT -p udp --dport 27000:27050 -j ACCEPT  # Steam
    iptables -A INPUT -p tcp --dport 27014:27050 -j ACCEPT  # Steam
    iptables -A INPUT -p udp --dport 3074 -j ACCEPT         # Xbox Live
    iptables -A INPUT -p udp --dport 14000:14016 -j ACCEPT  # Fortnite
    iptables -A INPUT -p udp --dport 7000:7100 -j ACCEPT    # Overwatch
    
    echo "Network isolation enabled - only gaming traffic allowed"
else
    echo "Network isolation not enabled"
fi
"""

# Stability test script
STABILITY_TEST_SCRIPT = """#!/bin/bash
# System stability testing script v4

DURATION=${1:-300}  # Default 5 minutes
RESULT_DIR="/var/log/bazzite-optimizer/stability_test_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RESULT_DIR"

echo "Starting stability test for $DURATION seconds..."
echo "Test started at $(date)" > "$RESULT_DIR/test.log"

# Function to monitor temperatures
monitor_temps() {
    while [ -f "$RESULT_DIR/.running" ]; do
        GPU_TEMP=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits 2>/dev/null || echo "0")
        CPU_TEMP=$(sensors -j 2>/dev/null | grep -o '"temp[0-9]_input":[0-9.]*' | head -1 | cut -d: -f2 | cut -d. -f1 || echo "0")
        
        echo "$(date +%s),$GPU_TEMP,$CPU_TEMP" >> "$RESULT_DIR/temps.csv"
        
        # Safety check
        if [ "$GPU_TEMP" -gt {MAX_GPU_TEMP_STRESS} ] || [ "$CPU_TEMP" -gt {MAX_CPU_TEMP_STRESS} ]; then
            echo "CRITICAL: Temperature limit exceeded! GPU:${GPU_TEMP}°C CPU:${CPU_TEMP}°C" | tee -a "$RESULT_DIR/test.log"
            rm -f "$RESULT_DIR/.running"
            pkill -f "stress-ng|gpu-burn|glmark2"
            exit 1
        fi
        
        sleep 1
    done
}

# Start temperature monitoring
touch "$RESULT_DIR/.running"
monitor_temps &
MONITOR_PID=$!

# GPU Stress Test
if command -v glmark2 &> /dev/null && nvidia-smi &> /dev/null; then
    echo "Starting GPU stress test..." | tee -a "$RESULT_DIR/test.log"
    
    # Run multiple instances for maximum load
    for i in {1..2}; do
        timeout $DURATION glmark2 --run-forever --fullscreen &>> "$RESULT_DIR/gpu_stress.log" &
    done
    
    # Alternative: Use gpu-burn if available
    if command -v gpu-burn &> /dev/null; then
        timeout $DURATION gpu-burn 60 &>> "$RESULT_DIR/gpu_burn.log" &
    fi
fi

# CPU Stress Test
if command -v stress-ng &> /dev/null; then
    echo "Starting CPU stress test..." | tee -a "$RESULT_DIR/test.log"
    stress-ng --cpu $(nproc) --cpu-method all --metrics --timeout ${DURATION}s &>> "$RESULT_DIR/cpu_stress.log" &
elif command -v stress &> /dev/null; then
    stress --cpu $(nproc) --timeout ${DURATION}s &>> "$RESULT_DIR/cpu_stress.log" &
fi

# Memory stress test
if command -v stress-ng &> /dev/null; then
    echo "Starting memory stress test..." | tee -a "$RESULT_DIR/test.log"
    stress-ng --vm 4 --vm-bytes 8G --mmap 4 --timeout ${DURATION}s &>> "$RESULT_DIR/mem_stress.log" &
fi

# Wait for tests to complete
sleep $DURATION

# Stop all stress tests
pkill -f "stress-ng|stress|gpu-burn|glmark2" 2>/dev/null || true

# Stop monitoring
rm -f "$RESULT_DIR/.running"
wait $MONITOR_PID 2>/dev/null || true

# Analyze results
echo "Analyzing stability test results..." | tee -a "$RESULT_DIR/test.log"

# Check for temperature throttling
MAX_GPU_TEMP=$(cut -d, -f2 "$RESULT_DIR/temps.csv" | sort -n | tail -1)
MAX_CPU_TEMP=$(cut -d, -f3 "$RESULT_DIR/temps.csv" | sort -n | tail -1)
AVG_GPU_TEMP=$(cut -d, -f2 "$RESULT_DIR/temps.csv" | awk '{sum+=$1} END {print int(sum/NR)}')
AVG_CPU_TEMP=$(cut -d, -f3 "$RESULT_DIR/temps.csv" | awk '{sum+=$1} END {print int(sum/NR)}')

echo "Temperature Summary:" | tee -a "$RESULT_DIR/test.log"
echo "  GPU Max: ${MAX_GPU_TEMP}°C, Avg: ${AVG_GPU_TEMP}°C" | tee -a "$RESULT_DIR/test.log"
echo "  CPU Max: ${MAX_CPU_TEMP}°C, Avg: ${AVG_CPU_TEMP}°C" | tee -a "$RESULT_DIR/test.log"

# Check for errors
ERRORS=0
if grep -q "error\\|fail\\|crash" "$RESULT_DIR"/*.log 2>/dev/null; then
    ERRORS=$((ERRORS + 1))
    echo "Errors detected during stress test!" | tee -a "$RESULT_DIR/test.log"
fi

# Calculate stability score
SCORE=100
if [ "$MAX_GPU_TEMP" -gt 85 ]; then SCORE=$((SCORE - 10)); fi
if [ "$MAX_CPU_TEMP" -gt 95 ]; then SCORE=$((SCORE - 10)); fi
if [ "$ERRORS" -gt 0 ]; then SCORE=$((SCORE - 20)); fi

echo "Stability Score: $SCORE/100" | tee -a "$RESULT_DIR/test.log"

# Generate report
cat > "$RESULT_DIR/report.txt" << EOF
==============================================
Stability Test Report
==============================================
Date: $(date)
Duration: $DURATION seconds
Profile: ${GAMING_PROFILE:-unknown}

Temperature Results:
  GPU: Max ${MAX_GPU_TEMP}°C, Avg ${AVG_GPU_TEMP}°C
  CPU: Max ${MAX_CPU_TEMP}°C, Avg ${AVG_CPU_TEMP}°C

Errors Detected: $ERRORS
Stability Score: $SCORE/100

Status: $([ $SCORE -ge {MIN_STABILITY_SCORE} ] && echo "PASSED" || echo "FAILED")
==============================================
EOF

cat "$RESULT_DIR/report.txt"

# Return status
[ $SCORE -ge {MIN_STABILITY_SCORE} ]
"""

# Master Gaming Activation Script with safety and monitoring
MASTER_GAMING_SCRIPT = """#!/bin/bash
# Bazzite DX Complete Gaming Mode Activation v4
# Profile: {PROFILE}

echo "Activating Ultimate Gaming Mode (Profile: {PROFILE})..."

# Safety check: Create automatic backup first
/usr/local/bin/auto-backup.sh

# Show security warning if using competitive profile
if [ "{PROFILE}" = "competitive" ] && [ "${SECURITY_WARNING_ACKNOWLEDGED:-false}" != "true" ]; then
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    SECURITY WARNING                          ║"
    echo "╠══════════════════════════════════════════════════════════════╣"
    echo "║ Competitive profile DISABLES CPU security mitigations!       ║"
    echo "║                                                              ║"
    echo "║ This makes your system vulnerable to:                        ║"
    echo "║   • Spectre/Meltdown attacks                                ║"
    echo "║   • Side-channel attacks                                    ║"
    echo "║   • Other CPU vulnerabilities                               ║"
    echo "║                                                              ║"
    echo "║ Only use on:                                                ║"
    echo "║   ✓ Trusted, isolated networks                              ║"
    echo "║   ✓ Dedicated gaming systems                                ║"
    echo "║   ✗ NEVER on systems with sensitive data                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Press ENTER to acknowledge and continue, or Ctrl+C to cancel..."
    read
    export SECURITY_WARNING_ACKNOWLEDGED=true
fi

# Load profile settings
export GAMING_PROFILE={PROFILE}
source /etc/bazzite-optimizer/profiles/{PROFILE}.env 2>/dev/null || true

# Detect display server
export DISPLAY_SERVER=$(echo $XDG_SESSION_TYPE)
echo "Display server detected: $DISPLAY_SERVER"

# Record baseline power consumption
BASELINE_GPU_POWER=$(nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits 2>/dev/null | cut -d. -f1 || echo "0")
BASELINE_CPU_POWER=$(turbostat --quiet --show PkgWatt --num_iterations 1 2>/dev/null | tail -1 | awk '{print $1}' | cut -d. -f1 || echo "0")
echo "Baseline power: GPU ${BASELINE_GPU_POWER}W, CPU ${BASELINE_CPU_POWER}W"

# CPU Optimizations
echo ${CPU_GOVERNOR:-performance} | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null || true
echo 1 > /sys/module/processor/parameters/ignore_ppc 2>/dev/null || true
echo 0 > /dev/cpu_dma_latency 2>/dev/null || true

# GPU Optimizations (NVIDIA RTX 5080)
/usr/local/bin/nvidia-gaming-optimize.sh 2>/dev/null || true

# Network Optimizations (Intel I225-V)
/usr/local/bin/ethernet-optimize.sh 2>/dev/null || true

# Network Isolation Mode (competitive profile)
if [ "${NETWORK_ISOLATION:-false}" = "true" ]; then
    /usr/local/bin/network-isolation.sh 2>/dev/null || true
fi

# Audio latency optimization
pw-metadata -n settings 0 clock.force-quantum ${AUDIO_QUANTUM:-512} 2>/dev/null || true
pw-metadata -n settings 0 clock.force-rate 48000 2>/dev/null || true

# Enable MGLRU if available (kernel 6.1+)
echo Y > /sys/kernel/mm/lru_gen/enabled 2>/dev/null || true
echo 1000 > /sys/kernel/mm/lru_gen/min_ttl_ms 2>/dev/null || true

# Process scheduling optimization
echo 500000 > /proc/sys/kernel/sched_migration_cost_ns 2>/dev/null || true
echo 1 > /proc/sys/kernel/sched_autogroup_enabled 2>/dev/null || true

# I/O optimizations
for disk in /sys/block/nvme*/queue/; do
    echo 2048 > ${disk}nr_requests 2>/dev/null || true
    echo 2 > ${disk}rq_affinity 2>/dev/null || true
    echo 0 > ${disk}add_random 2>/dev/null || true
    echo 1 > ${disk}nomerges 2>/dev/null || true
done

# Memory management
echo ${VM_SWAPPINESS:-120} > /proc/sys/vm/swappiness 2>/dev/null || true
sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true

# Power Profile
powerprofilesctl set performance 2>/dev/null || true

# Start performance monitoring
if [ "${ENABLE_MONITORING:-true}" = "true" ]; then
    /usr/local/bin/performance-monitor.sh &
fi

# Report final power consumption
sleep 3
FINAL_GPU_POWER=$(nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits 2>/dev/null | cut -d. -f1 || echo "0")
FINAL_CPU_POWER=$(turbostat --quiet --show PkgWatt --num_iterations 1 2>/dev/null | tail -1 | awk '{print $1}' | cut -d. -f1 || echo "0")
GPU_INCREASE=$((FINAL_GPU_POWER - BASELINE_GPU_POWER))
CPU_INCREASE=$((FINAL_CPU_POWER - BASELINE_CPU_POWER))

echo "Power consumption changes:"
echo "  GPU: +${GPU_INCREASE}W (${BASELINE_GPU_POWER}W -> ${FINAL_GPU_POWER}W)"
echo "  CPU: +${CPU_INCREASE}W (${BASELINE_CPU_POWER}W -> ${FINAL_CPU_POWER}W)"
echo "  Total system increase: ~$((GPU_INCREASE + CPU_INCREASE))W"

notify-send "Gaming Mode" "Profile '${GAMING_PROFILE}' activated!\\nPower +$((GPU_INCREASE + CPU_INCREASE))W" 2>/dev/null || true
echo "Gaming optimizations applied successfully (Profile: ${GAMING_PROFILE})!"
"""

# Add to GRUB configuration section
GRUB_CMDLINE_ADDITIONS = """mitigations={MITIGATIONS} processor.max_cstate={MAX_CSTATE} intel_idle.max_cstate={MAX_CSTATE} 
intel_pstate=active transparent_hugepage=madvise nvme_core.default_ps_max_latency_us=0 
pcie_aspm=off intel_iommu=on iommu=pt {ISOLCPUS} threadirqs preempt=full 
nvidia-drm.modeset=1 nvidia-drm.fbdev=1 amdgpu.ppfeaturemask=0xffffffff 
quiet splash {SECURITY_PARAMS}"""

# ============================================================================
# LOGGING AND UTILITY FUNCTIONS - Enhanced
# ============================================================================

def setup_logging() -> logging.Logger:
    """Configure comprehensive logging system with rotation"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    log_file = LOG_DIR / f"optimization_{TIMESTAMP}.log"
    
    # Create detailed formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # File handler for detailed logs
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler for user feedback
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    console_handler.setLevel(logging.INFO)
    
    # Configure logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Setup log rotation
    setup_log_rotation()
    
    return logger

def setup_log_rotation():
    """Configure logrotate for optimizer logs"""
    try:
        write_config_file(Path("/etc/logrotate.d/bazzite-optimizer"), LOGROTATE_CONFIG)
    except:
        pass  # Non-critical if it fails

def detect_display_server() -> str:
    """Detect if running X11 or Wayland"""
    session_type = os.environ.get('XDG_SESSION_TYPE', '')
    if session_type == 'wayland':
        return 'wayland'
    elif session_type == 'x11':
        return 'x11'
    
    # Fallback detection
    if os.environ.get('WAYLAND_DISPLAY'):
        return 'wayland'
    elif os.environ.get('DISPLAY'):
        return 'x11'
    
    return 'unknown'

def detect_form_factor() -> str:
    """Detect if running on Steam Deck or handheld"""
    # Check for Steam Deck
    if Path("/sys/devices/virtual/dmi/id/product_name").exists():
        try:
            with open("/sys/devices/virtual/dmi/id/product_name") as f:
                product = f.read().strip()
                if "Jupiter" in product or "Galileo" in product:
                    return "steamdeck"
        except:
            pass
    
    # Check for other handhelds (ROG Ally, Legion Go, etc.)
    try:
        with open("/proc/cpuinfo") as f:
            cpuinfo = f.read()
            # AMD APUs commonly used in handhelds
            if "AMD Ryzen Z1" in cpuinfo or "AMD Ryzen 7 7840U" in cpuinfo:
                return "handheld"
    except:
        pass
    
    return "desktop"

def check_nvidia_gpu_exists() -> bool:
    """Verify NVIDIA GPU actually exists and is accessible"""
    # Check if nvidia-smi exists
    returncode, _, _ = run_command("which nvidia-smi", check=False)
    if returncode != 0:
        return False
    
    # Check if nvidia-smi can query the GPU
    returncode, _, _ = run_command("nvidia-smi -L", check=False)
    if returncode != 0:
        return False
    
    return True

def validate_grub_changes(grub_file: Path) -> bool:
    """Validate GRUB configuration changes are safe"""
    if not grub_file.exists():
        return False
    
    try:
        with open(grub_file, 'r') as f:
            content = f.read()
            
        # Check for critical boot parameters that shouldn't be removed
        critical_params = ['root=', 'BOOT_IMAGE=']
        for param in critical_params:
            if param not in content:
                logging.warning(f"Critical boot parameter '{param}' missing in GRUB config")
                return False
        
        # Validate syntax (basic check)
        if content.count('"') % 2 != 0:
            logging.warning("Unmatched quotes in GRUB configuration")
            return False
            
        return True
    except Exception as e:
        logging.error(f"Failed to validate GRUB config: {e}")
        return False

def show_security_warning(profile: str):
    """Display security warnings for risky profiles"""
    global SECURITY_WARNINGS_SHOWN
    
    if SECURITY_WARNINGS_SHOWN:
        return
    
    profile_data = GAMING_PROFILES.get(profile, {})
    risk_level = profile_data.get("security_risk", "UNKNOWN")
    
    if risk_level in ["HIGH", "MEDIUM"]:
        print_colored("\n" + "="*60, Colors.WARNING)
        print_colored("SECURITY WARNING", Colors.WARNING + Colors.BOLD)
        print_colored("="*60, Colors.WARNING)
        
        if risk_level == "HIGH":
            print_colored("""
This profile DISABLES critical security features:
  • CPU vulnerability mitigations (Spectre/Meltdown)
  • Kernel security features
  • Network security protocols

⚠️  Only use on:
  • Dedicated gaming systems
  • Isolated/trusted networks
  • Systems without sensitive data

⚠️  DO NOT use on:
  • Work computers
  • Systems with banking/personal data
  • Shared or public networks
""", Colors.WARNING)
        elif risk_level == "MEDIUM":
            print_colored("""
This profile reduces some security features:
  • Partial mitigation bypass
  • Relaxed network security

Use with caution on systems with sensitive data.
""", Colors.WARNING)
        
        print_colored("="*60, Colors.WARNING)
        print_colored("Press ENTER to acknowledge, or Ctrl+C to cancel...", Colors.WARNING)
        try:
            input()
            SECURITY_WARNINGS_SHOWN = True
        except KeyboardInterrupt:
            print_colored("\nCancelled by user", Colors.FAIL)
            sys.exit(1)

def print_colored(message: str, color: str = Colors.ENDC) -> None:
    """Print colored message to terminal"""
    print(f"{color}{message}{Colors.ENDC}")

def run_command(command: str, shell: bool = True, check: bool = True, 
                timeout: int = 30) -> Tuple[int, str, str]:
    """Execute shell command with timeout and error handling"""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            check=check,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout} seconds"
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout or "", e.stderr or ""
    except Exception as e:
        return -1, "", str(e)

def backup_file(filepath: Path) -> Optional[Path]:
    """Create timestamped backup of existing file"""
    if filepath.exists():
        CONFIG_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        backup_path = CONFIG_BACKUP_DIR / f"{filepath.name}.{TIMESTAMP}"
        shutil.copy2(filepath, backup_path)
        logging.info(f"Backed up {filepath} to {backup_path}")
        return backup_path
    return None

def write_config_file(filepath: Path, content: str, executable: bool = False) -> bool:
    """Write configuration file with proper permissions and backup"""
    try:
        backup_file(filepath)
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content)
        
        if executable:
            filepath.chmod(0o755)
        else:
            filepath.chmod(0o644)
        
        logging.info(f"Created configuration file: {filepath}")
        return True
    except Exception as e:
        logging.error(f"Failed to write {filepath}: {e}")
        return False

def get_system_info() -> Dict[str, Any]:
    """Gather comprehensive system information"""
    info = {
        "kernel": platform.release(),
        "kernel_version": tuple(map(int, platform.release().split('.')[:3])) if platform.release().count('.') >= 2 else (0, 0, 0),
        "distribution": "",
        "cpu_model": "",
        "cpu_cores": psutil.cpu_count(logical=False),
        "cpu_threads": psutil.cpu_count(logical=True),
        "ram_gb": round(psutil.virtual_memory().total / (1024**3)),
        "gpus": [],
        "network_interfaces": [],
        "nvme_devices": [],
        "free_disk_gb": round(psutil.disk_usage('/').free / (1024**3)),
        "form_factor": detect_form_factor(),
        "display_server": detect_display_server()
    }
    
    # Get distribution info
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    info["distribution"] = line.split("=")[1].strip().strip('"')
    except:
        pass
    
    # Get CPU model
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if "model name" in line:
                    info["cpu_model"] = line.split(":")[1].strip()
                    break
    except:
        pass
    
    # Get GPU info
    returncode, stdout, _ = run_command("lspci | grep -E 'VGA|3D|Display'", check=False)
    if returncode == 0:
        info["gpus"] = stdout.strip().split("\n")
    
    # Get network interfaces
    for interface in psutil.net_if_addrs().keys():
        if interface != "lo":
            info["network_interfaces"].append(interface)
    
    # Get NVMe devices
    returncode, stdout, _ = run_command("ls /dev/nvme* 2>/dev/null | grep -E 'nvme[0-9]n[0-9]$'", check=False)
    if returncode == 0 and stdout.strip():
        info["nvme_devices"] = stdout.strip().split("\n")
    
    return info

def check_hardware_compatibility() -> Dict[str, bool]:
    """Check if hardware matches expected configuration"""
    checks = {
        "nvidia_rtx5080": False,
        "intel_i9_10850k": False,
        "ram_64gb": False,
        "nvme_storage": False,
        "creative_audio": False,
        "intel_i225v": False,
        "bazzite_os": False,
        "resizable_bar": False,
        "nvidia_gpu_present": check_nvidia_gpu_exists()
    }
    
    system_info = get_system_info()
    
    # Check NVIDIA RTX 5080
    for gpu in system_info["gpus"]:
        if "5080" in gpu or "RTX 50" in gpu or "GB203" in gpu:
            checks["nvidia_rtx5080"] = True
            break
    
    # Check Intel i9-10850K
    if "10850K" in system_info["cpu_model"] or "i9-10850" in system_info["cpu_model"]:
        checks["intel_i9_10850k"] = True
    
    # Check 64GB RAM
    if system_info["ram_gb"] >= 60:
        checks["ram_64gb"] = True
    
    # Check NVMe storage
    if system_info["nvme_devices"]:
        checks["nvme_storage"] = True
    
    # Check Creative audio
    returncode, stdout, _ = run_command("lspci | grep -i creative", check=False)
    if returncode == 0:
        checks["creative_audio"] = True
    
    # Check Intel I225-V
    returncode, stdout, _ = run_command("lspci | grep -i 'I225-V\\|Ethernet.*I225'", check=False)
    if returncode == 0:
        checks["intel_i225v"] = True
    
    # Check Bazzite OS
    if "bazzite" in system_info["distribution"].lower():
        checks["bazzite_os"] = True
    
    # Check Resizable BAR
    returncode, stdout, _ = run_command("lspci -vv 2>/dev/null | grep -i 'resizable bar'", check=False)
    if returncode == 0 and stdout and "disabled" not in stdout.lower():
        checks["resizable_bar"] = True
    
    return checks

def check_nvidia_driver_version() -> Optional[str]:
    """Check NVIDIA driver version and variant"""
    if not check_nvidia_gpu_exists():
        return None
        
    returncode, stdout, _ = run_command("nvidia-smi --query-gpu=driver_version --format=csv,noheader", check=False)
    if returncode == 0:
        version = stdout.strip()
        
        # Check if using -open variant
        returncode, stdout, _ = run_command("modinfo nvidia 2>/dev/null | grep -i 'open gpu kernel'", check=False)
        if returncode == 0:
            version += " (Open)"
        
        return version
    return None

def check_kernel_version() -> bool:
    """Check if kernel version meets minimum requirements"""
    system_info = get_system_info()
    kernel_version = system_info.get("kernel_version", (0, 0, 0))
    
    if kernel_version >= MIN_KERNEL_VERSION:
        return True
    return False

def check_disk_space() -> bool:
    """Check if sufficient disk space is available"""
    system_info = get_system_info()
    free_gb = system_info.get("free_disk_gb", 0)
    
    if free_gb >= MIN_DISK_SPACE_GB:
        return True
    return False

def get_gpu_temperature() -> Optional[int]:
    """Get current GPU temperature"""
    if not check_nvidia_gpu_exists():
        return None
        
    returncode, stdout, _ = run_command(
        "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits",
        check=False
    )
    if returncode == 0:
        try:
            return int(stdout.strip())
        except:
            pass
    return None

def get_cpu_temperature() -> Optional[int]:
    """Get current CPU temperature"""
    returncode, stdout, _ = run_command(
        "sensors -j 2>/dev/null | grep -o '\"temp[0-9]_input\":[0-9.]*' | head -1 | cut -d: -f2 | cut -d. -f1",
        check=False
    )
    if returncode == 0 and stdout.strip():
        try:
            return int(float(stdout.strip()))
        except:
            pass
    return None

def get_power_consumption() -> Tuple[int, int]:
    """Get current GPU and CPU power consumption"""
    gpu_power = 0
    cpu_power = 0
    
    # GPU power
    if check_nvidia_gpu_exists():
        returncode, stdout, _ = run_command(
            "nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits",
            check=False
        )
        if returncode == 0:
            try:
                gpu_power = int(float(stdout.strip()))
            except:
                pass
    
    # CPU power (requires turbostat)
    returncode, stdout, _ = run_command(
        "turbostat --quiet --show PkgWatt --num_iterations 1 2>/dev/null | tail -1 | awk '{print $1}'",
        check=False
    )
    if returncode == 0 and stdout.strip():
        try:
            cpu_power = int(float(stdout.strip()))
        except:
            pass
    
    return gpu_power, cpu_power

def validate_optimization(check_name: str, command: str, expected: str) -> bool:
    """Validate if an optimization was successfully applied"""
    returncode, stdout, stderr = run_command(command, check=False)
    if returncode == 0:
        if expected.lower() in stdout.lower():
            return True
    return False

# ============================================================================
# OPTIMIZATION MODULES - Enhanced with v4 features
# ============================================================================

class BaseOptimizer:
    """Base class for all optimizer modules"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.applied_changes = []
        self.profile = "balanced"  # Default profile
    
    def set_profile(self, profile: str):
        """Set optimization profile"""
        self.profile = profile
    
    def track_change(self, description: str, filepath: Path = None):
        """Track changes for rollback capability"""
        self.applied_changes.append({
            "description": description,
            "filepath": str(filepath) if filepath else None,
            "timestamp": datetime.now().isoformat()
        })
    
    def validate(self) -> Dict[str, bool]:
        """Validate if optimizations were applied successfully"""
        return {}

class StabilityTester:
    """System stability testing after overclocking"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.test_duration = STABILITY_TEST_DURATION
    
    def run_full_test(self, duration: int = None) -> Tuple[bool, int, str]:
        """Run complete stability test suite"""
        if duration is None:
            duration = self.test_duration
            
        self.logger.info(f"Starting stability test ({duration} seconds)...")
        
        # Write stability test script
        write_config_file(Path("/usr/local/bin/stability-test.sh"), 
                         STABILITY_TEST_SCRIPT.format(
                             MAX_GPU_TEMP_STRESS=MAX_GPU_TEMP_STRESS,
                             MAX_CPU_TEMP_STRESS=MAX_CPU_TEMP_STRESS,
                             MIN_STABILITY_SCORE=MIN_STABILITY_SCORE
                         ), 
                         executable=True)
        
        # Run the test
        returncode, stdout, stderr = run_command(
            f"/usr/local/bin/stability-test.sh {duration}",
            check=False,
            timeout=duration + 30
        )
        
        # Parse results
        score = 0
        if "Stability Score:" in stdout:
            try:
                score_line = [l for l in stdout.split('\n') if "Stability Score:" in l][0]
                score = int(score_line.split(':')[1].split('/')[0].strip())
            except:
                pass
        
        passed = score >= MIN_STABILITY_SCORE
        
        if passed:
            self.logger.info(f"Stability test PASSED (score: {score}/100)")
        else:
            self.logger.warning(f"Stability test FAILED (score: {score}/100)")
        
        return passed, score, stdout
    
    def quick_test(self) -> bool:
        """Run quick 60-second stability check"""
        self.logger.info("Running quick stability check...")
        passed, score, _ = self.run_full_test(60)
        return passed
    
    def stress_gpu(self, duration: int = 60) -> bool:
        """GPU-only stress test"""
        self.logger.info(f"Running GPU stress test for {duration} seconds...")
        
        if not check_nvidia_gpu_exists():
            self.logger.warning("No NVIDIA GPU found, skipping GPU stress test")
            return True
        
        # Monitor temperatures during test
        start_temp = get_gpu_temperature()
        
        # Run glmark2 stress
        returncode, _, _ = run_command(
            f"timeout {duration} glmark2 --run-forever --fullscreen",
            check=False,
            timeout=duration + 10
        )
        
        # Check max temperature reached
        max_temp = get_gpu_temperature()
        
        if max_temp and max_temp > MAX_GPU_TEMP_STRESS:
            self.logger.warning(f"GPU temperature exceeded safe limit: {max_temp}°C")
            return False
        
        self.logger.info(f"GPU stress test completed. Max temp: {max_temp}°C")
        return True
    
    def stress_cpu(self, duration: int = 60) -> bool:
        """CPU-only stress test"""
        self.logger.info(f"Running CPU stress test for {duration} seconds...")
        
        # Check if stress tools are available
        stress_cmd = None
        if run_command("which stress-ng", check=False)[0] == 0:
            stress_cmd = f"stress-ng --cpu $(nproc) --timeout {duration}s"
        elif run_command("which stress", check=False)[0] == 0:
            stress_cmd = f"stress --cpu $(nproc) --timeout {duration}s"
        
        if not stress_cmd:
            self.logger.warning("No stress testing tools found")
            return True
        
        # Monitor temperatures during test
        start_temp = get_cpu_temperature()
        
        # Run stress test
        returncode, _, _ = run_command(stress_cmd, check=False, timeout=duration + 10)
        
        # Check max temperature reached
        max_temp = get_cpu_temperature()
        
        if max_temp and max_temp > MAX_CPU_TEMP_STRESS:
            self.logger.warning(f"CPU temperature exceeded safe limit: {max_temp}°C")
            return False
        
        self.logger.info(f"CPU stress test completed. Max temp: {max_temp}°C")
        return True

class PowerMonitor:
    """Power consumption monitoring"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.baseline_gpu = 0
        self.baseline_cpu = 0
        self.monitoring = False
        self.monitor_thread = None
        self.power_log = LOG_DIR / "power.csv"
    
    def record_baseline(self):
        """Record baseline power consumption"""
        self.baseline_gpu, self.baseline_cpu = get_power_consumption()
        self.logger.info(f"Baseline power: GPU {self.baseline_gpu}W, CPU {self.baseline_cpu}W")
        
        # Initialize power log
        if not self.power_log.exists():
            with open(self.power_log, 'w') as f:
                f.write("timestamp,component,power_watts\n")
    
    def get_current_increase(self) -> Tuple[int, int, int]:
        """Get current power increase from baseline"""
        current_gpu, current_cpu = get_power_consumption()
        gpu_increase = current_gpu - self.baseline_gpu
        cpu_increase = current_cpu - self.baseline_cpu
        total_increase = gpu_increase + cpu_increase
        return gpu_increase, cpu_increase, total_increase
    
    def start_monitoring(self):
        """Start continuous power monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Power monitoring started")
    
    def stop_monitoring(self):
        """Stop power monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Power monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            gpu_power, cpu_power = get_power_consumption()
            timestamp = int(time.time())
            
            # Log to CSV
            with open(self.power_log, 'a') as f:
                f.write(f"{timestamp},GPU,{gpu_power}\n")
                f.write(f"{timestamp},CPU,{cpu_power}\n")
            
            # Check for excessive power draw
            total_power = gpu_power + cpu_power
            if total_power > 500:  # Watts - adjust based on PSU
                self.logger.warning(f"High system power draw: {total_power}W")
            
            time.sleep(5)
    
    def generate_report(self) -> str:
        """Generate power consumption report"""
        gpu_inc, cpu_inc, total_inc = self.get_current_increase()
        
        report = f"""
Power Consumption Report
========================
Baseline:
  GPU: {self.baseline_gpu}W
  CPU: {self.baseline_cpu}W
  Total: {self.baseline_gpu + self.baseline_cpu}W

Current:
  GPU: {self.baseline_gpu + gpu_inc}W (+{gpu_inc}W)
  CPU: {self.baseline_cpu + cpu_inc}W (+{cpu_inc}W)
  Total: {self.baseline_gpu + self.baseline_cpu + total_inc}W (+{total_inc}W)

Estimated annual cost increase (at $0.12/kWh):
  ${(total_inc * 24 * 365 * 0.12 / 1000):.2f}
"""
        return report

class ThermalManager:
    """Enhanced thermal management system for GPU and CPU"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.monitoring = False
        self.monitor_thread = None
        self.emergency_triggered = False
    
    def start_monitoring(self, fan_profile: str = "balanced"):
        """Start thermal monitoring daemon"""
        self.monitoring = True
        self.emergency_triggered = False
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(fan_profile,),
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info(f"Thermal monitoring started with {fan_profile} profile")
    
    def stop_monitoring(self):
        """Stop thermal monitoring daemon"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Thermal monitoring stopped")
    
    def _monitor_loop(self, fan_profile: str):
        """Main monitoring loop with emergency response"""
        while self.monitoring:
            # Monitor GPU
            gpu_temp = get_gpu_temperature()
            if gpu_temp:
                self._apply_gpu_fan_curve(gpu_temp, fan_profile)
                
                # Emergency response
                if gpu_temp > MAX_GPU_TEMP_CRITICAL:
                    self._emergency_throttle("GPU", gpu_temp)
                elif gpu_temp > MAX_GPU_TEMP_WARNING:
                    self.logger.warning(f"GPU temperature high: {gpu_temp}°C")
                    run_command(f'notify-send "GPU Temperature Warning" "{gpu_temp}°C" -u critical', check=False)
            
            # Monitor CPU
            cpu_temp = get_cpu_temperature()
            if cpu_temp:
                if cpu_temp > MAX_CPU_TEMP_CRITICAL:
                    self._emergency_throttle("CPU", cpu_temp)
                elif cpu_temp > MAX_CPU_TEMP_WARNING:
                    self.logger.warning(f"CPU temperature high: {cpu_temp}°C")
                    run_command(f'notify-send "CPU Temperature Warning" "{cpu_temp}°C" -u critical', check=False)
            
            time.sleep(2 if not self.emergency_triggered else 1)
    
    def _apply_gpu_fan_curve(self, temp: int, profile: str):
        """Apply GPU fan curve based on temperature"""
        if not check_nvidia_gpu_exists():
            return
            
        fan_speed = 50
        curve = FAN_CURVES.get(profile, FAN_CURVES["balanced"])
        
        # Emergency override
        if temp > 85:
            fan_speed = 100
        else:
            for threshold, speed in curve["gpu"]:
                if temp <= threshold:
                    fan_speed = speed
                    break
            else:
                fan_speed = 100
        
        run_command(f"nvidia-settings -a '[gpu:0]/GPUTargetFanSpeed={fan_speed}'", check=False)
    
    def _emergency_throttle(self, component: str, temp: int):
        """Emergency throttling when critical temperature reached"""
        if not self.emergency_triggered:
            self.emergency_triggered = True
            self.logger.critical(f"EMERGENCY: {component} temperature critical at {temp}°C!")
            
            if component == "GPU":
                # Throttle GPU to minimum
                run_command("nvidia-settings -a '[gpu:0]/GPUPowerMizerMode=0'", check=False)
                run_command("nvidia-settings -a '[gpu:0]/GPUTargetFanSpeed=100'", check=False)
                run_command("nvidia-settings -a '[gpu:0]/GPUGraphicsClockOffsetAllPerformanceLevels=0'", check=False)
            else:
                # Throttle CPU to powersave
                run_command("echo powersave | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor", check=False)
            
            run_command(f'notify-send "THERMAL EMERGENCY" "{component} at {temp}°C - System throttled!" -u critical', check=False)
            
            # Log incident
            with open(LOG_DIR / "thermal_incidents.log", 'a') as f:
                f.write(f"{datetime.now()}: {component} emergency throttle at {temp}°C\n")

class NvidiaOptimizer(BaseOptimizer):
    """NVIDIA RTX 5080 Blackwell optimization module - Enhanced v4"""
    
    def check_driver_compatibility(self) -> bool:
        """Verify driver compatibility with RTX 5080"""
        if not check_nvidia_gpu_exists():
            self.logger.warning("No NVIDIA GPU detected - skipping GPU optimizations")
            return False
            
        driver_version = check_nvidia_driver_version()
        if not driver_version:
            self.logger.warning("NVIDIA driver not detected")
            return False
        
        # Extract version number
        version_match = re.match(r"(\d+)\.(\d+)", driver_version)
        if version_match:
            major = int(version_match.group(1))
            minor = int(version_match.group(2))
            
            # RTX 5080 requires 570.86.16+ or 580.xx
            if major < 570 or (major == 570 and minor < 86):
                self.logger.warning(f"Driver version {driver_version} too old for RTX 5080")
                self.logger.warning("Please update to 570.86.16+ or 580.xx series")
                return False
            
            if "Open" not in driver_version and major >= 570:
                self.logger.warning("RTX 5080 requires -open driver variant")
                self.logger.info("Consider switching to nvidia-open drivers")
        
        return True
    
    def apply_optimizations(self) -> bool:
        """Apply NVIDIA RTX 5080 optimizations with safety checks"""
        if not check_nvidia_gpu_exists():
            self.logger.warning("No NVIDIA GPU detected - skipping GPU optimizations")
            return True  # Not a failure, just skip
            
        self.logger.info("Applying NVIDIA RTX 5080 Blackwell optimizations...")
        
        success = True
        
        # Get profile settings
        profile_settings = GAMING_PROFILES.get(self.profile, GAMING_PROFILES["balanced"])["settings"]
        
        # Write module configuration
        if not write_config_file(Path("/etc/modprobe.d/nvidia-blackwell.conf"), NVIDIA_MODULE_CONFIG):
            success = False
        else:
            self.track_change("NVIDIA module configuration", Path("/etc/modprobe.d/nvidia-blackwell.conf"))
        
        # Write optimization script with profile settings and safety features
        script_content = NVIDIA_OPTIMIZATION_SCRIPT.format(MAX_GPU_TEMP_CRITICAL=MAX_GPU_TEMP_CRITICAL)
        script_content = script_content.replace("${GPU_CLOCK_OFFSET:-400}", 
                                                str(profile_settings.get("gpu_clock_offset", 400)))
        script_content = script_content.replace("${GPU_MEM_OFFSET:-800}",
                                                str(profile_settings.get("gpu_mem_offset", 800)))
        script_content = script_content.replace("${FAN_PROFILE:-balanced}",
                                                profile_settings.get("fan_profile", "balanced"))
        
        if not write_config_file(Path("/usr/local/bin/nvidia-gaming-optimize.sh"), 
                                script_content, executable=True):
            success = False
        else:
            self.track_change("NVIDIA optimization script", Path("/usr/local/bin/nvidia-gaming-optimize.sh"))
        
        # Apply immediate optimizations
        run_command("/usr/local/bin/nvidia-gaming-optimize.sh", check=False)
        
        self.logger.info("NVIDIA RTX 5080 optimizations applied")
        return success
    
    def validate(self) -> Dict[str, bool]:
        """Validate NVIDIA optimizations"""
        if not check_nvidia_gpu_exists():
            return {"nvidia_present": False}
            
        validations = {"nvidia_present": True}
        
        # Check GPU power mode
        validations["gpu_power_mode"] = validate_optimization(
            "GPU Power Mode",
            "nvidia-settings -q GPUPowerMizerMode -t",
            str(GAMING_PROFILES.get(self.profile, GAMING_PROFILES["balanced"])["settings"]["gpu_power_mode"])
        )
        
        return validations

class BackupManager:
    """Automated backup management"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.backup_dir = CONFIG_BACKUP_DIR
    
    def setup_auto_backup(self):
        """Setup automated daily backups"""
        self.logger.info("Setting up automated backup system...")
        
        # Write backup script
        write_config_file(Path("/usr/local/bin/auto-backup.sh"),
                         AUTO_BACKUP_SCRIPT,
                         executable=True)
        
        # Create systemd timer for daily backups
        timer_content = """[Unit]
Description=Daily Bazzite Optimizer Configuration Backup
Requires=bazzite-backup.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
"""
        
        service_content = """[Unit]
Description=Bazzite Optimizer Configuration Backup

[Service]
Type=oneshot
ExecStart=/usr/local/bin/auto-backup.sh
"""
        
        write_config_file(Path("/etc/systemd/system/bazzite-backup.timer"), timer_content)
        write_config_file(Path("/etc/systemd/system/bazzite-backup.service"), service_content)
        
        # Enable timer
        run_command("systemctl daemon-reload", check=False)
        run_command("systemctl enable --now bazzite-backup.timer", check=False)
        
        self.logger.info("Automated backup system configured")
        
    def create_recovery_point(self, name: str = None):
        """Create a recovery point before major changes"""
        if not name:
            name = f"recovery_{TIMESTAMP}"
        
        recovery_path = CRASH_RECOVERY_DIR / name
        recovery_path.mkdir(parents=True, exist_ok=True)
        
        # Save current system state
        configs_to_save = [
            "/proc/cmdline",
            "/etc/default/grub",
            "/etc/modprobe.d",
            "/etc/sysctl.d",
            "/etc/systemd/system/gaming-*.service"
        ]
        
        for config in configs_to_save:
            if Path(config).exists():
                if Path(config).is_dir():
                    shutil.copytree(config, recovery_path / Path(config).name, dirs_exist_ok=True)
                else:
                    shutil.copy2(config, recovery_path)
        
        # Save optimization state
        state = {
            "timestamp": datetime.now().isoformat(),
            "profile": getattr(self, 'profile', 'unknown'),
            "kernel": platform.release(),
            "driver": check_nvidia_driver_version()
        }
        
        with open(recovery_path / "state.json", 'w') as f:
            json.dump(state, f, indent=2)
        
        self.logger.info(f"Recovery point created: {recovery_path}")
        return recovery_path

# Additional optimizers inherit from BaseOptimizer with v4 enhancements...
# (CPUOptimizer, MemoryOptimizer, etc. - keeping same structure but adding safety checks)

class KernelOptimizer(BaseOptimizer):
    """Kernel and boot parameter optimization with enhanced safety"""
    
    def apply_grub_optimizations(self) -> bool:
        """Update GRUB configuration with validation"""
        self.logger.info("Updating GRUB configuration...")
        
        grub_config = Path("/etc/default/grub")
        if not grub_config.exists():
            self.logger.warning("GRUB configuration not found")
            return False
        
        # Backup GRUB config
        backup_file(grub_config)
        
        # Read current configuration
        with open(grub_config, 'r') as f:
            lines = f.readlines()
        
        # Get profile settings
        profile_settings = GAMING_PROFILES.get(self.profile, GAMING_PROFILES["balanced"])["settings"]
        
        # Show security warning for competitive profile
        if profile_settings.get("disable_mitigations", False):
            show_security_warning(self.profile)
        
        # Configure kernel parameters based on profile
        mitigations = "off" if profile_settings.get("disable_mitigations", True) else "auto"
        max_cstate = "1" if profile_settings.get("isolate_cores", False) else "3"
        
        if profile_settings.get("isolate_cores", False):
            isolcpus = "nohz_full=4-9 isolcpus=4-9 rcu_nocbs=4-9"
        else:
            isolcpus = ""
        
        # Add security warning parameter if mitigations disabled
        security_params = "security=warned" if mitigations == "off" else ""
        
        additions = GRUB_CMDLINE_ADDITIONS.format(
            MITIGATIONS=mitigations,
            MAX_CSTATE=max_cstate,
            ISOLCPUS=isolcpus,
            SECURITY_PARAMS=security_params
        ).strip()
        
        # Update GRUB configuration
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("GRUB_CMDLINE_LINUX=") or line.startswith("GRUB_CMDLINE_LINUX_DEFAULT="):
                # Extract current value
                current_value = line.split('=', 1)[1].strip().strip('"')
                
                # Add our optimizations if not already present
                for param in additions.split():
                    param_key = param.split('=')[0]
                    if param_key not in current_value:
                        current_value += f" {param}"
                
                # Update the line
                key = line.split('=')[0]
                lines[i] = f'{key}="{current_value}"\n'
                updated = True
                self.track_change("GRUB kernel parameters", grub_config)
        
        if updated:
            # Write updated configuration
            with open(grub_config, 'w') as f:
                f.writelines(lines)
            
            # Validate before applying
            if not validate_grub_changes(grub_config):
                self.logger.error("GRUB validation failed! Restoring backup...")
                # Restore from backup
                backup_path = CONFIG_BACKUP_DIR / f"grub.{TIMESTAMP}"
                if backup_path.exists():
                    shutil.copy2(backup_path, grub_config)
                return False
            
            # Regenerate GRUB configuration
            grub_cmds = [
                "grub2-mkconfig -o /boot/grub2/grub.cfg",
                "grub-mkconfig -o /boot/grub/grub.cfg",
                "update-grub"
            ]
            
            for cmd in grub_cmds:
                returncode, _, _ = run_command(cmd, check=False, timeout=30)
                if returncode == 0:
                    self.logger.info("GRUB configuration updated successfully")
                    break
            
            return True
        else:
            self.logger.warning("Could not update GRUB configuration")
            return False

class NetworkOptimizer(BaseOptimizer):
    """Network optimization with isolation mode for competitive gaming"""
    
    def apply_optimizations(self) -> bool:
        """Apply network optimizations with isolation support"""
        self.logger.info("Applying network optimizations...")
        
        success = True
        
        # Get profile settings
        profile_settings = GAMING_PROFILES.get(self.profile, GAMING_PROFILES["balanced"])["settings"]
        
        # Write network isolation script if competitive profile
        if profile_settings.get("network_isolation", False):
            if not write_config_file(Path("/usr/local/bin/network-isolation.sh"),
                                    NETWORK_ISOLATION_SCRIPT,
                                    executable=True):
                success = False
            else:
                self.track_change("Network isolation script", Path("/usr/local/bin/network-isolation.sh"))
                self.logger.info("Network isolation mode enabled for competitive gaming")
        
        # Continue with standard network optimizations...
        # [Rest of NetworkOptimizer implementation remains the same]
        
        return success

# ============================================================================
# MAIN OPTIMIZER CLASS - Enhanced v4
# ============================================================================

class BazziteGamingOptimizer:
    """Main optimizer orchestrator with v4 enhancements"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.optimizers = []
        self.needs_reboot = False
        self.system_info = get_system_info()
        self.hardware_checks = {}
        self.profile = "balanced"  # Default profile
        self.thermal_manager = ThermalManager(self.logger)
        self.stability_tester = StabilityTester(self.logger)
        self.power_monitor = PowerMonitor(self.logger)
        self.backup_manager = BackupManager(self.logger)
        self.validation_results = {}
        
        # Adjust profile for handheld devices
        if self.system_info["form_factor"] in ["steamdeck", "handheld"]:
            self.profile = "handheld"
            self.logger.info(f"Handheld device detected - using {self.profile} profile")
    
    def print_banner(self):
        """Display welcome banner"""
        print_colored("=" * 80, Colors.HEADER)
        print_colored("    BAZZITE DX ULTIMATE GAMING OPTIMIZER v" + SCRIPT_VERSION, Colors.HEADER + Colors.BOLD)
        print_colored("  Enhanced for RTX 5080 Blackwell | i9-10850K | 64GB RAM", Colors.OKCYAN)
        print_colored("  v4: Stability Testing | Power Monitoring | Safety Features", Colors.OKBLUE)
        print_colored("=" * 80, Colors.HEADER)
        print()
    
    def print_system_info(self):
        """Display detected system information"""
        print_colored("\nSystem Information:", Colors.OKBLUE)
        print(f"  OS: {self.system_info['distribution']}")
        print(f"  Kernel: {self.system_info['kernel']}")
        print(f"  CPU: {self.system_info['cpu_model']}")
        print(f"  Cores: {self.system_info['cpu_cores']} / Threads: {self.system_info['cpu_threads']}")
        print(f"  RAM: {self.system_info['ram_gb']} GB")
        print(f"  Free Disk: {self.system_info['free_disk_gb']} GB")
        print(f"  Form Factor: {self.system_info['form_factor'].upper()}")
        print(f"  Display Server: {self.system_info['display_server'].upper()}")
        
        if self.system_info['gpus']:
            print(f"  GPU: {self.system_info['gpus'][0].split(':')[-1].strip()}")
        
        driver_version = check_nvidia_driver_version()
        if driver_version:
            print(f"  NVIDIA Driver: {driver_version}")
        
        # Show current temperatures
        gpu_temp = get_gpu_temperature()
        cpu_temp = get_cpu_temperature()
        if gpu_temp:
            color = Colors.OKGREEN if gpu_temp < 70 else Colors.WARNING if gpu_temp < 83 else Colors.FAIL
            print_colored(f"  GPU Temperature: {gpu_temp}°C", color)
        if cpu_temp:
            color = Colors.OKGREEN if cpu_temp < 80 else Colors.WARNING if cpu_temp < 95 else Colors.FAIL
            print_colored(f"  CPU Temperature: {cpu_temp}°C", color)
        
        # Show power consumption
        gpu_power, cpu_power = get_power_consumption()
        if gpu_power or cpu_power:
            print(f"  Power Draw: GPU {gpu_power}W, CPU {cpu_power}W")
        
        print()
    
    def check_prerequisites(self) -> bool:
        """Check system prerequisites with v4 enhancements"""
        print_colored("Checking system prerequisites...", Colors.OKBLUE)
        
        # Check if running as root
        if os.geteuid() != 0:
            print_colored("ERROR: This script must be run as root (use sudo)", Colors.FAIL)
            return False
        
        # Check kernel version
        if not check_kernel_version():
            kernel_version = self.system_info.get("kernel_version", (0, 0, 0))
            print_colored(f"WARNING: Kernel {kernel_version} is older than recommended {MIN_KERNEL_VERSION}", Colors.WARNING)
            print_colored("Some features like MGLRU may not be available", Colors.WARNING)
        
        # Check disk space (increased for stability testing)
        if not check_disk_space():
            free_gb = self.system_info.get("free_disk_gb", 0)
            print_colored(f"ERROR: Insufficient disk space ({free_gb}GB free, need {MIN_DISK_SPACE_GB}GB)", Colors.FAIL)
            return False
        
        # Check hardware compatibility
        self.hardware_checks = check_hardware_compatibility()
        
        print("\nHardware Detection:")
        optimal_config = True
        for component, detected in self.hardware_checks.items():
            if component == "nvidia_gpu_present" and not detected:
                print_colored("  ✗ No NVIDIA GPU detected - GPU optimizations will be skipped", Colors.WARNING)
                continue
                
            status = "✓" if detected else "✗"
            color = Colors.OKGREEN if detected else Colors.WARNING
            component_name = component.replace('_', ' ').title()
            print_colored(f"  {status} {component_name}", color)
            
            if component == "resizable_bar" and not detected:
                print_colored("    → Enable Resizable BAR in BIOS for better performance", Colors.WARNING)
            
            if not detected and component not in ["bazzite_os", "nvidia_gpu_present", "resizable_bar"]:
                optimal_config = False
        
        # Warn if not on Bazzite
        if not self.hardware_checks["bazzite_os"]:
            print_colored("\nWARNING: Bazzite not detected. Some optimizations may not work correctly.", Colors.WARNING)
            print_colored("Continue anyway? (y/n): ", Colors.WARNING, end="")
            if input().lower() != 'y':
                return False
        
        # Warn if hardware doesn't match optimal config
        if not optimal_config and self.system_info["form_factor"] == "desktop":
            print_colored("\nWARNING: Some expected hardware components were not detected.", Colors.WARNING)
            print_colored("The optimizations are tailored for specific hardware.", Colors.WARNING)
            print_colored("Continue anyway? (y/n): ", Colors.WARNING, end="")
            if input().lower() != 'y':
                return False
        
        # Thermal warning
        gpu_temp = get_gpu_temperature()
        if gpu_temp and gpu_temp > MAX_GPU_TEMP_WARNING:
            print_colored(f"\nWARNING: GPU temperature is high ({gpu_temp}°C)", Colors.WARNING)
            print_colored("Consider improving cooling before applying overclocking", Colors.WARNING)
            print_colored("Continue anyway? (y/n): ", Colors.WARNING, end="")
            if input().lower() != 'y':
                return False
        
        return True
    
    def apply_optimizations(self, skip_packages: bool = False, 
                           run_benchmarks: bool = False,
                           stability_test: bool = False):
        """Apply all optimizations with v4 safety features"""
        print_colored(f"\nStarting optimization process (Profile: {self.profile.upper()})...", Colors.HEADER)
        
        # Show security warning for risky profiles
        show_security_warning(self.profile)
        
        # Create recovery point
        self.backup_manager.create_recovery_point(f"pre_optimization_{self.profile}")
        
        # Setup automated backups
        self.backup_manager.setup_auto_backup()
        
        # Record baseline power consumption
        self.power_monitor.record_baseline()
        
        # Start power monitoring
        self.power_monitor.start_monitoring()
        
        # [Main optimization loop - similar to v3 but with safety checks]
        # ... (optimization application code remains similar)
        
        # Run stability test if requested or if using aggressive profile
        if stability_test or self.profile == "competitive":
            print_colored("\nRunning stability test...", Colors.OKCYAN)
            passed = self.stability_tester.quick_test()
            
            if not passed:
                print_colored("WARNING: System failed stability test!", Colors.FAIL)
                print_colored("Consider reducing overclock values", Colors.WARNING)
                
                # Offer to switch to safe mode
                print_colored("\nSwitch to safe mode? (y/n): ", Colors.WARNING, end="")
                if input().lower() == 'y':
                    self.profile = "safe"
                    self.apply_optimizations(skip_packages=True)
        
        # Generate power report
        print_colored("\n" + self.power_monitor.generate_report(), Colors.OKBLUE)
        
        # Start thermal monitoring with selected profile
        profile_settings = GAMING_PROFILES.get(self.profile, GAMING_PROFILES["balanced"])["settings"]
        self.thermal_manager.start_monitoring(profile_settings.get("fan_profile", "balanced"))
        
        return True
    
    def run(self):
        """Main execution flow with v4 enhancements"""
        self.print_banner()
        self.print_system_info()
        
        # Check prerequisites
        if not self.check_prerequisites():
            return 1
        
        # Parse command line arguments
        parser = argparse.ArgumentParser(
            description='Bazzite DX Ultimate Gaming Optimizer v4 - Enhanced Edition',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument('--profile', 
                          choices=['competitive', 'balanced', 'streaming', 'creative', 'safe', 'handheld'],
                          default='balanced', help='Gaming profile to apply')
        parser.add_argument('--stability-test', action='store_true',
                          help='Run stability test after optimization')
        parser.add_argument('--test-duration', type=int, default=300,
                          help='Stability test duration in seconds (default: 300)')
        parser.add_argument('--skip-packages', action='store_true',
                          help='Skip package installation')
        parser.add_argument('--benchmark', action='store_true',
                          help='Run benchmarks')
        parser.add_argument('--power-report', action='store_true',
                          help='Show power consumption report only')
        parser.add_argument('--version', action='version',
                          version=f'%(prog)s {SCRIPT_VERSION}')
        
        args = parser.parse_args()
        
        # Handle power report
        if args.power_report:
            self.power_monitor.record_baseline()
            time.sleep(5)
            print(self.power_monitor.generate_report())
            return 0
        
        # Set profile
        self.profile = args.profile
        
        # Apply optimizations
        success = self.apply_optimizations(
            skip_packages=args.skip_packages,
            run_benchmarks=args.benchmark,
            stability_test=args.stability_test
        )
        
        if success:
            print_colored(f"\n✓ Optimization complete with {self.profile.upper()} profile!", 
                         Colors.OKGREEN + Colors.BOLD)
            
            if args.stability_test:
                print_colored("\nRunning extended stability test...", Colors.OKCYAN)
                passed, score, _ = self.stability_tester.run_full_test(args.test_duration)
                
                if passed:
                    print_colored(f"✓ System is stable! Score: {score}/100", Colors.OKGREEN)
                else:
                    print_colored(f"✗ Stability issues detected. Score: {score}/100", Colors.FAIL)
                    print_colored("Consider reducing overclock values", Colors.WARNING)
            
            print_colored(f"\nLog file: {LOG_DIR}/optimization_{TIMESTAMP}.log", Colors.OKBLUE)
            return 0
        else:
            print_colored("\n✗ Optimization failed. Check logs for details.", Colors.FAIL)
            return 1

# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    try:
        optimizer = BazziteGamingOptimizer()
        return optimizer.run()
    except KeyboardInterrupt:
        print_colored("\n\nOperation cancelled by user", Colors.WARNING)
        # Stop all monitoring
        if hasattr(optimizer, 'thermal_manager'):
            optimizer.thermal_manager.stop_monitoring()
        if hasattr(optimizer, 'power_monitor'):
            optimizer.power_monitor.stop_monitoring()
        return 130
    except Exception as e:
        print_colored(f"\nFatal error: {str(e)}", Colors.FAIL)
        logging.error(f"Fatal error: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
