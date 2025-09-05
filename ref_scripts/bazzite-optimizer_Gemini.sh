#!/bin/bash

# ==============================================================================
# Bazzite DX Performance Optimization Script
# ==============================================================================
# This script applies a set of persistent system tweaks for low-latency gaming.
# It is designed for a high-RAM system with NVMe SSDs.
# Run this script with sudo privileges.
# ==============================================================================

set -e
echo "Applying Bazzite DX performance tweaks..."

# --- 1. Configure System Swappiness ---
# For systems with high amounts of RAM (32GB+), a low swappiness value is
# recommended to ensure the kernel prioritizes using physical RAM over swap.
echo "Configuring vm.swappiness to 10..."
cat > /etc/sysctl.d/99-gaming-swappiness.conf <<'EOF'
# Lower swappiness for high-RAM gaming systems
vm.swappiness=10
EOF

# --- 2. Configure Network Stack for Low Latency ---
# These settings tune the kernel's TCP/IP stack to prioritize low latency,
# which is beneficial for online gaming.
echo "Tuning network stack for low latency..."
cat > /etc/sysctl.d/98-network-tweaks.conf <<'EOF'
# Prioritize low latency for TCP connections
net.ipv4.tcp_low_latency=1

# Disable TCP timestamps to reduce CPU overhead
net.ipv4.tcp_timestamps=0

# Increase network buffer sizes to prevent packet loss
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.ipv4.tcp_rmem=4096 87380 16777216
net.ipv4.tcp_wmem=4096 65536 16777216

# Increase the queue size for incoming packets
net.core.netdev_max_backlog=250000
EOF

# --- 3. Set I/O Scheduler for NVMe Drives ---
# For high-performance NVMe SSDs, the 'none' scheduler minimizes kernel
# overhead and allows the drive's internal controller to manage I/O.
echo "Setting I/O scheduler for NVMe devices to 'none'..."
cat > /etc/udev/rules.d/60-ioschedulers.rules <<'EOF'
# Set the I/O scheduler for NVMe drives to 'none' for optimal performance
ACTION=="add|change", KERNEL=="nvme[0-9]*", ATTR{queue/scheduler}="none"
EOF

# --- Apply All sysctl Settings ---
echo "Applying all sysctl changes..."
sysctl --system

echo "=============================================================================="
echo "System tweaks applied successfully."
echo "A reboot is recommended for all changes to take full effect, especially the"
echo "I/O scheduler rule."
echo "=============================================================================="

exit 0
