"""
Model Trainer for Community Data

Trains ML models from aggregated community benchmark data
with continuous learning and model versioning.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    from sklearn.model_selection import cross_val_score, GridSearchCV
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from .profile_optimizer import ProfileOptimizer
from .performance_predictor import PerformancePredictor

logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Automated model trainer using community benchmark data

    Handles data preprocessing, model training, validation,
    and deployment of improved models.
    """

    def __init__(self, data_dir: Optional[Path] = None, models_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path.home() / '.local/share/bazzite-optimizer/community-data'
        self.models_dir = models_dir or Path.home() / '.local/share/bazzite-optimizer/ml-models'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self.training_history: List[Dict] = []
        self._load_history()

    def _load_history(self):
        """Load training history"""
        history_file = self.models_dir / 'training_history.json'
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    self.training_history = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load training history: {e}")

    def train_profile_optimizer(
        self,
        min_samples: int = 100,
        cv_folds: int = 5
    ) -> Dict[str, float]:
        """
        Train profile optimizer from community data

        Args:
            min_samples: Minimum samples required for training
            cv_folds: Cross-validation folds

        Returns:
            Training metrics dict
        """
        if not SKLEARN_AVAILABLE:
            logger.error("scikit-learn required for training")
            return {'error': 'scikit-learn not available'}

        logger.info("Starting profile optimizer training...")

        # Load community data
        data = self._load_community_data('profile_benchmarks.json')
        if len(data) < min_samples:
            logger.warning(f"Insufficient data: {len(data)} < {min_samples}")
            return {'error': f'Insufficient data: {len(data)} samples'}

        # Initialize optimizer
        optimizer = ProfileOptimizer(self.models_dir)

        # Train from community data
        success = optimizer.train_from_community_data(
            self.data_dir / 'profile_benchmarks.json'
        )

        if success:
            # Validate model
            metrics = self._validate_profile_model(optimizer, data, cv_folds)

            # Save training record
            self._record_training('profile_optimizer', metrics)

            logger.info(f"Profile optimizer trained successfully. Accuracy: {metrics.get('accuracy', 0):.2f}")
            return metrics
        else:
            return {'error': 'Training failed'}

    def train_performance_predictor(
        self,
        min_samples: int = 500
    ) -> Dict[str, float]:
        """
        Train performance predictor from benchmark data

        Args:
            min_samples: Minimum samples required

        Returns:
            Training metrics dict
        """
        if not SKLEARN_AVAILABLE:
            logger.error("scikit-learn required for training")
            return {'error': 'scikit-learn not available'}

        logger.info("Starting performance predictor training...")

        data = self._load_community_data('performance_benchmarks.json')
        if len(data) < min_samples:
            logger.warning(f"Insufficient data: {len(data)} < {min_samples}")
            return {'error': f'Insufficient data: {len(data)} samples'}

        predictor = PerformancePredictor(self.models_dir)

        # Extract training data
        X, y_fps, y_power = self._prepare_performance_data(data)

        # Train models
        from sklearn.model_selection import train_test_split

        X_train, X_test, y_fps_train, y_fps_test = train_test_split(
            X, y_fps, test_size=0.2, random_state=42
        )

        # Train FPS model
        predictor.feature_scaler.fit(X_train)
        X_train_scaled = predictor.feature_scaler.transform(X_train)
        X_test_scaled = predictor.feature_scaler.transform(X_test)

        predictor.fps_model.fit(X_train_scaled, y_fps_train)

        # Evaluate
        from sklearn.metrics import mean_absolute_error, r2_score
        y_pred = predictor.fps_model.predict(X_test_scaled)

        metrics = {
            'mae_fps': float(mean_absolute_error(y_fps_test, y_pred)),
            'r2_fps': float(r2_score(y_fps_test, y_pred)),
            'samples': len(data)
        }

        # Save models
        predictor.save_models()

        # Record training
        self._record_training('performance_predictor', metrics)

        logger.info(f"Performance predictor trained. MAE: {metrics['mae_fps']:.1f} FPS, R²: {metrics['r2_fps']:.3f}")
        return metrics

    def _load_community_data(self, filename: str) -> List[Dict]:
        """Load community benchmark data"""
        data_file = self.data_dir / filename
        if not data_file.exists():
            logger.warning(f"Data file not found: {filename}")
            return []

        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
            return data.get('benchmarks', [])
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            return []

    def _prepare_performance_data(self, data: List[Dict]) -> Tuple:
        """Prepare performance prediction training data"""
        import numpy as np

        X = []
        y_fps = []
        y_power = []

        for entry in data:
            # Extract features (simplified)
            features = [
                entry.get('cpu_cores', 8),
                entry.get('cpu_freq', 4000),
                entry.get('ram_gb', 16),
                entry.get('gpu_vram', 8),
                entry.get('gpu_compute', 60),
                # Profile features
                entry.get('profile_cpu_weight', 0.7),
                entry.get('profile_gpu_weight', 0.7),
                entry.get('profile_power_mode', 1),
                # Game config
                entry.get('resolution_pixels', 2073600),
                entry.get('graphics_preset', 2),
                1 if entry.get('ray_tracing') else 0,
                1 if entry.get('dlss') else 0,
                # System state
                entry.get('cpu_usage', 70),
                entry.get('gpu_usage', 85),
                entry.get('ram_usage', 12),
                entry.get('cpu_temp', 65),
                entry.get('gpu_temp', 70),
            ]

            X.append(features)
            y_fps.append(entry.get('fps_avg', 60))
            y_power.append(entry.get('power_watts', 150))

        return np.array(X), np.array(y_fps), np.array(y_power)

    def _validate_profile_model(
        self,
        optimizer: ProfileOptimizer,
        data: List[Dict],
        cv_folds: int
    ) -> Dict[str, float]:
        """Validate profile optimizer model"""
        if not SKLEARN_AVAILABLE or optimizer.classifier is None:
            return {'accuracy': 0.0}

        # Cross-validation
        X_val = []
        y_val = []

        for entry in data:
            from .profile_optimizer import HardwareProfile, UsagePattern

            hardware = HardwareProfile(**entry['hardware'])
            usage = UsagePattern(**entry['usage'])
            features = optimizer._extract_features(hardware, usage)
            X_val.append(features)

            optimal_profile = entry['optimal_profile']
            label = next(k for k, v in optimizer.profile_mapping.items() if v == optimal_profile)
            y_val.append(label)

        import numpy as np
        X_val = np.array(X_val)
        y_val = np.array(y_val)

        X_scaled = optimizer.scaler.transform(X_val)

        # Cross-validation scores
        scores = cross_val_score(optimizer.classifier, X_scaled, y_val, cv=cv_folds)

        return {
            'accuracy': float(scores.mean()),
            'std': float(scores.std()),
            'cv_folds': cv_folds
        }

    def _record_training(self, model_name: str, metrics: Dict):
        """Record training session"""
        record = {
            'model': model_name,
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics
        }

        self.training_history.append(record)

        # Save history
        history_file = self.models_dir / 'training_history.json'
        try:
            with open(history_file, 'w') as f:
                json.dump(self.training_history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save training history: {e}")

    def get_training_history(self) -> List[Dict]:
        """Get training history"""
        return self.training_history

    def schedule_retraining(self, interval_days: int = 7) -> bool:
        """
        Schedule automatic model retraining

        Args:
            interval_days: Retraining interval in days

        Returns:
            True if schedule created successfully
        """
        # In production, this would integrate with systemd timers or cron
        logger.info(f"Retraining scheduled every {interval_days} days")
        return True
