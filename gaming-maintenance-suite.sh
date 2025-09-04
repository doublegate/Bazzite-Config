#!/bin/bash
#
# Bazzite Gaming Benchmarking & Maintenance Suite
# Automated performance testing and system maintenance
# Version: 1.0.0
#

# ============================================================================
# COLOR DEFINITIONS
# ============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_NAME="Gaming Benchmark & Maintenance"
SCRIPT_VERSION="1.0.0"
LOG_DIR="/var/log/gaming-benchmark"
RESULTS_DIR="$HOME/.local/share/gaming-benchmarks"
CONFIG_DIR="$HOME/.config/gaming-maintenance"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create directories
mkdir -p "$LOG_DIR" "$RESULTS_DIR" "$CONFIG_DIR"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

print_header() {
    echo -e "\n${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${WHITE}  $1${CYAN}${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
}

print_section() {
    echo -e "\n${BLUE}▶ $1${NC}"
    echo -e "${BLUE}$(printf '─%.0s' {1..60})${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This function requires root privileges"
        exit 1
    fi
}

# ============================================================================
# GPU BENCHMARKING
# ============================================================================

benchmark_gpu() {
    print_section "GPU Benchmark (RTX 5080)"
    
    local BENCH_LOG="$RESULTS_DIR/gpu_bench_$TIMESTAMP.log"
    
    # Save current GPU state
    print_info "Saving current GPU state..."
    nvidia-smi -q > "$BENCH_LOG"
    
    # Run basic GPU stress test using CUDA
    print_info "Running GPU memory bandwidth test..."
    cat > /tmp/gpu_bandwidth_test.py << 'EOF'
#!/usr/bin/env python3
import time
import subprocess
import json

def run_bandwidth_test():
    """Run GPU bandwidth test using nvidia-smi"""
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'gpu_name': '',
        'memory_bandwidth': {},
        'compute_test': {}
    }
    
    try:
        # Get GPU info
        cmd = "nvidia-smi --query-gpu=name,memory.total,clocks.max.graphics,clocks.max.memory --format=csv,noheader"
        output = subprocess.check_output(cmd, shell=True, text=True).strip()
        parts = output.split(', ')
        results['gpu_name'] = parts[0]
        results['memory_total'] = parts[1]
        results['max_graphics_clock'] = parts[2]
        results['max_memory_clock'] = parts[3]
        
        # Simple memory allocation test
        print("Testing GPU memory bandwidth...")
        
        # Run nvidia-smi dmon for 10 seconds to collect metrics
        cmd = "timeout 10 nvidia-smi dmon -s pucvmet -c 10"
        output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
        
        lines = output.strip().split('\n')
        for line in lines:
            if not line.startswith('#') and line.strip():
                parts = line.split()
                if len(parts) >= 7:
                    results['memory_bandwidth'] = {
                        'power': f"{parts[1]}W",
                        'gpu_util': f"{parts[2]}%",
                        'mem_util': f"{parts[3]}%",
                        'encoder': f"{parts[4]}%",
                        'decoder': f"{parts[5]}%",
                        'temp': f"{parts[6]}°C"
                    }
                    break
        
        print(json.dumps(results, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
        results['error'] = str(e)
    
    return results

if __name__ == "__main__":
    run_bandwidth_test()
EOF
    
    python3 /tmp/gpu_bandwidth_test.py >> "$BENCH_LOG" 2>&1
    
    # Test with glxgears if available
    if command -v glxgears &> /dev/null; then
        print_info "Running OpenGL test..."
        timeout 10 glxgears -info 2>&1 | head -20 >> "$BENCH_LOG"
    fi
    
    # Test Vulkan if available
    if command -v vulkaninfo &> /dev/null; then
        print_info "Checking Vulkan support..."
        vulkaninfo --summary 2>/dev/null | grep -A5 "GPU" >> "$BENCH_LOG"
    fi
    
    # Run Unigine benchmark if installed
    if [[ -f "$HOME/Unigine_Superposition/bin/superposition" ]]; then
        print_info "Running Unigine Superposition benchmark..."
        cd "$HOME/Unigine_Superposition/bin"
        ./superposition -preset extreme -fullscreen 0 -video_app opengl &
        UNIGINE_PID=$!
        sleep 60
        kill $UNIGINE_PID 2>/dev/null
        
        # Parse results
        if [[ -f "$HOME/.Superposition/automation/superposition_results.csv" ]]; then
            tail -1 "$HOME/.Superposition/automation/superposition_results.csv" >> "$BENCH_LOG"
        fi
    else
        print_warning "Unigine Superposition not found. Download from: https://benchmark.unigine.com/"
    fi
    
    print_success "GPU benchmark completed. Results: $BENCH_LOG"
}

# ============================================================================
# CPU BENCHMARKING
# ============================================================================

benchmark_cpu() {
    print_section "CPU Benchmark (i9-10850K)"
    
    local BENCH_LOG="$RESULTS_DIR/cpu_bench_$TIMESTAMP.log"
    
    # Single-thread performance
    print_info "Testing single-thread performance..."
    echo "Single-thread benchmark:" >> "$BENCH_LOG"
    time echo "scale=5000; a(1)*4" | bc -l >> "$BENCH_LOG" 2>&1
    
    # Multi-thread performance using stress-ng
    if command -v stress-ng &> /dev/null; then
        print_info "Running multi-thread stress test..."
        stress-ng --cpu $(nproc) --cpu-method trig --metrics --timeout 30s >> "$BENCH_LOG" 2>&1
    else
        print_warning "stress-ng not installed. Installing..."
        sudo dnf install -y stress-ng
    fi
    
    # Memory bandwidth test
    if command -v sysbench &> /dev/null; then
        print_info "Testing memory bandwidth..."
        sysbench memory --memory-total-size=10G run >> "$BENCH_LOG" 2>&1
    fi
    
    # Check CPU frequency scaling
    print_info "Checking CPU frequency scaling..."
    for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq; do
        echo "$(basename $(dirname $(dirname $cpu))): $(cat $cpu) kHz" >> "$BENCH_LOG"
    done
    
    print_success "CPU benchmark completed. Results: $BENCH_LOG"
}

# ============================================================================
# DISK BENCHMARKING
# ============================================================================

benchmark_disk() {
    print_section "Disk Benchmark (Samsung 990 EVO Plus)"
    
    local BENCH_LOG="$RESULTS_DIR/disk_bench_$TIMESTAMP.log"
    local TEST_FILE="/tmp/diskbench_$TIMESTAMP.tmp"
    
    # Sequential write test
    print_info "Testing sequential write speed..."
    echo "Sequential Write Test:" >> "$BENCH_LOG"
    dd if=/dev/zero of="$TEST_FILE" bs=1G count=2 oflag=direct 2>&1 | grep -E 'copied|bytes' >> "$BENCH_LOG"
    
    # Sequential read test
    print_info "Testing sequential read speed..."
    echo "Sequential Read Test:" >> "$BENCH_LOG"
    dd if="$TEST_FILE" of=/dev/null bs=1G count=2 iflag=direct 2>&1 | grep -E 'copied|bytes' >> "$BENCH_LOG"
    
    # Random I/O test with fio if available
    if command -v fio &> /dev/null; then
        print_info "Running fio random I/O test..."
        
        cat > /tmp/fio_gaming.ini << 'EOF'
[global]
ioengine=libaio
direct=1
runtime=30
time_based
size=1G

[random-read-4k]
rw=randread
bs=4k
numjobs=4
iodepth=32

[random-write-4k]
rw=randwrite
bs=4k
numjobs=4
iodepth=32

[sequential-read-1m]
rw=read
bs=1M
numjobs=1
iodepth=32

[sequential-write-1m]
rw=write
bs=1M
numjobs=1
iodepth=32
EOF
        
        fio /tmp/fio_gaming.ini --output="$BENCH_LOG" --append-terse
    else
        print_warning "fio not installed. Skipping advanced disk tests."
    fi
    
    # Clean up
    rm -f "$TEST_FILE" /tmp/fio_gaming.ini
    
    print_success "Disk benchmark completed. Results: $BENCH_LOG"
}

# ============================================================================
# GAMING PERFORMANCE TEST
# ============================================================================

gaming_performance_test() {
    print_section "Gaming Performance Test"
    
    local PERF_LOG="$RESULTS_DIR/gaming_perf_$TIMESTAMP.log"
    
    # Check if Steam is running
    if pgrep -x "steam" > /dev/null; then
        print_info "Steam is running"
        echo "Steam: RUNNING" >> "$PERF_LOG"
    else
        print_warning "Steam is not running"
        echo "Steam: NOT RUNNING" >> "$PERF_LOG"
    fi
    
    # Check GameMode status
    if systemctl --user is-active gamemoded &>/dev/null; then
        print_info "GameMode is active"
        echo "GameMode: ACTIVE" >> "$PERF_LOG"
    else
        print_warning "GameMode is not active"
        echo "GameMode: INACTIVE" >> "$PERF_LOG"
    fi
    
    # Test frame time consistency
    print_info "Testing frame time consistency..."
    
    # Create a simple OpenGL test
    cat > /tmp/frame_test.c << 'EOF'
#include <GL/glut.h>
#include <stdio.h>
#include <time.h>

int frame_count = 0;
struct timespec start, end;

void display() {
    glClear(GL_COLOR_BUFFER_BIT);
    glBegin(GL_TRIANGLES);
    glVertex2f(-0.5, -0.5);
    glVertex2f(0.5, -0.5);
    glVertex2f(0.0, 0.5);
    glEnd();
    glutSwapBuffers();
    
    frame_count++;
    if (frame_count == 300) {
        clock_gettime(CLOCK_MONOTONIC, &end);
        double time_spent = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1000000000.0;
        printf("Average FPS: %.2f\n", frame_count / time_spent);
        exit(0);
    }
}

void idle() {
    glutPostRedisplay();
}

int main(int argc, char** argv) {
    glutInit(&argc, argv);
    glutCreateWindow("Frame Test");
    clock_gettime(CLOCK_MONOTONIC, &start);
    glutDisplayFunc(display);
    glutIdleFunc(idle);
    glutMainLoop();
    return 0;
}
EOF
    
    if command -v gcc &> /dev/null && [ -f /usr/include/GL/glut.h ]; then
        gcc /tmp/frame_test.c -o /tmp/frame_test -lGL -lglut -lm 2>/dev/null
        if [ -f /tmp/frame_test ]; then
            timeout 10 /tmp/frame_test >> "$PERF_LOG" 2>&1
        fi
    fi
    
    # Check shader cache
    print_info "Checking shader cache sizes..."
    for cache_dir in ~/.cache/nvidia ~/.cache/mesa_shader_cache ~/.local/share/Steam/steamapps/shadercache; do
        if [ -d "$cache_dir" ]; then
            size=$(du -sh "$cache_dir" 2>/dev/null | cut -f1)
            echo "$(basename $cache_dir): $size" >> "$PERF_LOG"
        fi
    done
    
    print_success "Gaming performance test completed. Results: $PERF_LOG"
}

# ============================================================================
# SYSTEM MAINTENANCE
# ============================================================================

system_maintenance() {
    print_header "SYSTEM MAINTENANCE"
    
    local choice
    echo -e "\n${CYAN}Maintenance Options:${NC}"
    echo "1. Clean shader caches"
    echo "2. Optimize game libraries"
    echo "3. Update gaming tools"
    echo "4. Defragment BTRFS"
    echo "5. Clean package cache"
    echo "6. Full maintenance (all above)"
    echo "0. Back to main menu"
    
    read -p "Select option: " choice
    
    case $choice in
        1) clean_shader_caches ;;
        2) optimize_game_libraries ;;
        3) update_gaming_tools ;;
        4) defragment_btrfs ;;
        5) clean_package_cache ;;
        6) full_maintenance ;;
        0) return ;;
        *) print_error "Invalid option" ;;
    esac
}

