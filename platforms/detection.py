# TEAM_005: Platform detection for cross-platform Linux gaming optimization
"""
Platform detection module.

Detects the current Linux distribution and determines:
- Platform type (Bazzite, Fedora ostree, Fedora traditional, Debian-based)
- Package manager (rpm-ostree, dnf, apt)
- Boot method (rpm-ostree-kargs, grub, systemd-boot)
- Special features (ujust availability)
"""

import subprocess
import shutil
from enum import Enum, auto
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import logging
import os


class PlatformType(Enum):
    """Supported platform types for the optimizer."""
    BAZZITE = auto()            # Bazzite (immutable, rpm-ostree + ujust)
    FEDORA_OSTREE = auto()      # Silverblue, Kinoite, Aurora (immutable, rpm-ostree)
    FEDORA_TRADITIONAL = auto()  # Fedora Workstation, Ultramarine, Nobara
    DEBIAN_BASED = auto()       # Ubuntu, Debian, Pop!_OS, Linux Mint
    UNKNOWN = auto()


# TEAM_009: GPU vendor IDs
GPU_VENDORS = {
    "0x10de": "nvidia",
    "0x1002": "amd",
    "0x8086": "intel",
}


@dataclass
class GPUInfo:
    """TEAM_009: GPU information for eGPU and multi-GPU support."""
    card_path: str              # /sys/class/drm/card0
    vendor: str                 # "nvidia", "amd", "intel"
    vendor_id: str              # "0x10de"
    device_id: str              # "0x2504"
    name: str                   # "GeForce RTX 3060" or "Unknown"
    is_egpu: bool               # True if connected via Thunderbolt
    is_primary: bool            # True if selected for gaming
    is_rendering: bool          # True if actively rendering
    driver: Optional[str]       # "nvidia", "nouveau", "amdgpu", "i915"


# TEAM_013: GPU capability profiles by generation
@dataclass
class NvidiaGPUCapabilities:
    """TEAM_013: NVIDIA GPU capabilities for dynamic optimization."""
    generation: str             # "ampere", "ada", "blackwell", "turing", "pascal", "unknown"
    architecture_code: str      # "GA106", "AD102", "GB203", etc.
    vram_mb: int                # VRAM in MB (detected or estimated)
    safe_core_offset_max: int   # Max safe core clock offset in MHz
    safe_mem_offset_max: int    # Max safe memory clock offset in MHz
    safe_power_limit_max: int   # Max power limit as percentage (e.g., 115)
    supports_resizable_bar: bool
    supports_nvenc: bool
    tdp_watts: int              # Typical TDP


# TEAM_013: NVIDIA GPU generation detection patterns
NVIDIA_GENERATIONS = {
    # Blackwell (RTX 50 series) - GB1xx, GB2xx
    "blackwell": {
        "prefixes": ["GB1", "GB2"],
        "name_patterns": ["RTX 50", "RTX 5"],
        "safe_core_offset": 200,
        "safe_mem_offset": 500,
        "safe_power_limit": 110,
    },
    # Ada Lovelace (RTX 40 series) - AD1xx, AD2xx
    "ada": {
        "prefixes": ["AD1", "AD2"],
        "name_patterns": ["RTX 40", "RTX 4"],
        "safe_core_offset": 250,
        "safe_mem_offset": 600,
        "safe_power_limit": 115,
    },
    # Ampere (RTX 30 series) - GA1xx, GA2xx
    "ampere": {
        "prefixes": ["GA1", "GA2"],
        "name_patterns": ["RTX 30", "RTX 3", "A2000", "A4000", "A5000", "A6000"],
        "safe_core_offset": 150,
        "safe_mem_offset": 500,
        "safe_power_limit": 110,
    },
    # Turing (RTX 20 series, GTX 16 series) - TU1xx, TU2xx
    "turing": {
        "prefixes": ["TU1", "TU2"],
        "name_patterns": ["RTX 20", "RTX 2", "GTX 16"],
        "safe_core_offset": 150,
        "safe_mem_offset": 400,
        "safe_power_limit": 110,
    },
    # Pascal (GTX 10 series) - GP1xx, GP2xx
    "pascal": {
        "prefixes": ["GP1", "GP2"],
        "name_patterns": ["GTX 10", "GTX 1"],
        "safe_core_offset": 100,
        "safe_mem_offset": 300,
        "safe_power_limit": 105,
    },
}


