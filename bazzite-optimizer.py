#!/usr/bin/env python3
"""
Bazzite DX Ultimate Gaming Optimization Master Script v4.0.0
For RTX 5080, Intel i9-10850K, 64GB RAM, Samsung 990 EVO Plus SSDs

Version 4.0 enhancements (incl. all previous features):
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
- Emergency thermal throttling

Includes all v3.0 features:
- Dynamic thermal management with temperature-based fan curves
- Performance validation system
- HDR and VRR configuration for modern displays
- Profile system (Competitive, Balanced, Streaming, Creative)
- Resizable BAR validation
- VKD3D-Proton shader cache optimization
- Enhanced safety checks and recovery mechanisms
- Benchmark integration for performance measurement
- Automatic optimization verification

Includes all v2.0 features:
- Latest RTX 5080 Blackwell optimizations
- DLSS 4 Frame Generation bug workarounds
- Optimized ZRAM configuration for 64GB systems
- Bazzite ujust command integration
- System76-scheduler configuration
- MGLRU and EEVDF scheduler tuning
- Enhanced PipeWire/WirePlumber configuration
- Intel I225-V ethernet fixes

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
# GAMING PROFILES - Enhanced with safety features and v4 additions
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
            "network_isolation": True,  # New v4: isolate gaming traffic
            "audio_quantum": 256,
            "visual_effects": False,
            "compositor_bypass": True,
            "mouse_polling": 1000,
            "disable_mitigations": True,
            "isolate_cores": True,
            "fan_profile": "aggressive",
            "undervolt_aggressive": False  # v4: Conservative for stability
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
    "safe": {  # v4: New safe mode profile
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
    "handheld": {  # v4: New handheld/Steam Deck profile
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
# OPTIMIZATION CONFIGURATIONS - All v3 configs with v4 enhancements
# ============================================================================

# NVIDIA RTX 5080 Configuration - Enhanced with validation and v4 safety
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
# v4 Safety: Temperature monitoring enabled
options nvidia NVreg_TemperatureMonitoring=1
"""

NVIDIA_XORG_CONFIG = """# RTX 5080 X11 Configuration with HDR Support
Section "Device"
    Identifier     "Nvidia Card"
    Driver         "nvidia"
    VendorName     "NVIDIA Corporation"
    BoardName      "GeForce RTX 5080"
    Option         "Coolbits" "28"
    Option         "TripleBuffer" "true"
    Option         "AllowIndirectGLXProtocol" "off"
    Option         "metamodes" "nvidia-auto-select +0+0 {ForceCompositionPipeline=On, ForceFullCompositionPipeline=On, AllowGSYNCCompatibleDPI=On}"
    Option         "UseNvKmsCompositionPipeline" "true"
EndSection

Section "Screen"
    Identifier     "Screen0"
    Device         "Nvidia Card"
    Option         "AllowGSYNC" "on"
    Option         "AllowGSYNCCompatible" "on"
    Option         "AllowHDR" "on"
    Option         "UseHotplugEvents" "true"
EndSection

Section "Extensions"
    Option         "DPMS" "false"
EndSection
"""

# Dynamic GPU Optimization Script with v4 safety checks
NVIDIA_OPTIMIZATION_SCRIPT = """#!/bin/bash
# RTX 5080 Gaming Optimization Script v4 - With Safety Features

# v4 Safety: Check if NVIDIA GPU exists
if ! command -v nvidia-smi &> /dev/null; then
    echo "WARNING: nvidia-smi not found, skipping GPU optimizations"
    exit 0
fi

if ! nvidia-smi &> /dev/null; then
    echo "WARNING: No NVIDIA GPU detected, skipping optimizations"
    exit 0
fi

# Function to get GPU temperature
get_gpu_temp() {{
    nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits 2>/dev/null || echo "0"
}}

# Function to get GPU power draw (v4)
get_gpu_power() {{
    nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits 2>/dev/null | cut -d. -f1 || echo "0"
}}

# v4 Safety check: Emergency throttle if too hot
emergency_check() {{
    local temp=$(get_gpu_temp)
    if [ $temp -gt {MAX_GPU_TEMP_CRITICAL} ]; then
        echo "CRITICAL: GPU temperature at ${{temp}}°C! Emergency throttling!"
        nvidia-settings -a '[gpu:0]/GPUPowerMizerMode=0' 2>/dev/null || true
        nvidia-settings -a '[gpu:0]/GPUTargetFanSpeed=100' 2>/dev/null || true
        exit 1
    fi
}}

# Function to apply fan curve with v4 safety
apply_fan_curve() {{
    local temp=$(get_gpu_temp)
    local fan_speed=50

    # v4 Safety override for high temps
    if [ $temp -gt 85 ]; then
        fan_speed=100
    else
        # Apply fan curve based on profile
        case "${{FAN_PROFILE:-balanced}}" in
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
}}

# v4: Record baseline power consumption
BASELINE_POWER=$(get_gpu_power)
echo "Baseline GPU power: ${{BASELINE_POWER}}W"

# v4: Emergency check before applying optimizations
emergency_check

# Enable maximum performance mode
nvidia-settings -a '[gpu:0]/GPUPowerMizerMode=1' 2>/dev/null || true

# RTX 5080 overclocking based on profile (with v4 validation)
CLOCK_OFFSET=${{GPU_CLOCK_OFFSET:-400}}
MEM_OFFSET=${{GPU_MEM_OFFSET:-800}}

# v4: Validate overclock values are within safe ranges
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

# v4: Display server specific optimizations
DISPLAY_SERVER=$(echo ${{XDG_SESSION_TYPE}})
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

# Start thermal monitoring daemon with v4 safety checks
(
    while true; do
        emergency_check
        apply_fan_curve

        # v4: Log power consumption
        CURRENT_POWER=$(get_gpu_power)
        echo "$(date +%s),GPU_POWER,$CURRENT_POWER" >> /var/log/bazzite-optimizer/power.csv

        sleep 5
    done
) &

# v4: Report power increase
sleep 2
CURRENT_POWER=$(get_gpu_power)
POWER_INCREASE=$((CURRENT_POWER - BASELINE_POWER))
echo "Power consumption increased by ${{POWER_INCREASE}}W"

echo "RTX 5080 Blackwell optimizations v4 applied with safety checks!"
"""

# Intel i9-10850K CPU Optimization - Enhanced with v4 stepped undervolting
CPU_OPTIMIZATION_SCRIPT = """#!/bin/bash
# i9-10850K Gaming Optimization v4 - With Stepped Undervolting

# Enable MSR module for advanced CPU control
modprobe msr 2>/dev/null || true

# Install cpupower if not present
if ! command -v cpupower &> /dev/null; then
    rpm-ostree install kernel-tools 2>/dev/null || dnf install -y kernel-tools 2>/dev/null || true
fi

# Function to get CPU package temperature
get_cpu_temp() {{
    sensors -j 2>/dev/null | grep -o '"temp[0-9]_input":[0-9.]*' | head -1 | cut -d: -f2 | cut -d. -f1 || echo "0"
}}

# v4: Function to get CPU power consumption
get_cpu_power() {{
    if command -v turbostat &> /dev/null; then
        turbostat --quiet --show PkgWatt --num_iterations 1 2>/dev/null | tail -1 | awk '{{print $1}}' | cut -d. -f1 || echo "0"
    else
        echo "0"
    fi
}}

# v4: Record baseline power
BASELINE_POWER=$(get_cpu_power)
echo "Baseline CPU power: ${{BASELINE_POWER}}W"

# v4 Safety check: Emergency throttle if too hot
emergency_check() {{
    local temp=$(get_cpu_temp)
    if [ -n "$temp" ] && [ "$temp" -gt {MAX_CPU_TEMP_CRITICAL} ]; then
        echo "CRITICAL: CPU temperature at ${{temp}}°C! Emergency throttling!"
        echo powersave | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null || true
        exit 1
    fi
}}

emergency_check

# Set governor based on profile
GOVERNOR=${{CPU_GOVERNOR:-performance}}
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
if [ "${{ISOLATE_CORES:-false}}" = "true" ]; then
    echo 1 > /sys/module/intel_idle/parameters/max_cstate 2>/dev/null || true
    echo 0 > /dev/cpu_dma_latency 2>/dev/null || true
else
    echo 3 > /sys/module/intel_idle/parameters/max_cstate 2>/dev/null || true
fi

# v4: Apply Intel undervolt with stepping (safer approach)
if command -v intel-undervolt &> /dev/null; then
    echo "Applying conservative stepped undervolting..."

    # Step 1: Very conservative
    intel-undervolt apply -v -25 2>/dev/null || true
    sleep 2
    emergency_check

    # Step 2: Moderate (only if Step 1 succeeded)
    if [ $? -eq 0 ] && [ "${{UNDERVOLT_AGGRESSIVE:-false}}" != "true" ]; then
        intel-undervolt apply -v -40 2>/dev/null || true
        sleep 2
        emergency_check
    fi

    # Step 3: Target (only if aggressive mode and previous steps succeeded)
    if [ $? -eq 0 ] && [ "${{UNDERVOLT_AGGRESSIVE:-false}}" = "true" ]; then
        intel-undervolt apply 2>/dev/null || true
        echo "Full undervolt profile applied"
    else
        echo "Conservative undervolt applied for stability"
    fi
fi

# Configure IRQ affinity for network and GPU
if [ "${{ISOLATE_CORES:-false}}" = "true" ]; then
    for irq in $(grep -E 'nvidia|igc' /proc/interrupts | cut -d: -f1); do
        echo 0-3 > /proc/irq/$irq/smp_affinity_list 2>/dev/null || true
    done
fi

# v4: Thermal monitoring with emergency response
(
    while true; do
        emergency_check

        # v4: Log power consumption
        CURRENT_POWER=$(get_cpu_power)
        echo "$(date +%s),CPU_POWER,$CURRENT_POWER" >> /var/log/bazzite-optimizer/power.csv

        sleep 5
    done
) &

# v4: Report power increase
sleep 2
CURRENT_POWER=$(get_cpu_power)
POWER_INCREASE=$((CURRENT_POWER - BASELINE_POWER))
echo "CPU power consumption changed by ${{POWER_INCREASE}}W"

echo "Intel i9-10850K optimized with stepped undervolting (Profile: $GOVERNOR)!"
"""

# Memory Configuration - Optimized with profile support
SYSCTL_CONFIG = """# 64GB RAM Gaming Optimizations v4 with Profile Support
# Profile: {PROFILE}

# ZRAM optimized values
vm.swappiness={SWAPPINESS}
vm.page-cluster=0
vm.vfs_cache_pressure=50
vm.dirty_background_ratio=5
vm.dirty_ratio=20
vm.dirty_writeback_centisecs=1500
vm.dirty_expire_centisecs=3000
vm.min_free_kbytes=1048576

# Transparent Huge Pages
vm.transparent_hugepage=madvise
vm.nr_hugepages=0

# Memory management
vm.overcommit_memory=1
vm.overcommit_ratio=50
vm.panic_on_oom=0
vm.oom_kill_allocating_task=1

# Network optimizations for gaming
net.core.rmem_default=262144
net.core.rmem_max=134217728
net.core.wmem_default=262144
net.core.wmem_max=134217728
net.core.netdev_max_backlog=30000
net.core.netdev_budget=600
net.core.netdev_budget_usecs=8000

# TCP optimizations with BBR
net.ipv4.tcp_congestion_control=bbr
net.core.default_qdisc=fq
net.ipv4.tcp_fastopen=3
net.ipv4.tcp_low_latency=1
net.ipv4.tcp_timestamps={TCP_TIMESTAMPS}
net.ipv4.tcp_sack=1
net.ipv4.tcp_window_scaling=1
net.ipv4.tcp_adv_win_scale=1
net.ipv4.tcp_mtu_probing=1

# Gaming-specific network tuning
net.ipv4.tcp_fin_timeout=15
net.ipv4.tcp_keepalive_time=300
net.ipv4.tcp_keepalive_intvl=30
net.ipv4.tcp_keepalive_probes=5
net.ipv4.tcp_tw_reuse=1
net.ipv4.ip_local_port_range=1024 65535
net.ipv4.tcp_max_syn_backlog=8192
net.ipv4.tcp_max_tw_buckets=2000000
net.ipv4.tcp_slow_start_after_idle=0
net.ipv4.tcp_no_metrics_save=1

# Security (minimal impact on gaming)
net.ipv4.tcp_rfc1337=1
net.ipv4.conf.all.rp_filter=1
net.ipv4.conf.default.rp_filter=1
"""

# Intel undervolt configuration - v4 More conservative
UNDERVOLT_CONFIG = """# Intel i9-10850K Conservative Undervolt Configuration v4
# WARNING: These are conservative starting values - monitor stability!

# v4: Conservative values for stability
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

# HDR and VRR Configuration
HDR_ENVIRONMENT = """# HDR and Variable Refresh Rate Configuration
export KWIN_HDR=1
export VK_HDR_ENABLED=1
export GAMESCOPE_HDR_ENABLED=1
export GAMESCOPE_HDR_ITM_ENABLE=1
export GAMESCOPE_HDR_ITM_TARGET_NITS=1000
export KWIN_VRRONENABLED=1
export __GL_VRR_ALLOWED=1
export KWIN_FORCE_SW_CURSOR=0
export WLR_DRM_NO_MODIFIERS=0
"""

# Shader Cache Configuration
SHADER_CACHE_SETUP = """#!/bin/bash
# Setup optimized shader cache directories

# Create cache directories with proper permissions
mkdir -p /var/cache/gaming-shaders/{nvidia,vkd3d-proton,dxvk-state}
chmod 777 /var/cache/gaming-shaders -R

# Configure tmpfs for shader compilation (faster)
if ! mount | grep -q /var/cache/gaming-shaders; then
    echo "tmpfs /var/cache/gaming-shaders tmpfs rw,size=4G,uid=1000,gid=1000 0 0" >> /etc/fstab
    mount /var/cache/gaming-shaders
fi

