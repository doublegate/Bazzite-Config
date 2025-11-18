"""
AI Engine for Bazzite Gaming Optimization Suite

Deep learning-based features for game detection, performance prediction,
anomaly detection, adaptive tuning, and intelligent recommendations.

Version: 1.4.0
"""

from .game_detection import GameDetector
from .performance_models import LSTMPerformancePredictor
from .anomaly_detection import AnomalyDetector
from .adaptive_tuning import RLAdaptiveOptimizer
from .recommendation import CollaborativeRecommender

__all__ = [
    'GameDetector',
    'LSTMPerformancePredictor',
    'AnomalyDetector',
    'RLAdaptiveOptimizer',
    'CollaborativeRecommender',
]

__version__ = '1.4.0'
