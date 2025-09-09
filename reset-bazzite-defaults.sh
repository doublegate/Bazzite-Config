#!/usr/bin/env bash
set -euo pipefail
#
# reset-bazzite-defaults.sh
#
# Targeted reset for rpm-ostree (Bazzite DX) systems:
#   - Reset kernel args (kargs) to image defaults
#   - Restore /etc from /usr/etc with SAFE exclusions
#   - Keep layered packages intact
#   - Optionally reset repo files
#   - Create backups and support a one-shot rollback
#
# Design goals:
#   * Safe-by-default: preserve identity, connectivity, and secrets
#   * Idempotent: repeatable with minimal side effects
#   * Auditable: backup /etc and kargs; show config diff after changes
#
# Flags:
#   --dry-run            : plan only
#   --no-kargs           : do not touch kernel args
#   --no-etc             : do not sync /etc from /usr/etc
#   --no-repos           : skip repo reset
#   --only-repos         : only reset repos (implies no kargs, no etc sync)
#   --aggressive         : do not exclude anything under /etc (dangerous)
#   --backup-dir DIR     : set backup dir
#   --rollback           : restore /etc and kargs from a backup
#   --list-backups       : list available backups
#   --no-reboot-prompt   : do not print reboot guidance
#   --verbose            : extra logging
#
# Usage examples:
#   sudo bash reset-bazzite-defaults.sh --dry-run
#   sudo bash reset-bazzite-defaults.sh
#   sudo bash reset-bazzite-defaults.sh --no-repos
#   sudo bash reset-bazzite-defaults.sh --aggressive
#   sudo bash reset-bazzite-defaults.sh --only-repos
#   sudo bash reset-bazzite-defaults.sh --rollback
#   sudo bash reset-bazzite-defaults.sh --list-backups
#
# Notes:
#   * Layered RPMs remain installed.
#   * "Reset kargs" = clear overrides so image defaults apply at next boot.
#   * SAFE exclusions protect common stateful service configs and secrets.
#   * To tune exclusions, edit SAFE_EXCLUDES below or add toggles if desired.
#

DRY_RUN=0
DO_KARGS=1
DO_ETC=1
DO_REPOS=1
ONLY_REPOS=0
AGGRESSIVE=0
BACKUP_DIR=""
REBOOT_PROMPT=1
VERBOSE=0
DO_ROLLBACK=0
LIST_BACKUPS=0

log()  { echo "[*] $*"; }
vlog() { (( VERBOSE )) && echo "[v] $*"; }
err()  { echo "[!] $*" >&2; }

need_bin() {
  command -v "$1" >/dev/null 2>&1 || {
    err "Missing dependency: $1"
    exit 1
  }
}

usage() { grep '^# ' "$0" | sed 's/^# //'; }

list_backups() {
  ls -1dt /var/backups/bazzite-reset-* 2>/dev/null || true
}

# ----------------------------- Arg parsing -----------------------------------

while (( $# )); do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --no-kargs) DO_KARGS=0 ;;
    --no-etc) DO_ETC=0 ;;
    --no-repos) DO_REPOS=0 ;;
    --only-repos)
      ONLY_REPOS=1
      DO_KARGS=0
      DO_ETC=0
      DO_REPOS=1
      ;;
    --aggressive) AGGRESSIVE=1 ;;
    --backup-dir) shift; BACKUP_DIR="${1:-}" ;;
    --rollback) DO_ROLLBACK=1 ;;
    --list-backups) LIST_BACKUPS=1 ;;
    --no-reboot-prompt) REBOOT_PROMPT=0 ;;
    --verbose) VERBOSE=1 ;;
    -h|--help) usage; exit 0 ;;
    *)
      err "Unknown option: $1"
      usage
      exit 2
      ;;
  esac
  shift
done

if (( LIST_BACKUPS )); then
  list_backups
  exit 0
fi

# --------------------------- Pre-flight checks -------------------------------