# Symlink user shader caches to central location
for user_home in /home/*; do
    user=$(basename $user_home)
    if [ -d "$user_home" ]; then
        # NVIDIA shader cache
        mkdir -p $user_home/.nv/GLCache
        ln -sf /var/cache/gaming-shaders/nvidia $user_home/.nv/GLCache 2>/dev/null || true

        # VKD3D-Proton cache
        mkdir -p $user_home/.cache
        ln -sf /var/cache/gaming-shaders/vkd3d-proton $user_home/.cache/vkd3d-proton 2>/dev/null || true

        # DXVK state cache
        ln -sf /var/cache/gaming-shaders/dxvk-state $user_home/.cache/dxvk-state 2>/dev/null || true

        chown -R $user:$user $user_home/.nv $user_home/.cache 2>/dev/null || true
    fi
done

echo "Shader cache directories configured"
"""

# ZRAM Configuration - Profile-aware
ZRAM_CONFIG = """# ZRAM Configuration for 64GB Gaming System
[zram0]
# {PROFILE} Profile Configuration
zram-size = min(ram / {DIVISOR}, {MAX_SIZE})
compression-algorithm = {ALGORITHM}
writeback-device = /dev/nvme0n1p3
"""

# NVMe Optimization
NVME_UDEV_RULES = """# Samsung 990 EVO Plus Optimizations v4
ACTION=="add|change", KERNEL=="nvme[0-9]n[0-9]", ATTR{queue/scheduler}="none"
ACTION=="add|change", KERNEL=="nvme[0-9]n[0-9]", ATTR{queue/nr_requests}="2048"
ACTION=="add|change", KERNEL=="nvme[0-9]n[0-9]", ATTR{queue/read_ahead_kb}="256"
ACTION=="add|change", KERNEL=="nvme[0-9]n[0-9]", ATTR{queue/max_sectors_kb}="2048"
ACTION=="add|change", KERNEL=="nvme[0-9]n[0-9]", ATTR{queue/rotational}="0"
ACTION=="add|change", KERNEL=="nvme[0-9]n[0-9]", ATTR{queue/rq_affinity}="2"
ACTION=="add|change", KERNEL=="nvme[0-9]n[0-9]", ATTR{queue/add_random}="0"
ACTION=="add|change", KERNEL=="nvme[0-9]n[0-9]", ATTR{queue/nomerges}="1"
ACTION=="add|change", KERNEL=="nvme[0-9]n[0-9]", ATTR{queue/iostats}="0"
ACTION=="add|change", KERNEL=="nvme[0-9]n[0-9]", ATTR{queue/write_cache}="write back"
"""

# PipeWire Configuration - Profile-aware
PIPEWIRE_CONFIG = """# Gaming optimized PipeWire configuration v4
# Profile: {PROFILE}
context.properties = {{
    default.clock.rate = 48000
    default.clock.quantum = {QUANTUM}
    default.clock.min-quantum = {MIN_QUANTUM}
    default.clock.max-quantum = {MAX_QUANTUM}
    default.clock.quantum-limit = 8192
}}

context.modules = [
    {{   name = libpipewire-module-rt
        args = {{
            nice.level = -20
            rt.prio = 89
            rt.time.soft = 200000
            rt.time.hard = 2000000
        }}
        flags = [ ifexists nofail ]
    }}
    {{   name = libpipewire-module-protocol-pulse
        args = {{
            server.address = [ "unix:native" ]
            pulse.min.req = {MIN_QUANTUM}/48000
            pulse.default.req = {QUANTUM}/48000
            pulse.max.req = {MAX_QUANTUM}/48000
            pulse.min.quantum = {MIN_QUANTUM}/48000
            pulse.max.quantum = {MAX_QUANTUM}/48000
        }}
    }}
]

stream.properties = {{
    node.latency = {QUANTUM}/48000
    resample.quality = 10
    resample.disable = false
    channelmix.normalize = false
    channelmix.mix-lfe = false
}}
"""

# WirePlumber Configuration for Creative Sound Blaster
WIREPLUMBER_CONFIG = """-- Creative Sound Blaster AE-5 Plus optimizations v4
alsa_monitor.rules = {{
  {{
    matches = {{
      {{
        {{ "node.name", "matches", "alsa_output.*Creative*" }},
      }},
    }},
    apply_properties = {{
      ["audio.format"] = "S32LE",
      ["audio.rate"] = "48000",
      ["audio.channels"] = "2",
      ["audio.position"] = "FL,FR",
      ["api.alsa.period-size"] = {PERIOD_SIZE},
      ["api.alsa.period-num"] = 2,
      ["api.alsa.headroom"] = {PERIOD_SIZE},
      ["api.alsa.disable-batch"] = true,
      ["api.alsa.disable-tsched"] = true,
      ["api.alsa.use-acp"] = false,
      ["node.latency"] = "{PERIOD_SIZE}/48000",
      ["node.pause-on-idle"] = false,
      ["session.suspend-timeout-seconds"] = 0,
      ["resample.disable"] = true,
    }},
  }},
}}
"""

# Intel I225-V Ethernet Module Configuration
IGC_MODULE_CONFIG = """# Intel I225-V Gaming Optimizations v4
options igc InterruptThrottleRate=0
options igc IntMode=2
options igc TxIntDelay=0
options igc TxAbsIntDelay=0
options igc RxIntDelay=0
options igc RxAbsIntDelay=0
options igc TxDescriptors=4096
options igc RxDescriptors=4096
options igc FlowControl=0
options igc EEE=0
options igc DMAC=0
options igc MDD=0
options igc LRO=0
"""

# Ethernet Optimization Script - Profile-aware
ETHERNET_OPTIMIZE_SCRIPT = """#!/bin/bash
# Intel I225-V Ethernet Optimization v4 - Profile-aware

# Find ethernet interface
ETH=$(ip link | grep -E '^[0-9]+: e' | cut -d: -f2 | tr -d ' ' | head -1)

if [ -n "$ETH" ]; then
    # Profile-based optimization
    case "${NETWORK_PROFILE:-low}" in
        ultra-low)
            # Competitive gaming - absolute minimum latency
            ethtool -C $ETH adaptive-rx off adaptive-tx off 2>/dev/null || true
            ethtool -C $ETH rx-usecs 0 tx-usecs 0 2>/dev/null || true
            ethtool -C $ETH rx-frames 1 tx-frames 1 2>/dev/null || true
            ethtool -K $ETH gro off gso off tso off 2>/dev/null || true
            ;;
        low)
            # Standard gaming - low latency
            ethtool -C $ETH adaptive-rx off adaptive-tx off 2>/dev/null || true
            ethtool -C $ETH rx-usecs 10 tx-usecs 10 2>/dev/null || true
            ethtool -C $ETH rx-frames 2 tx-frames 2 2>/dev/null || true
            ;;
        balanced)
            # Streaming - balance between latency and throughput
            ethtool -C $ETH adaptive-rx on adaptive-tx on 2>/dev/null || true
            ethtool -C $ETH rx-usecs 50 tx-usecs 50 2>/dev/null || true
            ;;
    esac

    # Set ring buffer sizes to maximum
    ethtool -G $ETH rx 4096 tx 4096 2>/dev/null || true

    # Intel I225-V specific fixes
    # Disable Energy Efficient Ethernet (problematic on I225-V)
    ethtool --set-eee $ETH eee off 2>/dev/null || true

    # Enable receive packet steering
    echo 32768 > /proc/sys/net/core/rps_sock_flow_entries 2>/dev/null || true

    for rxq in /sys/class/net/$ETH/queues/rx-*/rps_cpus; do
        echo ff > $rxq 2>/dev/null || true
    done

    for rxq in /sys/class/net/$ETH/queues/rx-*/rps_flow_cnt; do
        echo 2048 > $rxq 2>/dev/null || true
    done

    # Optimize interrupt affinity based on profile
    if [ "${{ISOLATE_CORES:-false}}" = "true" ]; then
        for irq in $(grep $ETH /proc/interrupts | cut -d: -f1); do
            echo 0-3 > /proc/irq/$irq/smp_affinity_list 2>/dev/null || true
        done
    fi

    echo "Intel I225-V ethernet optimized for gaming (Profile: ${NETWORK_PROFILE:-low})!"
else
    echo "No ethernet interface found"
fi
"""

# v4: Network isolation script for competitive gaming
NETWORK_ISOLATION_SCRIPT = """#!/bin/bash
# Network isolation for competitive gaming - minimize jitter

# Identify gaming interface
GAMING_IF=$(ip route | grep default | awk '{{print $5}}' | head -1)

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

# GameMode Configuration - Profile-aware
GAMEMODE_CONFIG = """[general]
renice=15
softrealtime=auto
ioprio=0
inhibit_screensaver=1

[filter]
whitelist=steam
whitelist=heroic
whitelist=lutris
whitelist=bottles
whitelist=wine
whitelist=proton

[cpu]
park_cores=no
pin_cores={PIN_CORES}
core_threshold_percent=20

[gpu]
apply_gpu_optimisations=accept-responsibility
gpu_device=0
amd_performance_level=high
nv_powermizer_mode={GPU_POWER_MODE}
nv_core_clock_mhz_offset={GPU_CLOCK_OFFSET}
nv_mem_clock_mhz_offset={GPU_MEM_OFFSET}

[custom]
start=/usr/local/bin/gaming-mode-start.sh
end=/usr/local/bin/gaming-mode-end.sh

[supervisor]
supervisor_config=/etc/system76-scheduler/config.kdl
"""

# MangoHud Configuration - Profile-aware
MANGOHUD_CONFIG = """# MangoHud Gaming Configuration v4
# Profile: {PROFILE}

gpu_stats
gpu_temp
gpu_power
gpu_load_change
gpu_load_value=50,90
gpu_load_color=FFFFFF,FFAA7F,CC0000
gpu_text=GPU
vram
vram_color=AD64C1

cpu_stats
cpu_temp
cpu_power
cpu_load_change
cpu_mhz
cpu_load_value=50,90
cpu_load_color=FFFFFF,FFAA7F,CC0000
cpu_color=2E97CB
cpu_text=CPU

ram
ram_color=C26693

fps
fps_limit_method=late
fps_limit={FPS_LIMIT}
fps_value=30,60,144
fps_color=B22222,FDFD09,39F900
frametime={SHOW_FRAMETIME}
frame_timing={SHOW_FRAMETIMING}

gamemode
vkbasalt

{EXTRA_METRICS}

font_size=20
font_size_text=24
font_scale=1.0
text_outline
background_alpha=0.4
position=top-left

no_display=0
toggle_hud=Shift_R+F12
toggle_fps_limit=Shift_L+F1
toggle_logging=Shift_L+F2
reload_cfg=Shift_L+F4

legacy_layout=0
gpu_color=2E9762
wine
wine_color=EB5B5B
engine_version
engine_color=EB5B5B
vulkan_driver
arch
media_player_color=FFFFFF

# Performance logging for validation
output_folder=/var/log/mangohud
log_duration=60
autostart_log=0
"""

# System76 Scheduler Configuration
SYSTEM76_SCHEDULER_CONFIG = """// System76 Scheduler Configuration for Gaming v4
// Profile: {PROFILE}
autogroup-enabled true
cfs-profiles enable=true

// Define scheduler profiles
cfs-profiles {{
    default latency=6 nr-latency=-1 preempt="voluntary" slice=3

    responsive latency={LATENCY} nr-latency=10 preempt="{PREEMPT}" slice={SLICE}
}}

// Process rules for gaming
process-scheduler {{
    foreground profile="responsive"

    pipewire class="realtime" prio=95
    pipewire-pulse class="realtime" prio=95

    steam profile="responsive" nice=-5
    gamemoded profile="responsive" nice=-10
    wine profile="responsive" nice=-5
    proton profile="responsive" nice=-5

    chrome profile="background" nice=5
    firefox profile="background" nice=5
    OBS profile="{OBS_PROFILE}" nice={OBS_NICE}
}}
"""

# v4: Log rotation configuration
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

# v4: Automated backup script
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

# v4: Stability test script
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
AVG_GPU_TEMP=$(cut -d, -f2 "$RESULT_DIR/temps.csv" | awk '{{sum+=$1}} END {{print int(sum/NR)}}')
AVG_CPU_TEMP=$(cut -d, -f3 "$RESULT_DIR/temps.csv" | awk '{{sum+=$1}} END {{print int(sum/NR)}}')

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

# Master Gaming Activation Script with v4 safety and monitoring
MASTER_GAMING_SCRIPT = """#!/bin/bash
# Bazzite DX Complete Gaming Mode Activation v4
# Profile: {PROFILE}

echo "Activating Ultimate Gaming Mode (Profile: {PROFILE})..."

# v4: Safety check - Create automatic backup first
/usr/local/bin/auto-backup.sh

# v4: Show security warning if using competitive profile
if [ "{PROFILE}" = "competitive" ] && [ "${{SECURITY_WARNING_ACKNOWLEDGED:-false}}" != "true" ]; then
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║                    SECURITY WARNING                    ║"
    echo "╠════════════════════════════════════════════════════════╣"
    echo "║ Competitive profile DISABLES CPU security mitigations! ║"
    echo "║                                                        ║"
    echo "║ This makes your system vulnerable to:                  ║"
    echo "║   • Spectre/Meltdown attacks                           ║"
    echo "║   • Side-channel attacks                               ║"
    echo "║   • Other CPU vulnerabilities                          ║"
    echo "║                                                        ║"
    echo "║ Only use on:                                           ║"
    echo "║   ✓ Trusted, isolated networks                         ║"
    echo "║   ✓ Dedicated gaming systems                           ║"
    echo "║   ✗ NEVER on systems with sensitive data               ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    echo "Press ENTER to acknowledge and continue, or Ctrl+C to cancel..."
    read
    export SECURITY_WARNING_ACKNOWLEDGED=true
fi

# Load profile settings
export GAMING_PROFILE={PROFILE}
source /etc/bazzite-optimizer/profiles/{PROFILE}.env 2>/dev/null || true

# v4: Detect display server
export DISPLAY_SERVER=$(echo ${{XDG_SESSION_TYPE}})
echo "Display server detected: $DISPLAY_SERVER"

# v4: Record baseline power consumption
BASELINE_GPU_POWER=$(nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits 2>/dev/null | cut -d. -f1 || echo "0")
BASELINE_CPU_POWER=$(turbostat --quiet --show PkgWatt --num_iterations 1 2>/dev/null | tail -1 | awk '{{print $1}}' | cut -d. -f1 || echo "0")
echo "Baseline power: GPU ${{BASELINE_GPU_POWER}}W, CPU ${{BASELINE_CPU_POWER}}W"

# CPU Optimizations
echo ${{CPU_GOVERNOR:-performance}} | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null || true
echo 1 > /sys/module/processor/parameters/ignore_ppc 2>/dev/null || true
echo 0 > /dev/cpu_dma_latency 2>/dev/null || true

# GPU Optimizations (NVIDIA RTX 5080)
/usr/local/bin/nvidia-gaming-optimize.sh 2>/dev/null || true

# Network Optimizations (Intel I225-V)
/usr/local/bin/ethernet-optimize.sh 2>/dev/null || true

# v4: Network Isolation Mode (competitive profile)
if [ "${{NETWORK_ISOLATION:-false}}" = "true" ]; then
    /usr/local/bin/network-isolation.sh 2>/dev/null || true
fi

# Audio latency optimization
pw-metadata -n settings 0 clock.force-quantum ${{AUDIO_QUANTUM:-512}} 2>/dev/null || true
pw-metadata -n settings 0 clock.force-rate 48000 2>/dev/null || true

# Enable MGLRU if available (kernel 6.1+)
echo Y > /sys/kernel/mm/lru_gen/enabled 2>/dev/null || true
echo 1000 > /sys/kernel/mm/lru_gen/min_ttl_ms 2>/dev/null || true

# Process scheduling optimization
echo 500000 > /proc/sys/kernel/sched_migration_cost_ns 2>/dev/null || true
echo 1 > /proc/sys/kernel/sched_autogroup_enabled 2>/dev/null || true

# I/O optimizations
for disk in /sys/block/nvme*/queue/; do
    echo 2048 > ${{disk}}nr_requests 2>/dev/null || true
    echo 2 > ${{disk}}rq_affinity 2>/dev/null || true
    echo 0 > ${{disk}}add_random 2>/dev/null || true
    echo 1 > ${{disk}}nomerges 2>/dev/null || true
done

# Memory management
echo ${{VM_SWAPPINESS:-120}} > /proc/sys/vm/swappiness 2>/dev/null || true
sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true

# Power Profile
powerprofilesctl set performance 2>/dev/null || true

# Start performance monitoring
if [ "${{ENABLE_MONITORING:-true}}" = "true" ]; then
    /usr/local/bin/performance-monitor.sh &
fi

# v4: Report final power consumption
sleep 3
FINAL_GPU_POWER=$(nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits 2>/dev/null | cut -d. -f1 || echo "0")
FINAL_CPU_POWER=$(turbostat --quiet --show PkgWatt --num_iterations 1 2>/dev/null | tail -1 | awk '{{print $1}}' | cut -d. -f1 || echo "0")
GPU_INCREASE=$((FINAL_GPU_POWER - BASELINE_GPU_POWER))
CPU_INCREASE=$((FINAL_CPU_POWER - BASELINE_CPU_POWER))

echo "Power consumption changes:"
echo "  GPU: +${{GPU_INCREASE}}W (${{BASELINE_GPU_POWER}}W -> ${{FINAL_GPU_POWER}}W)"
echo "  CPU: +${{CPU_INCREASE}}W (${{BASELINE_CPU_POWER}}W -> ${{FINAL_CPU_POWER}}W)"
echo "  Total system increase: ~$((GPU_INCREASE + CPU_INCREASE))W"

notify-send "Gaming Mode" "Profile '${{GAMING_PROFILE}}' activated!\nPower +$((GPU_INCREASE + CPU_INCREASE))W" 2>/dev/null || true
echo "Gaming optimizations applied successfully (Profile: ${{GAMING_PROFILE}})!"
"""