@dataclass
class CPUTopology:
    """TEAM_012: CPU topology information for hybrid CPU support."""
    total_cores: int            # Physical cores
    total_threads: int          # Logical CPUs (with hyperthreading)
    is_hybrid: bool             # True for Intel Alder Lake, Raptor Lake, etc.
    p_cores: List[int]          # Performance core CPU IDs
    e_cores: List[int]          # Efficiency core CPU IDs
    recommended_isolate: List[int]  # Cores safe to isolate for gaming


@dataclass
class PlatformInfo:
    """Platform metadata collected during detection."""
    platform_type: PlatformType
    distro_name: str
    distro_version: str
    is_immutable: bool
    has_ujust: bool
    package_manager: str   # "rpm-ostree", "dnf", "apt"
    boot_method: str       # "rpm-ostree-kargs", "grub", "systemd-boot"


def _parse_os_release() -> Dict[str, str]:
    """Parse /etc/os-release into a dictionary."""
    result = {}
    os_release = Path("/etc/os-release")
    if os_release.exists():
        with open(os_release) as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    key, _, value = line.partition("=")
                    result[key] = value.strip('"')
    return result


def _check_rpm_ostree_deployment() -> bool:
    """Check if system has an rpm-ostree deployment."""
    if not shutil.which("rpm-ostree"):
        return False
    try:
        result = subprocess.run(
            ["rpm-ostree", "status", "--json"],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0 and b"deployments" in result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _detect_boot_method(is_immutable: bool) -> str:
    """Detect how kernel parameters are configured."""
    if is_immutable:
        return "rpm-ostree-kargs"
    if Path("/etc/default/grub").exists():
        return "grub"
    if Path("/boot/loader/entries").exists():
        return "systemd-boot"
    return "unknown"


# TEAM_012: CPU Topology Detection

def detect_cpu_topology() -> CPUTopology:
    """
    TEAM_012: Detect CPU topology including hybrid P-core/E-core architecture.
    
    For Intel Alder Lake and newer hybrid CPUs, identifies:
    - P-cores (Performance): Higher max frequency
    - E-cores (Efficiency): Lower max frequency
    
    Returns CPUTopology with recommended cores to isolate for gaming.
    """
    logger = logging.getLogger(__name__)
    
    cpu_path = Path("/sys/devices/system/cpu")
    
    # Get total CPUs
    online_cpus = []
    for cpu_dir in sorted(cpu_path.glob("cpu[0-9]*")):
        cpu_name = cpu_dir.name
        if cpu_name.startswith("cpu") and cpu_name[3:].isdigit():
            cpu_id = int(cpu_name[3:])
            online_cpus.append(cpu_id)
    
    total_threads = len(online_cpus)
    if total_threads == 0:
        logger.warning("Could not detect CPU topology")
        return CPUTopology(
            total_cores=0, total_threads=0, is_hybrid=False,
            p_cores=[], e_cores=[], recommended_isolate=[]
        )
    
    # Get physical core count
    try:
        import psutil
        total_cores = psutil.cpu_count(logical=False) or total_threads
    except ImportError:
        total_cores = total_threads
    
    # Detect hybrid architecture by checking max frequencies
    cpu_freqs = {}
    for cpu_id in online_cpus:
        freq_file = cpu_path / f"cpu{cpu_id}" / "cpufreq" / "cpuinfo_max_freq"
        if freq_file.exists():
            try:
                freq = int(freq_file.read_text().strip())
                cpu_freqs[cpu_id] = freq
            except (ValueError, IOError):
                pass
    
    # Determine if hybrid based on frequency variance
    p_cores = []
    e_cores = []
    is_hybrid = False
    
    if cpu_freqs:
        freqs = list(cpu_freqs.values())
        max_freq = max(freqs)
        min_freq = min(freqs)
        
        # Hybrid if there's >15% frequency difference between cores
        if min_freq < max_freq * 0.85:
            is_hybrid = True
            threshold = (max_freq + min_freq) / 2
            
            for cpu_id, freq in cpu_freqs.items():
                if freq >= threshold:
                    p_cores.append(cpu_id)
                else:
                    e_cores.append(cpu_id)
            
            p_cores.sort()
            e_cores.sort()
            logger.info(f"Detected hybrid CPU: P-cores={p_cores}, E-cores={e_cores}")
    
    # Determine recommended cores to isolate
    recommended_isolate = []
    
    if is_hybrid and e_cores:
        # For hybrid CPUs, isolate E-cores (they're for efficiency, not gaming)
        recommended_isolate = e_cores.copy()
        logger.info(f"Hybrid CPU: Recommending E-core isolation: {recommended_isolate}")
    elif total_threads >= 8:
        # For non-hybrid, isolate last 25% of cores (traditional approach)
        num_to_isolate = max(2, total_threads // 4)
        recommended_isolate = list(range(total_threads - num_to_isolate, total_threads))
        logger.info(f"Non-hybrid CPU: Recommending last {num_to_isolate} cores: {recommended_isolate}")
    
    return CPUTopology(
        total_cores=total_cores,
        total_threads=total_threads,
        is_hybrid=is_hybrid,
        p_cores=p_cores,
        e_cores=e_cores,
        recommended_isolate=recommended_isolate
    )


# TEAM_009: GPU Detection Functions

def detect_thunderbolt_devices() -> List[str]:
    """TEAM_009: Detect Thunderbolt devices (for eGPU detection)."""
    devices = []
    tb_path = Path("/sys/bus/thunderbolt/devices")
    if tb_path.exists():
        for device in tb_path.iterdir():
            name_file = device / "device_name"
            if name_file.exists():
                try:
                    name = name_file.read_text().strip()
                    if name:
                        devices.append(name)
                except Exception:
                    pass
    return devices


def _get_gpu_name_from_lspci(pci_slot: str) -> str:
    """TEAM_009: Get GPU name from lspci output."""
    try:
        result = subprocess.run(
            ["lspci", "-s", pci_slot, "-mm"],
            capture_output=True, timeout=5
        )
        if result.returncode == 0:
            # Parse lspci -mm output: Slot, Class, Vendor, Device, ...
            parts = result.stdout.decode().strip().split('"')
            if len(parts) >= 6:
                return parts[5]  # Device name
    except Exception:
        pass
    return "Unknown"


def _get_active_rendering_gpu() -> Optional[str]:
    """TEAM_009: Detect which GPU is actively rendering (for Q3:C)."""
    logger = logging.getLogger(__name__)
    
    # Method 1: Check DRI_PRIME environment
    dri_prime = os.environ.get("DRI_PRIME", "")
    if dri_prime:
        logger.debug(f"DRI_PRIME set to: {dri_prime}")
        return f"card{dri_prime}" if dri_prime.isdigit() else dri_prime
    
    # Method 2: Check which card has connected displays
    drm_path = Path("/sys/class/drm")
    for card_dir in sorted(drm_path.glob("card[0-9]*")):
        if "-" not in card_dir.name:  # Skip card0-DP-1 etc
            continue
        status_file = card_dir / "status"
        if status_file.exists():
            try:
                status = status_file.read_text().strip()
                if status == "connected":
                    # Extract card number from card0-DP-1
                    card_name = card_dir.name.split("-")[0]
                    logger.debug(f"Found connected display on {card_name}")
                    return card_name
            except Exception:
                pass
    
    # Method 3: Check /proc/driver/nvidia for NVIDIA
    nvidia_proc = Path("/proc/driver/nvidia/gpus")
    if nvidia_proc.exists():
        for gpu_dir in nvidia_proc.iterdir():
            # GPU directories are named by PCI address
            return "nvidia"  # NVIDIA is actively loaded
    
    return None


def detect_gpus() -> List[GPUInfo]:
    """
    TEAM_009: Detect all GPUs with detailed info.
    
    Scans /sys/class/drm for GPU cards and determines:
    - Vendor (nvidia, amd, intel)
    - Whether it's an eGPU (via Thunderbolt)
    - Whether it's actively rendering
    - Driver in use
    
    Returns:
        List of GPUInfo objects, sorted with primary GPU first
    """
    logger = logging.getLogger(__name__)
    gpus = []
    thunderbolt_devices = detect_thunderbolt_devices()
    has_egpu_enclosure = any(
        "core" in d.lower() or "egpu" in d.lower() or "breakaway" in d.lower()
        for d in thunderbolt_devices
    )
    
    active_gpu = _get_active_rendering_gpu()
    drm_path = Path("/sys/class/drm")
    
    for card_dir in sorted(drm_path.glob("card[0-9]")):
        device_path = card_dir / "device"
        if not device_path.exists():
            continue
        
        # Read vendor and device IDs
        vendor_file = device_path / "vendor"
        device_file = device_path / "device"
        driver_link = device_path / "driver"
        
        try:
            vendor_id = vendor_file.read_text().strip() if vendor_file.exists() else ""
            device_id = device_file.read_text().strip() if device_file.exists() else ""
            vendor = GPU_VENDORS.get(vendor_id, "unknown")
            
            # Get driver name
            driver = None
            if driver_link.exists():
                driver = driver_link.resolve().name
            
            # Get PCI slot for name lookup
            pci_slot = ""
            uevent_file = device_path / "uevent"
            if uevent_file.exists():
                for line in uevent_file.read_text().splitlines():
                    if line.startswith("PCI_SLOT_NAME="):
                        pci_slot = line.split("=")[1]
                        break
            
            name = _get_gpu_name_from_lspci(pci_slot) if pci_slot else "Unknown"
            
            # Determine if eGPU: discrete GPU + Thunderbolt enclosure present
            # High PCI bus numbers (>0x10) often indicate external
            is_egpu = False
            if has_egpu_enclosure and vendor in ("nvidia", "amd"):
                # Check PCI bus number - eGPUs typically have high bus numbers
                # PCI slot format: domain:bus:device.function (e.g., 0000:3c:00.0)
                if pci_slot:
                    try:
                        parts = pci_slot.split(":")
                        if len(parts) >= 2:
                            bus_num = int(parts[1], 16)  # [1] is bus, not [0] (domain)
                            is_egpu = bus_num > 0x10  # External buses are usually > 16
                    except (ValueError, IndexError):
                        pass
            
            # Check if this is the active rendering GPU
            is_rendering = (active_gpu == card_dir.name or 
                           (active_gpu == "nvidia" and vendor == "nvidia"))
            
            # Primary GPU logic: prefer discrete GPU that's rendering
            is_primary = False
            if is_rendering:
                is_primary = True
            elif vendor in ("nvidia", "amd") and not active_gpu:
                # If no active detection, prefer discrete
                is_primary = True
            
            gpu = GPUInfo(
                card_path=str(card_dir),
                vendor=vendor,
                vendor_id=vendor_id,
                device_id=device_id,
                name=name,
                is_egpu=is_egpu,
                is_primary=is_primary,
                is_rendering=is_rendering,
                driver=driver
            )
            gpus.append(gpu)
            logger.debug(f"Detected GPU: {gpu}")
            
        except Exception as e:
            logger.warning(f"Failed to read GPU info from {card_dir}: {e}")
    
    # Sort: primary first, then discrete, then integrated
    def gpu_sort_key(g: GPUInfo) -> tuple:
        return (
            not g.is_primary,
            not g.is_rendering,
            g.vendor == "intel",  # Intel last
            g.card_path
        )
    
    gpus.sort(key=gpu_sort_key)
    
    # If no GPU marked primary, mark first discrete as primary
    if gpus and not any(g.is_primary for g in gpus):
        for gpu in gpus:
            if gpu.vendor in ("nvidia", "amd"):
                gpu.is_primary = True
                break
        else:
            gpus[0].is_primary = True
    
    return gpus


def get_primary_gpu() -> Optional[GPUInfo]:
    """TEAM_009: Get the primary GPU for gaming optimizations."""
    gpus = detect_gpus()
    for gpu in gpus:
        if gpu.is_primary:
            return gpu
    return gpus[0] if gpus else None


def detect_nvidia_capabilities(gpu: GPUInfo = None) -> Optional[NvidiaGPUCapabilities]:
    """
    TEAM_013: Detect NVIDIA GPU capabilities for dynamic optimization.
    
    Determines GPU generation from architecture code (GA106, AD102, etc.) or name,
    then returns appropriate safe overclock limits and capabilities.
    
    Args:
        gpu: Optional GPUInfo. If None, detects primary GPU.
        
    Returns:
        NvidiaGPUCapabilities with generation-appropriate limits, or None if not NVIDIA.
    """
    logger = logging.getLogger(__name__)
    
    if gpu is None:
        gpu = get_primary_gpu()
    
    if gpu is None or gpu.vendor != "nvidia":
        return None
    
    # Extract architecture code from name (e.g., "GA106" from "GA106 [GeForce RTX 3060]")
    arch_code = ""
    name_upper = gpu.name.upper()
    
    # Look for architecture patterns like GA106, AD102, GB203, TU116, GP104
    import re
    arch_match = re.search(r'\b(G[ABP]\d{3}|TU\d{3}|AD\d{3})\b', name_upper)
    if arch_match:
        arch_code = arch_match.group(1)
    
    # Detect generation from architecture code or name
    detected_gen = "unknown"
    gen_info = None
    
    for gen_name, gen_data in NVIDIA_GENERATIONS.items():
        # Check architecture prefix
        for prefix in gen_data["prefixes"]:
            if arch_code.startswith(prefix):
                detected_gen = gen_name
                gen_info = gen_data
                break
        if gen_info:
            break
        
        # Check name patterns
        for pattern in gen_data["name_patterns"]:
            if pattern.upper() in name_upper:
                detected_gen = gen_name
                gen_info = gen_data
                break
        if gen_info:
            break
    
    # Get VRAM from nvidia-smi
    vram_mb = 0
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, timeout=5
        )
        if result.returncode == 0:
            vram_mb = int(result.stdout.decode().strip().split('\n')[0])
    except Exception:
        # Estimate from GPU name
        if "3060" in gpu.name:
            vram_mb = 12288
        elif "3070" in gpu.name:
            vram_mb = 8192
        elif "3080" in gpu.name:
            vram_mb = 10240 if "10" in gpu.name else 12288
        elif "3090" in gpu.name:
            vram_mb = 24576
        elif "4060" in gpu.name:
            vram_mb = 8192
        elif "4070" in gpu.name:
            vram_mb = 12288
        elif "4080" in gpu.name:
            vram_mb = 16384
        elif "4090" in gpu.name:
            vram_mb = 24576
        else:
            vram_mb = 8192  # Conservative default
    
    # Use generation-specific limits or conservative defaults
    if gen_info:
        safe_core = gen_info["safe_core_offset"]
        safe_mem = gen_info["safe_mem_offset"]
        safe_power = gen_info["safe_power_limit"]
    else:
        # Conservative defaults for unknown GPUs
        safe_core = 100
        safe_mem = 300
        safe_power = 105
        logger.warning(f"Unknown NVIDIA generation for {gpu.name}, using conservative limits")
    
    # Estimate TDP from GPU class
    tdp = 170  # Default
    if "3060" in gpu.name:
        tdp = 170
    elif "3070" in gpu.name:
        tdp = 220
    elif "3080" in gpu.name:
        tdp = 320
    elif "3090" in gpu.name:
        tdp = 350
    elif "4060" in gpu.name:
        tdp = 115
    elif "4070" in gpu.name:
        tdp = 200
    elif "4080" in gpu.name:
        tdp = 320
    elif "4090" in gpu.name:
        tdp = 450
    elif "5080" in gpu.name:
        tdp = 360
    elif "5090" in gpu.name:
        tdp = 575
    
    caps = NvidiaGPUCapabilities(
        generation=detected_gen,
        architecture_code=arch_code or "unknown",
        vram_mb=vram_mb,
        safe_core_offset_max=safe_core,
        safe_mem_offset_max=safe_mem,
        safe_power_limit_max=safe_power,
        supports_resizable_bar=detected_gen in ("ampere", "ada", "blackwell"),
        supports_nvenc=True,  # All modern NVIDIA GPUs support NVENC
        tdp_watts=tdp
    )
    
    logger.info(f"Detected NVIDIA {detected_gen.upper()} GPU: {gpu.name} ({arch_code}), "
                f"VRAM: {vram_mb}MB, safe OC: +{safe_core}MHz core, +{safe_mem}MHz mem")
    
    return caps


def detect_platform() -> PlatformInfo:
    """
    Detect the current platform and return metadata.
    
    This is the main entry point for platform detection. It examines
    the system to determine:
    - Distribution name and version
    - Whether the system is immutable (rpm-ostree based)
    - Available package manager
    - Boot configuration method
    - Special features like ujust
    
    Returns:
        PlatformInfo with all detected metadata
    
    Example:
        >>> info = detect_platform()
        >>> print(f"Running on {info.distro_name}")
        >>> if info.is_immutable:
        ...     print("Using rpm-ostree for packages")
    """
    os_info = _parse_os_release()
    is_immutable = _check_rpm_ostree_deployment()
    has_ujust = shutil.which("ujust") is not None
    
    distro_name = os_info.get("NAME", "Unknown")
    distro_version = os_info.get("VERSION_ID", "")
    distro_id = os_info.get("ID", "").lower()
    variant_id = os_info.get("VARIANT_ID", "").lower()
    
    # Determine platform type
    if is_immutable:
        if has_ujust or "bazzite" in distro_id or "bazzite" in variant_id:
            platform_type = PlatformType.BAZZITE
        else:
            platform_type = PlatformType.FEDORA_OSTREE
        package_manager = "rpm-ostree"
    elif distro_id in ("fedora", "ultramarine", "nobara", "centos", "rhel", "rocky", "alma"):
        platform_type = PlatformType.FEDORA_TRADITIONAL
        package_manager = "dnf"
    elif distro_id in ("ubuntu", "debian", "pop", "linuxmint", "elementary", "zorin"):
        platform_type = PlatformType.DEBIAN_BASED
        package_manager = "apt"
    else:
        platform_type = PlatformType.UNKNOWN
        # Try to detect package manager
        if shutil.which("dnf"):
            package_manager = "dnf"
        elif shutil.which("apt"):
            package_manager = "apt"
        else:
            package_manager = "unknown"
    
    boot_method = _detect_boot_method(is_immutable)
    
    return PlatformInfo(
        platform_type=platform_type,
        distro_name=distro_name,
        distro_version=distro_version,
        is_immutable=is_immutable,
        has_ujust=has_ujust,
        package_manager=package_manager,
        boot_method=boot_method
    )
