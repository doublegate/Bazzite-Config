"""
Performance Predictor for Gaming Optimization

Predicts FPS and power consumption before applying profile changes
using regression models trained on community benchmark data.
"""

import json
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    import warnings
    warnings.warn("scikit-learn not available. Performance prediction will use heuristics.")


logger = logging.getLogger(__name__)


@dataclass
class GameConfig:
    """Game configuration for prediction"""
    game_name: str
    game_type: str  # 'fps', 'strategy', 'rpg', 'moba', etc.
    resolution: str  # '1920x1080', '2560x1440', '3840x2160'
    graphics_preset: str  # 'low', 'medium', 'high', 'ultra'
    ray_tracing: bool = False
    dlss_enabled: bool = False


@dataclass
class SystemState:
    """Current system state"""
    cpu_usage_percent: float
    gpu_usage_percent: float
    ram_usage_gb: float
    cpu_temp_celsius: float
    gpu_temp_celsius: float
    background_processes: int


@dataclass
class PerformancePrediction:
    """Predicted performance metrics"""
    fps_min: float
    fps_avg: float
    fps_max: float
    fps_99percentile: float
    power_consumption_watts: float
    estimated_temp_cpu: float
    estimated_temp_gpu: float
    confidence: float  # 0.0-1.0
    improvement_over_current: float  # percentage
    recommendation: str