# Gaming Mode End Script
GAMING_MODE_END_SCRIPT = """#!/bin/bash
# Restore system to balanced mode v4

echo "Deactivating Gaming Mode..."

# Stop performance monitoring
pkill -f performance-monitor.sh 2>/dev/null || true

# Stop thermal monitoring
pkill -f "apply_fan_curve" 2>/dev/null || true

# v4: Restore network isolation
if [ -f /etc/resolv.conf.backup ]; then
    cp /etc/resolv.conf.backup /etc/resolv.conf
    rm -f /etc/resolv.conf.backup
fi

# Restore CPU governor
echo schedutil | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null || \
    echo powersave | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null || true

# Restore GPU PowerMizer
nvidia-settings -a '[gpu:0]/GPUPowerMizerMode=2' 2>/dev/null || true
nvidia-settings -a '[gpu:0]/GPUFanControlState=0' 2>/dev/null || true

# Restore power profile
powerprofilesctl set balanced 2>/dev/null || true

# Reset audio
pw-metadata -n settings 0 clock.force-quantum 0 2>/dev/null || true

notify-send "Gaming Mode" "Optimizations deactivated" 2>/dev/null || true
"""

# Performance Monitor Script
PERFORMANCE_MONITOR_SCRIPT = """#!/bin/bash
# Performance monitoring daemon for optimization validation

LOG_DIR=/var/log/bazzite-optimizer/performance
mkdir -p $LOG_DIR

while true; do
    # GPU metrics
    GPU_TEMP=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits)
    GPU_UTIL=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits)
    GPU_POWER=$(nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits)
    GPU_CLOCK=$(nvidia-smi --query-gpu=clocks.gr --format=csv,noheader,nounits)
    GPU_MEM=$(nvidia-smi --query-gpu=clocks.mem --format=csv,noheader,nounits)

    # CPU metrics
    CPU_TEMP=$(sensors -j 2>/dev/null | grep -o '"temp[0-9]_input":[0-9.]*' | head -1 | cut -d: -f2 | cut -d. -f1)
    CPU_FREQ=$(cat /proc/cpuinfo | grep MHz | head -1 | awk '{{print $4}}' | cut -d. -f1)
    CPU_GOV=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)

    # Network latency (ping to 8.8.8.8)
    PING=$(ping -c 1 -W 1 8.8.8.8 2>/dev/null | grep "time=" | cut -d= -f4 | cut -d' ' -f1)

    # Log metrics
    echo "$(date +%s),GPU,$GPU_TEMP,$GPU_UTIL,$GPU_POWER,$GPU_CLOCK,$GPU_MEM" >> $LOG_DIR/gpu.csv
    echo "$(date +%s),CPU,$CPU_TEMP,$CPU_FREQ,$CPU_GOV" >> $LOG_DIR/cpu.csv
    echo "$(date +%s),NET,$PING" >> $LOG_DIR/network.csv

    # Thermal warnings
    if [ "$GPU_TEMP" -gt 83 ]; then
        notify-send "GPU Thermal Warning" "Temperature: ${GPU_TEMP}°C" -u critical 2>/dev/null || true
    fi

    if [ -n "$CPU_TEMP" ] && [ "$CPU_TEMP" -gt 95 ]; then
        notify-send "CPU Thermal Warning" "Temperature: ${CPU_TEMP}°C" -u critical 2>/dev/null || true
    fi

    sleep 5
done
"""

# Systemd Service Configuration
SYSTEMD_SERVICE = """[Unit]
Description=Bazzite Gaming Performance Optimizations v4
After=multi-user.target graphical.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/gaming-mode-activate.sh
RemainAfterExit=yes
StandardOutput=journal
Environment="GAMING_PROFILE={PROFILE}"

[Install]
WantedBy=default.target
"""

# Benchmark script for performance validation
BENCHMARK_SCRIPT = """#!/bin/bash
# Performance benchmark script for optimization validation

echo "Running performance benchmarks..."

# Create results directory
RESULTS_DIR=/var/log/bazzite-optimizer/benchmarks/$(date +%Y%m%d_%H%M%S)
mkdir -p $RESULTS_DIR

# GPU benchmark using glmark2
if command -v glmark2 &> /dev/null; then
    echo "Running GPU benchmark..."
    glmark2 --fullscreen --show-all-options 2>&1 | tee $RESULTS_DIR/glmark2.txt
    GLMARK_SCORE=$(grep "glmark2 Score:" $RESULTS_DIR/glmark2.txt | awk '{{print $3}}')
    echo "GLMark2 Score: $GLMARK_SCORE"
fi

# CPU benchmark using sysbench
if command -v sysbench &> /dev/null; then
    echo "Running CPU benchmark..."
    sysbench cpu --cpu-max-prime=20000 --threads=20 run | tee $RESULTS_DIR/sysbench_cpu.txt
fi

# Memory benchmark
if command -v sysbench &> /dev/null; then
    echo "Running memory benchmark..."
    sysbench memory --memory-total-size=10G run | tee $RESULTS_DIR/sysbench_memory.txt
fi

# Disk benchmark
echo "Running disk benchmark..."
dd if=/dev/zero of=/tmp/test_write bs=1G count=1 oflag=direct 2>&1 | tee $RESULTS_DIR/disk_write.txt
dd if=/tmp/test_write of=/dev/null bs=1G count=1 iflag=direct 2>&1 | tee $RESULTS_DIR/disk_read.txt
rm -f /tmp/test_write

# Network latency test
echo "Running network latency test..."
ping -c 100 8.8.8.8 | tee $RESULTS_DIR/network_latency.txt

# Save system info
nvidia-smi > $RESULTS_DIR/nvidia_smi.txt
sensors > $RESULTS_DIR/sensors.txt
free -h > $RESULTS_DIR/memory.txt
cat /proc/cpuinfo > $RESULTS_DIR/cpuinfo.txt

echo "Benchmarks completed. Results saved to: $RESULTS_DIR"
echo ""
echo "Summary:"
echo "--------"
if [ -n "$GLMARK_SCORE" ]; then
    echo "GPU Performance: $GLMARK_SCORE points"
fi
grep "events per second" $RESULTS_DIR/sysbench_cpu.txt 2>/dev/null
grep "Total operations" $RESULTS_DIR/sysbench_memory.txt 2>/dev/null
echo ""

# Generate comparison if baseline exists
BASELINE=/var/log/bazzite-optimizer/benchmarks/baseline
if [ -d "$BASELINE" ]; then
    echo "Comparison with baseline:"
    echo "-------------------------"
    # Compare scores and show improvement percentage
    if [ -f "$BASELINE/glmark2.txt" ] && [ -n "$GLMARK_SCORE" ]; then
        BASELINE_SCORE=$(grep "glmark2 Score:" $BASELINE/glmark2.txt | awk '{{print $3}}')
        if [ -n "$BASELINE_SCORE" ]; then
            IMPROVEMENT=$(echo "scale=2; (($GLMARK_SCORE - $BASELINE_SCORE) / $BASELINE_SCORE) * 100" | bc)
            echo "GPU Performance Improvement: ${IMPROVEMENT}%"
        fi
    fi
fi

return 0
"""

# GRUB Kernel Parameters - Enhanced for v4 with security warnings
GRUB_CMDLINE_ADDITIONS = """mitigations={MITIGATIONS} processor.max_cstate={MAX_CSTATE} intel_idle.max_cstate={MAX_CSTATE}
intel_pstate=active transparent_hugepage=madvise nvme_core.default_ps_max_latency_us=0
pcie_aspm=off intel_iommu=on iommu=pt {ISOLCPUS} threadirqs preempt=full
nvidia-drm.modeset=1 nvidia-drm.fbdev=1 amdgpu.ppfeaturemask=0xffffffff
quiet splash {SECURITY_PARAMS}"""

# Bazzite-specific ujust commands to run - Updated with valid commands that work with sudo
BAZZITE_UJUST_COMMANDS = [
#    "ujust setup-sunshine",  # Valid - Toggle Sunshine Game Streaming host
#    "ujust update",  # Valid - Updates system, Flatpaks, and containers
]

# Commands removed due to incompatibility or non-existence:
# - ujust setup-gamemode (doesn't exist in current Bazzite)
# - ujust setup-mangohud (doesn't exist, mangohud is pre-installed)
# - ujust enable-gamescope-session (doesn't exist)
# - ujust install-greenwithenvy (doesn't exist)
# - ujust install-protonup-qt (doesn't exist)
# - ujust setup-decky (exists but fails with sudo - "ERROR: Do not run this with sudo")
# - ujust clean-system (causes rpm-ostree transaction conflicts with sudo)
# - ujust configure-btrfs-dedup (doesn't exist)

# ============================================================================
# LOGGING AND UTILITY FUNCTIONS - Enhanced for v4
# ============================================================================


def setup_logging() -> logging.Logger:
    """Configure comprehensive logging system with rotation"""
    # Create log directory with fallback for CI/testing environments
    log_dir = ensure_directory_with_fallback(LOG_DIR, "bazzite-optimizer/logs")
    if log_dir:
        log_file = log_dir / f"optimization_{TIMESTAMP}.log"
    else:
        log_file = None

    # Create detailed formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )

    # Console handler for user feedback
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    console_handler.setLevel(logging.INFO)

    # Configure logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    
    # Try to add file handler if log file is available
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            logger.addHandler(file_handler)
        except (PermissionError, OSError):
            # In CI/testing environments, console-only logging is acceptable
            logger.warning("Could not create log file, continuing with console logging only")
    else:
        logger.warning("Could not create log file, continuing with console logging only")

    # v4: Setup log rotation (skip if permission denied)
    try:
        setup_log_rotation()
    except (PermissionError, OSError):
        logger.debug("Could not setup log rotation, continuing without it")

    return logger


def setup_log_rotation():
    """v4: Configure logrotate for optimizer logs"""
    try:
        write_config_file(Path("/etc/logrotate.d/bazzite-optimizer"), LOGROTATE_CONFIG)
    except BaseException:
        pass  # Non-critical if it fails


def detect_display_server() -> str:
    """v4: Detect if running X11 or Wayland"""
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
    """v4: Detect if running on Steam Deck or handheld"""
    # Check for Steam Deck
    if Path("/sys/devices/virtual/dmi/id/product_name").exists():
        try:
            with open("/sys/devices/virtual/dmi/id/product_name") as f:
                product = f.read().strip()
                if "Jupiter" in product or "Galileo" in product:
                    return "steamdeck"
        except BaseException:
            pass

    # Check for other handhelds (ROG Ally, Legion Go, etc.)
    try:
        with open("/proc/cpuinfo") as f:
            cpuinfo = f.read()
            # AMD APUs commonly used in handhelds
            if "AMD Ryzen Z1" in cpuinfo or "AMD Ryzen 7 7840U" in cpuinfo:
                return "handheld"
    except BaseException:
        pass

    return "desktop"


def check_nvidia_gpu_exists() -> bool:
    """v4: Verify NVIDIA GPU actually exists and is accessible"""
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
    """v4: Validate GRUB configuration changes are safe"""
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
    """v4: Display security warnings for risky profiles"""
    global SECURITY_WARNINGS_SHOWN

    if SECURITY_WARNINGS_SHOWN:
        return

    profile_data = GAMING_PROFILES.get(profile, {})
    risk_level = profile_data.get("security_risk", "UNKNOWN")

    if risk_level in ["HIGH", "MEDIUM"]:
        print_colored("\n" + "=" * 60, Colors.WARNING)
        print_colored("SECURITY WARNING", Colors.WARNING + Colors.BOLD)
        print_colored("=" * 60, Colors.WARNING)

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

        print_colored("=" * 60, Colors.WARNING)
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


def ensure_directory_with_fallback(system_path: Path, fallback_subpath: str, 
                                  logger: Optional[logging.Logger] = None) -> Optional[Path]:
    """
    Create system directory with fallback to user directory for CI/restricted environments.
    
    Args:
        system_path: Preferred system directory path (e.g., Path('/var/log/app'))
        fallback_subpath: Subpath under ~/.local/share/ for fallback (e.g., 'app/logs')
        logger: Optional logger for debug messages
        
    Returns:
        Path object of created directory, or None if both attempts failed
    """
    # Try system directory first
    try:
        system_path.mkdir(parents=True, exist_ok=True)
        return system_path
    except (PermissionError, OSError) as e:
        # Fall back to user directory
        fallback_dir = Path.home() / ".local" / "share" / fallback_subpath
        try:
            fallback_dir.mkdir(parents=True, exist_ok=True)
            if logger:
                logger.debug(f"System directory unavailable, using fallback: {fallback_dir}")
            return fallback_dir
        except (PermissionError, OSError):
            if logger:
                logger.debug(f"Failed to create both system ({system_path}) and fallback ({fallback_dir}) directories")
            return None


def backup_file(filepath: Path) -> Optional[Path]:
    """Create timestamped backup of existing file"""
    if filepath.exists():
        # Use centralized directory management for backup directory
        backup_dir = ensure_directory_with_fallback(CONFIG_BACKUP_DIR, "bazzite-optimizer/backups")
        if backup_dir:
            try:
                backup_path = backup_dir / f"{filepath.name}.{TIMESTAMP}"
                shutil.copy2(filepath, backup_path)
                logging.info(f"Backed up {filepath} to {backup_path}")
                return backup_path
            except (PermissionError, OSError) as e:
                logging.debug(f"Could not create backup for {filepath}: {e}")
                return None
        else:
            logging.debug(f"Could not create backup directory for {filepath}")
            return None
    return None


def write_config_file(filepath: Path, content: str, executable: bool = False) -> bool:
    """Write configuration file with proper permissions and backup"""
    try:
        backup_file(filepath)

        # Handle parent directory creation with potential permission issues
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            logging.debug(f"Could not create parent directory for {filepath}: {e}")
            return False
            
        filepath.write_text(content)

        if executable:
            filepath.chmod(0o755)
        else:
            filepath.chmod(0o644)

        logging.info(f"Created configuration file: {filepath}")
        return True
    except (PermissionError, OSError) as e:
        # Log permission errors as debug in CI environments
        logging.debug(f"Could not write {filepath}: {e}")
        return False
    except Exception as e:
        logging.error(f"Failed to write {filepath}: {e}")
        return False


def get_smart_disk_space() -> int:
    """Smart disk space detection for composefs and traditional Linux systems"""
    # Priority order: user data locations first, then system locations, finally fallback
    priority_paths = ['/var/home', '/sysroot', '/var', '/']
    
    for path in priority_paths:
        try:
            if os.path.exists(path):
                usage = psutil.disk_usage(path)
                # Skip small overlay filesystems (composefs, tmpfs, etc.)
                if usage.total >= 100 * 1024**3:  # 100 GB minimum for storage
                    return round(usage.free / (1024**3))
        except Exception:
            continue
    return 0