if [[ $EUID -ne 0 ]]; then
  err "Run as root (sudo)."
  exit 1
fi

need_bin rpm-ostree
need_bin rsync
need_bin awk
need_bin date
command -v zstd >/dev/null 2>&1 || true
command -v bootctl >/dev/null 2>&1 || true
command -v ostree >/dev/null 2>&1 || true

if ! rpm-ostree status >/dev/null 2>&1; then
  err "rpm-ostree status failed. Not an rpm-ostree system?"
  exit 1
fi

# --------------------------- Backup directory --------------------------------

TS="$(date +%Y%m%d-%H%M%S)"
if [[ -z "${BACKUP_DIR}" ]]; then
  BACKUP_DIR="/var/backups/bazzite-reset-${TS}"
fi
mkdir -p "${BACKUP_DIR}"
STATE_MD="${BACKUP_DIR}/STATE.txt"

# ------------------------------ State capture --------------------------------

write_state() {
  {
    echo "Timestamp: ${TS}"
    echo "Host: $(hostnamectl --static 2>/dev/null || echo unknown)"
    echo "OS: $(grep PRETTY_NAME /etc/os-release 2>/dev/null || true)"
    echo "Kernel: $(uname -r)"
    echo "--- rpm-ostree status ---"
    rpm-ostree status || true
  } > "${STATE_MD}"
}

# ------------------------------- Backups -------------------------------------

backup_etc() {
  log "Backup /etc → ${BACKUP_DIR}/etc.(dir,tar)"
  if (( DRY_RUN )); then
    vlog "[dry-run] skip /etc backup"
    return
  fi
  mkdir -p "${BACKUP_DIR}/etc"
  rsync -aHAX --numeric-ids /etc/ "${BACKUP_DIR}/etc/"
  if command -v zstd >/dev/null 2>&1; then
    tar --xattrs --xattrs-include='*' --acls --selinux \
      -C / -cf - etc \
      | zstd -19 -T0 -o "${BACKUP_DIR}/etc.tar.zst"
  else
    tar --xattrs --xattrs-include='*' --acls --selinux \
      -C / -czf "${BACKUP_DIR}/etc.tar.gz" etc
  fi
}

backup_kargs() {
  log "Backup kargs → ${BACKUP_DIR}/kargs.txt"
  if (( DRY_RUN )); then
    vlog "[dry-run] skip kargs backup"
    return
  fi
  {
    echo "EFFECTIVE_KARGS=$(cat /proc/cmdline 2>/dev/null || true)"
    echo
    echo "--- rpm-ostree kargs (current) ---"
    rpm-ostree kargs || true
    echo
    if command -v bootctl >/dev/null 2>&1; then
      echo "--- bootctl status (snippet) ---"
      bootctl status 2>/dev/null | sed -n '1,120p' || true
    fi
  } > "${BACKUP_DIR}/kargs.txt"
}

# ------------------------------ Kargs reset ----------------------------------

reset_kargs() {
  log "Reset kernel args (clear overrides → image defaults)"
  if (( DRY_RUN )); then
    vlog "[dry-run] rpm-ostree kargs --delete-all"
    return
  fi
  rpm-ostree kargs --delete-all
  echo "--- New kargs (view) ---" >> "${BACKUP_DIR}/kargs.txt"
  rpm-ostree kargs >> "${BACKUP_DIR}/kargs.txt" || true
}

# ---------------------- SAFE exclusions for /etc sync ------------------------
# The following array controls what is preserved when syncing /usr/etc → /etc.
# Categories and rationale are provided. Adjust to your environment as needed.
#
# Rule of thumb:
#   * Preserve identity, network, secrets, and stateful service configs.
#   * If you want a clean slate for a category, remove it from this list.

