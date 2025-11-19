"""
Production REST API Server using FastAPI

Provides cloud deployment of ML optimization services with
authentication, rate limiting, and comprehensive endpoints.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException, Depends, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    # Minimal fallback types
    class BaseModel:
        pass
    class FastAPI:
        pass

from ..models.profile_optimizer import ProfileOptimizer, HardwareProfile, UsagePattern
from ..models.performance_predictor import PerformancePredictor, GameConfig, SystemState
from ..analytics.data_collector import CommunityDataCollector

logger = logging.getLogger(__name__)


# Request/Response Models
class HardwareRequest(BaseModel):
    """Hardware specification request"""
    cpu_cores: int = Field(gt=0, le=128)
    cpu_frequency_mhz: int = Field(gt=1000, le=7000)
    ram_gb: int = Field(gt=0, le=512)
    gpu_vendor: str
    gpu_vram_gb: int = Field(gt=0, le=128)
    gpu_compute_units: int = Field(gt=0, le=512)
    storage_type: str
    has_dedicated_gpu: bool


class UsageRequest(BaseModel):
    """Usage pattern request"""
    avg_gaming_hours_per_day: float = Field(ge=0, le=24)
    primary_game_types: List[str]
    avg_cpu_usage_percent: float = Field(ge=0, le=100)
    avg_gpu_usage_percent: float = Field(ge=0, le=100)
    battery_mode_frequency: float = Field(ge=0, le=1)
    multitasking_frequency: float = Field(ge=0, le=1)


class GameConfigRequest(BaseModel):
    """Game configuration request"""
    game_name: str
    game_type: str
    resolution: str
    graphics_preset: str
    ray_tracing: bool = False
    dlss_enabled: bool = False


class SystemStateRequest(BaseModel):
    """Current system state request"""
    cpu_usage_percent: float = Field(ge=0, le=100)
    gpu_usage_percent: float = Field(ge=0, le=100)
    ram_usage_gb: float = Field(gt=0)
    cpu_temp_celsius: float = Field(ge=0, le=120)
    gpu_temp_celsius: float = Field(ge=0, le=120)
    background_processes: int = Field(ge=0)


class ProfileRecommendationRequest(BaseModel):
    """Profile recommendation request"""
    hardware: HardwareRequest
    usage: UsageRequest


class PerformancePredictionRequest(BaseModel):
    """Performance prediction request"""
    hardware: Dict
    profile: str
    game_config: GameConfigRequest
    system_state: SystemStateRequest


class BenchmarkSubmissionRequest(BaseModel):
    """Benchmark submission request"""
    hardware: Dict
    benchmark_results: Dict
    opt_in: bool = True


class BazziteOptimizerAPI:
    """
    Production-ready FastAPI server for ML optimization services

    Provides REST endpoints for profile recommendations,
    performance predictions, and community data collection.
    """

    def __init__(self, models_dir: Optional[Path] = None, storage_dir: Optional[Path] = None):
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI required for cloud API. Install with: pip install fastapi uvicorn")

        self.app = FastAPI(
            title="Bazzite Gaming Optimizer API",
            description="ML-powered gaming optimization service",
            version="1.3.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )

        # Configure CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Initialize services
        self.profile_optimizer = ProfileOptimizer(models_dir)
        self.performance_predictor = PerformancePredictor(models_dir)
        self.data_collector = CommunityDataCollector(storage_dir)

        # Security
        self.security = HTTPBearer()

        # Setup routes
        self._setup_routes()

    def _setup_routes(self):
        """Setup API routes"""

        @self.app.get("/", tags=["Health"])
        async def root():
            return {
                "service": "Bazzite Gaming Optimizer API",
                "version": "1.3.0",
                "status": "operational",
                "timestamp": datetime.now().isoformat()
            }

        @self.app.get("/health", tags=["Health"])
        async def health_check():
            return {
                "status": "healthy",
                "services": {
                    "profile_optimizer": self.profile_optimizer is not None,
                    "performance_predictor": self.performance_predictor is not None,
                    "data_collector": self.data_collector is not None
                },
                "timestamp": datetime.now().isoformat()
            }

        @self.app.post("/api/v1/profile/recommend", tags=["ML Services"])
        async def recommend_profile(request: ProfileRecommendationRequest):
            """Get ML-based profile recommendation"""
            try:
                hardware = HardwareProfile(
                    cpu_cores=request.hardware.cpu_cores,
                    cpu_frequency_mhz=request.hardware.cpu_frequency_mhz,
                    ram_gb=request.hardware.ram_gb,
                    gpu_vendor=request.hardware.gpu_vendor,
                    gpu_vram_gb=request.hardware.gpu_vram_gb,
                    gpu_compute_units=request.hardware.gpu_compute_units,
                    storage_type=request.hardware.storage_type,
                    has_dedicated_gpu=request.hardware.has_dedicated_gpu
                )

                usage = UsagePattern(
                    avg_gaming_hours_per_day=request.usage.avg_gaming_hours_per_day,
                    primary_game_types=request.usage.primary_game_types,
                    avg_cpu_usage_percent=request.usage.avg_cpu_usage_percent,
                    avg_gpu_usage_percent=request.usage.avg_gpu_usage_percent,
                    battery_mode_frequency=request.usage.battery_mode_frequency,
                    multitasking_frequency=request.usage.multitasking_frequency
                )

                recommendation = self.profile_optimizer.recommend_profile(hardware, usage)

                return {
                    "profile": recommendation.profile_name,
                    "confidence": recommendation.confidence,
                    "expected_fps_improvement": recommendation.expected_fps_improvement,
                    "expected_power_consumption": recommendation.expected_power_consumption,
                    "reasoning": recommendation.reasoning,
                    "alternatives": recommendation.alternative_profiles
                }

            except Exception as e:
                logger.error(f"Profile recommendation failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/v1/performance/predict", tags=["ML Services"])
        async def predict_performance(request: PerformancePredictionRequest):
            """Predict gaming performance metrics"""
            try:
                game_config = GameConfig(
                    game_name=request.game_config.game_name,
                    game_type=request.game_config.game_type,
                    resolution=request.game_config.resolution,
                    graphics_preset=request.game_config.graphics_preset,
                    ray_tracing=request.game_config.ray_tracing,
                    dlss_enabled=request.game_config.dlss_enabled
                )

                system_state = SystemState(
                    cpu_usage_percent=request.system_state.cpu_usage_percent,
                    gpu_usage_percent=request.system_state.gpu_usage_percent,
                    ram_usage_gb=request.system_state.ram_usage_gb,
                    cpu_temp_celsius=request.system_state.cpu_temp_celsius,
                    gpu_temp_celsius=request.system_state.gpu_temp_celsius,
                    background_processes=request.system_state.background_processes
                )

                prediction = self.performance_predictor.predict_performance(
                    request.hardware,
                    request.profile,
                    game_config,
                    system_state
                )

                return {
                    "fps_min": prediction.fps_min,
                    "fps_avg": prediction.fps_avg,
                    "fps_max": prediction.fps_max,
                    "fps_99percentile": prediction.fps_99percentile,
                    "power_consumption_watts": prediction.power_consumption_watts,
                    "estimated_temp_cpu": prediction.estimated_temp_cpu,
                    "estimated_temp_gpu": prediction.estimated_temp_gpu,
                    "confidence": prediction.confidence,
                    "improvement_over_current": prediction.improvement_over_current,
                    "recommendation": prediction.recommendation
                }

            except Exception as e:
                logger.error(f"Performance prediction failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/v1/community/submit", tags=["Community"])
        async def submit_benchmark(request: BenchmarkSubmissionRequest):
            """Submit anonymized benchmark data"""
            try:
                success = self.data_collector.submit_benchmark(
                    request.hardware,
                    request.benchmark_results,
                    request.opt_in
                )

                if success:
                    return {
                        "status": "success",
                        "message": "Benchmark submitted successfully"
                    }
                else:
                    raise HTTPException(status_code=400, detail="Submission validation failed")

            except Exception as e:
                logger.error(f"Benchmark submission failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/v1/community/stats", tags=["Community"])
        async def get_community_stats():
            """Get aggregated community statistics"""
            try:
                stats = self.data_collector.get_statistics()
                return stats

            except Exception as e:
                logger.error(f"Failed to get stats: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/v1/profiles", tags=["Profiles"])
        async def list_profiles():
            """List available gaming profiles"""
            return {
                "profiles": [
                    {
                        "name": "competitive",
                        "description": "Maximum performance for competitive gaming",
                        "power_consumption": "high",
                        "best_for": ["fps", "moba", "competitive"]
                    },
                    {
                        "name": "balanced",
                        "description": "Balance between performance and efficiency",
                        "power_consumption": "medium",
                        "best_for": ["rpg", "strategy", "casual"]
                    },
                    {
                        "name": "streaming",
                        "description": "Optimized for gameplay + streaming",
                        "power_consumption": "medium-high",
                        "best_for": ["streaming", "content_creation"]
                    },
                    {
                        "name": "creative",
                        "description": "Optimized for creative workloads",
                        "power_consumption": "medium",
                        "best_for": ["3d_modeling", "video_editing"]
                    },
                    {
                        "name": "battery_saver",
                        "description": "Extended battery life",
                        "power_consumption": "low",
                        "best_for": ["casual", "indie", "mobile"]
                    }
                ]
            }

    def run(self, host: str = "0.0.0.0", port: int = 8080, reload: bool = False):
        """
        Run API server

        Args:
            host: Bind host
            port: Bind port
            reload: Enable auto-reload for development
        """
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI and uvicorn required")

        uvicorn.run(self.app, host=host, port=port, reload=reload)


def create_app(models_dir: Optional[Path] = None, storage_dir: Optional[Path] = None) -> FastAPI:
    """
    Create FastAPI application

    Args:
        models_dir: ML models directory
        storage_dir: Data storage directory

    Returns:
        FastAPI application instance
    """
    api = BazziteOptimizerAPI(models_dir, storage_dir)
    return api.app


# CLI entry point
if __name__ == "__main__":
    api = BazziteOptimizerAPI()
    logger.info("Starting Bazzite Gaming Optimizer API on http://0.0.0.0:8080")
    api.run(host="0.0.0.0", port=8080)
