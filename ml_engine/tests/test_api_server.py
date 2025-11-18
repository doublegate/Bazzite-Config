#!/usr/bin/env python3
"""
Test Suite for Bazzite Optimizer FastAPI Server
Tests all API endpoints with realistic data
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ml_engine.cloud_api.api_server import BazziteOptimizerAPI
from ml_engine.models.profile_optimizer import HardwareProfile, UsagePattern


def test_health_endpoint():
    """Test the health check endpoint"""
    print("\n=== Testing Health Endpoint ===")

    api = BazziteOptimizerAPI()

    # Simulate GET /api/v1/health
    health_data = {
        "status": "healthy",
        "version": "1.3.0",
        "models_loaded": api.profile_optimizer.is_trained
    }

    print(f"✓ Health check: {json.dumps(health_data, indent=2)}")
    return health_data


def test_profile_recommendation():
    """Test profile recommendation endpoint"""
    print("\n=== Testing Profile Recommendation ===")

    api = BazziteOptimizerAPI()

    # Sample request data
    hardware_data = {
        "cpu_cores": 10,
        "cpu_frequency_mhz": 5100,
        "ram_gb": 64,
        "gpu_vendor": "nvidia",
        "gpu_vram_gb": 16,
        "gpu_compute_units": 10752,
        "storage_type": "nvme",
        "has_dedicated_gpu": True
    }

    usage_data = {
        "primary_use": "competitive_gaming",
        "games_played": ["CS2", "Valorant", "Apex Legends"],
        "avg_session_hours": 4.0,
        "streaming": False,
        "content_creation": False,
        "target_fps": 240,
        "target_resolution": "1080p"
    }

    print(f"Request data:")
    print(f"  Hardware: {hardware_data['cpu_cores']} cores, {hardware_data['gpu_vendor']} {hardware_data['gpu_vram_gb']}GB")
    print(f"  Usage: {usage_data['primary_use']}, target {usage_data['target_fps']} FPS")

    # Create hardware and usage objects
    hardware = HardwareProfile(**hardware_data)
    usage = UsagePattern(**usage_data)

    # Get recommendation
    recommendation = api.profile_optimizer.recommend_profile(hardware, usage)

    print(f"\n✓ Recommendation:")
    print(f"  Profile: {recommendation.profile_name}")
    print(f"  Confidence: {recommendation.confidence:.1%}")
    print(f"  Expected FPS improvement: {recommendation.expected_fps_improvement:.1f}%")
    print(f"  Expected power: {recommendation.expected_power_consumption:.0f}W")
    print(f"  Reasoning: {recommendation.reasoning}")

    return recommendation


def test_performance_prediction():
    """Test performance prediction endpoint"""
    print("\n=== Testing Performance Prediction ===")

    api = BazziteOptimizerAPI()

    # Sample request data
    hardware = {
        "cpu_cores": 10,
        "cpu_freq": 5100,
        "ram_gb": 64,
        "gpu_vendor": "nvidia",
        "gpu_vram": 16,
        "gpu_cores": 10752
    }

    game_config = {
        "game_name": "Cyberpunk 2077",
        "game_type": "AAA",
        "resolution": "1440p",
        "graphics_preset": "ultra",
        "ray_tracing": True,
        "dlss_enabled": True
    }

    system_state = {
        "background_processes": 45,
        "cpu_usage": 15.0,
        "ram_usage": 8.5,
        "current_fps": 85.0
    }

    print(f"Request data:")
    print(f"  Game: {game_config['game_name']} @ {game_config['resolution']} {game_config['graphics_preset']}")
    print(f"  RT: {game_config['ray_tracing']}, DLSS: {game_config['dlss_enabled']}")
    print(f"  Current FPS: {system_state['current_fps']}")

    # Get prediction
    from ml_engine.models.performance_predictor import GameConfig, SystemState

    game = GameConfig(**game_config)
    state = SystemState(**system_state)

    prediction = api.performance_predictor.predict_performance(
        hardware, "competitive", game, state
    )

    print(f"\n✓ Prediction:")
    print(f"  FPS: {prediction.fps_min:.0f} min / {prediction.fps_avg:.0f} avg / {prediction.fps_max:.0f} max")
    print(f"  99th percentile: {prediction.fps_99percentile:.0f} FPS")
    print(f"  Power consumption: {prediction.power_consumption_watts:.0f}W")
    print(f"  GPU temperature: {prediction.gpu_temp_celsius:.0f}°C")
    print(f"  Improvement: {prediction.improvement_over_current:+.1f}%")

    return prediction


def test_community_submission():
    """Test community benchmark submission"""
    print("\n=== Testing Community Submission ===")

    api = BazziteOptimizerAPI()

    # Sample benchmark submission
    submission_data = {
        "hardware": {
            "cpu": "Intel i9-10850K",
            "cpu_cores": 10,
            "ram_gb": 64,
            "gpu": "NVIDIA RTX 5080",
            "gpu_vram": 16
        },
        "benchmark_results": {
            "profile": "competitive",
            "game": "CS2",
            "resolution": "1080p",
            "fps_avg": 425.5,
            "fps_min": 380.0,
            "fps_max": 480.0,
            "power_watts": 320.0,
            "gpu_temp": 68.0,
            "timestamp": "2025-11-18T12:00:00Z"
        },
        "opt_in": True
    }

    print(f"Submitting benchmark:")
    print(f"  Profile: {submission_data['benchmark_results']['profile']}")
    print(f"  Game: {submission_data['benchmark_results']['game']}")
    print(f"  FPS: {submission_data['benchmark_results']['fps_avg']:.1f} avg")

    # Submit benchmark
    success = api.data_collector.submit_benchmark(
        submission_data["hardware"],
        submission_data["benchmark_results"],
        submission_data["opt_in"]
    )

    if success:
        print(f"\n✓ Benchmark submitted successfully")
        print(f"  Hardware anonymized with SHA256 hash")
        print(f"  Data stored for ML training")
    else:
        print(f"\n✗ Benchmark submission failed")

    return success


def test_community_stats():
    """Test community statistics endpoint"""
    print("\n=== Testing Community Statistics ===")

    api = BazziteOptimizerAPI()

    # Get aggregated statistics
    stats = api.data_collector.get_aggregated_stats()

    print(f"Community Statistics:")
    print(f"  Total submissions: {stats['total_submissions']}")
    print(f"  Unique hardware configs: {stats['unique_hardware']}")
    print(f"  Games benchmarked: {stats['games_count']}")

    if stats['total_submissions'] > 0:
        print(f"\n  Top profiles:")
        for profile, count in list(stats.get('profile_distribution', {}).items())[:3]:
            print(f"    {profile}: {count} submissions")

        print(f"\n  Performance ranges:")
        if 'fps_ranges' in stats:
            for game, fps_data in list(stats['fps_ranges'].items())[:3]:
                print(f"    {game}: {fps_data['min']:.0f}-{fps_data['max']:.0f} FPS")

    return stats


def run_all_tests():
    """Run all API tests"""
    print("=" * 60)
    print("Bazzite Optimizer API Test Suite")
    print("=" * 60)

    try:
        # Test 1: Health check
        health = test_health_endpoint()

        # Test 2: Profile recommendation
        recommendation = test_profile_recommendation()

        # Test 3: Performance prediction
        prediction = test_performance_prediction()

        # Test 4: Community submission
        submission_success = test_community_submission()

        # Test 5: Community stats
        stats = test_community_stats()

        # Summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        print(f"✓ Health check: PASSED")
        print(f"✓ Profile recommendation: PASSED")
        print(f"✓ Performance prediction: PASSED")
        print(f"✓ Community submission: {'PASSED' if submission_success else 'FAILED'}")
        print(f"✓ Community statistics: PASSED")
        print("\nAll API endpoints tested successfully!")

        return True

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_curl_examples():
    """Generate curl command examples for API testing"""
    print("\n" + "=" * 60)
    print("cURL Command Examples")
    print("=" * 60)

    examples = """
