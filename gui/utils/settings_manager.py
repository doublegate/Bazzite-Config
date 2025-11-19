"""
Settings Manager - Persistent Settings Storage
Saves and loads GUI settings across sessions
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class ApplicationSettings:
    """Application settings data class"""
    # Window settings
    window_width: int = 1200
    window_height: int = 800
    window_maximized: bool = False

    # General settings
    auto_start: bool = False
    minimize_to_tray: bool = False
    show_notifications: bool = True
    check_for_updates: bool = True

    # Optimization settings
    default_profile: str = "balanced"
    auto_switch_profile: bool = False
    apply_profile_on_startup: bool = False

    # Monitoring settings
    monitoring_enabled: bool = False
    monitoring_interval: int = 1000  # ms
    monitoring_history_size: int = 300  # data points

    # Advanced settings
    enable_debug_logging: bool = False
    backup_before_optimization: bool = True
    use_experimental_features: bool = False

    # Theme settings
    dark_mode: bool = True
    accent_color: str = "#3584e4"

    # Community features
    enable_profile_sharing: bool = False
    enable_cloud_benchmarks: bool = False
    anonymous_stats: bool = False

    # Remote management
    enable_remote_api: bool = False
    api_port: int = 8080
    api_auth_required: bool = True


class SettingsManager:
    """Manages application settings persistence"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_dir = Path.home() / '.config' / 'bazzite-optimizer'
        self.settings_file = self.config_dir / 'settings.json'

        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load settings
        self.settings = self.load()

    def load(self) -> ApplicationSettings:
        """Load settings from file"""
        if not self.settings_file.exists():
            self.logger.info("No settings file found, using defaults")
            return ApplicationSettings()

        try:
            with open(self.settings_file, 'r') as f:
                data = json.load(f)

            # Convert dict to ApplicationSettings
            settings = ApplicationSettings(**data)
            self.logger.info(f"Loaded settings from {self.settings_file}")
            return settings

        except (json.JSONDecodeError, TypeError, FileNotFoundError) as e:
            self.logger.error(f"Failed to load settings: {e}")
            return ApplicationSettings()

    def save(self, settings: Optional[ApplicationSettings] = None):
        """Save settings to file"""
        if settings is not None:
            self.settings = settings

        try:
            # Convert ApplicationSettings to dict
            data = asdict(self.settings)

            with open(self.settings_file, 'w') as f:
                json.dump(data, f, indent=2)

            self.logger.info(f"Saved settings to {self.settings_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value"""
        return getattr(self.settings, key, default)

    def set(self, key: str, value: Any, save: bool = True):
        """Set a specific setting value"""
        if hasattr(self.settings, key):
            setattr(self.settings, key, value)
            if save:
                self.save()
            return True
        else:
            self.logger.warning(f"Unknown setting key: {key}")
            return False

    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = ApplicationSettings()
        self.save()
        self.logger.info("Settings reset to defaults")

    def export_settings(self, file_path: Path) -> bool:
        """Export settings to a file"""
        try:
            data = asdict(self.settings)
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            self.logger.info(f"Settings exported to {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export settings: {e}")
            return False

    def import_settings(self, file_path: Path) -> bool:
        """Import settings from a file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            self.settings = ApplicationSettings(**data)
            self.save()
            self.logger.info(f"Settings imported from {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to import settings: {e}")
            return False


class ProfileCache:
    """Caches custom profile data"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache_dir = Path.home() / '.config' / 'bazzite-optimizer' / 'custom-profiles'
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def list_profiles(self) -> list[Dict[str, Any]]:
        """List all cached custom profiles"""
        profiles = []

        for profile_file in self.cache_dir.glob('*.json'):
            try:
                with open(profile_file, 'r') as f:
                    profile_data = json.load(f)
                    profile_data['file_path'] = str(profile_file)
                    profiles.append(profile_data)
            except Exception as e:
                self.logger.error(f"Failed to load profile {profile_file}: {e}")

        return profiles

    def get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific profile by name"""
        profile_file = self.cache_dir / f"{name}.json"

        if not profile_file.exists():
            return None

        try:
            with open(profile_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load profile {name}: {e}")
            return None

    def save_profile(self, name: str, profile_data: Dict[str, Any]) -> bool:
        """Save a profile"""
        profile_file = self.cache_dir / f"{name}.json"

        try:
            with open(profile_file, 'w') as f:
                json.dump(profile_data, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save profile {name}: {e}")
            return False

    def delete_profile(self, name: str) -> bool:
        """Delete a profile"""
        profile_file = self.cache_dir / f"{name}.json"

        try:
            if profile_file.exists():
                profile_file.unlink()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete profile {name}: {e}")
            return False


class BenchmarkCache:
    """Caches benchmark results"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache_dir = Path.home() / '.local' / 'share' / 'bazzite-optimizer' / 'benchmarks'
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def save_result(self, benchmark_id: str, results: Dict[str, Any]) -> bool:
        """Save benchmark results"""
        result_file = self.cache_dir / f"{benchmark_id}.json"

        try:
            with open(result_file, 'w') as f:
                json.dump(results, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save benchmark result: {e}")
            return False

    def get_result(self, benchmark_id: str) -> Optional[Dict[str, Any]]:
        """Get benchmark results"""
        result_file = self.cache_dir / f"{benchmark_id}.json"

        if not result_file.exists():
            return None

        try:
            with open(result_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load benchmark result: {e}")
            return None

    def list_results(self) -> list[Dict[str, Any]]:
        """List all benchmark results"""
        results = []

        for result_file in self.cache_dir.glob('*.json'):
            try:
                with open(result_file, 'r') as f:
                    result_data = json.load(f)
                    result_data['benchmark_id'] = result_file.stem
                    results.append(result_data)
            except Exception as e:
                self.logger.error(f"Failed to load result {result_file}: {e}")

        return results


# Global settings manager instance
_settings_manager = None


def get_settings_manager() -> SettingsManager:
    """Get global settings manager instance"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager
