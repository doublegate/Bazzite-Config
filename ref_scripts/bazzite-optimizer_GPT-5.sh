#!/usr/bin/env bash
set -euo pipefail

# Bazzite DX "Master" Optimizer — i9-10850K / RTX 5080 / 64GB
# Safe to re-run. Requires: sudo.
# Logs: /var/log/bazzite-master-optimize.log

LOG=/var/log/bazzite-master-optimize.log
exec > >(tee -a "$LOG") 2>&1

need_reboot=false
need_relogin=false

red()   { printf "\033[31m%s\033[0m\n" "$*"; }
green() { printf "\033[32m%s\033[0m\n" "$*"; }
yellow(){ printf "\033[33m%s\033[0m\n" "$*"; }

require_root() {
  if [[ $EUID -ne 0 ]]; then
    red "Please run as root (use: sudo $0)"; exit 1
  fi
}
require_cmds() {
  local missing=()
  for c in "$@"; do command -v "$c" >/dev/null 2>&1 || missing+=("$c"); done
  if (( ${#missing[@]} )); then
    red "Missing required commands: ${missing[*]}"; exit 1
  fi
}

require_root
require_cmds awk sed grep sysctl findmnt lsblk flatpak

# ---------- Detect OS ----------
. /etc/os-release || true
echo "Detected OS: ${PRETTY_NAME:-unknown}"

# ---------- Helper: write file if content differs ----------
write_file() {
  local path="$1"; shift
  local content="$*"
  if [[ -f "$path" ]] && diff -q <(printf "%s" "$content") "$path" >/dev/null 2>&1; then
    echo "No change: $path"
  else
    mkdir -p "$(dirname "$path")"
    printf "%s" "$content" > "$path"
    echo "Updated: $path"
  fi
}

# ---------- CPU: cpupower + performance toggle ----------
if ! command -v cpupower >/dev/null 2>&1; then
  echo "Installing cpupower via rpm-ostree..."
  rpm-ostree install kernel-tools || true
  need_reboot=true
fi

# Performance toggle scripts
write_file /usr/local/bin/performance-on.sh \
'#!/usr/bin/env bash
set -euo pipefail
# Set CPU governor to performance (all policies)
if command -v cpupower >/dev/null 2>&1; then
  cpupower frequency-set -g performance || true
fi
# NVIDIA: Prefer Maximum Performance during high-load window
if command -v nvidia-settings >/dev/null 2>&1; then
  # GPUPowerMizerMode=1 => prefer max performance
  nvidia-settings -a "[gpu:0]/GPUPowerMizerMode=1" >/dev/null 2>&1 || true
fi
echo "Performance mode ON"
'
chmod +x /usr/local/bin/performance-on.sh

write_file /usr/local/bin/performance-off.sh \
'#!/usr/bin/env bash
set -euo pipefail
# Revert CPU governor to schedutil where supported
if command -v cpupower >/dev/null 2>&1; then
  cpupower frequency-set -g schedutil || cpupower frequency-set -g ondemand || true
fi
# NVIDIA: revert to adaptive/auto (2 is adaptive; some drivers map 0/1/2 differently)
if command -v nvidia-settings >/dev/null 2>&1; then
  nvidia-settings -a "[gpu:0]/GPUPowerMizerMode=2" >/dev/null 2>&1 || true
fi
echo "Performance mode OFF"
'
chmod +x /usr/local/bin/performance-off.sh

# One-shot systemd service to toggle performance mode
write_file /etc/systemd/system/performance-toggle.service \
'[Unit]
Description=Toggle Performance Mode (ON/OFF via systemctl start/stop)
After=multi-user.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/local/bin/performance-on.sh
ExecStop=/usr/local/bin/performance-off.sh

[Install]
WantedBy=multi-user.target
'
systemctl daemon-reload
systemctl enable performance-toggle.service >/dev/null 2>&1 || true

echo "Tip: Use 'sudo systemctl start performance-toggle' before a heavy session; 'stop' to revert."

# ---------- GameMode: system-wide config ----------
# Ensures CPU governor + NVIDIA PowerMizer bump only while GameMode is active.
write_file /etc/gamemode.ini \
'[general]
; Verbose logs can help verify activation
verbose=false

[cpu]
; Let gamemode try governor change (will revert afterwards)
desiredgov=performance
softrealtime=true

[gpu]
; NVIDIA: 1 = Prefer Maximum Performance while in GameMode
apply_gpu_optimizations=true
nv_powermizer_mode=1

[custom]
; hooks (optional)
; start=/usr/local/bin/performance-on.sh
; end=/usr/local/bin/performance-off.sh
'
systemctl restart gamemoded.service >/dev/null 2>&1 || true

# ---------- NVIDIA: Coolbits (for fan/OC control on Xorg) ----------
# Safe on Wayland; only takes effect for Xorg sessions / tools like nvidia-settings.
write_file /etc/X11/xorg.conf.d/90-nvidia-coolbits.conf \
'Section "Device"
    Identifier     "Nvidia0"
    Driver         "nvidia"
    Option         "Coolbits" "28"
EndSection
'
need_relogin=true

# ---------- Btrfs: tune /var/mnt/Data_SSD if present ----------
DATA_MNT="/var/mnt/Data_SSD"
if findmnt -n -o FSTYPE "$DATA_MNT" 2>/dev/null | grep -qi btrfs; then
  UUID=$(findmnt -no SOURCE "$DATA_MNT" | xargs lsblk -no UUID 2>/dev/null | head -n1 || true)
  if [[ -n "${UUID:-}" ]]; then
    FSTAB=/etc/fstab
    LINE="UUID=${UUID} ${DATA_MNT} btrfs rw,noatime,compress=zstd:1,ssd,discard=async,space_cache=v2 0 0"
    if grep -q " ${DATA_MNT} " "$FSTAB"; then
      # Replace existing line for that mountpoint
      awk -v mnt=" ${DATA_MNT} " -v rep="$LINE" '
        BEGIN{changed=0}
        $0 ~ mnt {print rep; changed=1; next}
        {print}
        END{if(changed==0) print rep}
      ' "$FSTAB" > "${FSTAB}.tmp" && mv "${FSTAB}.tmp" "$FSTAB"
    else
      echo "$LINE" >> "$FSTAB"
    fi
    echo "fstab updated for ${DATA_MNT} (Btrfs tuned options)."
    # Apply live options where possible
    mount -o remount,"noatime,compress=zstd:1,ssd,discard=async,space_cache=v2" "$DATA_MNT" || true
  else
    yellow "Could not resolve UUID for ${DATA_MNT}; skipped fstab tune."
  fi
else
  echo "No Btrfs mount at ${DATA_MNT}; skipping Btrfs tuning for data drive."
fi

# Enable btrfs maintenance timers if present
for tmr in btrfsmaintenance-refresh.timer btrfs-balance.timer btrfs-scrub@-.timer; do
  if systemctl list-unit-files | grep -q "^$tmr"; then
    systemctl enable --now "$tmr" || true
    echo "Enabled: $tmr"
  fi
done

# ---------- ZRAM: 50% RAM, zstd compression ----------
write_file /etc/modules-load.d/zstd.conf 'zstd'
if ! lsmod | grep -q '^zstd'; then modprobe zstd || true; fi

write_file /etc/systemd/zram-generator.conf \
'[zram0]
zram-fraction=0.5
# Cap (MiB): optional; comment to let fraction decide
#max-zram-size=32768
compression-algorithm=zstd
'
# Try (re)start without reboot
if systemctl list-unit-files | grep -q 'zram-generator'; then
  systemctl daemon-reload
  if systemctl restart systemd-zram-setup@zram0.service 2>/dev/null; then
    echo "zram reconfigured (zstd, 50% RAM)."
  else
    yellow "zram restart failed; will apply on next boot."
    need_reboot=true
  fi
else
  echo "zram-generator not detected as a unit; changes will apply on next boot."
  need_reboot=true
fi

# ---------- sysctl tuning ----------
write_file /etc/sysctl.d/99-bazzite-tuning.conf \
'vm.swappiness = 20
vm.vfs_cache_pressure = 50
'
sysctl -p /etc/sysctl.d/99-bazzite-tuning.conf || true

# ---------- Flatpaks & overrides (Android Studio, Blender, Flatseal, ProtonUp-Qt) ----------
# Install useful tools if not present
FLATS=(
  com.github.tchx84.Flatseal
  com.github.FroggingFamily.ProtonUp-Qt
  org.blender.Blender
  com.google.AndroidStudio
)
for app in "${FLATS[@]}"; do
  if ! flatpak info "$app" >/dev/null 2>&1; then
    flatpak install -y flathub "$app" || true
  fi
done

# Android Studio: allow KVM (emulator acceleration)
flatpak override --user --device=kvm com.google.AndroidStudio || true
# Blender: allow access to data SSD (adjust path if you use a different mount)
if [[ -d "$DATA_MNT" ]]; then
  flatpak override --user --filesystem="$DATA_MNT:rw" org.blender.Blender || true
fi

# ---------- Game tooling tips (no-op but documented) ----------
cat >/usr/local/share/bazzite-gaming-notes.txt <<'TXT'
Steam per-game (Proton, NVAPI/DLSS/RTX):
  PROTON_ENABLE_NVAPI=1 DXVK_ENABLE_NVAPI=1 PROTON_HIDE_NVIDIA_GPU=0 %command%

MangoHUD:
  Use: MANGOHUD=1 %command%  (or set a MangoHud.conf in ~/.config/MangoHud/)
Gamescope example (1080p→4K@120Hz):
  gamescope -w 1920 -h 1080 -r 120 -f -- %command%
TXT

# ---------- Optional: local LLM server (vLLM) systemd unit (disabled by default) ----------
write_file /etc/systemd/system/vllm.service \
'[Unit]
Description=vLLM model server (disabled by default)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User='"$(logname)"'
Environment=HF_HOME=%h/.cache/huggingface
WorkingDirectory=%h
ExecStart=/usr/bin/env bash -lc '"'"'if ! command -v vllm >/dev/null; then pipx install vllm || pip install --user vllm; fi; \
  vllm serve --host 127.0.0.1 --port 8000 --model meta-llama/Llama-3.1-8B-Instruct'"'"'
Restart=on-failure
# Hardening (loosen if you serve remotely)
NoNewPrivileges=yes
ProtectSystem=strict
PrivateTmp=yes
ProtectHome=read-only

[Install]
WantedBy=multi-user.target
'
systemctl daemon-reload
echo "vLLM service installed (disabled). Enable with: systemctl --user or systemctl enable --now vllm (edit model first)."

# ---------- Final status ----------
$need_reboot   && yellow "Reboot recommended to apply all changes (rpmostree layering, zram)."
$need_relogin  && yellow "Log out/in (or restart Xorg session) for NVIDIA Coolbits to load."

green "All done. Review ${LOG} for details."
