"""
Community Data Collector

Aggregates anonymized benchmark data from community users
for ML model training and analytics.
"""

import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkSubmission:
    """Anonymous benchmark submission"""
    hardware_hash: str  # Anonymized hardware ID
    cpu_cores: int
    cpu_frequency: int
    ram_gb: int
    gpu_vendor: str
    gpu_vram_gb: int
    profile_used: str
    game_name: str
    resolution: str
    graphics_preset: str
    fps_avg: float
    fps_min: float
    power_watts: float
    timestamp: str


class CommunityDataCollector:
    """
    Collects and aggregates anonymized benchmark data

    Handles data validation, anonymization, and storage
    for ML model training.
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path.home() / '.local/share/bazzite-optimizer/community-data'
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.submissions_file = self.storage_dir / 'submissions.json'
        self.aggregated_file = self.storage_dir / 'aggregated_stats.json'

        self.submissions: List[Dict] = []
        self._load_submissions()

    def _load_submissions(self):
        """Load existing submissions"""
        if self.submissions_file.exists():
            try:
                with open(self.submissions_file, 'r') as f:
                    data = json.load(f)
                    self.submissions = data.get('submissions', [])
            except Exception as e:
                logger.error(f"Failed to load submissions: {e}")

    def submit_benchmark(self, hardware: Dict, benchmark_results: Dict, opt_in: bool = True) -> bool:
        """
        Submit anonymized benchmark data

        Args:
            hardware: Hardware specifications
            benchmark_results: Benchmark results
            opt_in: User consent for data sharing

        Returns:
            True if submission successful
        """
        if not opt_in:
            logger.info("User opted out of data sharing")
            return False

        try:
            # Create anonymized hardware hash
            hardware_str = json.dumps(sorted(hardware.items()))
            hardware_hash = hashlib.sha256(hardware_str.encode()).hexdigest()[:16]

            # Create submission
            submission = BenchmarkSubmission(
                hardware_hash=hardware_hash,
                cpu_cores=hardware.get('cpu_cores', 0),
                cpu_frequency=hardware.get('cpu_frequency_mhz', 0),
                ram_gb=hardware.get('ram_gb', 0),
                gpu_vendor=hardware.get('gpu_vendor', 'unknown'),
                gpu_vram_gb=hardware.get('gpu_vram_gb', 0),
                profile_used=benchmark_results.get('profile', 'unknown'),
                game_name=self._anonymize_game_name(benchmark_results.get('game', 'unknown')),
                resolution=benchmark_results.get('resolution', '1920x1080'),
                graphics_preset=benchmark_results.get('graphics_preset', 'medium'),
                fps_avg=benchmark_results.get('fps_avg', 0.0),
                fps_min=benchmark_results.get('fps_min', 0.0),
                power_watts=benchmark_results.get('power_watts', 0.0),
                timestamp=datetime.now().isoformat()
            )

            # Validate
            if not self._validate_submission(submission):
                logger.warning("Submission validation failed")
                return False

            # Store
            self.submissions.append(asdict(submission))
            self._save_submissions()

            logger.info(f"Benchmark submitted successfully (hardware: {hardware_hash})")
            return True

        except Exception as e:
            logger.error(f"Failed to submit benchmark: {e}")
            return False

    def _anonymize_game_name(self, game: str) -> str:
        """Anonymize game name to game type"""
        # Map specific games to types
        fps_games = ['csgo', 'valorant', 'cod', 'apex', 'overwatch']
        strategy_games = ['civ', 'aoe', 'sc2', 'total war']
        rpg_games = ['witcher', 'elden ring', 'skyrim', 'cyberpunk']

        game_lower = game.lower()

        if any(g in game_lower for g in fps_games):
            return 'fps'
        elif any(g in game_lower for g in strategy_games):
            return 'strategy'
        elif any(g in game_lower for g in rpg_games):
            return 'rpg'
        else:
            return 'other'

    def _validate_submission(self, submission: BenchmarkSubmission) -> bool:
        """Validate submission data"""
        # Check required fields
        if submission.cpu_cores <= 0 or submission.ram_gb <= 0:
            return False

        # Check reasonable ranges
        if not (10 <= submission.fps_avg <= 500):
            return False

        if not (30 <= submission.power_watts <= 600):
            return False

        return True

    def _save_submissions(self):
        """Save submissions to disk"""
        try:
            data = {
                'version': '1.0',
                'total_submissions': len(self.submissions),
                'last_updated': datetime.now().isoformat(),
                'submissions': self.submissions
            }

            with open(self.submissions_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save submissions: {e}")

    def aggregate_statistics(self) -> Dict:
        """
        Aggregate community statistics

        Returns:
            Aggregated stats dict
        """
        if not self.submissions:
            return {}

        stats = {
            'total_benchmarks': len(self.submissions),
            'unique_systems': len(set(s['hardware_hash'] for s in self.submissions)),
            'profiles': self._aggregate_by_profile(),
            'games': self._aggregate_by_game(),
            'resolutions': self._aggregate_by_resolution(),
            'last_updated': datetime.now().isoformat()
        }

        # Save aggregated stats
        try:
            with open(self.aggregated_file, 'w') as f:
                json.dump(stats, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save aggregated stats: {e}")

        return stats

    def _aggregate_by_profile(self) -> Dict:
        """Aggregate by profile"""
        profiles = {}

        for sub in self.submissions:
            profile = sub['profile_used']
            if profile not in profiles:
                profiles[profile] = {
                    'count': 0,
                    'avg_fps': [],
                    'avg_power': []
                }

            profiles[profile]['count'] += 1
            profiles[profile]['avg_fps'].append(sub['fps_avg'])
            profiles[profile]['avg_power'].append(sub['power_watts'])

        # Calculate averages
        for profile in profiles:
            fps_list = profiles[profile]['avg_fps']
            power_list = profiles[profile]['avg_power']

            profiles[profile]['avg_fps'] = sum(fps_list) / len(fps_list)
            profiles[profile]['avg_power'] = sum(power_list) / len(power_list)

        return profiles

    def _aggregate_by_game(self) -> Dict:
        """Aggregate by game type"""
        games = {}

        for sub in self.submissions:
            game = sub['game_name']
            if game not in games:
                games[game] = {'count': 0, 'avg_fps': []}

            games[game]['count'] += 1
            games[game]['avg_fps'].append(sub['fps_avg'])

        # Calculate averages
        for game in games:
            fps_list = games[game]['avg_fps']
            games[game]['avg_fps'] = sum(fps_list) / len(fps_list)

        return games

    def _aggregate_by_resolution(self) -> Dict:
        """Aggregate by resolution"""
        resolutions = {}

        for sub in self.submissions:
            res = sub['resolution']
            if res not in resolutions:
                resolutions[res] = {'count': 0, 'avg_fps': []}

            resolutions[res]['count'] += 1
            resolutions[res]['avg_fps'].append(sub['fps_avg'])

        # Calculate averages
        for res in resolutions:
            fps_list = resolutions[res]['avg_fps']
            resolutions[res]['avg_fps'] = sum(fps_list) / len(fps_list)

        return resolutions

    def get_statistics(self) -> Dict:
        """Get current statistics"""
        return self.aggregate_statistics()

    def export_for_training(self, output_file: Path) -> bool:
        """
        Export data in format for ML training

        Args:
            output_file: Output file path

        Returns:
            True if export successful
        """
        try:
            training_data = {
                'benchmarks': self.submissions,
                'version': '1.0',
                'exported': datetime.now().isoformat()
            }

            with open(output_file, 'w') as f:
                json.dump(training_data, f, indent=2)

            logger.info(f"Exported {len(self.submissions)} benchmarks for training")
            return True

        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