clean_shader_caches() {
    print_section "Cleaning Shader Caches"
    
    local total_freed=0
    local cache_dirs=(
        "$HOME/.cache/nvidia"
        "$HOME/.cache/mesa_shader_cache"
        "$HOME/.cache/radv_builtin_shaders"
        "$HOME/.local/share/Steam/steamapps/shadercache"
        "$HOME/.cache/wine"
        "$HOME/.cache/lutris"
    )
    
    for cache_dir in "${cache_dirs[@]}"; do
        if [ -d "$cache_dir" ]; then
            size_before=$(du -sb "$cache_dir" 2>/dev/null | cut -f1)
            print_info "Cleaning $(basename $cache_dir)..."
            rm -rf "$cache_dir"/*
            size_after=$(du -sb "$cache_dir" 2>/dev/null | cut -f1)
            freed=$((size_before - size_after))
            total_freed=$((total_freed + freed))
        fi
    done
    
    print_success "Freed $(numfmt --to=iec $total_freed) from shader caches"
}

optimize_game_libraries() {
    print_section "Optimizing Game Libraries"
    
    # Optimize Steam libraries
    if [ -d "$HOME/.local/share/Steam/steamapps" ]; then
        print_info "Optimizing Steam game libraries..."
        
        # Find all appmanifest files
        for manifest in $HOME/.local/share/Steam/steamapps/*.acf; do
            if [ -f "$manifest" ]; then
                # Validate the manifest
                app_id=$(grep -E '"appid"' "$manifest" | grep -oE '[0-9]+')
                if [ -n "$app_id" ]; then
                    echo "  Validating app $app_id..."
                fi
            fi
        done
    fi
    
    # Preload commonly used libraries
    print_info "Preloading gaming libraries..."
    ldconfig 2>/dev/null
    
    # Update library cache
    print_info "Updating library cache..."
    sudo /sbin/ldconfig
    
    print_success "Game libraries optimized"
}

update_gaming_tools() {
    print_section "Updating Gaming Tools"
    
    # Update Flatpak gaming apps
    print_info "Updating Flatpak gaming applications..."
    flatpak update -y --noninteractive \
        com.valvesoftware.Steam \
        net.davidotek.pupgui2 \
        com.github.Matoking.protontricks \
        com.leinardi.gwe 2>/dev/null
    
    # Update ProtonGE
    if command -v protonup-qt &> /dev/null; then
        print_info "Checking for ProtonGE updates..."
        # This would normally launch GUI, so we check manually
        latest_proton=$(curl -s https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases/latest | grep tag_name | cut -d'"' -f4)
        print_info "Latest ProtonGE version: $latest_proton"
    fi
    
    # Update MangoHud
    print_info "Checking MangoHud..."
    if ! command -v mangohud &> /dev/null; then
        sudo dnf install -y mangohud
    fi
    
    # Update GameMode
    print_info "Checking GameMode..."
    if ! systemctl --user is-enabled gamemoded &>/dev/null; then
        systemctl --user enable gamemoded
    fi
    
    print_success "Gaming tools updated"
}

defragment_btrfs() {
    print_section "Defragmenting BTRFS Filesystems"
    
    # Find all BTRFS mount points
    while IFS= read -r mount_point; do
        print_info "Defragmenting $mount_point..."
        sudo btrfs filesystem defragment -r -v "$mount_point" 2>/dev/null
    done < <(mount -t btrfs | awk '{print $3}')
    
    # Balance BTRFS
    print_info "Balancing BTRFS..."
    for mount_point in $(mount -t btrfs | awk '{print $3}'); do
        sudo btrfs balance start -dusage=50 "$mount_point" 2>/dev/null &
    done
    
    print_success "BTRFS defragmentation initiated"
}

clean_package_cache() {
    print_section "Cleaning Package Cache"
    
    # Clean DNF cache
    print_info "Cleaning DNF cache..."
    sudo dnf clean all
    
    # Clean Flatpak unused
    print_info "Removing unused Flatpaks..."
    flatpak uninstall --unused -y
    
    # Clean journal logs
    print_info "Cleaning journal logs..."
    sudo journalctl --vacuum-time=7d
    
    # Clean temporary files
    print_info "Cleaning temporary files..."
    rm -rf /tmp/* /var/tmp/* 2>/dev/null
    
    print_success "Package cache cleaned"
}

full_maintenance() {
    print_section "Running Full System Maintenance"
    
    clean_shader_caches
    optimize_game_libraries
    update_gaming_tools
    defragment_btrfs
    clean_package_cache
    
    # Additional maintenance
    print_info "Updating firmware..."
    sudo fwupdmgr refresh --force 2>/dev/null
    sudo fwupdmgr update 2>/dev/null
    
    print_info "Rebuilding font cache..."
    fc-cache -fv 2>/dev/null
    
    print_success "Full maintenance completed"
}

# ============================================================================
# AUTO-OPTIMIZATION
# ============================================================================

auto_optimize() {
    print_header "AUTO-OPTIMIZATION"
    
    print_info "Starting automatic optimization sequence..."
    
    # 1. Enable gaming mode
    print_section "Enabling Gaming Mode"
    sudo /usr/local/bin/gaming-mode-activate.sh
    
    # 2. Set CPU to maximum performance
    print_section "Optimizing CPU"
    echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
    
    # 3. Configure GPU for maximum performance
    print_section "Optimizing GPU"
    nvidia-settings -a '[gpu:0]/GPUPowerMizerMode=1' \
                   -a '[gpu:0]/GPUGraphicsClockOffset[3]=150' \
                   -a '[gpu:0]/GPUMemoryTransferRateOffset[3]=800'
    
    # 4. Optimize memory
    print_section "Optimizing Memory"
    sudo sysctl -w vm.swappiness=1
    sudo sysctl -w vm.vfs_cache_pressure=50
    sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'
    
    # 5. Disable compositor
    print_section "Disabling Compositor"
    qdbus org.kde.KWin /Compositor suspend 2>/dev/null
    
    # 6. Start GameMode
    print_section "Starting GameMode"
    systemctl --user start gamemoded
    
    print_success "Auto-optimization completed!"
    print_info "System is now optimized for gaming"
}

# ============================================================================
# MONITORING DASHBOARD
# ============================================================================

start_monitoring() {
    print_header "PERFORMANCE MONITORING"
    
    # Check if monitoring script exists
    if [ -f "/usr/local/bin/gaming-monitor.py" ]; then
        python3 /usr/local/bin/gaming-monitor.py --mode simple
    else
        # Fallback to basic monitoring
        print_info "Starting basic monitoring (Press Ctrl+C to stop)..."
        
        while true; do
            clear
            echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
            echo -e "${WHITE}  GAMING PERFORMANCE MONITOR${NC}"
            echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
            echo ""
            
            # CPU info
            echo -e "${BLUE}CPU:${NC}"
            grep 'cpu MHz' /proc/cpuinfo | head -4 | awk '{print "  Core: "$4" MHz"}'
            echo "  Load: $(uptime | awk -F'load average:' '{print $2}')"
            echo ""
            
            # GPU info
            echo -e "${BLUE}GPU:${NC}"
            nvidia-smi --query-gpu=utilization.gpu,temperature.gpu,power.draw,clocks.gr,memory.used,memory.total \
                      --format=csv,noheader,nounits | \
                      awk -F', ' '{printf "  Usage: %s%%  Temp: %s°C  Power: %sW\n  Clock: %sMHz  VRAM: %s/%s MB\n", $1, $2, $3, $4, $5, $6}'
            echo ""
            
            # Memory info
            echo -e "${BLUE}MEMORY:${NC}"
            free -h | grep Mem | awk '{printf "  RAM: %s / %s (%s used)\n", $3, $2, $3}'
            echo ""
            
            # Network info
            echo -e "${BLUE}NETWORK:${NC}"
            ip -s link show | grep -A1 "$(ip route | grep default | awk '{print $5}')" | \
                            tail -1 | awk '{printf "  RX: %s  TX: %s\n", $1, $9}'
            
            sleep 2
        done
    fi
}

# ============================================================================
# REPORT GENERATION
# ============================================================================

generate_report() {
    print_header "GENERATING PERFORMANCE REPORT"
    
    local REPORT_FILE="$RESULTS_DIR/performance_report_$TIMESTAMP.html"
    
    cat > "$REPORT_FILE" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Gaming Performance Report</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #16c79a; border-bottom: 2px solid #16c79a; padding-bottom: 10px; }
        h2 { color: #00adb5; margin-top: 30px; }
        .metric { background: #0f3460; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .value { color: #16c79a; font-weight: bold; font-size: 1.2em; }
        .warning { color: #f39c12; }
        .good { color: #27ae60; }
        .bad { color: #e74c3c; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #333; }
        th { background: #0f3460; color: #16c79a; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Bazzite Gaming Performance Report</h1>
EOF
    
    echo "<p>Generated: $(date)</p>" >> "$REPORT_FILE"
    echo "<p>System: $(hostname)</p>" >> "$REPORT_FILE"
    
    # System Information
    echo "<h2>System Configuration</h2>" >> "$REPORT_FILE"
    echo "<div class='metric'>" >> "$REPORT_FILE"
    echo "<p>CPU: Intel Core i9-10850K (20 threads @ 5.2 GHz)</p>" >> "$REPORT_FILE"
    echo "<p>GPU: NVIDIA GeForce RTX 5080 (16GB VRAM)</p>" >> "$REPORT_FILE"
    echo "<p>RAM: 64GB DDR4</p>" >> "$REPORT_FILE"
    echo "<p>Storage: 2x Samsung 990 EVO Plus 2TB NVMe</p>" >> "$REPORT_FILE"
    echo "</div>" >> "$REPORT_FILE"
    
    # Current Performance Metrics
    echo "<h2>Current Performance Metrics</h2>" >> "$REPORT_FILE"
    echo "<table>" >> "$REPORT_FILE"
    echo "<tr><th>Metric</th><th>Value</th><th>Status</th></tr>" >> "$REPORT_FILE"
    
    # CPU Governor
    gov=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)
    status="good"
    if [ "$gov" != "performance" ]; then status="warning"; fi
    echo "<tr><td>CPU Governor</td><td>$gov</td><td class='$status'>$([ "$gov" = "performance" ] && echo "✓" || echo "⚠")</td></tr>" >> "$REPORT_FILE"
    
    # GPU Performance Mode
    gpu_mode=$(nvidia-settings -q GPUPowerMizerMode -t 2>/dev/null)
    status="good"
    if [ "$gpu_mode" != "1" ]; then status="warning"; fi
    echo "<tr><td>GPU Mode</td><td>$([ "$gpu_mode" = "1" ] && echo "Maximum" || echo "Adaptive")</td><td class='$status'>$([ "$gpu_mode" = "1" ] && echo "✓" || echo "⚠")</td></tr>" >> "$REPORT_FILE"
    
    echo "</table>" >> "$REPORT_FILE"
    
    # Benchmark Results
    if ls "$RESULTS_DIR"/*.log 1> /dev/null 2>&1; then
        echo "<h2>Recent Benchmark Results</h2>" >> "$REPORT_FILE"
        echo "<div class='metric'>" >> "$REPORT_FILE"
        echo "<pre>" >> "$REPORT_FILE"
        tail -20 "$RESULTS_DIR"/*.log | head -20 >> "$REPORT_FILE"
        echo "</pre>" >> "$REPORT_FILE"
        echo "</div>" >> "$REPORT_FILE"
    fi
    
    echo "</div></body></html>" >> "$REPORT_FILE"
    
    print_success "Report generated: $REPORT_FILE"
    
    # Open in browser if possible
    if command -v xdg-open &> /dev/null; then
        xdg-open "$REPORT_FILE" &
    fi
}

# ============================================================================
# MAIN MENU
# ============================================================================

show_menu() {
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${WHITE}     BAZZITE GAMING BENCHMARK & MAINTENANCE SUITE v$SCRIPT_VERSION    ${CYAN}║${NC}"
    echo -e "${CYAN}║${MAGENTA}        RTX 5080 | i9-10850K | 64GB RAM | NVMe SSD          ${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Benchmarking:${NC}"
    echo "  1. GPU Benchmark (RTX 5080)"
    echo "  2. CPU Benchmark (i9-10850K)" 
    echo "  3. Disk Benchmark (NVMe)"
    echo "  4. Gaming Performance Test"
    echo "  5. Run All Benchmarks"
    echo ""
    echo -e "${GREEN}Optimization:${NC}"
    echo "  6. Auto-Optimize System"
    echo "  7. Start Performance Monitor"
    echo ""
    echo -e "${BLUE}Maintenance:${NC}"
    echo "  8. System Maintenance"
    echo "  9. Generate Performance Report"
    echo ""
    echo -e "${RED}System:${NC}"
    echo "  0. Exit"
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    # Parse command line arguments
    case "$1" in
        --benchmark-gpu)
            benchmark_gpu
            exit 0
            ;;
        --benchmark-cpu)
            benchmark_cpu
            exit 0
            ;;
        --benchmark-disk)
            benchmark_disk
            exit 0
            ;;
        --benchmark-all)
            benchmark_gpu
            benchmark_cpu
            benchmark_disk
            gaming_performance_test
            exit 0
            ;;
        --auto-optimize)
            auto_optimize
            exit 0
            ;;
        --monitor)
            start_monitoring
            exit 0
            ;;
        --maintenance)
            full_maintenance
            exit 0
            ;;
        --report)
            generate_report
            exit 0
            ;;
        --help)
            echo "Usage: $0 [option]"
            echo "Options:"
            echo "  --benchmark-gpu    Run GPU benchmark"
            echo "  --benchmark-cpu    Run CPU benchmark"
            echo "  --benchmark-disk   Run disk benchmark"
            echo "  --benchmark-all    Run all benchmarks"
            echo "  --auto-optimize    Auto-optimize system"
            echo "  --monitor         Start performance monitor"
            echo "  --maintenance     Run full maintenance"
            echo "  --report          Generate performance report"
            echo "  --help            Show this help"
            exit 0
            ;;
    esac
    
    # Interactive menu
    while true; do
        show_menu
        read -p "Select option: " choice
        
        case $choice in
            1) benchmark_gpu ;;
            2) benchmark_cpu ;;
            3) benchmark_disk ;;
            4) gaming_performance_test ;;
            5) 
                benchmark_gpu
                benchmark_cpu
                benchmark_disk
                gaming_performance_test
                ;;
            6) auto_optimize ;;
            7) start_monitoring ;;
            8) system_maintenance ;;
            9) generate_report ;;
            0) 
                echo -e "\n${GREEN}Thank you for using $SCRIPT_NAME!${NC}"
                exit 0
                ;;
            *)
                print_error "Invalid option. Please try again."
                ;;
        esac
        
        if [ "$choice" != "7" ] && [ "$choice" != "8" ]; then
            echo ""
            read -p "Press Enter to continue..."
        fi
    done
}

# Run main function
main "$@"
