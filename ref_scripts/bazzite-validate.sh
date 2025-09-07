#!/bin/bash
# Bazzite Boot Configuration Validation Script v4.1
# Verifies all boot optimizations and fixes have been properly applied

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Test functions
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
}

test_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

test_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

test_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

# 1. Check kernel parameters for duplicates
check_kernel_params() {
    print_header "KERNEL PARAMETERS CHECK"
    
    local cmdline=$(cat /proc/cmdline)
    local params=()
    local duplicates=()
    
    # Parse parameters
    for param in $cmdline; do
        local key=${param%%=*}
        if [[ " ${params[@]} " =~ " ${key} " ]]; then
            duplicates+=("$key")
        else
            params+=("$key")
        fi
    done
    
    # Remove duplicates from duplicates array
    duplicates=($(printf '%s\n' "${duplicates[@]}" | sort -u))
    
    if [ ${#duplicates[@]} -eq 0 ]; then
        test_pass "No duplicate kernel parameters found"
    else
        test_fail "Found duplicate kernel parameters: ${duplicates[*]}"
        echo "  Current cmdline:"
        echo "  $cmdline" | fold -w 70 -s | sed 's/^/    /'
    fi
    
    # Check for important parameters
    echo -e "\n  Checking critical parameters:"
    
    [[ "$cmdline" =~ pci=realloc ]] && test_pass "PCI reallocation enabled" || test_warn "PCI reallocation not enabled (pci=realloc)"
    [[ "$cmdline" =~ mitigations= ]] && test_pass "CPU mitigations configured" || test_warn "CPU mitigations not configured"
    [[ "$cmdline" =~ intel_iommu=on ]] && test_pass "Intel IOMMU enabled" || test_fail "Intel IOMMU not enabled"
    [[ "$cmdline" =~ nvidia-drm.modeset=1 ]] && test_pass "NVIDIA DRM modeset enabled" || test_warn "NVIDIA DRM modeset not enabled"
    [[ "$cmdline" =~ transparent_hugepage= ]] && test_pass "Transparent hugepages configured" || test_warn "Transparent hugepages not configured"
}

# 2. Check module configuration
check_modules() {
    print_header "MODULE CONFIGURATION CHECK"
    
    # Check blacklisted modules
    if [ -f /etc/modprobe.d/bazzite-blacklist.conf ]; then
        test_pass "Module blacklist configured"
        
        # Verify problematic modules are not loaded
        if ! lsmod | grep -q nct6687; then
            test_pass "NCT6687 module not loaded (correct)"
        else
            test_fail "NCT6687 module is loaded (should be blacklisted)"
        fi
        
        if ! lsmod | grep -q nvidia_peermem; then
            test_pass "nvidia_peermem not loaded (correct for open driver)"
        else
            test_warn "nvidia_peermem is loaded (incompatible with open driver)"
        fi
    else
        test_fail "Module blacklist not found"
    fi
    
    # Check gaming modules
    local gaming_modules=(i2c_dev fuse kvmfr uhid ntsync)
    for mod in "${gaming_modules[@]}"; do
        if lsmod | grep -q "^$mod " || [ -d "/sys/module/$mod" ]; then
            test_pass "Module $mod loaded"
        else
            test_warn "Module $mod not loaded"
        fi
    done
    
    # Check NVIDIA modules
    if lsmod | grep -q "^nvidia "; then
        test_pass "NVIDIA driver loaded"
        
        # Check if using open modules
        if modinfo nvidia 2>/dev/null | grep -q "license.*MIT"; then
            test_pass "Using NVIDIA open kernel modules"
        else
            test_warn "Using proprietary NVIDIA modules"
        fi
    else
        test_fail "NVIDIA driver not loaded"
    fi
}

# 3. Check network configuration
check_network() {
    print_header "NETWORK CONFIGURATION CHECK"
    
    # Check TCP congestion control
    local current_cc=$(sysctl -n net.ipv4.tcp_congestion_control 2>/dev/null)
    local available_cc=$(sysctl -n net.ipv4.tcp_available_congestion_control 2>/dev/null)
    
    echo "  Current congestion control: $current_cc"
    echo "  Available algorithms: $available_cc"
    
    if [[ "$available_cc" =~ bbr ]]; then
        if [ "$current_cc" = "bbr" ]; then
            test_pass "TCP BBR congestion control active"
        else
            test_warn "BBR available but not active (using $current_cc)"
        fi
    else
        if [ "$current_cc" = "cubic" ]; then
            test_pass "Using cubic (BBR not available)"
        else
            test_warn "BBR not available, using $current_cc"
        fi
    fi
    
    # Check Intel I225-V configuration
    local eth_dev=$(ip link | grep -E '^[0-9]+: (en|eth)' | head -1 | cut -d: -f2 | tr -d ' ')
    if [ -n "$eth_dev" ]; then
        echo -e "\n  Ethernet device: $eth_dev"
        
        # Check driver
        local driver=$(ethtool -i $eth_dev 2>/dev/null | grep "^driver:" | awk '{print $2}')
        if [ "$driver" = "igc" ]; then
            test_pass "Intel I225-V driver (igc) detected"
            
            # Check interrupt coalescing
            if ethtool -c $eth_dev 2>/dev/null | grep -q "rx-usecs: 0"; then
                test_pass "Interrupt coalescing optimized for low latency"
            else
                test_warn "Interrupt coalescing not optimized"
            fi
        else
            test_warn "Ethernet driver is $driver (expected igc for I225-V)"
        fi
    else
        test_warn "No ethernet device found"
    fi
}

# 4. Check USB fixes
check_usb() {
    print_header "USB DEVICE FIXES CHECK"
    
    # Check for ITE device issues
    if [ -f /etc/udev/rules.d/99-ite-usb-fix.rules ] || [ -f /etc/udev/rules.d/99-usb-gaming-fixes.rules ]; then
        test_pass "USB device fix rules installed"
        
        # Check if ITE device is still causing issues
        if dmesg | tail -100 | grep -q "048d:5702.*disabled by hub"; then
            test_fail "ITE USB device still showing disconnect issues"
        else
            test_pass "No recent ITE USB device issues detected"
        fi
    else
        test_warn "USB device fix rules not found"
    fi
    
    # Check for USB errors in last 100 kernel messages
    local usb_errors=$(dmesg | tail -100 | grep -c "USB.*error\|usb.*disabled" || true)
    if [ $usb_errors -eq 0 ]; then
        test_pass "No recent USB errors detected"
    else
        test_warn "Found $usb_errors USB-related errors in recent kernel log"
    fi
}

# 5. Check system groups
check_groups() {
    print_header "SYSTEM GROUPS CHECK"
    
    local required_groups=(audio disk kvm video render input)
    local missing_groups=()
    
    for group in "${required_groups[@]}"; do
        if getent group $group >/dev/null 2>&1; then
            test_pass "Group '$group' exists"
        else
            test_fail "Group '$group' missing"
            missing_groups+=($group)
        fi
    done
    
    if [ ${#missing_groups[@]} -eq 0 ]; then
        echo -e "\n  All required system groups present"
    else
        echo -e "\n  ${RED}Missing groups: ${missing_groups[*]}${NC}"
        echo "  Run: sudo groupadd <group_name> for each missing group"
    fi
}

# 6. Check GPU configuration
check_gpu() {
    print_header "GPU CONFIGURATION CHECK"
    
    if command -v nvidia-smi >/dev/null 2>&1; then
        # Get GPU info
        local gpu_name=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
        local gpu_driver=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1)
        
        echo "  GPU: $gpu_name"
        echo "  Driver: $gpu_driver"
        
        test_pass "NVIDIA driver operational"
        
        # Check for ReBAR support
        if nvidia-smi -q 2>/dev/null | grep -q "Resizable BAR.*Enabled"; then
            test_pass "Resizable BAR enabled"
        else
            test_warn "Resizable BAR not enabled"
        fi
        
        # Check power mode
        local power_mode=$(nvidia-smi --query-gpu=power.management --format=csv,noheader 2>/dev/null | head -1)
        if [ "$power_mode" = "Enabled" ]; then
            test_pass "GPU power management enabled"
        else
            test_warn "GPU power management disabled"
        fi
    else
        test_fail "nvidia-smi not available"
    fi
}

# 7. Check GRUB configuration
check_grub() {
    print_header "GRUB CONFIGURATION CHECK"
    
    if [ -f /etc/default/grub ]; then
        test_pass "GRUB configuration file exists"
        
        # Check for backup
        if ls /etc/default/grub.bazzite-backup* >/dev/null 2>&1; then
            test_pass "GRUB backup exists"
        else
            test_warn "No GRUB backup found"
        fi
        
        # Check if GRUB cmdline has our parameters
        if grep -q "GRUB_CMDLINE_LINUX.*pci=realloc" /etc/default/grub; then
            test_pass "PCI reallocation in GRUB config"
        else
            test_warn "PCI reallocation not in GRUB config"
        fi
    else
        test_fail "GRUB configuration file not found"
    fi
}

# 8. Check sysctl settings
check_sysctl() {
    print_header "SYSCTL CONFIGURATION CHECK"
    
    if [ -f /etc/sysctl.d/99-gaming-optimizations.conf ]; then
        test_pass "Gaming sysctl configuration exists"
        
        # Check key parameters
        local swappiness=$(sysctl -n vm.swappiness 2>/dev/null)
        echo "  vm.swappiness = $swappiness"
        
        if [ "$swappiness" -gt 60 ]; then
            test_pass "Swappiness optimized for ZRAM ($swappiness)"
        else
            test_warn "Swappiness may be too low for ZRAM ($swappiness)"
        fi
        
        # Check network buffer sizes
        local rmem_max=$(sysctl -n net.core.rmem_max 2>/dev/null)
        if [ "$rmem_max" -ge 134217728 ]; then
            test_pass "Network buffers optimized for gaming"
        else
            test_warn "Network buffers not fully optimized"
        fi
    else
        test_fail "Gaming sysctl configuration not found"
    fi
}

# 9. Performance validation
check_performance() {
    print_header "PERFORMANCE VALIDATION"
    
    # Check CPU frequency governor
    local governor=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null)
    echo "  CPU Governor: $governor"
    
    case "$governor" in
        performance)
            test_pass "CPU governor set to performance"
            ;;
        schedutil|ondemand)
            test_warn "CPU governor is $governor (not optimal for gaming)"
            ;;
        powersave)
            test_fail "CPU governor is powersave (bad for gaming)"
            ;;
        *)
            test_warn "Unknown CPU governor: $governor"
            ;;
    esac
    
    # Check if turbo boost is enabled
    if [ -f /sys/devices/system/cpu/intel_pstate/no_turbo ]; then
        local no_turbo=$(cat /sys/devices/system/cpu/intel_pstate/no_turbo)
        if [ "$no_turbo" = "0" ]; then
            test_pass "Intel Turbo Boost enabled"
        else
            test_fail "Intel Turbo Boost disabled"
        fi
    fi
    
    # Check C-state configuration
    if [ -f /sys/module/intel_idle/parameters/max_cstate ]; then
        local max_cstate=$(cat /sys/module/intel_idle/parameters/max_cstate)
        echo "  Max C-State: $max_cstate"
        if [ "$max_cstate" -le 1 ]; then
            test_pass "C-States limited for low latency"
        else
            test_warn "C-States not fully limited (max: $max_cstate)"
        fi
    fi
}