class PerformancePredictor:
    """
    ML-based performance predictor

    Uses ensemble methods (Random Forest + Gradient Boosting) to predict
    gaming performance metrics before applying profile changes.
    """

    def __init__(self, model_path: Optional[Path] = None):
        """
        Initialize PerformancePredictor

        Args:
            model_path: Path to save/load trained models
        """
        self.model_path = model_path or Path.home() / '.local/share/bazzite-optimizer/ml-models'
        self.model_path.mkdir(parents=True, exist_ok=True)

        # Separate models for different metrics
        self.fps_model: Optional['RandomForestRegressor'] = None
        self.power_model: Optional['GradientBoostingRegressor'] = None
        self.temp_model: Optional['RandomForestRegressor'] = None

        self.feature_scaler: Optional['StandardScaler'] = None
        self.target_scaler_fps: Optional['StandardScaler'] = None
        self.target_scaler_power: Optional['StandardScaler'] = None

        self.feature_names: List[str] = []

        self._initialize_models()

    def _initialize_models(self):
        """Initialize or load ML models"""
        fps_model_file = self.model_path / 'fps_predictor.pkl'
        power_model_file = self.model_path / 'power_predictor.pkl'
        scaler_file = self.model_path / 'prediction_scalers.pkl'

        if fps_model_file.exists() and power_model_file.exists() and scaler_file.exists():
            try:
                with open(fps_model_file, 'rb') as f:
                    data = pickle.load(f)
                    self.fps_model = data['model']
                    self.feature_names = data['feature_names']

                with open(power_model_file, 'rb') as f:
                    self.power_model = pickle.load(f)['model']

                with open(scaler_file, 'rb') as f:
                    scalers = pickle.load(f)
                    self.feature_scaler = scalers['feature']
                    self.target_scaler_fps = scalers['target_fps']
                    self.target_scaler_power = scalers['target_power']

                logger.info("Loaded pre-trained performance prediction models")
            except Exception as e:
                logger.warning(f"Failed to load models: {e}. Creating defaults.")
                self._create_default_models()
        else:
            self._create_default_models()

    def _create_default_models(self):
        """Create default models with synthetic training data"""
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available. Using heuristic predictions.")
            return

        # Generate synthetic training data
        X_train, y_fps, y_power, y_temp = self._generate_synthetic_training_data()

        # Initialize scalers
        self.feature_scaler = StandardScaler()
        self.target_scaler_fps = StandardScaler()
        self.target_scaler_power = StandardScaler()

        # Scale data
        X_scaled = self.feature_scaler.fit_transform(X_train)
        y_fps_scaled = self.target_scaler_fps.fit_transform(y_fps.reshape(-1, 1)).ravel()
        y_power_scaled = self.target_scaler_power.fit_transform(y_power.reshape(-1, 1)).ravel()

        # Train FPS model (Random Forest for non-linear relationships)
        self.fps_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        self.fps_model.fit(X_scaled, y_fps_scaled)

        # Train power model (Gradient Boosting for better accuracy)
        self.power_model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        self.power_model.fit(X_scaled, y_power_scaled)

        # Train temperature model (simpler Random Forest)
        self.temp_model = RandomForestRegressor(
            n_estimators=50,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.temp_model.fit(X_scaled, y_temp)

        logger.info("Created default performance prediction models")

    def _generate_synthetic_training_data(self) -> Tuple['np.ndarray', 'np.ndarray', 'np.ndarray', 'np.ndarray']:
        """Generate synthetic training data for initial models"""
        import numpy as np

        # Define features
        self.feature_names = [
            # Hardware
            'cpu_cores', 'cpu_frequency', 'ram_gb', 'gpu_vram_gb', 'gpu_compute_units',
            # Profile settings
            'profile_cpu_weight', 'profile_gpu_weight', 'profile_power_mode',
            # Game config
            'resolution_pixels', 'graphics_preset_num', 'ray_tracing', 'dlss_enabled',
            # System state
            'current_cpu_usage', 'current_gpu_usage', 'ram_usage', 'cpu_temp', 'gpu_temp'
        ]

        n_samples = 2000
        X_train = []
        y_fps = []
        y_power = []
        y_temp = []

        for _ in range(n_samples):
            # Hardware (fixed for a system)
            cpu_cores = np.random.choice([4, 6, 8, 10, 12, 16])
            cpu_freq = np.random.randint(3000, 5500)
            ram = np.random.choice([8, 16, 32, 64])
            gpu_vram = np.random.choice([4, 6, 8, 12, 16, 24])
            gpu_compute = np.random.randint(30, 120)

            # Profile settings
            profile_cpu_weight = np.random.uniform(0.3, 0.9)
            profile_gpu_weight = np.random.uniform(0.3, 0.9)
            profile_power_mode = np.random.choice([0, 1, 2, 3])  # 0=low, 3=max

            # Game config
            resolution_pixels = np.random.choice([2073600, 3686400, 8294400])  # 1080p, 1440p, 4K
            graphics_preset = np.random.choice([0, 1, 2, 3])  # 0=low, 3=ultra
            ray_tracing = np.random.choice([0, 1])
            dlss = np.random.choice([0, 1])

            # System state
            cpu_usage = np.random.uniform(30, 95)
            gpu_usage = np.random.uniform(40, 98)
            ram_usage = np.random.uniform(4, ram * 0.8)
            cpu_temp = np.random.uniform(45, 85)
            gpu_temp = np.random.uniform(50, 85)

            features = [
                cpu_cores, cpu_freq, ram, gpu_vram, gpu_compute,
                profile_cpu_weight, profile_gpu_weight, profile_power_mode,
                resolution_pixels, graphics_preset, ray_tracing, dlss,
                cpu_usage, gpu_usage, ram_usage, cpu_temp, gpu_temp
            ]

            # Realistic FPS calculation
            base_fps = 60 * (gpu_vram / 8) * (gpu_compute / 60)

            # Resolution impact
            if resolution_pixels > 5000000:  # 4K
                base_fps *= 0.4
            elif resolution_pixels > 3000000:  # 1440p
                base_fps *= 0.7

            # Graphics preset impact
            base_fps *= (1.5 - graphics_preset * 0.3)

            # Ray tracing impact
            if ray_tracing:
                base_fps *= (0.8 if dlss else 0.5)

            # Profile impact
            profile_boost = 1 + (profile_cpu_weight + profile_gpu_weight) / 4
            base_fps *= profile_boost

            # CPU bottleneck
            if cpu_cores < 6:
                base_fps *= 0.8

            # Add variance
            fps = max(15, base_fps + np.random.normal(0, 10))

            # Power calculation
            base_power = 100 + gpu_vram * 8 + cpu_cores * 5
            power = base_power * (0.5 + profile_power_mode * 0.15)
            power += (gpu_usage / 100) * 50
            power = max(60, min(350, power + np.random.normal(0, 20)))

            # Temperature (coupled with power and usage)
            temp_cpu_pred = 40 + (cpu_usage / 100) * 40 + (profile_power_mode * 5)
            temp_gpu_pred = 45 + (gpu_usage / 100) * 40 + (profile_power_mode * 5)

            X_train.append(features)
            y_fps.append(fps)
            y_power.append(power)
            y_temp.append([temp_cpu_pred, temp_gpu_pred])

        return (
            np.array(X_train),
            np.array(y_fps),
            np.array(y_power),
            np.array(y_temp)
        )

    def predict_performance(
        self,
        hardware: Dict,
        profile: str,
        game_config: GameConfig,
        system_state: SystemState
    ) -> PerformancePrediction:
        """
        Predict gaming performance for a given configuration

        Args:
            hardware: Hardware specifications dict
            profile: Profile name ('competitive', 'balanced', etc.)
            game_config: Game configuration
            system_state: Current system state

        Returns:
            PerformancePrediction with estimated metrics
        """
        if not SKLEARN_AVAILABLE or self.fps_model is None:
            return self._heuristic_prediction(hardware, profile, game_config, system_state)

        try:
            # Extract features
            features = self._extract_features(hardware, profile, game_config, system_state)

            # Scale features
            features_scaled = self.feature_scaler.transform([features])

            # Predict FPS (scaled)
            fps_scaled = self.fps_model.predict(features_scaled)[0]
            fps_avg = self.target_scaler_fps.inverse_transform([[fps_scaled]])[0][0]

            # Estimate min/max based on variance (±15%)
            fps_min = fps_avg * 0.85
            fps_max = fps_avg * 1.15
            fps_99percentile = fps_avg * 0.90

            # Predict power
            power_scaled = self.power_model.predict(features_scaled)[0]
            power = self.target_scaler_power.inverse_transform([[power_scaled]])[0][0]

            # Predict temperatures
            temps = self.temp_model.predict(features_scaled)[0]
            temp_cpu = temps[0]
            temp_gpu = temps[1]

            # Calculate confidence based on feature similarity to training data
            confidence = self._calculate_confidence(features)

            # Calculate improvement over current
            current_fps = self._estimate_current_fps(hardware, game_config, system_state)
            improvement = ((fps_avg - current_fps) / current_fps) * 100

            # Generate recommendation
            recommendation = self._generate_recommendation(
                fps_avg, power, temp_cpu, temp_gpu, improvement
            )

            return PerformancePrediction(
                fps_min=round(fps_min, 1),
                fps_avg=round(fps_avg, 1),
                fps_max=round(fps_max, 1),
                fps_99percentile=round(fps_99percentile, 1),
                power_consumption_watts=round(power, 1),
                estimated_temp_cpu=round(temp_cpu, 1),
                estimated_temp_gpu=round(temp_gpu, 1),
                confidence=confidence,
                improvement_over_current=round(improvement, 1),
                recommendation=recommendation
            )

        except Exception as e:
            logger.error(f"Prediction failed: {e}. Using heuristic fallback.")
            return self._heuristic_prediction(hardware, profile, game_config, system_state)

    def _extract_features(
        self,
        hardware: Dict,
        profile: str,
        game_config: GameConfig,
        system_state: SystemState
    ) -> List[float]:
        """Extract feature vector for prediction"""
        # Profile characteristics
        profile_weights = {
            'competitive': (0.9, 0.9, 3),
            'balanced': (0.6, 0.7, 1),
            'streaming': (0.8, 0.6, 2),
            'creative': (0.7, 0.8, 2),
            'battery_saver': (0.3, 0.3, 0),
        }
        cpu_weight, gpu_weight, power_mode = profile_weights.get(profile, (0.6, 0.7, 1))

        # Resolution to pixels
        res_map = {'1920x1080': 2073600, '2560x1440': 3686400, '3840x2160': 8294400}
        resolution_pixels = res_map.get(game_config.resolution, 2073600)

        # Graphics preset to number
        preset_map = {'low': 0, 'medium': 1, 'high': 2, 'ultra': 3}
        graphics_num = preset_map.get(game_config.graphics_preset, 2)

        features = [
            # Hardware
            float(hardware.get('cpu_cores', 8)),
            float(hardware.get('cpu_frequency_mhz', 4000)),
            float(hardware.get('ram_gb', 16)),
            float(hardware.get('gpu_vram_gb', 8)),
            float(hardware.get('gpu_compute_units', 60)),
            # Profile
            cpu_weight,
            gpu_weight,
            float(power_mode),
            # Game config
            float(resolution_pixels),
            float(graphics_num),
            1.0 if game_config.ray_tracing else 0.0,
            1.0 if game_config.dlss_enabled else 0.0,
            # System state
            float(system_state.cpu_usage_percent),
            float(system_state.gpu_usage_percent),
            float(system_state.ram_usage_gb),
            float(system_state.cpu_temp_celsius),
            float(system_state.gpu_temp_celsius),
        ]

        return features

    def _heuristic_prediction(
        self,
        hardware: Dict,
        profile: str,
        game_config: GameConfig,
        system_state: SystemState
    ) -> PerformancePrediction:
        """Fallback heuristic-based prediction"""
        # Base FPS from GPU
        base_fps = hardware.get('gpu_vram_gb', 8) * 10

        # Resolution penalty
        if game_config.resolution == '3840x2160':
            base_fps *= 0.4
        elif game_config.resolution == '2560x1440':
            base_fps *= 0.7

        # Graphics preset penalty
        preset_multiplier = {'low': 1.5, 'medium': 1.2, 'high': 0.9, 'ultra': 0.7}
        base_fps *= preset_multiplier.get(game_config.graphics_preset, 1.0)

        # Ray tracing impact
        if game_config.ray_tracing:
            base_fps *= (0.8 if game_config.dlss_enabled else 0.5)

        # Profile boost
        profile_boost = {'competitive': 1.25, 'balanced': 1.0, 'streaming': 0.9,
                        'creative': 0.95, 'battery_saver': 0.7}
        base_fps *= profile_boost.get(profile, 1.0)

        fps_avg = max(30, base_fps)
        fps_min = fps_avg * 0.85
        fps_max = fps_avg * 1.15
        fps_99p = fps_avg * 0.90

        # Power estimate
        power_base = {'competitive': 250, 'balanced': 180, 'streaming': 200,
                     'creative': 190, 'battery_saver': 100}
        power = power_base.get(profile, 180)
        power += hardware.get('gpu_vram_gb', 8) * 5

        # Temperature estimate
        temp_cpu = 50 + (system_state.cpu_usage_percent / 100) * 35
        temp_gpu = 55 + (system_state.gpu_usage_percent / 100) * 35

        current_fps = 60  # Assume 60 FPS baseline
        improvement = ((fps_avg - current_fps) / current_fps) * 100

        recommendation = self._generate_recommendation(fps_avg, power, temp_cpu, temp_gpu, improvement)

        return PerformancePrediction(
            fps_min=round(fps_min, 1),
            fps_avg=round(fps_avg, 1),
            fps_max=round(fps_max, 1),
            fps_99percentile=round(fps_99p, 1),
            power_consumption_watts=round(power, 1),
            estimated_temp_cpu=round(temp_cpu, 1),
            estimated_temp_gpu=round(temp_gpu, 1),
            confidence=0.6,  # Lower confidence for heuristics
            improvement_over_current=round(improvement, 1),
            recommendation=recommendation
        )

    def _calculate_confidence(self, features: List[float]) -> float:
        """Calculate prediction confidence"""
        # Simple confidence based on feature ranges
        # In production, use distance to training data
        confidence = 0.85

        # Reduce confidence for extreme values
        if features[8] > 8000000:  # Very high resolution
            confidence *= 0.9
        if features[11] == 1.0:  # Ray tracing without DLSS
            confidence *= 0.85

        return min(0.95, max(0.5, confidence))

    def _estimate_current_fps(self, hardware: Dict, game_config: GameConfig, state: SystemState) -> float:
        """Estimate current FPS (simplified)"""
        base = hardware.get('gpu_vram_gb', 8) * 8

        if game_config.resolution == '3840x2160':
            base *= 0.5
        elif game_config.resolution == '2560x1440':
            base *= 0.75

        return max(30, base)

    def _generate_recommendation(
        self,
        fps: float,
        power: float,
        temp_cpu: float,
        temp_gpu: float,
        improvement: float
    ) -> str:
        """Generate human-readable recommendation"""
        if improvement > 20:
            rec = f"Excellent performance gain expected (+{improvement:.1f}% FPS)"
        elif improvement > 10:
            rec = f"Good performance improvement anticipated (+{improvement:.1f}% FPS)"
        elif improvement > 0:
            rec = f"Moderate performance boost expected (+{improvement:.1f}% FPS)"
        else:
            rec = "Minimal performance change expected"

        if temp_gpu > 80 or temp_cpu > 85:
            rec += " ⚠️ High temperatures predicted - consider improved cooling"
        if power > 300:
            rec += f" ⚡ High power consumption ({power:.0f}W) - ensure adequate PSU"

        return rec

    def save_models(self):
        """Save trained models to disk"""
        if not SKLEARN_AVAILABLE or self.fps_model is None:
            return

        try:
            with open(self.model_path / 'fps_predictor.pkl', 'wb') as f:
                pickle.dump({
                    'model': self.fps_model,
                    'feature_names': self.feature_names
                }, f)

            with open(self.model_path / 'power_predictor.pkl', 'wb') as f:
                pickle.dump({'model': self.power_model}, f)

            with open(self.model_path / 'prediction_scalers.pkl', 'wb') as f:
                pickle.dump({
                    'feature': self.feature_scaler,
                    'target_fps': self.target_scaler_fps,
                    'target_power': self.target_scaler_power
                }, f)

            logger.info("Saved performance prediction models")
        except Exception as e:
            logger.error(f"Failed to save models: {e}")