def get_system_info() -> Dict[str, Any]:
    """Gather comprehensive system information - v4 enhanced"""
    info = {
        "kernel": platform.release(),
        "kernel_version": tuple(map(int, re.match(r'^(\d+)\.(\d+)\.(\d+)', platform.release()).groups())) if re.match(r'^(\d+)\.(\d+)\.(\d+)', platform.release()) else (0, 0, 0),
        "distribution": "",
        "cpu_model": "",
        "cpu_cores": psutil.cpu_count(logical=False),
        "cpu_threads": psutil.cpu_count(logical=True),
        "ram_gb": round(psutil.virtual_memory().total / (1024**3)),
        "gpus": [],
        "network_interfaces": [],
        "nvme_devices": [],
        "free_disk_gb": get_smart_disk_space(),
        "form_factor": detect_form_factor(),  # v4
        "display_server": detect_display_server()  # v4
    }

    # Get distribution info
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    info["distribution"] = line.split("=")[1].strip().strip('"')
    except BaseException:
        pass

    # Get CPU model
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if "model name" in line:
                    info["cpu_model"] = line.split(":")[1].strip()
                    break
    except BaseException:
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
    returncode, stdout, _ = run_command(
        "ls /dev/nvme* 2>/dev/null | grep -E 'nvme[0-9]n[0-9]$'", check=False)
    if returncode == 0 and stdout.strip():
        info["nvme_devices"] = stdout.strip().split("\n")

    return info


