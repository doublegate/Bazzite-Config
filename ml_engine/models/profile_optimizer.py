"""
ML-Based Profile Optimizer

Uses machine learning to recommend optimal gaming profiles based on
hardware characteristics, usage patterns, and community benchmarks.
"""

import json
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    import warnings
    warnings.warn("scikit-learn not available. ML features will be limited.")


logger = logging.getLogger(__name__)


@dataclass
class HardwareProfile:
    """Hardware configuration for ML training"""
    cpu_cores: int
    cpu_frequency_mhz: int
    ram_gb: int
    gpu_vendor: str  # 'nvidia', 'amd', 'intel'
    gpu_vram_gb: int
    gpu_compute_units: int
    storage_type: str  # 'nvme', 'ssd', 'hdd'
    has_dedicated_gpu: bool


@dataclass
class UsagePattern:
    """User usage pattern for recommendations"""
    avg_gaming_hours_per_day: float
    primary_game_types: List[str]  # ['fps', 'strategy', 'rpg', etc.]
    avg_cpu_usage_percent: float
    avg_gpu_usage_percent: float
    battery_mode_frequency: float  # 0.0-1.0
    multitasking_frequency: float  # 0.0-1.0


@dataclass
class ProfileRecommendation:
    """ML-generated profile recommendation"""
    profile_name: str
    confidence: float  # 0.0-1.0
    expected_fps_improvement: float
    expected_power_consumption: float  # watts
    reasoning: List[str]
    alternative_profiles: List[Tuple[str, float]]  # [(profile, confidence), ...]