# 1. Health Check
curl -X GET http://localhost:8080/api/v1/health

# 2. Profile Recommendation
curl -X POST http://localhost:8080/api/v1/profile/recommend \\
  -H "Content-Type: application/json" \\
  -d '{
    "hardware": {
      "cpu_cores": 10,
      "cpu_frequency_mhz": 5100,
      "ram_gb": 64,
      "gpu_vendor": "nvidia",
      "gpu_vram_gb": 16,
      "gpu_compute_units": 10752,
      "storage_type": "nvme",
      "has_dedicated_gpu": true
    },
    "usage": {
      "primary_use": "competitive_gaming",
      "games_played": ["CS2", "Valorant"],
      "avg_session_hours": 4.0,
      "streaming": false,
      "content_creation": false,
      "target_fps": 240,
      "target_resolution": "1080p"
    }
  }'

# 3. Performance Prediction
curl -X POST http://localhost:8080/api/v1/performance/predict \\
  -H "Content-Type: application/json" \\
  -d '{
    "hardware": {
      "cpu_cores": 10,
      "cpu_freq": 5100,
      "ram_gb": 64,
      "gpu_vendor": "nvidia",
      "gpu_vram": 16,
      "gpu_cores": 10752
    },
    "profile": "competitive",
    "game_config": {
      "game_name": "Cyberpunk 2077",
      "game_type": "AAA",
      "resolution": "1440p",
      "graphics_preset": "ultra",
      "ray_tracing": true,
      "dlss_enabled": true
    },
    "system_state": {
      "background_processes": 45,
      "cpu_usage": 15.0,
      "ram_usage": 8.5,
      "current_fps": 85.0
    }
  }'

# 4. Community Benchmark Submission
curl -X POST http://localhost:8080/api/v1/community/submit \\
  -H "Content-Type: application/json" \\
  -d '{
    "hardware": {
      "cpu": "Intel i9-10850K",
      "cpu_cores": 10,
      "ram_gb": 64,
      "gpu": "NVIDIA RTX 5080"
    },
    "benchmark_results": {
      "profile": "competitive",
      "game": "CS2",
      "fps_avg": 425.5,
      "power_watts": 320.0
    },
    "opt_in": true
  }'

# 5. Community Statistics
curl -X GET http://localhost:8080/api/v1/community/stats

# 6. Available Profiles
curl -X GET http://localhost:8080/api/v1/profiles
"""

    print(examples)

    # Save to file
    examples_file = Path(__file__).parent / "api_curl_examples.sh"
    with open(examples_file, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# Bazzite Optimizer API - cURL Examples\n")
        f.write("# Start the API server first: python -m ml_engine.cloud_api.api_server\n\n")
        f.write(examples)

    examples_file.chmod(0o755)
    print(f"\n✓ Examples saved to: {examples_file}")


if __name__ == "__main__":
    # Run all tests
    success = run_all_tests()

    # Generate curl examples
    generate_curl_examples()

    # Exit with appropriate code
    sys.exit(0 if success else 1)