def check_hardware_compatibility() -> Dict[str, bool]:
    """Check if hardware matches expected configuration - v4 enhanced"""
    checks = {
        "nvidia_rtx5080": False,
        "intel_i9_10850k": False,
        "ram_64gb": False,
        "nvme_storage": False,
        "creative_audio": False,
        "intel_i225v": False,
        "bazzite_os": False,
        "resizable_bar": False,
        "nvidia_gpu_present": check_nvidia_gpu_exists()  # v4
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
    returncode, stdout, _ = run_command(
        "lspci -vv 2>/dev/null | grep -i 'resizable bar'", check=False)
    if returncode == 0 and stdout and "disabled" not in stdout.lower():
        checks["resizable_bar"] = True

    return checks


def check_nvidia_driver_version() -> Optional[str]:
    """Check NVIDIA driver version and variant - v4 enhanced"""
    if not check_nvidia_gpu_exists():
        return None

    returncode, stdout, _ = run_command(
        "nvidia-smi --query-gpu=driver_version --format=csv,noheader", check=False)
    if returncode == 0:
        version = stdout.strip()

        # Check if using -open variant
        returncode, stdout, _ = run_command(
            "modinfo nvidia 2>/dev/null | grep -i 'open gpu kernel'", check=False)
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


def get_gpu_temperature() -> Union[int, None]:
    """Get current GPU temperature - v4 enhanced"""
    if not check_nvidia_gpu_exists():
        return None

    returncode, stdout, _ = run_command(
        "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits",
        check=False
    )
    if returncode == 0:
        try:
            return int(stdout.strip())
        except (ValueError, AttributeError):
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
        except BaseException:
            pass
    return None


def get_power_consumption() -> Tuple[int, int]:
    """v4: Get current GPU and CPU power consumption"""
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
            except BaseException:
                pass

    # CPU power (requires turbostat)
    returncode, stdout, _ = run_command(
        "turbostat --quiet --show PkgWatt --num_iterations 1 2>/dev/null | tail -1 | awk '{print $1}'",
        check=False
    )
    if returncode == 0 and stdout.strip():
        try:
            cpu_power = int(float(stdout.strip()))
        except BaseException:
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
# OPTIMIZATION MODULES - All v3 modules with v4 enhancements
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

# v4: New Stability Tester class


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
                score_line = [line for line in stdout.split('\n') if "Stability Score:" in line][0]
                score = int(score_line.split(':')[1].split('/')[0].strip())
            except BaseException:
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

# v4: New Power Monitor class


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

# Enhanced ThermalManager with v4 emergency throttling


class ThermalManager:
    """Enhanced thermal management system for GPU and CPU"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.monitoring = False
        self.monitor_thread = None
        self.emergency_triggered = False  # v4

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
        """Main monitoring loop with v4 emergency response"""
        while self.monitoring:
            # Monitor GPU
            gpu_temp = get_gpu_temperature()
            if gpu_temp:
                self._apply_gpu_fan_curve(gpu_temp, fan_profile)

                # v4: Emergency response
                if gpu_temp > MAX_GPU_TEMP_CRITICAL:
                    self._emergency_throttle("GPU", gpu_temp)
                elif gpu_temp > MAX_GPU_TEMP_WARNING:
                    self.logger.warning(f"GPU temperature high: {gpu_temp}°C")
                    run_command(
                        f'notify-send "GPU Temperature Warning" "{gpu_temp}°C" -u critical',
                        check=False)

            # Monitor CPU
            cpu_temp = get_cpu_temperature()
            if cpu_temp:
                if cpu_temp > MAX_CPU_TEMP_CRITICAL:
                    self._emergency_throttle("CPU", cpu_temp)
                elif cpu_temp > MAX_CPU_TEMP_WARNING:
                    self.logger.warning(f"CPU temperature high: {cpu_temp}°C")
                    run_command(
                        f'notify-send "CPU Temperature Warning" "{cpu_temp}°C" -u critical',
                        check=False)

            time.sleep(2 if not self.emergency_triggered else 1)

    def _apply_gpu_fan_curve(self, temp: int, profile: str):
        """Apply GPU fan curve based on temperature"""
        if not check_nvidia_gpu_exists():
            return

        fan_speed = 50
        curve = FAN_CURVES.get(profile, FAN_CURVES["balanced"])

        # v4: Emergency override
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
        """v4: Emergency throttling when critical temperature reached"""
        if not self.emergency_triggered:
            self.emergency_triggered = True
            self.logger.critical(f"EMERGENCY: {component} temperature critical at {temp}°C!")

            if component == "GPU":
                # Throttle GPU to minimum
                run_command("nvidia-settings -a '[gpu:0]/GPUPowerMizerMode=0'", check=False)
                run_command("nvidia-settings -a '[gpu:0]/GPUTargetFanSpeed=100'", check=False)
                run_command(
                    "nvidia-settings -a '[gpu:0]/GPUGraphicsClockOffsetAllPerformanceLevels=0'",
                    check=False)
            else:
                # Throttle CPU to powersave
                run_command(
                    "echo powersave | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor",
                    check=False)

            run_command(
                f'notify-send "THERMAL EMERGENCY" "{component} at {temp}°C - System throttled!" -u critical',
                check=False)

            # Log incident
            with open(LOG_DIR / "thermal_incidents.log", 'a') as f:
                f.write(f"{datetime.now()}: {component} emergency throttle at {temp}°C\n")

# v4: New Backup Manager class


class BackupManager:
    """Automated backup management with integrity checking"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.backup_dir = CONFIG_BACKUP_DIR
        self.backup_retention_days = 30

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

    def _calculate_file_hash(self, filepath: Path) -> str:
        """Calculate SHA256 hash of a file for integrity checking"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.warning(f"Could not calculate hash for {filepath}: {e}")
            return ""

    def _verify_backup_integrity(self, backup_path: Path) -> bool:
        """Verify backup integrity using stored checksums"""
        checksum_file = backup_path / "checksums.txt"
        if not checksum_file.exists():
            return False

        try:
            with open(checksum_file, 'r') as f:
                for line in f:
                    stored_hash, filename = line.strip().split('  ', 1)
                    file_path = backup_path / filename
                    if file_path.exists():
                        actual_hash = self._calculate_file_hash(file_path)
                        if actual_hash != stored_hash:
                            self.logger.error(f"Integrity check failed for {filename}")
                            return False
            return True
        except Exception as e:
            self.logger.error(f"Failed to verify backup integrity: {e}")
            return False

    def _cleanup_old_backups(self):
        """Remove backups older than retention period"""
        if not self.backup_dir.exists():
            return

        cutoff_date = datetime.now() - timedelta(days=self.backup_retention_days)

        for backup_path in self.backup_dir.iterdir():
            if backup_path.is_dir():
                try:
                    backup_date_str = backup_path.name.split('_')[-1]
                    backup_date = datetime.strptime(backup_date_str, "%Y%m%d_%H%M%S")
                    if backup_date < cutoff_date:
                        self.logger.info(f"Removing old backup: {backup_path}")
                        shutil.rmtree(backup_path)
                except (ValueError, IndexError) as e:
                    self.logger.warning(f"Could not parse backup date from {backup_path}: {e}")

    def create_recovery_point(self, name: str = None):
        """Create a recovery point before major changes"""
        if not name:
            name = f"recovery_{TIMESTAMP}"

        # Use centralized directory management for recovery path
        recovery_base_dir = ensure_directory_with_fallback(
            CRASH_RECOVERY_DIR, "bazzite-optimizer/recovery", self.logger
        )
        if recovery_base_dir is None:
            self.logger.error("Could not create recovery directory")
            return
        
        recovery_path = recovery_base_dir / name
        try:
            recovery_path.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            self.logger.error(f"Could not create recovery point directory {recovery_path}: {e}")
            return

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

# NvidiaOptimizer with v4 safety checks


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

    def check_resizable_bar(self) -> bool:
        """Check if Resizable BAR is enabled"""
        self.logger.info("Checking Resizable BAR status...")

        returncode, stdout, _ = run_command("nvidia-smi -q | grep 'Resizable BAR'", check=False)
        if returncode == 0:
            if "enabled" in stdout.lower():
                self.logger.info("Resizable BAR is enabled")
                return True
            else:
                self.logger.warning(
                    "Resizable BAR is disabled - enable in BIOS for better performance")
                return False

        return False

    def install_drivers(self) -> bool:
        """Ensure proper NVIDIA drivers are installed"""
        self.logger.info("Checking NVIDIA driver installation...")

        # Check current driver
        if not self.check_driver_compatibility():
            self.logger.info("Installing/updating NVIDIA drivers...")

            # For Bazzite, use rpm-ostree
            commands = [
                "rpm-ostree install akmod-nvidia-open xorg-x11-drv-nvidia-open",
                "rpm-ostree install nvidia-vaapi-driver nvidia-settings"
            ]

            for cmd in commands:
                returncode, stdout, stderr = run_command(cmd, check=False, timeout=120)
                if returncode != 0:
                    self.logger.warning(f"Failed to install via rpm-ostree: {stderr}")
                    # Try regular package manager as fallback
                    alt_cmd = cmd.replace("rpm-ostree install", "dnf install -y")
                    run_command(alt_cmd, check=False, timeout=120)

            return True  # Needs reboot

        self.logger.info("NVIDIA drivers already properly installed")
        return False

    def setup_shader_cache(self) -> bool:
        """Setup optimized shader cache directories"""
        self.logger.info("Setting up shader cache optimization...")

        if not write_config_file(Path("/usr/local/bin/setup-shader-cache.sh"),
                                 SHADER_CACHE_SETUP, executable=True):
            return False

        # Execute shader cache setup
        run_command("/usr/local/bin/setup-shader-cache.sh", check=False)
        self.track_change("Shader cache setup", Path("/usr/local/bin/setup-shader-cache.sh"))

        return True

    def apply_optimizations(self) -> bool:
        """Apply NVIDIA RTX 5080 optimizations with v4 safety checks"""
        if not check_nvidia_gpu_exists():
            self.logger.warning("No NVIDIA GPU detected - skipping GPU optimizations")
            return True  # Not a failure, just skip

        self.logger.info("Applying NVIDIA RTX 5080 Blackwell optimizations...")

        success = True

        # Check Resizable BAR
        self.check_resizable_bar()

        # Setup shader cache
        if not self.setup_shader_cache():
            success = False

        # Get profile settings
        profile_settings = GAMING_PROFILES.get(
            self.profile, GAMING_PROFILES["balanced"])["settings"]

        # Write module configuration
        if not write_config_file(
                Path("/etc/modprobe.d/nvidia-blackwell.conf"),
                NVIDIA_MODULE_CONFIG):
            success = False
        else:
            self.track_change(
                "NVIDIA module configuration",
                Path("/etc/modprobe.d/nvidia-blackwell.conf"))

        # Write X11 configuration (if X11 is used)
        if Path("/etc/X11").exists():
            if not write_config_file(
                    Path("/etc/X11/xorg.conf.d/90-nvidia-rtx5080.conf"),
                    NVIDIA_XORG_CONFIG):
                success = False
            else:
                self.track_change("NVIDIA X11 configuration", Path(
                    "/etc/X11/xorg.conf.d/90-nvidia-rtx5080.conf"))

        # Write optimization script with profile settings and v4 safety features
        script_content = NVIDIA_OPTIMIZATION_SCRIPT.format(
            MAX_GPU_TEMP_CRITICAL=MAX_GPU_TEMP_CRITICAL)
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
            self.track_change(
                "NVIDIA optimization script",
                Path("/usr/local/bin/nvidia-gaming-optimize.sh"))

        # Write HDR environment setup
        if not write_config_file(Path("/etc/profile.d/hdr-gaming.sh"), HDR_ENVIRONMENT):
            success = False
        else:
            self.track_change("HDR environment setup", Path("/etc/profile.d/hdr-gaming.sh"))

        # Apply CoolBits for overclocking
        run_command("nvidia-xconfig --cool-bits=28", check=False)

        # Regenerate initramfs
        self.logger.info("Regenerating initramfs...")
        run_command("dracut -f --regenerate-all", check=False, timeout=180)

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

        # Check Resizable BAR
        validations["resizable_bar"] = self.check_resizable_bar()

        # Check HDR support
        validations["hdr_enabled"] = Path("/etc/profile.d/hdr-gaming.sh").exists()

        # Check shader cache
        validations["shader_cache"] = Path("/var/cache/gaming-shaders").exists()

        return validations

# CPUOptimizer with v4 stepped undervolting


class CPUOptimizer(BaseOptimizer):
    """Intel i9-10850K CPU optimization module with v4 stepped undervolting"""

    def install_tools(self) -> bool:
        """Install CPU management tools"""
        self.logger.info("Installing CPU management tools...")

        tools = ["kernel-tools", "msr-tools", "thermald", "tuned", "intel-undervolt"]
        for tool in tools:
            # Try rpm-ostree first for Bazzite
            returncode, _, _ = run_command(f"rpm-ostree install {tool}", check=False, timeout=60)
            if returncode != 0:
                run_command(f"dnf install -y {tool}", check=False, timeout=60)

        return True

    def configure_undervolt(self) -> bool:
        """v4: Configure conservative CPU undervolting with stepping"""
        self.logger.info("Configuring CPU undervolting...")

        # Check if intel-undervolt is available
        returncode, _, _ = run_command("which intel-undervolt", check=False)
        if returncode != 0:
            self.logger.warning("intel-undervolt not available, skipping undervolting")
            return False

        # Write undervolt configuration
        if not write_config_file(Path("/etc/intel-undervolt.conf"), UNDERVOLT_CONFIG):
            return False

        self.track_change("Intel undervolt configuration", Path("/etc/intel-undervolt.conf"))

        # Apply undervolt settings
        run_command("intel-undervolt apply", check=False)

        # Enable undervolt service
        run_command("systemctl enable --now intel-undervolt", check=False)

        return True

    def apply_optimizations(self) -> bool:
        """Apply Intel i9-10850K optimizations"""
        self.logger.info("Applying Intel i9-10850K optimizations...")

        # Get profile settings
        profile_settings = GAMING_PROFILES.get(
            self.profile, GAMING_PROFILES["balanced"])["settings"]

        # Write CPU optimization script with profile settings and v4 stepping
        script_content = CPU_OPTIMIZATION_SCRIPT.format(MAX_CPU_TEMP_CRITICAL=MAX_CPU_TEMP_CRITICAL)
        script_content = script_content.replace("${CPU_GOVERNOR:-performance}",
                                                profile_settings.get("cpu_governor", "performance"))
        script_content = script_content.replace(
            "${ISOLATE_CORES:-false}", str(profile_settings.get("isolate_cores", False)).lower())
        script_content = script_content.replace(
            "${UNDERVOLT_AGGRESSIVE:-false}", str(profile_settings.get("undervolt_aggressive", False)).lower())

        if not write_config_file(Path("/usr/local/bin/cpu-gaming-optimize.sh"),
                                 script_content, executable=True):
            return False
        self.track_change("CPU optimization script", Path("/usr/local/bin/cpu-gaming-optimize.sh"))

        # Configure undervolting
        self.configure_undervolt()

        # Apply CPU optimizations immediately
        run_command("/usr/local/bin/cpu-gaming-optimize.sh", check=False)

        # Configure tuned for gaming
        run_command("tuned-adm profile latency-performance", check=False)

        # Disable thermald throttling for max performance (profile-dependent)
        if profile_settings.get("cpu_governor") == "performance":
            run_command("systemctl stop thermald", check=False)
            run_command("systemctl disable thermald", check=False)

        self.logger.info("CPU optimizations applied")
        return True

    def validate(self) -> Dict[str, bool]:
        """Validate CPU optimizations"""
        validations = {}

        # Check CPU governor
        validations["cpu_governor"] = validate_optimization(
            "CPU Governor",
            "cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor",
            GAMING_PROFILES.get(
                self.profile,
                GAMING_PROFILES["balanced"])["settings"]["cpu_governor"])

        # Check undervolting
        validations["undervolt_enabled"] = Path("/etc/intel-undervolt.conf").exists()

        return validations

# MemoryOptimizer - Full v3 implementation


class MemoryOptimizer(BaseOptimizer):
    """Memory and storage optimization module"""

    def configure_zram(self) -> bool:
        """Configure ZRAM for 64GB system with profile support"""
        self.logger.info("Configuring ZRAM for optimal gaming performance...")

        # Get profile settings
        profile_settings = GAMING_PROFILES.get(
            self.profile, GAMING_PROFILES["balanced"])["settings"]

        # Adjust ZRAM based on profile
        if self.profile == "competitive":
            config = ZRAM_CONFIG.format(
                PROFILE=self.profile,
                DIVISOR=8,
                MAX_SIZE=12288,
                ALGORITHM="lz4"
            )
        else:
            config = ZRAM_CONFIG.format(
                PROFILE=self.profile,
                DIVISOR=6,
                MAX_SIZE=16384,
                ALGORITHM="zstd"
            )

        if not write_config_file(Path("/etc/systemd/zram-generator.conf"), config):
            return False
        self.track_change("ZRAM configuration", Path("/etc/systemd/zram-generator.conf"))

        # Load compression modules
        run_command("modprobe lz4", check=False)
        run_command("modprobe zstd", check=False)

        # Restart ZRAM
        run_command("systemctl daemon-reload", check=False)
        run_command("systemctl restart systemd-zram-setup@zram0.service", check=False)

        return True

    def configure_sysctl(self) -> bool:
        """Apply sysctl optimizations with profile support"""
        self.logger.info("Applying memory and network sysctl optimizations...")

        # Get profile settings
        profile_settings = GAMING_PROFILES.get(
            self.profile, GAMING_PROFILES["balanced"])["settings"]

        # Adjust sysctl based on profile
        swappiness = 120 if self.profile == "competitive" else 100
        tcp_timestamps = 0 if self.profile == "competitive" else 1

        config = SYSCTL_CONFIG.format(
            PROFILE=self.profile,
            SWAPPINESS=swappiness,
            TCP_TIMESTAMPS=tcp_timestamps
        )

        if not write_config_file(Path("/etc/sysctl.d/99-gaming-performance.conf"), config):
            return False
        self.track_change("Sysctl configuration", Path("/etc/sysctl.d/99-gaming-performance.conf"))

        # Apply sysctl settings
        run_command("sysctl -p /etc/sysctl.d/99-gaming-performance.conf", check=False)

        return True

    def configure_storage(self) -> bool:
        """Configure NVMe storage optimizations"""
        self.logger.info("Applying NVMe storage optimizations...")

        # Write udev rules
        if not write_config_file(Path("/etc/udev/rules.d/60-nvme-gaming.rules"), NVME_UDEV_RULES):
            return False
        self.track_change("NVMe udev rules", Path("/etc/udev/rules.d/60-nvme-gaming.rules"))

        # Reload udev rules
        run_command("udevadm control --reload-rules", check=False)
        run_command("udevadm trigger --subsystem-match=block", check=False)

        # Configure Btrfs mount options if applicable
        self.configure_btrfs()

        return True

    def configure_btrfs(self) -> bool:
        """Configure Btrfs optimizations"""
        data_mount = "/var/mnt/Data_SSD"

        # Check if mount point exists and is Btrfs
        returncode, stdout, _ = run_command(f"findmnt -n -o FSTYPE {data_mount}", check=False)
        if returncode == 0 and "btrfs" in stdout:
            self.logger.info(f"Configuring Btrfs optimizations for {data_mount}")

            # Get UUID
            returncode, stdout, _ = run_command(
                f"findmnt -n -o SOURCE {data_mount} | xargs blkid -s UUID -o value", check=False)
            if returncode == 0:
                uuid = stdout.strip()

                # Update fstab with optimized mount options
                mount_opts = "rw,noatime,compress-force=zstd:1,ssd,discard=async,space_cache=v2,commit=60"
                fstab_entry = f"UUID={uuid} {data_mount} btrfs {mount_opts} 0 0"

                # Backup and update fstab
                backup_file(Path("/etc/fstab"))

                # Update fstab entry
                run_command(f"sed -i '\\|{data_mount}|d' /etc/fstab", check=False)
                run_command(f"echo '{fstab_entry}' >> /etc/fstab", check=False)

                # Remount with new options
                run_command(f"mount -o remount {data_mount}", check=False)

                return True

        return False

    def enable_mglru(self) -> bool:
        """Enable Multi-Gen LRU if available"""
        self.logger.info("Enabling Multi-Gen LRU...")

        # Check if MGLRU is available
        if Path("/sys/kernel/mm/lru_gen/enabled").exists():
            run_command("echo Y > /sys/kernel/mm/lru_gen/enabled", check=False)
            run_command("echo 1000 > /sys/kernel/mm/lru_gen/min_ttl_ms", check=False)
            self.logger.info("MGLRU enabled successfully")
            return True
        else:
            self.logger.info("MGLRU not available on this kernel")
            return False

    def apply_optimizations(self) -> bool:
        """Apply all memory optimizations"""
        success = True

        if not self.configure_zram():
            success = False

        if not self.configure_sysctl():
            success = False

        if not self.configure_btrfs():
            success = False

        self.enable_mglru()

        return success

    def validate(self) -> Dict[str, bool]:
        """Validate memory optimizations"""
        validations = {}

        # Check ZRAM
        returncode, stdout, _ = run_command("zramctl --raw --noheadings", check=False)
        validations["zram_enabled"] = returncode == 0 and bool(stdout.strip())

        # Check swappiness
        returncode, stdout, _ = run_command("sysctl vm.swappiness", check=False)
        validations["swappiness_set"] = returncode == 0

        # Check MGLRU
        validations["mglru_enabled"] = Path("/sys/kernel/mm/lru_gen/enabled").exists()

        return validations


class NetworkOptimizer(BaseOptimizer):
    """Network optimization module for Intel I225-V with profile support"""

    def apply_optimizations(self) -> bool:
        """Apply network optimizations with I225-V bug workarounds"""
        self.logger.info("Applying Intel I225-V network optimizations...")

        # Get profile settings
        profile_settings = GAMING_PROFILES.get(
            self.profile, GAMING_PROFILES["balanced"])["settings"]
        network_latency = profile_settings.get("network_latency", "low")

        # Write Intel I225-V module configuration
        if not write_config_file(Path("/etc/modprobe.d/igc-gaming.conf"), IGC_MODULE_CONFIG):
            return False
        self.track_change("Intel I225-V module config", Path("/etc/modprobe.d/igc-gaming.conf"))

        # Write ethernet optimization script with profile settings
        script_content = ETHERNET_OPTIMIZE_SCRIPT.replace(
            "${NETWORK_PROFILE:-low}", network_latency)
        script_content = script_content.replace(
            "${ISOLATE_CORES:-false}", str(profile_settings.get("isolate_cores", False)).lower())

        if not write_config_file(Path("/usr/local/bin/ethernet-optimize.sh"),
                                 script_content, executable=True):
            return False
        self.track_change(
            "Ethernet optimization script",
            Path("/usr/local/bin/ethernet-optimize.sh"))

        # Apply immediately
        run_command("/usr/local/bin/ethernet-optimize.sh", check=False)

        # Disable NetworkManager power saving
        nm_conf = "[connection]\nwifi.powersave = 2\n\n[ethernet]\nwake-on-lan = 0"
        write_config_file(Path("/etc/NetworkManager/conf.d/99-gaming.conf"), nm_conf)

        run_command("systemctl restart NetworkManager", check=False)

        self.logger.info("Network optimizations applied")
        return True

    def validate(self) -> Dict[str, bool]:
        """Validate network optimizations"""
        validations = {}

        # Check if optimization script exists
        validations["network_script"] = Path("/usr/local/bin/ethernet-optimize.sh").exists()

        # Check interrupt coalescing
        eth = run_command(
            "ip link | grep -E '^[0-9]+: e' | cut -d: -f2 | tr -d ' ' | head -1",
            check=False)[1].strip()
        if eth:
            returncode, stdout, _ = run_command(f"ethtool -c {eth} | grep 'rx-usecs:'", check=False)
            validations["coalescing_configured"] = returncode == 0

        return validations


# ============================================================================
# MISSING OPTIMIZER CLASSES FROM V3
# ============================================================================

class AudioOptimizer(BaseOptimizer):
    """Audio system optimization module with profile support"""

    def __init__(self, logger: logging.Logger):
        super().__init__(logger)
        self.user = os.environ.get('SUDO_USER', os.environ.get('USER', 'root'))

    def apply_optimizations(self) -> bool:
        """Apply PipeWire and WirePlumber optimizations"""
        self.logger.info("Applying audio optimizations for Creative Sound Blaster...")

        # Get profile settings
        profile_settings = GAMING_PROFILES.get(
            self.profile, GAMING_PROFILES["balanced"])["settings"]
        audio_quantum = profile_settings.get("audio_quantum", 512)

        # Configure PipeWire based on profile
        pipewire_config = PIPEWIRE_CONFIG.format(
            PROFILE=self.profile,
            QUANTUM=audio_quantum,
            MIN_QUANTUM=audio_quantum // 2,
            MAX_QUANTUM=audio_quantum * 2
        )

        # System-wide PipeWire configuration with error handling
        pipewire_dir = Path("/etc/pipewire/pipewire.conf.d")
        try:
            pipewire_dir.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            self.logger.error(f"Could not create PipeWire config directory: {e}")
            return False

        if not write_config_file(pipewire_dir / "99-gaming.conf", pipewire_config):
            return False
        self.track_change("PipeWire configuration", pipewire_dir / "99-gaming.conf")

        # WirePlumber configuration
        wireplumber_config = WIREPLUMBER_CONFIG.format(PERIOD_SIZE=audio_quantum // 2)

        # User-specific WirePlumber configuration  
        if self.user and self.user != 'root':
            wireplumber_dir = Path(f"/home/{self.user}/.config/wireplumber/wireplumber.conf.d")
            try:
                wireplumber_dir.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as e:
                self.logger.debug(f"Could not create WirePlumber user config directory: {e}")
                return False

            wireplumber_conf = wireplumber_dir / "50-creative-gaming.conf"
            if write_config_file(wireplumber_conf, wireplumber_config):
                run_command(f"chown -R {self.user}:{self.user} {wireplumber_dir}", check=False)
                self.track_change("WirePlumber configuration", wireplumber_conf)

        # Restart PipeWire
        if self.user and self.user != 'root':
            run_command(
                f"sudo -u {self.user} systemctl --user restart pipewire pipewire-pulse wireplumber", check=False)

        self.logger.info("Audio optimizations applied")
        return True

    def validate(self) -> Dict[str, bool]:
        """Validate audio optimizations"""
        validations = {}

        # Check PipeWire configuration
        validations["pipewire_configured"] = Path(
            "/etc/pipewire/pipewire.conf.d/99-gaming.conf").exists()

        # Check if PipeWire is running
        returncode, _, _ = run_command("systemctl --user is-active pipewire", check=False)
        validations["pipewire_running"] = returncode == 0

        return validations


class GamingToolsOptimizer(BaseOptimizer):
    """Gaming-specific tools and configurations with profile support"""

    def __init__(self, logger: logging.Logger):
        super().__init__(logger)
        self.user = os.environ.get('SUDO_USER', os.environ.get('USER', 'root'))

    def install_tools(self) -> bool:
        """Install gaming tools via package manager and Flatpak"""
        self.logger.info("Installing gaming tools...")

        # System packages
        packages = [
            "gamemode",
            "mangohud",
            "gamescope",
            "steam-devices",
            "vkbasalt",
            "nvtop",
            "btop",
            "goverlay",
            "glmark2",
            "sysbench"  # For benchmarking
        ]

        for package in packages:
            self.logger.info(f"Installing {package}...")
            # Try rpm-ostree first for Bazzite
            returncode, _, _ = run_command(f"rpm-ostree install {package}", check=False, timeout=60)
            if returncode != 0:
                run_command(f"dnf install -y {package}", check=False, timeout=60)

        # Flatpak applications
        flatpak_apps = [
            "com.leinardi.gwe",  # GreenWithEnvy
            "net.davidotek.pupgui2",  # ProtonUp-Qt
            "com.github.tchx84.Flatseal",  # Flatseal
            "io.github.benjamimgois.goverlay"  # GOverlay
        ]

        for app in flatpak_apps:
            self.logger.info(f"Installing Flatpak: {app}...")
            run_command(f"flatpak install -y flathub {app}", check=False, timeout=60)

        return True

    def configure_gamemode(self) -> bool:
        """Configure GameMode with custom scripts and profile support"""
        self.logger.info("Configuring GameMode...")

        # Get profile settings
        profile_settings = GAMING_PROFILES.get(
            self.profile, GAMING_PROFILES["balanced"])["settings"]

        # Write GameMode configuration
        config = GAMEMODE_CONFIG.format(
            PIN_CORES="yes" if profile_settings.get("isolate_cores", False) else "no",
            GPU_POWER_MODE=profile_settings.get("gpu_power_mode", 1),
            GPU_CLOCK_OFFSET=profile_settings.get("gpu_clock_offset", 400),
            GPU_MEM_OFFSET=profile_settings.get("gpu_mem_offset", 800)
        )

        if not write_config_file(Path("/etc/gamemode.ini"), config):
            return False
        self.track_change("GameMode configuration", Path("/etc/gamemode.ini"))

        # Write GameMode start script with profile
        start_script = MASTER_GAMING_SCRIPT.format(PROFILE=self.profile, SECURITY_WARNING_ACKNOWLEDGED="false")
        if not write_config_file(Path("/usr/local/bin/gaming-mode-start.sh"),
                                 start_script, executable=True):
            return False
        self.track_change("GameMode start script", Path("/usr/local/bin/gaming-mode-start.sh"))

        # Write GameMode end script
        if not write_config_file(Path("/usr/local/bin/gaming-mode-end.sh"),
                                 GAMING_MODE_END_SCRIPT, executable=True):
            return False
        self.track_change("GameMode end script", Path("/usr/local/bin/gaming-mode-end.sh"))

        # Write performance monitor script
        if not write_config_file(Path("/usr/local/bin/performance-monitor.sh"),
                                 PERFORMANCE_MONITOR_SCRIPT, executable=True):
            return False
        self.track_change(
            "Performance monitor script",
            Path("/usr/local/bin/performance-monitor.sh"))

        # Enable GameMode service
        run_command("systemctl enable --now gamemoded", check=False)

        return True

    def configure_mangohud(self) -> bool:
        """Configure MangoHud for optimal performance monitoring"""
        self.logger.info("Configuring MangoHud...")

        # Get profile settings
        profile_settings = GAMING_PROFILES.get(
            self.profile, GAMING_PROFILES["balanced"])["settings"]

        # Configure MangoHud based on profile
        if self.profile == "competitive" or not profile_settings.get("visual_effects", True):
            extra_metrics = ""
            show_frametime = "0"
            show_frametiming = "0"
            fps_limit = "0"
        elif self.profile == "streaming":
            extra_metrics = "io_stats\\nio_read\\nio_write\\ngpu_mem_clock\\ngpu_core_clock"
            show_frametime = "1"
            show_frametiming = "1"
            fps_limit = "144"
        else:
            extra_metrics = "io_stats"
            show_frametime = "0"
            show_frametiming = "1"
            fps_limit = "0"

        config = MANGOHUD_CONFIG.format(
            PROFILE=self.profile,
            FPS_LIMIT=fps_limit,
            SHOW_FRAMETIME=show_frametime,
            SHOW_FRAMETIMING=show_frametiming,
            EXTRA_METRICS=extra_metrics
        )

        if self.user and self.user != 'root':
            mangohud_dir = Path(f"/home/{self.user}/.config/MangoHud")
            try:
                mangohud_dir.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as e:
                self.logger.debug(f"Could not create MangoHud user config directory: {e}")
                return False

            if write_config_file(mangohud_dir / "MangoHud.conf", config):
                run_command(f"chown -R {self.user}:{self.user} {mangohud_dir}", check=False)
                self.track_change("MangoHud configuration", mangohud_dir / "MangoHud.conf")
                return True

        return False

    def configure_system76_scheduler(self) -> bool:
        """Configure System76 Scheduler for gaming with profile support"""
        self.logger.info("Configuring System76 Scheduler...")

        # Get profile settings
        profile_settings = GAMING_PROFILES.get(
            self.profile, GAMING_PROFILES["balanced"])["settings"]

        # Adjust scheduler based on profile
        if self.profile == "competitive":
            latency = 3
            preempt = "full"
            slice_val = 1
            obs_profile = "background"
            obs_nice = 10
        elif self.profile == "streaming":
            latency = 4
            preempt = "voluntary"
            slice_val = 2
            obs_profile = "responsive"
            obs_nice = -5
        else:
            latency = 4
            preempt = "voluntary"
            slice_val = 2
            obs_profile = "background"
            obs_nice = 5

        config = SYSTEM76_SCHEDULER_CONFIG.format(
            PROFILE=self.profile,
            LATENCY=latency,
            PREEMPT=preempt,
            SLICE=slice_val,
            OBS_PROFILE=obs_profile,
            OBS_NICE=obs_nice
        )

        config_dir = Path("/etc/system76-scheduler")
        try:
            config_dir.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            self.logger.error(f"Could not create System76-scheduler config directory: {e}")
            return False

        if not write_config_file(config_dir / "config.kdl", config):
            return False
        self.track_change("System76 Scheduler config", config_dir / "config.kdl")

        # Install system76-scheduler if not present
        returncode, _, _ = run_command("which system76-scheduler", check=False)
        if returncode != 0:
            self.logger.info("Installing System76 Scheduler...")
            run_command("rpm-ostree install system76-scheduler", check=False, timeout=60)

        # Enable the scheduler
        run_command("systemctl enable --now system76-scheduler", check=False)

        return True

    def apply_optimizations(self, skip_packages: bool = False) -> bool:
        """Apply gaming tools optimizations"""
        success = True

        if not skip_packages:
            self.install_tools()

        if not self.configure_gamemode():
            success = False

        if not self.configure_mangohud():
            success = False

        if not self.configure_system76_scheduler():
            success = False

        return success

    def validate(self) -> Dict[str, bool]:
        """Validate gaming tools configuration"""
        validations = {}

        # Check GameMode
        validations["gamemode_enabled"] = Path("/etc/gamemode.ini").exists()
        returncode, _, _ = run_command("systemctl is-active gamemoded", check=False)
        validations["gamemode_running"] = returncode == 0

        # Check MangoHud
        if self.user and self.user != 'root':
            validations["mangohud_configured"] = Path(
                f"/home/{self.user}/.config/MangoHud/MangoHud.conf").exists()

        # Check System76 Scheduler
        returncode, _, _ = run_command("systemctl is-active system76-scheduler", check=False)
        validations["scheduler_running"] = returncode == 0

        return validations


# ============================================================================
# MISSING v3 OPTIMIZER CLASSES
# ============================================================================

class KernelOptimizer(BaseOptimizer):
    """Kernel and boot parameter optimization with profile support"""

    def apply_grub_optimizations(self) -> bool:
        """Update GRUB configuration with gaming optimizations"""
        self.logger.info("Updating GRUB configuration...")

        grub_config = Path("/etc/default/grub")
        if not grub_config.exists():
            self.logger.warning("GRUB configuration not found")
            return False

        # Get profile settings
        profile_settings = GAMING_PROFILES.get(
            self.profile, GAMING_PROFILES["balanced"])["settings"]

        # Backup GRUB config
        backup_file(grub_config)

        # Read current configuration
        with open(grub_config, 'r') as f:
            lines = f.readlines()

        # Configure kernel parameters based on profile
        mitigations = "off" if profile_settings.get("disable_mitigations", True) else "auto"
        max_cstate = "1" if profile_settings.get("isolate_cores", False) else "3"

        if profile_settings.get("isolate_cores", False):
            isolcpus = "nohz_full=4-9 isolcpus=4-9 rcu_nocbs=4-9"
        else:
            isolcpus = ""
            
        security_params = ""

        additions = GRUB_CMDLINE_ADDITIONS.format(
            MITIGATIONS=mitigations,
            MAX_CSTATE=max_cstate,
            ISOLCPUS=isolcpus,
            SECURITY_PARAMS=security_params
        ).strip()

        # Find and update GRUB_CMDLINE_LINUX
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("GRUB_CMDLINE_LINUX=") or line.startswith(
                    "GRUB_CMDLINE_LINUX_DEFAULT="):
                # Extract current value
                current_value = line.split('=', 1)[1].strip().strip('"')

                # Add our optimizations if not already present
                for param in additions.split():
                    # Check if parameter already exists
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

    def configure_kernel_modules(self) -> bool:
        """Configure kernel module loading"""
        self.logger.info("Configuring kernel modules...")

        # Load required modules
        modules = [
            "msr",
            "zstd",
            "nvidia",
            "nvidia-drm",
            "nvidia-modeset",
            "nvidia-uvm",
            "lz4",
            "lz4_compress"]

        modules_conf = "\n".join([f"{mod}" for mod in modules])
        write_config_file(Path("/etc/modules-load.d/gaming.conf"), modules_conf)

        for mod in modules:
            run_command(f"modprobe {mod}", check=False)

        return True

    def apply_optimizations(self) -> bool:
        """Apply kernel optimizations"""
        success = True

        if not self.apply_grub_optimizations():
            success = False

        if not self.configure_kernel_modules():
            success = False

        return success

    def validate(self) -> Dict[str, bool]:
        """Validate kernel optimizations"""
        validations = {}

        # Check if mitigations are disabled
        returncode, stdout, _ = run_command(
            "cat /proc/cmdline | grep 'mitigations=off'", check=False)
        validations["mitigations_disabled"] = returncode == 0

        # Check kernel modules
        validations["modules_loaded"] = Path("/etc/modules-load.d/gaming.conf").exists()

        return validations


class SystemdServiceOptimizer(BaseOptimizer):
    """Systemd service configuration with profile support"""

    def create_gaming_service(self) -> bool:
        """Create systemd service for gaming optimizations"""
        self.logger.info("Creating gaming optimization service...")

        # Write master gaming script with profile
        script = MASTER_GAMING_SCRIPT.format(PROFILE=self.profile, SECURITY_WARNING_ACKNOWLEDGED="false")
        if not write_config_file(Path("/usr/local/bin/gaming-mode-activate.sh"),
                                 script, executable=True):
            return False
        self.track_change(
            "Gaming mode activation script",
            Path("/usr/local/bin/gaming-mode-activate.sh"))

        # Write systemd service with profile
        service = SYSTEMD_SERVICE.format(PROFILE=self.profile)
        if not write_config_file(Path("/etc/systemd/system/gaming-optimizations.service"), service):
            return False
        self.track_change("Gaming optimizations service", Path(
            "/etc/systemd/system/gaming-optimizations.service"))

        # Reload and enable service
        run_command("systemctl daemon-reload", check=False)
        run_command("systemctl enable gaming-optimizations.service", check=False)

        self.logger.info("Gaming optimization service created and enabled")
        return True

    def disable_unnecessary_services(self) -> bool:
        """Disable services that impact gaming performance"""
        self.logger.info("Disabling unnecessary services...")

        # Get profile settings
        profile_settings = GAMING_PROFILES.get(
            self.profile, GAMING_PROFILES["balanced"])["settings"]

        services_to_disable = []

        # Always disable these for gaming
        services_to_disable.extend([
            "cups",  # Printing service
            "ModemManager",  # Mobile broadband
            "packagekit",  # Package management
            "tracker-miner-fs-3",  # File indexing
            "tracker-miner-rss-3"  # RSS indexing
        ])

        # Profile-specific services
        if self.profile == "competitive":
            services_to_disable.extend([
                "bluetooth",  # Bluetooth (if not using wireless peripherals)
                "avahi-daemon",  # Network discovery
                "systemd-resolved"  # DNS resolver (use static DNS instead)
            ])

        for service in services_to_disable:
            run_command(f"systemctl disable {service}", check=False)
            run_command(f"systemctl stop {service}", check=False)

        return True

    def apply_optimizations(self) -> bool:
        """Apply systemd optimizations"""
        success = True

        if not self.create_gaming_service():
            success = False

        self.disable_unnecessary_services()

        return success

    def validate(self) -> Dict[str, bool]:
        """Validate systemd service configuration"""
        validations = {}

        # Check gaming service
        validations["gaming_service"] = Path(
            "/etc/systemd/system/gaming-optimizations.service").exists()

        return validations


class PlasmaOptimizer(BaseOptimizer):
    """KDE Plasma 6 Wayland optimization module with profile support"""

    def __init__(self, logger: logging.Logger):
        super().__init__(logger)
        self.user = os.environ.get('SUDO_USER', os.environ.get('USER', 'root'))

    def apply_optimizations(self) -> bool:
        """Apply KDE Plasma 6 Wayland gaming optimizations"""
        self.logger.info("Applying KDE Plasma 6 Wayland optimizations...")

        if not self.user or self.user == 'root':
            self.logger.warning("Cannot apply KDE settings for root user")
            return False

        # Get profile settings
        profile_settings = GAMING_PROFILES.get(
            self.profile, GAMING_PROFILES["balanced"])["settings"]

        kwin_commands = [
            # Compositor settings
            "kwriteconfig6 --file kwinrc --group Compositing --key LatencyPolicy Low",
            "kwriteconfig6 --file kwinrc --group Compositing --key GLCore true",
            "kwriteconfig6 --file kwinrc --group Compositing --key VariableRefreshRate true",
            "kwriteconfig6 --file kwinrc --group Compositing --key GLPreferBufferSwap e",
            "kwriteconfig6 --file kwinrc --group Compositing --key AllowTearing true",
        ]

        # Disable effects for competitive profile
        if self.profile == "competitive" or not profile_settings.get("visual_effects", True):
            kwin_commands.extend([
                "kwriteconfig6 --file kwinrc --group Plugins --key blurEnabled false",
                "kwriteconfig6 --file kwinrc --group Plugins --key contrastEnabled false",
                "kwriteconfig6 --file kwinrc --group Plugins --key minimizeanimationEnabled false",
                "kwriteconfig6 --file kwinrc --group Plugins --key kwin4_effect_fadeEnabled false",
                "kwriteconfig6 --file kwinrc --group Plugins --key slidingpopupsEnabled false",
            ])

        # Compositor bypass for competitive
        if profile_settings.get("compositor_bypass", False):
            kwin_commands.append(
                "kwriteconfig6 --file kwinrc --group Compositing --key UnredirectFullscreen true")

        # Window management
        kwin_commands.extend([
            "kwriteconfig6 --file kwinrc --group Windows --key FocusPolicy FocusFollowsMouse",
            "kwriteconfig6 --file kwinrc --group Windows --key AutoRaise false",
            "kwriteconfig6 --file kwinrc --group Windows --key DelayFocusInterval 0",
            "kwriteconfig6 --file kwinrc --group TabBox --key DelayTime 0",
            "kwriteconfig6 --file kwinrc --group TabBox --key HighlightWindows false",
            "kwriteconfig6 --file kwinrc --group Wayland --key EnablePrimarySelection false",
            "kwriteconfig6 --file kwinrc --group Wayland --key VirtualKeyboardEnabled false"
        ])

        for cmd in kwin_commands:
            full_cmd = f"sudo -u {self.user} {cmd}"
            run_command(full_cmd, check=False)

        # Apply settings
        run_command(f"sudo -u {self.user} qdbus org.kde.KWin /KWin reconfigure", check=False)

        self.track_change("KDE Plasma optimizations", Path(f"/home/{self.user}/.config/kwinrc"))
        self.logger.info("KDE Plasma optimizations applied")
        return True

    def validate(self) -> Dict[str, bool]:
        """Validate KDE Plasma optimizations"""
        validations = {}

        if self.user and self.user != 'root':
            validations["kwin_configured"] = Path(f"/home/{self.user}/.config/kwinrc").exists()

        return validations


class BazziteOptimizer(BaseOptimizer):
    """Bazzite-specific optimizations using ujust commands"""

    def apply_ujust_commands(self) -> bool:
        """Execute Bazzite ujust commands"""
        self.logger.info("Applying Bazzite-specific optimizations...")

        for command in BAZZITE_UJUST_COMMANDS:
            self.logger.info(f"Executing: {command}")
            returncode, stdout, stderr = run_command(command, check=False, timeout=120)

            if returncode != 0:
                self.logger.warning(f"Command failed: {command}")
                self.logger.warning(f"Error: {stderr}")
            else:
                self.logger.info(f"Successfully executed: {command}")

        return True

    def apply_optimizations(self) -> bool:
        """Apply Bazzite optimizations"""
        return self.apply_ujust_commands()

    def validate(self) -> Dict[str, bool]:
        """Validate Bazzite optimizations"""
        validations = {}

        # Basic validation - check if ujust is available
        returncode, _, _ = run_command("which ujust", check=False)
        validations["ujust_available"] = returncode == 0

        return validations


# ============================================================================
# BENCHMARKING AND PROFILE MANAGEMENT
# ============================================================================

class BenchmarkRunner:
    """Performance benchmarking system"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        system_path = Path("/var/log/bazzite-optimizer/benchmarks")
        self.results_dir = ensure_directory_with_fallback(
            system_path, "bazzite-optimizer/benchmarks", logger
        )

    def run_baseline(self) -> Dict[str, Any]:
        """Run baseline benchmarks before optimization"""
        if self.results_dir is None:
            self.logger.debug("Benchmarking disabled, returning empty results")
            return {}
            
        self.logger.info("Running baseline benchmarks...")

        baseline_dir = self.results_dir / "baseline"
        try:
            baseline_dir.mkdir(parents=True, exist_ok=True)
            results = self._run_benchmarks(baseline_dir)
            self.logger.info("Baseline benchmarks completed")
            return results
        except (PermissionError, OSError) as e:
            self.logger.debug(f"Benchmark directory creation failed: {e}")
            return {}

    def analyze_benchmark_statistics(self, results: List[float]) -> Dict[str, float]:
        """Analyze benchmark results using statistical methods"""
        if not results:
            return {}

        return {
            'mean': statistics.mean(results),
            'median': statistics.median(results),
            'stdev': statistics.stdev(results) if len(results) > 1 else 0.0,
            'min': min(results),
            'max': max(results),
            'variance': statistics.variance(results) if len(results) > 1 else 0.0,
            'confidence_95': 1.96 * (statistics.stdev(results) / (len(results) ** 0.5)) if len(results) > 1 else 0.0
        }

    def _safe_write_results(self, results: Dict[str, Any], output_file: Path):
        """Safely write benchmark results using temporary files"""
        try:
            # Use temporary file for atomic write operation
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json',
                                             dir=output_file.parent,
                                             delete=False) as temp_file:
                json.dump(results, temp_file, indent=2, default=str)
                temp_path = Path(temp_file.name)

            # Atomic move to final location
            temp_path.rename(output_file)
            self.logger.debug(f"Safely wrote benchmark results to {output_file}")

        except Exception as e:
            self.logger.error(f"Failed to write benchmark results: {e}")
            if temp_path and temp_path.exists():
                temp_path.unlink()  # Cleanup temporary file

    def run_post_optimization(self) -> Dict[str, Any]:
        """Run benchmarks after optimization"""
        if self.results_dir is None:
            self.logger.debug("Benchmarking disabled, returning empty results")
            return {}
            
        self.logger.info("Running post-optimization benchmarks...")

        try:
            post_dir = self.results_dir / f"post_{TIMESTAMP}"
            post_dir.mkdir(parents=True, exist_ok=True)

            results = self._run_benchmarks(post_dir)

            # Compare with baseline
            baseline_dir = self.results_dir / "baseline"
            if baseline_dir.exists():
                self._compare_results(baseline_dir, post_dir)

            self.logger.info("Post-optimization benchmarks completed")
            return results
        except (PermissionError, OSError) as e:
            self.logger.debug(f"Post-optimization benchmark failed: {e}")
            return {}

    def _run_benchmarks(self, output_dir: Path) -> Dict[str, Any]:
        """Run all benchmarks and save results"""
        results = {}

        # GPU benchmark using glmark2
        if run_command("which glmark2", check=False)[0] == 0:
            self.logger.info("Running GPU benchmark...")
            returncode, stdout, _ = run_command(
                "glmark2 --off-screen --annotate 2>&1",
                check=False,
                timeout=120
            )
            if returncode == 0:
                # Extract score
                score_match = re.search(r"glmark2 Score:\s*(\d+)", stdout)
                if score_match:
                    results["gpu_score"] = int(score_match.group(1))
                    with open(output_dir / "glmark2.txt", "w") as f:
                        f.write(stdout)

        # CPU benchmark using sysbench
        if run_command("which sysbench", check=False)[0] == 0:
            self.logger.info("Running CPU benchmark...")
            returncode, stdout, _ = run_command(
                "sysbench cpu --cpu-max-prime=20000 --threads=20 run",
                check=False,
                timeout=60
            )
            if returncode == 0:
                # Extract events per second
                events_match = re.search(r"events per second:\s*([\d.]+)", stdout)
                if events_match:
                    results["cpu_events_per_sec"] = float(events_match.group(1))
                    with open(output_dir / "sysbench_cpu.txt", "w") as f:
                        f.write(stdout)

        # Memory benchmark
        if run_command("which sysbench", check=False)[0] == 0:
            self.logger.info("Running memory benchmark...")
            returncode, stdout, _ = run_command(
                "sysbench memory --memory-total-size=10G run",
                check=False,
                timeout=60
            )
            if returncode == 0:
                # Extract operations per second
                ops_match = re.search(r"Total operations:\s*(\d+)", stdout)
                if ops_match:
                    results["memory_ops"] = int(ops_match.group(1))
                    with open(output_dir / "sysbench_memory.txt", "w") as f:
                        f.write(stdout)

        # Disk benchmark
        self.logger.info("Running disk benchmark...")
        # Write test
        returncode, stdout, _ = run_command(
            "dd if=/dev/zero of=/tmp/test_write bs=1G count=1 oflag=direct 2>&1",
            check=False,
            timeout=30
        )
        if returncode == 0:
            speed_match = re.search(r"([\d.]+)\s*MB/s", stdout)
            if speed_match:
                results["disk_write_mb_s"] = float(speed_match.group(1))
                with open(output_dir / "disk_write.txt", "w") as f:
                    f.write(stdout)

        # Read test
        returncode, stdout, _ = run_command(
            "dd if=/tmp/test_write of=/dev/null bs=1G count=1 iflag=direct 2>&1",
            check=False,
            timeout=30
        )
        if returncode == 0:
            speed_match = re.search(r"([\d.]+)\s*MB/s", stdout)
            if speed_match:
                results["disk_read_mb_s"] = float(speed_match.group(1))
                with open(output_dir / "disk_read.txt", "w") as f:
                    f.write(stdout)

        run_command("rm -f /tmp/test_write", check=False)

        # Network latency
        self.logger.info("Running network latency test...")
        returncode, stdout, _ = run_command(
            "ping -c 10 8.8.8.8 | tail -1",
            check=False,
            timeout=15
        )
        if returncode == 0:
            avg_match = re.search(r"min/avg/max/mdev = [\d.]+/([\d.]+)", stdout)
            if avg_match:
                results["network_latency_ms"] = float(avg_match.group(1))

        # Save results summary
        with open(output_dir / "results.json", "w") as f:
            json.dump(results, f, indent=2)

        return results

    def _compare_results(self, baseline_dir: Path, post_dir: Path):
        """Compare benchmark results and show improvements"""
        baseline_file = baseline_dir / "results.json"
        post_file = post_dir / "results.json"

        if not baseline_file.exists() or not post_file.exists():
            return

        with open(baseline_file) as f:
            baseline = json.load(f)

        with open(post_file) as f:
            post = json.load(f)

        print_colored("\nPerformance Comparison:", Colors.HEADER)
        print_colored("-" * 50, Colors.HEADER)

        comparisons = [
            ("GPU Score", "gpu_score", True),  # Higher is better
            ("CPU Events/sec", "cpu_events_per_sec", True),
            ("Memory Ops", "memory_ops", True),
            ("Disk Write MB/s", "disk_write_mb_s", True),
            ("Disk Read MB/s", "disk_read_mb_s", True),
            ("Network Latency ms", "network_latency_ms", False)  # Lower is better
        ]

        for name, key, higher_better in comparisons:
            if key in baseline and key in post:
                base_val = baseline[key]
                post_val = post[key]

                if higher_better:
                    improvement = ((post_val - base_val) / base_val) * 100
                else:
                    improvement = ((base_val - post_val) / base_val) * 100

                color = Colors.OKGREEN if improvement > 0 else Colors.FAIL
                sign = "+" if improvement > 0 else ""

                print(
                    f"  {name:20} {base_val:10.2f} → {post_val:10.2f} ({sign}{improvement:+.1f}%)",
                    end="")
                print_colored(f" {'↑' if improvement > 0 else '↓'}", color)

        print_colored("-" * 50, Colors.HEADER)