SAFE_EXCLUDES=(
  # --- Identity and host specifics
  "/etc/machine-id"             # unique system identity
  "/etc/hostname"               # host name
  "/etc/hosts"                  # local name resolution
  "/etc/fstab"                  # mounts
  "/etc/crypttab"               # LUKS mappings
  "/etc/localtime"              # timezone link
  "/etc/adjtime"                # hwclock state
  "/etc/cryptsetup-*"           # cryptsetup confs

  # --- Secure shell and network essentials
  "/etc/ssh"                    # SSH host keys and daemon config
  "/etc/NetworkManager/system-connections"  # saved net profiles
  "/etc/resolv.conf"            # resolver (may be managed)

  # --- Requested preserves (VPN snapshots and backups)
  "/etc/wireguard"              # WireGuard keys and confs
  "/etc/snapper"                # snapper config sets
  "/etc/timeshift*"             # timeshift metadata and cfg
  "/etc/default/timeshift"      # timeshift defaults

  # --- Virtualization and containers
  "/etc/libvirt"                # VM defs, nets, storage pools
  "/etc/qemu"                   # QEMU config
  "/etc/vbox"                   # VirtualBox system config
  "/etc/lxc"                    # LXC config
  "/etc/lxd"                    # LXD config
  "/etc/docker"                 # docker daemon.json, regs
  "/etc/podman"                 # podman system config
  "/etc/containers"             # storage.conf, registries

  # --- Flatpak and session defaults
  "/etc/flatpak"                # remotes, overrides
  "/etc/dconf"                  # default dconf DB

  # --- Dev tooling and PKI
  "/etc/pki"                    # trust anchors and certs
  "/etc/gnupg"                  # system GnuPG cfg (rare)
  "/etc/gpg"                    # alt GPG path (rare)

  # --- Systemd and security policy
  "/etc/systemd"                # unit files, drop-ins
  "/etc/security"               # PAM and limits
  "/etc/sudoers"                # sudo main file
  "/etc/sudoers.d"              # sudo drop-ins

  # --- VPN suites
  "/etc/openvpn"                # OpenVPN
  "/etc/strongswan"             # strongSwan IPSec
  "/etc/ipsec.d"                # IPSec content
  "/etc/tailscale"              # Tailscale state

  # --- Storage stacks and RAID
  "/etc/zfs"                    # ZFS module and pools
  "/etc/mdadm"                  # mdadm RAID conf
  "/etc/ceph"                   # Ceph cluster conf
  "/etc/multipath.conf"         # multipath

  # --- Desktop, audio, and app defaults
  "/etc/X11"                    # Xorg confs (GPU/monitors)
  "/etc/xdg"                    # app defaults and menus
  "/etc/alsa"                   # ALSA conf
  "/etc/pulse"                  # PulseAudio conf

  # --- Time sync, firewall, and log policy
  "/etc/chrony.conf"            # chrony time sync
  "/etc/ntp.conf"               # ntpd time sync
  "/etc/firewalld"              # firewalld zones
  "/etc/ufw"                    # ufw rules
  "/etc/logrotate.d"            # logrotate rules

  # --- Kernel, modules, and udev rules
  "/etc/sysctl.conf"            # sysctl base
  "/etc/sysctl.d"               # sysctl drop-ins
  "/etc/modprobe.d"             # kernel mod params
  "/etc/udev/rules.d"           # device rules
)

# ---------------------------- /etc restoration -------------------------------

restore_etc() {
  if [[ ! -d "/usr/etc" ]]; then
    err "/usr/etc not found; cannot sync."
    return 1
  fi
  log "Restore /etc from /usr/etc (safe exclusions unless aggressive)"
  local RSYNC_ARGS
  RSYNC_ARGS=(-aHAX --delete --numeric-ids)
  if (( ! AGGRESSIVE )); then
    for p in "${SAFE_EXCLUDES[@]}"; do
      RSYNC_ARGS+=(--exclude="${p#/}")
    done
    log "Using SAFE exclusions (identity, net, secrets, services)"
  else
    log "AGGRESSIVE: NO exclusions (destructive)"
  fi
  if (( DRY_RUN )); then
    echo "[dry-run] rsync ${RSYNC_ARGS[*]} /usr/etc/ /etc/"
    return
  fi
  rsync "${RSYNC_ARGS[@]}" /usr/etc/ /etc/
}

