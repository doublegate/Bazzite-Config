"""
Machine Learning Engine for Bazzite Gaming Optimization Suite

This module provides ML-based optimization, performance prediction,
and community analytics for intelligent gaming system tuning.

Version: 1.3.0
"""

from .models.profile_optimizer import ProfileOptimizer
from .models.performance_predictor import PerformancePredictor
from .analytics.data_collector import CommunityDataCollector
from .analytics.dashboard import AnalyticsDashboard

__all__ = [
    'ProfileOptimizer',
    'PerformancePredictor',
    'CommunityDataCollector',
    'AnalyticsDashboard',
]

__version__ = '1.3.0'
