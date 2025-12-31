# TEAM_010: Kernel Security Investigation

## Mission
Thorough investigation of kernel parameters, modules, and system integrity to check for anything malicious or problematic.

## System Info
- **OS**: Ultramarine Linux 43
- **Kernel**: 6.17.12-300.fc43.x86_64
- **Boot**: GRUB + BTRFS

---

## Phase 1: Current Kernel Parameters

### Boot Command Line
```
BOOT_IMAGE=(hd0,gpt2)/vmlinuz-6.17.12-300.fc43.x86_64 
root=UUID=f1de89ad-0fe6-4c20-ad2b-19d2e80cc7c0 ro 
rootflags=subvol=root 
rhgb quiet 
rd.driver.blacklist=nouveau,nova_core 
modprobe.blacklist=nouveau,nova_core
```

### Analysis
| Parameter | Purpose | Status |
|-----------|---------|--------|
| `rhgb` | Red Hat Graphical Boot | ✅ Normal |
| `quiet` | Suppress boot messages | ✅ Normal |
| `rd.driver.blacklist=nouveau` | Block nouveau for NVIDIA | ✅ Expected for NVIDIA |
| `modprobe.blacklist=nouveau` | Block nouveau at modprobe | ✅ Expected for NVIDIA |
| `rootflags=subvol=root` | BTRFS subvolume | ✅ Normal |

**No suspicious parameters found.**

---

## Phase 2: Kernel Taint Status

**Taint Value**: 12288 (0x3000)

Decoded flags:
- Bit 12 (4096): `O` — Out-of-tree module loaded
- Bit 13 (8192): `E` — Unsigned module loaded

**Cause**: NVIDIA proprietary driver (expected)
```
nvidia: loading out-of-tree module taints kernel.
nvidia: module verification failed: signature and/or required key missing
```

**Verdict**: ✅ Normal for systems with NVIDIA proprietary drivers.

---

## Phase 3: Kernel Modules Audit

### High-Risk Module Check
| Module | Status | Notes |
|--------|--------|-------|
| nvidia/nvidia_drm/nvidia_modeset/nvidia_uvm | ✅ Expected | NVIDIA driver |
| tun | ✅ Normal | VPN/container networking |
| rfcomm/bnep | ✅ Normal | Bluetooth |
| nf_tables/nft_* | ✅ Normal | Firewall |
| binfmt_misc | ✅ Normal | Binary format support |

### Suspicious Module Search
**No unknown or suspicious modules found.**

All loaded modules are:
- Standard kernel modules
- NVIDIA proprietary drivers
- Sound subsystem (snd_*)
- Network (nf_*, iwl*, mac80211)
- Storage (nvme, btrfs)
- Thunderbolt

---

## Phase 4: Security Posture

| Security Feature | Status | Notes |
|------------------|--------|-------|
| **ASLR** | ✅ Enabled (2) | Full randomization |
| **SELinux** | ✅ Enforcing | Active protection |
| **Kernel Lockdown** | ⚠️ None | Not locked down |
| **kptr_restrict** | ⚠️ 0 | Kernel pointers exposed |
| **modules_disabled** | ⚠️ 0 | Can load modules |
| **ld.so.preload** | ✅ Clean | No preload hijacking |

### Recommendations
1. **kptr_restrict=1** — Hide kernel pointers from non-root
2. Consider **lockdown=integrity** for higher security

---

## Phase 5: Network Audit

### Listening Services (Non-Localhost)
| Port | Service | Status |
|------|---------|--------|
| 27036/tcp,udp | Steam | ✅ Expected |
| 5353/udp | Avahi (mDNS) | ✅ Normal |
| 5355/tcp,udp | LLMNR | ✅ Normal |
| 1716/tcp,udp | KDE Connect | ✅ Normal |
| 41641/udp | Tailscale | ✅ Expected |
| 55197/tcp | Tailscale | ✅ Expected |

**No suspicious network listeners found.**

---

## Phase 6: Kernel Errors

### dmesg Errors
| Error | Severity | Impact |
|-------|----------|--------|
| `thunderbolt 1-1: failed to initialize port 1` | ⚠️ Warning | Thunderbolt port init issue |
| `INT3515: IRQ index 1 not found` | ⚠️ Warning | I2C device init issue |
| `asus_wmi: fan_curve_get_factory_default failed` | ℹ️ Info | ASUS WMI not fully supported |

**None of these are security concerns** — they're hardware compatibility warnings.

---

## Verdict: ✅ CLEAN

### Summary
| Category | Status |
|----------|--------|
| Kernel Parameters | ✅ Clean |
| Kernel Modules | ✅ Clean |
| Rootkit Indicators | ✅ None found |
| Network Listeners | ✅ All legitimate |
| Security Features | ✅ SELinux enforcing |
| System Integrity | ✅ No tampering detected |

### Notes
1. **Kernel taint** is ONLY from NVIDIA driver (expected)
2. **No malicious code** or rootkit indicators found
3. **SELinux is enforcing** — strong security baseline
4. **Thunderbolt errors** are hardware-related, not security

### Minor Hardening Suggestions (Optional)
```bash
# Hide kernel pointers
echo 1 | sudo tee /proc/sys/kernel/kptr_restrict

# Make persistent in /etc/sysctl.d/99-security.conf:
# kernel.kptr_restrict = 1
```

---

## Handoff
System is clean. No malicious activity detected. Ready for gaming optimization.