# Main execution
main() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     Bazzite Boot Configuration Validation Script v4.1      ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    
    # Run all checks
    check_kernel_params
    check_modules
    check_network
    check_usb
    check_groups
    check_gpu
    check_grub
    check_sysctl
    check_performance
    
    # Summary
    print_header "VALIDATION SUMMARY"
    
    echo -e "\n  Results:"
    echo -e "  ${GREEN}Passed:${NC}   $PASSED"
    echo -e "  ${YELLOW}Warnings:${NC} $WARNINGS"
    echo -e "  ${RED}Failed:${NC}   $FAILED"
    
    local total=$((PASSED + WARNINGS + FAILED))
    local score=$((PASSED * 100 / total))
    
    echo -e "\n  Score: $score%"
    
    if [ $FAILED -eq 0 ]; then
        echo -e "\n  ${GREEN}✓ All critical checks passed!${NC}"
    else
        echo -e "\n  ${RED}✗ Some critical checks failed. Review the output above.${NC}"
    fi
    
    if [ $WARNINGS -gt 0 ]; then
        echo -e "  ${YELLOW}⚠ Some warnings detected. Consider addressing them.${NC}"
    fi
    
    # Recommendations
    if [ $FAILED -gt 0 ] || [ $WARNINGS -gt 5 ]; then
        echo -e "\n${BLUE}Recommendations:${NC}"
        echo "  1. Run the bazzite-optimizer.py script with appropriate profile"
        echo "  2. Reboot the system after applying fixes"
        echo "  3. Run this validation script again after reboot"
    fi
    
    # Check if reboot is needed
    if [ -f /var/run/reboot-required ]; then
        echo -e "\n${YELLOW}⚠ System reboot required to apply all changes${NC}"
    fi
    
    exit $([ $FAILED -eq 0 ] && echo 0 || echo 1)
}

# Check if running as root for full validation
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}Note: Running as non-root. Some checks may be limited.${NC}"
    echo "For complete validation, run: sudo $0"
    echo
fi

main "$@"
