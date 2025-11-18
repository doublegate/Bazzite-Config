#!/usr/bin/env python3
"""
Profile Model for Bazzite Optimizer GUI

Manages gaming profiles and their configurations.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class ProfileType(Enum):
    """Gaming profile types"""
    COMPETITIVE = "competitive"
    BALANCED = "balanced"
    STREAMING = "streaming"
    CREATIVE = "creative"


@dataclass
class ProfileDetails:
    """Detailed profile configuration"""
    name: str
    display_name: str
    description: str
    icon_name: str
    features: List[str] = field(default_factory=list)
    optimizations: Dict[str, str] = field(default_factory=dict)
    recommended_for: List[str] = field(default_factory=list)


class ProfileModel:
    """Gaming profile model with predefined profiles"""

    PROFILES = {
        ProfileType.COMPETITIVE: ProfileDetails(
            name="competitive",
            display_name="Competitive",
            description="Maximum performance for competitive gaming with no compromises",
            icon_name="⚡",
            features=[
                "No C-states (maximum CPU responsiveness)",
                "Maximum CPU/GPU clocks",
                "Core isolation for gaming threads",
                "Disabled mitigations for peak performance",
                "Minimum latency network tuning",
                "Compositor disabled"
            ],
            optimizations={
                "cpu_cstate": "0",
                "cpu_governor": "performance",
                "gpu_power_mode": "max_performance",
                "io_scheduler": "none",
                "compositor": "disabled"
            },
            recommended_for=["FPS games", "Esports", "Competitive multiplayer"]
        ),
        ProfileType.BALANCED: ProfileDetails(
            name="balanced",
            display_name="Balanced",
            description="Optimal balance between performance and system responsiveness",
            icon_name="⚖️",
            features=[
                "Moderate C-state tuning (C-state 3)",
                "Balanced power management",
                "Auto-tuned clocks",
                "Some mitigations enabled",
                "Optimized network settings",
                "Adaptive compositor"
            ],
            optimizations={
                "cpu_cstate": "3",
                "cpu_governor": "schedutil",
                "gpu_power_mode": "balanced",
                "io_scheduler": "mq-deadline",
                "compositor": "adaptive"
            },
            recommended_for=["Single player games", "General gaming", "Daily use"]
        ),
        ProfileType.STREAMING: ProfileDetails(
            name="streaming",
            display_name="Streaming",
            description="Optimized for game streaming with encoding support",
            icon_name="📹",
            features=[
                "Power-efficient settings",
                "NVENC/VAAPI encoding optimization",
                "Reduced system impact",
                "Network upload optimization",
                "Multi-threaded encoding support",
                "Background task management"
            ],
            optimizations={
                "cpu_cstate": "3",
                "cpu_governor": "schedutil",
                "gpu_power_mode": "balanced",
                "encoding": "optimized",
                "network": "upload_priority"
            },
            recommended_for=["Twitch streaming", "YouTube streaming", "Content creation"]
        ),
        ProfileType.CREATIVE: ProfileDetails(
            name="creative",
            display_name="Creative",
            description="Optimized for content creation and productivity",
            icon_name="🎨",
            features=[
                "Multi-core optimization",
                "High memory bandwidth",
                "Storage performance focus",
                "GPU compute optimization",
                "Rendering acceleration",
                "Background task support"
            ],
            optimizations={
                "cpu_cstate": "2",
                "cpu_governor": "schedutil",
                "gpu_power_mode": "balanced",
                "io_scheduler": "mq-deadline",
                "memory": "high_bandwidth"
            },
            recommended_for=["Video editing", "3D rendering", "Game development"]
        )
    }

    def __init__(self):
        self.current_profile: Optional[ProfileType] = None
        self._observers: List = []

    def get_all_profiles(self) -> List[ProfileDetails]:
        """Get all available profiles"""
        return list(self.PROFILES.values())

    def get_profile(self, profile_type: ProfileType) -> ProfileDetails:
        """Get specific profile details"""
        return self.PROFILES[profile_type]

    def get_profile_by_name(self, name: str) -> Optional[ProfileDetails]:
        """Get profile by string name"""
        for profile_type, details in self.PROFILES.items():
            if details.name == name:
                return details
        return None

    def set_current_profile(self, profile_type: ProfileType):
        """Set the currently active profile"""
        self.current_profile = profile_type
        self.notify_observers()

    def attach_observer(self, observer):
        """Attach observer for profile changes"""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach_observer(self, observer):
        """Detach observer"""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self):
        """Notify all observers of profile change"""
        for observer in self._observers:
            observer.on_profile_changed(self.current_profile)

    def get_profile_comparison(self, profile1: ProfileType, profile2: ProfileType) -> Dict:
        """Compare two profiles"""
        p1 = self.PROFILES[profile1]
        p2 = self.PROFILES[profile2]

        comparison = {
            "profile1": p1.display_name,
            "profile2": p2.display_name,
            "differences": []
        }

        # Compare optimizations
        all_keys = set(p1.optimizations.keys()) | set(p2.optimizations.keys())
        for key in all_keys:
            val1 = p1.optimizations.get(key, "Not set")
            val2 = p2.optimizations.get(key, "Not set")
            if val1 != val2:
                comparison["differences"].append({
                    "setting": key,
                    "profile1_value": val1,
                    "profile2_value": val2
                })

        return comparison