# ----------------------------- Repo reset ------------------------------------

reset_repos() {
  log "Reset /etc/yum.repos.d to image defaults"
  if (( DRY_RUN )); then
    vlog "[dry-run] rm repos; cp from /usr/etc/yum.repos.d/"
    return
  fi
  mkdir -p /etc/yum.repos.d
  rm -f /etc/yum.repos.d/*.repo || true
  if [[ -d /usr/etc/yum.repos.d ]]; then
    cp -a /usr/etc/yum.repos.d/*.repo /etc/yum.repos.d/ 2>/dev/null \
      || true
  fi
}

# ----------------------------- Diff for audit --------------------------------

config_diff() {
  if ! command -v ostree >/dev/null 2>&1; then
    return 0
  fi
  log "Config diff vs image (post-ops)"
  if (( DRY_RUN )); then
    vlog "[dry-run] ostree admin config-diff"
  else
    ostree admin config-diff || true
  fi
}

# ----------------------------- Rollback logic --------------------------------

find_latest_backup() {
  list_backups | head -n1 || true
}

restore_etc_from_backup() {
  local src="${1}/etc"
  if [[ ! -d "${src}" ]]; then
    err "No etc backup in ${1}"
    return 1
  fi
  log "Restore /etc from backup ${src}"
  if (( DRY_RUN )); then
    echo "[dry-run] rsync -aHAX --delete --numeric-ids ${src}/ /etc/"
    return
  fi
  rsync -aHAX --delete --numeric-ids "${src}/" /etc/
}

restore_kargs_from_backup() {
  local kf="${1}/kargs.txt"
  if [[ ! -f "${kf}" ]]; then
    err "No kargs.txt in ${1}"
    return 1
  fi
  local line
  line="$(grep -m1 '^EFFECTIVE_KARGS=' "${kf}" \
    | sed 's/^EFFECTIVE_KARGS=//')"
  if [[ -z "${line}" ]]; then
    err "EFFECTIVE_KARGS missing; skipping kargs restore."
    return 0
  fi
  log "Restore kernel args from backup"
  if (( DRY_RUN )); then
    echo "[dry-run] rpm-ostree kargs --delete-all; append tokens"
    return
  fi
  rpm-ostree kargs --delete-all
  # Split effective cmdline into tokens and append each.
  # shellcheck disable=SC2206
  local tokens=( $line )
  for t in "${tokens[@]}"; do
    rpm-ostree kargs --append "${t}"
  done
}

perform_rollback() {
  local target="${BACKUP_DIR}"
  if [[ ! -f "${target}/STATE.txt" ]]; then
    target="$(find_latest_backup)"
    if [[ -z "${target}" ]]; then
      err "No backups found."
      exit 1
    fi
  fi
  log "Rollback → ${target}"
  restore_etc_from_backup "${target}"
  restore_kargs_from_backup "${target}"
  log "Rollback complete."
  if (( REBOOT_PROMPT )); then
    echo
    echo "Reboot to apply kargs: sudo systemctl reboot"
    echo
  fi
}

# --------------------------------- Main --------------------------------------

if (( DO_ROLLBACK )); then
  perform_rollback
  exit 0
fi

write_state
log "Targeted reset (layered packages preserved)"
backup_etc
backup_kargs

if (( ONLY_REPOS )); then
  reset_repos
else
  (( DO_KARGS )) && reset_kargs
  (( DO_ETC )) && restore_etc
  (( DO_REPOS )) && reset_repos
fi

config_diff
log "Backups: ${BACKUP_DIR}"
if (( REBOOT_PROMPT )); then
  echo
  echo "Review ${BACKUP_DIR} → reboot: sudo systemctl reboot"
  echo
fi
log "Done."