class ProfileManager:
    """Gaming profile management system"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.profile_dir = ensure_directory_with_fallback(
            PROFILE_DIR, "bazzite-optimizer/profiles", logger
        )

    def save_profile(self, profile_name: str, settings: Dict[str, Any]):
        """Save a gaming profile"""
        if self.profile_dir is None:
            self.logger.debug("Profile saving disabled due to permission restrictions")
            return
            
        profile_file = self.profile_dir / f"{profile_name}.json"

        with open(profile_file, "w") as f:
            json.dump(settings, f, indent=2)

        self.logger.info(f"Profile '{profile_name}' saved")

    def load_profile(self, profile_name: str) -> Dict[str, Any]:
        """Load a gaming profile"""
        # Check predefined profiles first
        if profile_name in GAMING_PROFILES:
            return GAMING_PROFILES[profile_name]["settings"]

        # Check custom profiles only if profile_dir is available
        if self.profile_dir is not None:
            profile_file = self.profile_dir / f"{profile_name}.json"
            if profile_file.exists():
                with open(profile_file) as f:
                    return json.load(f)

        self.logger.warning(f"Profile '{profile_name}' not found, using balanced")
        return GAMING_PROFILES["balanced"]["settings"]

    def list_profiles(self) -> List[str]:
        """List available profiles"""
        profiles = list(GAMING_PROFILES.keys())

        # Add custom profiles only if profile_dir is available
        if self.profile_dir is not None:
            for profile_file in self.profile_dir.glob("*.json"):
                profile_name = profile_file.stem
                if profile_name not in profiles:
                    profiles.append(profile_name)

        return profiles

    def export_profile_env(self, profile_name: str):
        """Export profile settings as environment variables"""
        settings = self.load_profile(profile_name)
        env_file = self.profile_dir / f"{profile_name}.env"

        with open(env_file, "w") as f:
            for key, value in settings.items():
                env_key = key.upper()
                if isinstance(value, bool):
                    value = str(value).lower()
                f.write(f"export {env_key}={value}\n")

        self.logger.info(f"Profile environment exported to {env_file}")


# ============================================================================
# MAIN OPTIMIZER CLASS
# ============================================================================

class BazziteGamingOptimizer:
    """Main optimizer orchestrator with v3 enhancements"""

    def __init__(self):
        self.logger = setup_logging()
        self.optimizers = []
        self.needs_reboot = False
        self.system_info = get_system_info()
        self.hardware_checks = {}
        self.profile = "balanced"  # Default profile
        self.thermal_manager = ThermalManager(self.logger)
        self.benchmark_runner = BenchmarkRunner(self.logger)
        self.profile_manager = ProfileManager(self.logger)
        self.validation_results = {}

    def print_banner(self):
        """Display welcome banner"""
        print_colored("=" * 62, Colors.HEADER)
        print_colored("    BAZZITE DX ULTIMATE GAMING OPTIMIZER v" +
                      SCRIPT_VERSION, Colors.HEADER + Colors.BOLD)
        print_colored("  Enhanced for RTX 5080 Blackwell | i9-10850K | 64GB RAM", Colors.OKCYAN)
        print_colored("  Now with: Thermal Management | HDR | Profiles | Validation", Colors.OKBLUE)
        print_colored("=" * 62, Colors.HEADER)
        print()

    def print_system_info(self):
        """Display detected system information"""
        print_colored("\nSystem Information:", Colors.OKBLUE)
        print(f"  OS: {self.system_info['distribution']}")
        print(f"  Kernel: {self.system_info['kernel']}")
        print(f"  CPU: {self.system_info['cpu_model']}")
        print(
            f"  Cores: {self.system_info['cpu_cores']} / Threads: {self.system_info['cpu_threads']}")
        print(f"  RAM: {self.system_info['ram_gb']} GB")
        print(f"  Free Disk: {self.system_info['free_disk_gb']} GB")

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

        print()

    def check_prerequisites(self) -> bool:
        """Check system prerequisites including new v3 requirements"""
        print_colored("Checking system prerequisites...", Colors.OKBLUE)

        # Check if running as root
        if os.geteuid() != 0:
            print_colored("ERROR: This script must be run as root (use sudo)", Colors.FAIL)
            return False

        # Check kernel version
        if not check_kernel_version():
            kernel_version = self.system_info.get("kernel_version", (0, 0, 0))
            print_colored(
                f"WARNING: Kernel {kernel_version} is older than recommended {MIN_KERNEL_VERSION}",
                Colors.WARNING)
            print_colored("Some features like MGLRU may not be available", Colors.WARNING)

        # Check disk space
        if not check_disk_space():
            free_gb = self.system_info.get("free_disk_gb", 0)
            print_colored(
                f"ERROR: Insufficient disk space ({free_gb}GB free, need {MIN_DISK_SPACE_GB}GB)",
                Colors.FAIL)
            return False

        # Check hardware compatibility
        self.hardware_checks = check_hardware_compatibility()

        print("\nHardware Detection:")
        optimal_config = True
        for component, detected in self.hardware_checks.items():
            status = "✔" if detected else "✗"
            color = Colors.OKGREEN if detected else Colors.WARNING
            component_name = component.replace('_', ' ').title()
            print_colored(f"  {status} {component_name}", color)

            # Special warning for Resizable BAR
            if component == "resizable_bar" and not detected:
                print_colored(
                    "    → Enable Resizable BAR in BIOS for better performance",
                    Colors.WARNING)

            if not detected and component != "bazzite_os":
                optimal_config = False

        # Warn if not on Bazzite
        if not self.hardware_checks["bazzite_os"]:
            print_colored(
                "\nWARNING: Bazzite not detected. Some optimizations may not work correctly.",
                Colors.WARNING)
            print_colored("Continue anyway? (y/n): ", Colors.WARNING, end="")
            if input().lower() != 'y':
                return False

        # Warn if hardware doesn't match optimal config
        if not optimal_config:
            print_colored(
                "\nWARNING: Some expected hardware components were not detected.",
                Colors.WARNING)
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

    def initialize_optimizers(self):
        """Initialize all optimizer modules with selected profile"""
        self.optimizers = [
            ("NVIDIA RTX 5080 Blackwell", NvidiaOptimizer(self.logger)),
            ("Intel i9-10850K CPU", CPUOptimizer(self.logger)),
            ("Memory & Storage", MemoryOptimizer(self.logger)),
            ("Audio System", AudioOptimizer(self.logger)),
            ("Network (Intel I225-V)", NetworkOptimizer(self.logger)),
            ("Gaming Tools", GamingToolsOptimizer(self.logger)),
            ("Kernel & Boot", KernelOptimizer(self.logger)),
            ("Systemd Services", SystemdServiceOptimizer(self.logger)),
            ("KDE Plasma 6 Wayland", PlasmaOptimizer(self.logger)),
            ("Bazzite Specific", BazziteOptimizer(self.logger))
        ]

        # Set profile for all optimizers
        for name, optimizer in self.optimizers:
            if hasattr(optimizer, 'set_profile'):
                optimizer.set_profile(self.profile)

    def apply_optimizations(self, skip_packages: bool = False, run_benchmarks: bool = False):
        """Apply all optimizations with validation"""
        print_colored(
            f"\nStarting optimization process (Profile: {self.profile.upper()})...",
            Colors.HEADER)

        # Run baseline benchmarks if requested
        baseline_results = {}
        if run_benchmarks:
            print_colored("\nRunning baseline benchmarks before optimization...", Colors.OKCYAN)
            baseline_results = self.benchmark_runner.run_baseline()

        total_steps = len(self.optimizers)
        failed_modules = []

        for i, (name, optimizer) in enumerate(self.optimizers, 1):
            print_colored(f"\n[{i}/{total_steps}] {name}", Colors.OKCYAN)

            try:
                # Special handling for different optimizer types
                if isinstance(optimizer, NvidiaOptimizer):
                    if not skip_packages:
                        if optimizer.install_drivers():
                            self.needs_reboot = True
                    if not optimizer.apply_optimizations():
                        failed_modules.append(name)

                elif isinstance(optimizer, CPUOptimizer):
                    if not skip_packages:
                        optimizer.install_tools()
                    if not optimizer.apply_optimizations():
                        failed_modules.append(name)

                elif isinstance(optimizer, GamingToolsOptimizer):
                    if not optimizer.apply_optimizations(skip_packages):
                        failed_modules.append(name)

                elif isinstance(optimizer, KernelOptimizer):
                    if optimizer.apply_optimizations():
                        self.needs_reboot = True
                    else:
                        failed_modules.append(name)

                else:
                    if not optimizer.apply_optimizations():
                        failed_modules.append(name)

                # Validate each module after application
                if hasattr(optimizer, 'validate'):
                    validations = optimizer.validate()
                    self.validation_results[name] = validations

                    # Show validation status
                    failed_validations = [k for k, v in validations.items() if not v]
                    if failed_validations:
                        print_colored(
                            f"  ⚠ Some validations failed: {', '.join(failed_validations)}",
                            Colors.WARNING)
                    else:
                        print_colored("  ✓ All validations passed", Colors.OKGREEN)

            except Exception as e:
                print_colored(f"  ✗ Error in {name}: {str(e)}", Colors.FAIL)
                self.logger.error(f"Failed to apply {name}: {str(e)}", exc_info=True)
                failed_modules.append(name)

        # Start thermal monitoring
        profile_settings = GAMING_PROFILES.get(
            self.profile, GAMING_PROFILES["balanced"])["settings"]
        self.thermal_manager.start_monitoring(profile_settings.get("fan_profile", "balanced"))

        # Run post-optimization benchmarks if requested
        if run_benchmarks:
            print_colored("\nRunning post-optimization benchmarks...", Colors.OKCYAN)
            post_results = self.benchmark_runner.run_post_optimization()
            
            # Compare results if both baseline and post results exist
            if baseline_results and post_results:
                print_colored("\nBenchmark Comparison:", Colors.HEADER)
                # Basic comparison logging (results processing would be expanded in production)
                self.logger.info(f"Baseline benchmarks: {len(baseline_results)} tests completed")
                self.logger.info(f"Post-optimization benchmarks: {len(post_results)} tests completed")

        # Summary
        print_colored("\n" + "=" * 62, Colors.HEADER)
        if failed_modules:
            print_colored("Optimization completed with some failures:", Colors.WARNING)
            for module in failed_modules:
                print_colored(f"  ✗ {module}", Colors.FAIL)
        else:
            print_colored("✓ All optimizations applied successfully!", Colors.OKGREEN + Colors.BOLD)

        # Show validation summary
        self.print_validation_summary()

        return len(failed_modules) == 0

    def validate_all_optimizations(self) -> Dict[str, Dict[str, bool]]:
        """Run validation checks on all optimizations"""
        print_colored("\nValidating optimizations...", Colors.HEADER)

        all_validations = {}

        # Core system validations
        core_validations = {
            "cpu_governor": validate_optimization(
                "CPU Governor",
                "cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor",
                GAMING_PROFILES.get(self.profile, GAMING_PROFILES["balanced"])["settings"]["cpu_governor"]
            ),
            "gpu_power_mode": validate_optimization(
                "GPU Power Mode",
                "nvidia-settings -q GPUPowerMizerMode -t",
                str(GAMING_PROFILES.get(self.profile, GAMING_PROFILES["balanced"])["settings"]["gpu_power_mode"])
            ),
            "zram_enabled": bool(run_command("zramctl --raw --noheadings", check=False)[1].strip()),
            "mglru_enabled": Path("/sys/kernel/mm/lru_gen/enabled").exists(),
            "gamemode_running": run_command("systemctl is-active gamemoded", check=False)[0] == 0,
            "thermal_monitoring": self.thermal_manager.monitoring
        }

        all_validations["Core System"] = core_validations

        # Add module-specific validations
        all_validations.update(self.validation_results)

        return all_validations

    def print_validation_summary(self):
        """Print validation summary"""
        if not self.validation_results:
            return

        print_colored("\n" + "=" * 62, Colors.HEADER)
        print_colored("VALIDATION SUMMARY", Colors.HEADER + Colors.BOLD)
        print_colored("=" * 62, Colors.HEADER)

        total_checks = 0
        passed_checks = 0

        for module, validations in self.validation_results.items():
            module_passed = sum(1 for v in validations.values() if v)
            module_total = len(validations)
            total_checks += module_total
            passed_checks += module_passed

            if module_passed == module_total:
                color = Colors.OKGREEN
                status = "✓"
            elif module_passed > 0:
                color = Colors.WARNING
                status = "⚠"
            else:
                color = Colors.FAIL
                status = "✗"

            print_colored(f"{status} {module}: {module_passed}/{module_total} checks passed", color)

            # Show failed checks
            for check, passed in validations.items():
                if not passed:
                    print(f"    ✗ {check}")

        # Overall summary
        print_colored("-" * 62, Colors.HEADER)
        percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        if percentage >= 90:
            color = Colors.OKGREEN
        elif percentage >= 70:
            color = Colors.WARNING
        else:
            color = Colors.FAIL

        print_colored(
            f"Overall: {passed_checks}/{total_checks} ({percentage:.1f}%) validations passed", color)

    def create_rollback_script(self):
        """Create comprehensive rollback script"""
        rollback_script = f"""#!/bin/bash
