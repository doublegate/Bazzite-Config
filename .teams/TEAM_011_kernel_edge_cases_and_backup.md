# TEAM_011: Kernel Edge Cases & Backup/Switch Feature

## Mission
1. Identify kernel param edge cases for user's system
2. Implement kernel param backup/restore/switch functionality

## User's System Profile
- **CPU**: Intel i5-1240P (12th Gen Alder Lake)
  - **Hybrid Architecture**: 4 P-cores + 8 E-cores = 12 cores / 16 threads
  - **Special consideration**: P-cores vs E-cores scheduling
- **GPU**: eGPU via Thunderbolt (RTX 3060 in Razer Core X)
- **Platform**: Ultramarine Linux 43 (GRUB-based)

---

## Phase 1: Edge Cases Not Handled

### 1. Alder Lake Hybrid CPU
| Issue | Current State | Impact |
|-------|---------------|--------|
| `isolcpus` for E-cores | Hardcoded `4-9` | ❌ Wrong for this CPU topology |
| `nohz_full` | Hardcoded ranges | ❌ May target wrong cores |
| Intel Thread Director | Not considered | ⚠️ May conflict with manual scheduling |
| `intel_pstate` | Generic | ⚠️ Alder Lake has specific modes |

**Current hardcoded values** (from optimizer):
```python
"nohz_full=4-9 isolcpus=4-9 rcu_nocbs=4-9"  # Wrong for user's CPU!
```

**User's actual topology**:
- CPUs 0-7: P-cores (performance)
- CPUs 8-15: E-cores (efficiency)

### 2. eGPU via Thunderbolt
| Issue | Current State | Impact |
|-------|---------------|--------|
| PCIe params for eGPU | Generic | May not be optimal |
| Thunderbolt hotplug | Not handled | Could crash if eGPU disconnects |
| External PCIe latency | Not tuned | Higher latency than internal |

**Missing params for eGPU**:
```
pcie_port_pm=off          # Disable PCIe power management for eGPU
thunderbolt.force_power=1 # Keep Thunderbolt powered
```

### 3. Kernel Param Backup/Switch
| Issue | Current State | Impact |
|-------|---------------|--------|
| Baseline snapshot | ❌ None | Can't restore original |
| Stock vs Optimized | ❌ No switch | Must manually edit GRUB |
| Profile-based params | ❌ Limited | Can't switch gaming profiles |

---

## Phase 2: Design - Kernel Param Backup/Switch

### Proposed Solution

```
/var/lib/bazzite-optimizer/kernel-profiles/
├── baseline.conf          # Original params before any optimization
├── current.conf           # Currently applied params
├── balanced.conf          # Balanced gaming profile
├── competitive.conf       # Low-latency competitive profile
└── stock.conf             # Restore to stock params
```

### New CLI Commands
```bash
# Backup current (stock) params before first optimization
sudo ./bazzite-optimizer.py --save-baseline

# Switch between profiles
sudo ./bazzite-optimizer.py --kernel-profile stock
sudo ./bazzite-optimizer.py --kernel-profile balanced
sudo ./bazzite-optimizer.py --kernel-profile competitive

# List available kernel profiles
sudo ./bazzite-optimizer.py --list-kernel-profiles

# Show diff between current and target profile
sudo ./bazzite-optimizer.py --kernel-diff balanced
```

### Implementation Location
- `platforms/traditional/grub.py` — Add profile management
- `bazzite-optimizer.py` — Add CLI commands

---

## Phase 3: Implementation Plan

### Step 1: Add kernel profile storage to GrubKernelParams
- Create profile directory structure
- Save/load profile methods
- Baseline capture on first run

### Step 2: Fix Alder Lake CPU detection
- Detect hybrid CPU topology
- Generate correct isolcpus ranges for E-cores
- Add Intel Thread Director awareness

### Step 3: Add eGPU-specific kernel params
- Detect Thunderbolt eGPU
- Add PCIe power management params
- Add Thunderbolt-specific tuning

### Step 4: Add CLI commands
- `--save-baseline`
- `--kernel-profile <name>`
- `--list-kernel-profiles`
- `--kernel-diff <name>`

---

## Status
- [x] Edge case analysis complete
- [ ] Implement kernel profile management
- [ ] Fix Alder Lake CPU handling
- [ ] Add eGPU kernel params
- [ ] Add CLI commands