class ProfileOptimizer:
    """
    ML-based profile optimizer using Random Forest classification

    Trains on community benchmark data to recommend optimal profiles
    based on hardware and usage patterns.
    """

    def __init__(self, model_path: Optional[Path] = None):
        """
        Initialize ProfileOptimizer

        Args:
            model_path: Path to save/load trained models
        """
        self.model_path = model_path or Path.home() / '.local/share/bazzite-optimizer/ml-models'
        self.model_path.mkdir(parents=True, exist_ok=True)

        self.classifier: Optional['RandomForestClassifier'] = None
        self.scaler: Optional['StandardScaler'] = None
        self.feature_names: List[str] = []
        self.profile_mapping: Dict[int, str] = {}

        # Profile characteristics for reasoning
        self.profile_characteristics = {
            'competitive': {
                'cpu_weight': 0.9,
                'gpu_weight': 0.9,
                'power_consumption': 'high',
                'best_for': ['fps', 'moba', 'competitive'],
            },
            'balanced': {
                'cpu_weight': 0.6,
                'gpu_weight': 0.7,
                'power_consumption': 'medium',
                'best_for': ['rpg', 'strategy', 'casual'],
            },
            'streaming': {
                'cpu_weight': 0.8,
                'gpu_weight': 0.6,
                'power_consumption': 'medium-high',
                'best_for': ['streaming', 'content_creation'],
            },
            'creative': {
                'cpu_weight': 0.7,
                'gpu_weight': 0.8,
                'power_consumption': 'medium',
                'best_for': ['3d_modeling', 'video_editing'],
            },
            'battery_saver': {
                'cpu_weight': 0.3,
                'gpu_weight': 0.3,
                'power_consumption': 'low',
                'best_for': ['casual', 'indie', 'mobile'],
            },
        }

        self._initialize_model()

    def _initialize_model(self):
        """Initialize or load ML model"""
        model_file = self.model_path / 'profile_optimizer.pkl'
        scaler_file = self.model_path / 'feature_scaler.pkl'

        if model_file.exists() and scaler_file.exists():
            try:
                with open(model_file, 'rb') as f:
                    data = pickle.load(f)
                    self.classifier = data['classifier']
                    self.feature_names = data['feature_names']
                    self.profile_mapping = data['profile_mapping']

                with open(scaler_file, 'rb') as f:
                    self.scaler = pickle.load(f)

                logger.info("Loaded pre-trained profile optimizer model")
            except Exception as e:
                logger.warning(f"Failed to load model: {e}. Using heuristic fallback.")
                self._create_default_model()
        else:
            self._create_default_model()

    def _create_default_model(self):
        """Create default model with synthetic training data"""
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available. Using rule-based recommendations.")
            return

        # Create synthetic training data based on typical configurations
        X_train, y_train = self._generate_synthetic_training_data()

        self.classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X_train)
        self.classifier.fit(X_scaled, y_train)

        logger.info("Created default profile optimizer model with synthetic data")

    def _generate_synthetic_training_data(self) -> Tuple['np.ndarray', 'np.ndarray']:
        """Generate synthetic training data for initial model"""
        import numpy as np

        # Define feature names
        self.feature_names = [
            'cpu_cores', 'cpu_frequency', 'ram_gb', 'gpu_vram_gb',
            'gpu_compute_units', 'has_dedicated_gpu', 'is_nvme',
            'avg_gaming_hours', 'avg_cpu_usage', 'avg_gpu_usage',
            'battery_mode_freq', 'multitasking_freq',
            'plays_fps', 'plays_strategy', 'plays_rpg'
        ]

        # Profile mapping
        self.profile_mapping = {
            0: 'competitive',
            1: 'balanced',
            2: 'streaming',
            3: 'creative',
            4: 'battery_saver'
        }

        # Generate 1000 synthetic samples
        n_samples = 1000
        X_train = []
        y_train = []

        for _ in range(n_samples):
            # Random hardware
            cpu_cores = np.random.choice([4, 6, 8, 10, 12, 16])
            cpu_freq = np.random.randint(2000, 5000)
            ram = np.random.choice([8, 16, 32, 64])
            gpu_vram = np.random.choice([4, 6, 8, 12, 16, 24])
            gpu_compute = np.random.randint(20, 100)
            has_dgpu = 1 if gpu_vram >= 6 else 0
            is_nvme = np.random.choice([0, 1])

            # Random usage
            gaming_hours = np.random.uniform(1, 8)
            cpu_usage = np.random.uniform(30, 90)
            gpu_usage = np.random.uniform(40, 95)
            battery_freq = np.random.uniform(0, 0.5)
            multitask_freq = np.random.uniform(0, 0.7)

            # Game preferences
            plays_fps = np.random.choice([0, 1])
            plays_strategy = np.random.choice([0, 1])
            plays_rpg = np.random.choice([0, 1])

            features = [
                cpu_cores, cpu_freq, ram, gpu_vram, gpu_compute,
                has_dgpu, is_nvme, gaming_hours, cpu_usage, gpu_usage,
                battery_freq, multitask_freq, plays_fps, plays_strategy, plays_rpg
            ]

            # Determine label using heuristics
            if battery_freq > 0.3:
                label = 4  # battery_saver
            elif gaming_hours > 5 and plays_fps and cpu_usage > 70 and gpu_usage > 80:
                label = 0  # competitive
            elif gaming_hours > 3 and multitask_freq > 0.5:
                label = 2  # streaming
            elif plays_strategy or plays_rpg:
                label = 3  # creative
            else:
                label = 1  # balanced

            X_train.append(features)
            y_train.append(label)

        return np.array(X_train), np.array(y_train)

    def recommend_profile(
        self,
        hardware: HardwareProfile,
        usage: UsagePattern
    ) -> ProfileRecommendation:
        """
        Recommend optimal profile using ML model

        Args:
            hardware: Hardware configuration
            usage: Usage patterns

        Returns:
            ProfileRecommendation with confidence and reasoning
        """
        if not SKLEARN_AVAILABLE or self.classifier is None:
            return self._heuristic_recommendation(hardware, usage)

        # Extract features
        features = self._extract_features(hardware, usage)

        try:
            # Scale features
            features_scaled = self.scaler.transform([features])

            # Get prediction and probabilities
            prediction = self.classifier.predict(features_scaled)[0]
            probabilities = self.classifier.predict_proba(features_scaled)[0]

            # Get profile name
            profile_name = self.profile_mapping[prediction]
            confidence = probabilities[prediction]

            # Get alternative profiles
            alternatives = []
            for idx, prob in enumerate(probabilities):
                if idx != prediction and prob > 0.1:
                    alternatives.append((self.profile_mapping[idx], prob))
            alternatives.sort(key=lambda x: x[1], reverse=True)

            # Generate reasoning
            reasoning = self._generate_reasoning(profile_name, hardware, usage, features)

            # Estimate performance
            fps_improvement = self._estimate_fps_improvement(profile_name, hardware, usage)
            power_consumption = self._estimate_power_consumption(profile_name, hardware)

            return ProfileRecommendation(
                profile_name=profile_name,
                confidence=float(confidence),
                expected_fps_improvement=fps_improvement,
                expected_power_consumption=power_consumption,
                reasoning=reasoning,
                alternative_profiles=alternatives[:3]
            )

        except Exception as e:
            logger.error(f"ML prediction failed: {e}. Using heuristic fallback.")
            return self._heuristic_recommendation(hardware, usage)

    def _extract_features(self, hardware: HardwareProfile, usage: UsagePattern) -> List[float]:
        """Extract feature vector from hardware and usage"""
        # Game type encoding
        plays_fps = 1.0 if 'fps' in usage.primary_game_types else 0.0
        plays_strategy = 1.0 if 'strategy' in usage.primary_game_types else 0.0
        plays_rpg = 1.0 if 'rpg' in usage.primary_game_types else 0.0

        features = [
            float(hardware.cpu_cores),
            float(hardware.cpu_frequency_mhz),
            float(hardware.ram_gb),
            float(hardware.gpu_vram_gb),
            float(hardware.gpu_compute_units),
            1.0 if hardware.has_dedicated_gpu else 0.0,
            1.0 if hardware.storage_type == 'nvme' else 0.0,
            float(usage.avg_gaming_hours_per_day),
            float(usage.avg_cpu_usage_percent),
            float(usage.avg_gpu_usage_percent),
            float(usage.battery_mode_frequency),
            float(usage.multitasking_frequency),
            plays_fps,
            plays_strategy,
            plays_rpg,
        ]

        return features

    def _heuristic_recommendation(
        self,
        hardware: HardwareProfile,
        usage: UsagePattern
    ) -> ProfileRecommendation:
        """Fallback heuristic-based recommendation"""
        # Battery priority
        if usage.battery_mode_frequency > 0.3:
            profile = 'battery_saver'
            confidence = 0.85
            reasoning = [
                "High battery mode usage detected (>30%)",
                "Battery-optimized profile recommended for extended runtime"
            ]
        # High-performance gaming
        elif (usage.avg_gaming_hours_per_day > 4 and
              usage.avg_cpu_usage_percent > 70 and
              usage.avg_gpu_usage_percent > 80 and
              'fps' in usage.primary_game_types):
            profile = 'competitive'
            confidence = 0.90
            reasoning = [
                "High gaming hours with intensive CPU/GPU usage",
                "FPS games detected - competitive profile for maximum performance",
                f"Hardware capable: {hardware.cpu_cores} cores, {hardware.gpu_vram_gb}GB VRAM"
            ]
        # Streaming/multitasking
        elif usage.multitasking_frequency > 0.5 and usage.avg_gaming_hours_per_day > 3:
            profile = 'streaming'
            confidence = 0.80
            reasoning = [
                "High multitasking frequency detected",
                "Streaming profile optimizes for gameplay + background tasks",
                "Balanced CPU priority for encoding/streaming"
            ]
        # Creative work
        elif 'strategy' in usage.primary_game_types or 'rpg' in usage.primary_game_types:
            profile = 'creative'
            confidence = 0.75
            reasoning = [
                "Strategy/RPG games with moderate resource usage",
                "Creative profile balances visuals and performance"
            ]
        # Default balanced
        else:
            profile = 'balanced'
            confidence = 0.70
            reasoning = [
                "General gaming usage pattern",
                "Balanced profile recommended for versatile performance"
            ]

        fps_improvement = self._estimate_fps_improvement(profile, hardware, usage)
        power_consumption = self._estimate_power_consumption(profile, hardware)

        return ProfileRecommendation(
            profile_name=profile,
            confidence=confidence,
            expected_fps_improvement=fps_improvement,
            expected_power_consumption=power_consumption,
            reasoning=reasoning,
            alternative_profiles=[('balanced', 0.6), ('competitive', 0.5)]
        )

    def _generate_reasoning(
        self,
        profile: str,
        hardware: HardwareProfile,
        usage: UsagePattern,
        features: List[float]
    ) -> List[str]:
        """Generate human-readable reasoning for recommendation"""
        reasoning = []

        char = self.profile_characteristics.get(profile, {})

        # Hardware-based reasoning
        if hardware.has_dedicated_gpu and hardware.gpu_vram_gb >= 8:
            reasoning.append(f"High-end GPU ({hardware.gpu_vram_gb}GB VRAM) supports {profile} profile")

        if hardware.cpu_cores >= 8:
            reasoning.append(f"{hardware.cpu_cores}-core CPU ideal for {char.get('best_for', [])[0]} workloads")

        # Usage-based reasoning
        if usage.avg_gaming_hours_per_day > 4:
            reasoning.append(f"Heavy gaming usage ({usage.avg_gaming_hours_per_day:.1f}h/day) benefits from optimized profile")

        if usage.avg_cpu_usage_percent > 70 or usage.avg_gpu_usage_percent > 80:
            reasoning.append("High resource utilization detected - performance profile recommended")

        # Game type reasoning
        game_match = any(game in char.get('best_for', []) for game in usage.primary_game_types)
        if game_match:
            reasoning.append(f"Profile optimized for {usage.primary_game_types[0]} games")

        if not reasoning:
            reasoning.append(f"{profile.title()} profile matches your usage pattern")

        return reasoning

    def _estimate_fps_improvement(
        self,
        profile: str,
        hardware: HardwareProfile,
        usage: UsagePattern
    ) -> float:
        """Estimate FPS improvement percentage"""
        base_improvement = {
            'competitive': 15.0,
            'balanced': 8.0,
            'streaming': 5.0,
            'creative': 10.0,
            'battery_saver': -10.0,  # Reduced performance for battery
        }

        improvement = base_improvement.get(profile, 5.0)

        # Adjust based on hardware capability
        if hardware.has_dedicated_gpu and hardware.gpu_vram_gb >= 8:
            improvement *= 1.2
        if hardware.cpu_cores >= 10:
            improvement *= 1.1

        return round(improvement, 1)

    def _estimate_power_consumption(self, profile: str, hardware: HardwareProfile) -> float:
        """Estimate power consumption in watts"""
        base_power = {
            'competitive': 200.0,
            'balanced': 150.0,
            'streaming': 180.0,
            'creative': 160.0,
            'battery_saver': 80.0,
        }

        power = base_power.get(profile, 150.0)

        # Adjust for hardware
        if hardware.has_dedicated_gpu:
            power += hardware.gpu_vram_gb * 5  # Rough GPU power estimate
        power += hardware.cpu_cores * 3  # CPU power estimate

        return round(power, 1)

    def train_from_community_data(self, data_path: Path) -> bool:
        """
        Train model from community benchmark data

        Args:
            data_path: Path to JSON file with community data

        Returns:
            True if training successful
        """
        if not SKLEARN_AVAILABLE:
            logger.error("scikit-learn required for training")
            return False

        try:
            with open(data_path, 'r') as f:
                data = json.load(f)

            # Extract features and labels from community data
            X_train = []
            y_train = []

            for entry in data['benchmarks']:
                hardware = HardwareProfile(**entry['hardware'])
                usage = UsagePattern(**entry['usage'])
                optimal_profile = entry['optimal_profile']

                features = self._extract_features(hardware, usage)
                X_train.append(features)

                # Convert profile name to label
                label = next(k for k, v in self.profile_mapping.items() if v == optimal_profile)
                y_train.append(label)

            # Train model
            import numpy as np
            X_train = np.array(X_train)
            y_train = np.array(y_train)

            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X_train)

            self.classifier = RandomForestClassifier(
                n_estimators=150,
                max_depth=15,
                random_state=42,
                n_jobs=-1
            )
            self.classifier.fit(X_scaled, y_train)

            # Save model
            self._save_model()

            logger.info(f"Trained model on {len(X_train)} community benchmarks")
            return True

        except Exception as e:
            logger.error(f"Training failed: {e}")
            return False

    def _save_model(self):
        """Save trained model to disk"""
        model_file = self.model_path / 'profile_optimizer.pkl'
        scaler_file = self.model_path / 'feature_scaler.pkl'

        try:
            with open(model_file, 'wb') as f:
                pickle.dump({
                    'classifier': self.classifier,
                    'feature_names': self.feature_names,
                    'profile_mapping': self.profile_mapping,
                }, f)

            with open(scaler_file, 'wb') as f:
                pickle.dump(self.scaler, f)

            logger.info("Saved trained model to disk")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