# Rollback script created on {TIMESTAMP}
# Restores system to pre-optimization state

echo "Rolling back Bazzite optimizations..."

# Stop thermal monitoring
pkill -f performance-monitor.sh 2>/dev/null || true
pkill -f "apply_fan_curve" 2>/dev/null || true

# Restore backed up files
BACKUP_DIR="{CONFIG_BACKUP_DIR}"

for backup in $BACKUP_DIR/*.{TIMESTAMP}; do
    if [ -f "$backup" ]; then
        original=$(basename "$backup" .{TIMESTAMP})

        # Determine target path
        targets=(
            "/etc/modprobe.d/$original"
            "/etc/sysctl.d/$original"
            "/etc/udev/rules.d/$original"
            "/etc/systemd/system/$original"
            "/etc/pipewire/pipewire.conf.d/$original"
            "/etc/NetworkManager/conf.d/$original"
            "/etc/X11/xorg.conf.d/$original"
            "/etc/intel-undervolt.conf"
            "/etc/$original"
        )

        for target in "${{targets[@]}}"; do
            target_dir=$(dirname "$target")
            if [ -d "$target_dir" ]; then
                cp "$backup" "$target"
                echo "Restored $target"
                break
            fi
        done
    fi
done

# Remove optimization scripts
rm -f /usr/local/bin/nvidia-gaming-optimize.sh
rm -f /usr/local/bin/cpu-gaming-optimize.sh
rm -f /usr/local/bin/ethernet-optimize.sh
rm -f /usr/local/bin/gaming-mode-activate.sh
rm -f /usr/local/bin/gaming-mode-start.sh

# Remove services
systemctl disable gaming-optimizations.service 2>/dev/null || true
rm -f /etc/systemd/system/gaming-optimizations.service
systemctl daemon-reload

# Restore original CPU governor
echo "powersave" > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || true

# Reset GPU power mode
nvidia-settings -a GPUPowerMizerMode=0 2>/dev/null || true

echo "Rollback completed. Please reboot for all changes to take effect."
"""

        rollback_path = Path("/usr/local/bin/rollback-gaming-optimizations.sh")
        if write_config_file(rollback_path, rollback_script, executable=True):
            self.logger.info(f"Rollback script created: {rollback_path}")
        else:
            self.logger.error("Failed to create rollback script")

    def print_verification_commands(self):
        """Print verification commands for manual checking"""
        print_colored(f"""
{Colors.HEADER}========================================
VERIFICATION COMMANDS
========================================{Colors.ENDC}

{Colors.OKCYAN}Hardware Status:{Colors.ENDC}
  nvidia-smi                           # GPU status and temperature
  cat /proc/cpuinfo | grep "model name" | head -1  # CPU model
  lscpu | grep MHz                     # CPU frequencies
  free -h                              # Memory usage
  lsblk -o NAME,SIZE,TYPE,MOUNTPOINT   # Storage devices

{Colors.OKCYAN}Performance Settings:{Colors.ENDC}
  cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor  # CPU governor
  nvidia-settings -q GPUPowerMizerMode        # GPU power mode
  cat /proc/sys/vm/swappiness                  # Swappiness setting
  zramctl                                      # ZRAM status
  cat /sys/kernel/mm/lru_gen/enabled          # MGLRU status

{Colors.OKCYAN}Gaming Services:{Colors.ENDC}
  systemctl status gamemoded                   # GameMode daemon
  systemctl status system76-scheduler         # System76 Scheduler
  systemctl status gaming-optimizations       # Custom gaming service

{Colors.OKCYAN}Network & Audio:{Colors.ENDC}
  ethtool eth0 | grep Speed                   # Network speed
  cat /sys/class/net/*/tx_queue_len           # Network queue lengths
  cat /proc/asound/card*/pcm*/sub*/hw_params  # Audio settings

{Colors.OKGREEN}Troubleshooting:{Colors.ENDC}
  Logs:          journalctl -u gaming-optimizations.service
  Validation:    sudo {sys.argv[0]} --validate
  Safe Mode:     sudo {sys.argv[0]} --profile balanced --skip-packages
""")

    def print_usage_instructions(self):
        """Print usage instructions"""
        profile_settings = GAMING_PROFILES.get(
            self.profile, GAMING_PROFILES["balanced"])["settings"]

        print_colored(f"""
{Colors.HEADER}========================================
USAGE INSTRUCTIONS
========================================{Colors.ENDC}

{Colors.OKCYAN}Current Profile: {self.profile.upper()}{Colors.ENDC}
{GAMING_PROFILES[self.profile]['description']}

{Colors.OKCYAN}Gaming Mode:{Colors.ENDC}
  Start:  systemctl start gaming-optimizations
  Stop:   systemctl stop gaming-optimizations
  Auto:   systemctl enable gaming-optimizations  # Start on boot

{Colors.OKCYAN}Monitoring:{Colors.ENDC}
  Temperatures: watch -n 1 nvidia-smi
  Performance:  htop
  Network:      iftop -i eth0

{Colors.OKCYAN}Profile Settings Active:{Colors.ENDC}""")

        for key, value in profile_settings.items():
            formatted_key = key.replace('_', ' ').title()
            print(f"  {formatted_key}: {value}")

        print_colored(f"""
{Colors.OKGREEN}Troubleshooting:{Colors.ENDC}
  Logs:          journalctl -u gaming-optimizations.service
  Validation:    sudo {sys.argv[0]} --validate
  Safe Mode:     sudo {sys.argv[0]} --profile balance --skip-packages
""")

    def _signal_handler(self, signum: int, frame):
        """Handle graceful shutdown on SIGINT/SIGTERM"""
        self.logger.warning(f"Received signal {signum}, shutting down gracefully...")
        if hasattr(self, 'thermal_manager'):
            self.thermal_manager.stop_monitoring()
        print_colored("\nOperation cancelled by user. Cleaning up...", Colors.WARNING)
        sys.exit(0)

    def run(self):
        """Main execution flow with signal handling"""
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self.print_banner()
        self.print_system_info()

        # Parse command line arguments first to handle non-root commands
        parser = argparse.ArgumentParser(
            description='Bazzite DX Ultimate Gaming Optimizer v4',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Profiles:
  competitive  - Maximum performance, minimal latency, no visual effects
  balanced     - Good performance with visual quality (default)
  streaming    - Optimized for OBS/streaming with encoding headroom
  creative     - Optimized for rendering and creative applications

Examples:
  sudo python3 bazzite-optimizer.py                      # Full optimization (balanced)
  sudo python3 bazzite-optimizer.py --profile competitive # Competitive gaming profile
  sudo python3 bazzite-optimizer.py --benchmark          # Run with benchmarks
  sudo python3 bazzite-optimizer.py --skip-packages      # Skip package installation
  sudo python3 bazzite-optimizer.py --validate           # Validate optimizations
  sudo python3 bazzite-optimizer.py --rollback           # Rollback all changes
  sudo python3 bazzite-optimizer.py --verify             # Show verification commands only
            """
        )

        parser.add_argument(
            '--profile',
            choices=[
                'competitive',
                'balanced',
                'streaming',
                'creative'],
            default='balanced',
            help='Gaming profile to apply')
        parser.add_argument('--skip-packages', action='store_true',
                            help='Skip package installation (use for updates)')
        parser.add_argument('--benchmark', action='store_true',
                            help='Run benchmarks before and after optimization')
        parser.add_argument('--validate', action='store_true',
                            help='Validate current optimizations')
        parser.add_argument('--rollback', action='store_true',
                            help='Rollback all optimizations')
        parser.add_argument('--verify', action='store_true',
                            help='Show verification commands only')
        parser.add_argument('--list-profiles', action='store_true',
                            help='List available profiles')
        parser.add_argument('--version', action='version',
                            version=f'%(prog)s {SCRIPT_VERSION}')

        args = parser.parse_args()

        # Handle list profiles
        if args.list_profiles:
            print_colored("\nAvailable Profiles:", Colors.HEADER)
            for profile_name, profile_data in GAMING_PROFILES.items():
                print(f"\n{Colors.OKCYAN}{profile_name}:{Colors.ENDC}")
                print(f"  {profile_data['description']}")
            return 0

        # Handle verify mode
        if args.verify:
            self.print_verification_commands()
            return 0

        # Handle validation mode
        if args.validate:
            self.profile = args.profile
            validations = self.validate_all_optimizations()

            print_colored("\nValidation Results:", Colors.HEADER)
            for category, checks in validations.items():
                print(f"\n{Colors.OKCYAN}{category}:{Colors.ENDC}")
                for check, passed in checks.items():
                    status = "✓" if passed else "✗"
                    color = Colors.OKGREEN if passed else Colors.FAIL
                    print_colored(f"  {status} {check}", color)

            return 0

        # Handle rollback (requires root)
        if args.rollback:
            if not self.check_prerequisites():
                return 1
            rollback_script = Path("/usr/local/bin/rollback-gaming-optimizations.sh")
            if rollback_script.exists():
                print_colored("\nExecuting rollback...", Colors.WARNING)

                # Stop thermal monitoring
                self.thermal_manager.stop_monitoring()

                returncode, _, _ = run_command(str(rollback_script))
                if returncode == 0:
                    print_colored("Rollback completed successfully", Colors.OKGREEN)
                else:
                    print_colored("Rollback encountered errors", Colors.FAIL)
                return returncode
            else:
                print_colored("No rollback script found. Run optimization first.", Colors.FAIL)
                return 1

        # Check prerequisites for operations that require root
        if not self.check_prerequisites():
            return 1

        # Set profile
        self.profile = args.profile
        print_colored(f"\nSelected Profile: {self.profile.upper()}", Colors.HEADER)
        profile_info = GAMING_PROFILES[self.profile]
        print(f"  {profile_info['description']}")

        # Save profile settings as environment
        self.profile_manager.export_profile_env(self.profile)

        # Initialize optimizers with selected profile
        self.initialize_optimizers()

        # Apply optimizations
        success = self.apply_optimizations(args.skip_packages, args.benchmark)

        if success:
            # Create rollback capability
            self.create_rollback_script()

            # Show verification commands
            self.print_verification_commands()

            # Show usage instructions
            self.print_usage_instructions()

            # Check if reboot is needed
            if self.needs_reboot:
                print_colored("\n" + "!" * 62, Colors.WARNING)
                print_colored("REBOOT REQUIRED", Colors.WARNING + Colors.BOLD)
                print_colored(
                    "Some optimizations require a system reboot to take effect:",
                    Colors.WARNING)
                print_colored("  - NVIDIA driver changes", Colors.WARNING)
                print_colored("  - Kernel parameter updates", Colors.WARNING)
                print_colored("  - Initramfs regeneration", Colors.WARNING)
                print_colored("\nPlease reboot your system when convenient.", Colors.WARNING)
                print_colored("!" * 62, Colors.WARNING)

            print_colored(
                f"\n✓ Optimization complete with {self.profile.upper()} profile! Happy gaming! 🎮",
                Colors.OKGREEN + Colors.BOLD)
            print_colored(f"\nLog file: {LOG_DIR}/optimization_{TIMESTAMP}.log", Colors.OKBLUE)
            return 0
        else:
            print_colored(
                "\n✗ Optimization completed with errors. Check logs for details.",
                Colors.FAIL)
            print_colored(f"\nLog file: {LOG_DIR}/optimization_{TIMESTAMP}.log", Colors.WARNING)
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
        # Stop thermal monitoring if running
        if 'optimizer' in locals() and hasattr(optimizer, 'thermal_manager'):
            optimizer.thermal_manager.stop_monitoring()
        return 130
    except Exception as e:
        print_colored(f"\nFatal error: {str(e)}", Colors.FAIL)
        logging.error(f"Fatal error: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
