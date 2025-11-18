# Bazzite Optimizer Cloud API Documentation

## Overview

The Bazzite Optimizer Cloud API provides machine learning-powered gaming optimization services through a RESTful API. Built with FastAPI, it offers profile recommendations, performance predictions, and community benchmarking capabilities.

**Base URL**: `http://localhost:8080/api/v1`
**Version**: 1.3.0
**Protocol**: HTTP/HTTPS
**Format**: JSON

## Quick Start

### Starting the API Server

```bash
# Install dependencies
pip install fastapi uvicorn pydantic scikit-learn

# Start the server
python -m ml_engine.cloud_api.api_server

# Or with uvicorn directly
uvicorn ml_engine.cloud_api.api_server:app --host 0.0.0.0 --port 8080 --reload
```

The API will be available at `http://localhost:8080` with interactive documentation at `http://localhost:8080/docs`.

---

## Authentication

Currently, the API uses HTTPBearer token authentication framework (placeholder for future implementation).

**Header**: `Authorization: Bearer <token>`

---

## Endpoints

### 1. Health Check

Check API status and model availability.

**Endpoint**: `GET /api/v1/health`

**Response**:
```json
{
  "status": "healthy",
  "version": "1.3.0",
  "models_loaded": true,
  "timestamp": "2025-11-18T12:00:00Z"
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:8080/api/v1/health
```

---

### 2. Profile Recommendation

Get ML-based profile recommendation based on hardware and usage patterns.

**Endpoint**: `POST /api/v1/profile/recommend`

**Request Body**:
```json
{
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
    "games_played": ["CS2", "Valorant", "Apex Legends"],
    "avg_session_hours": 4.0,
    "streaming": false,
    "content_creation": false,
    "target_fps": 240,
    "target_resolution": "1080p"
  }
}
```

**Response**:
```json
{
  "profile": "competitive",
  "confidence": 0.92,
  "expected_fps_improvement": 18.5,
  "expected_power_consumption": 285,
  "reasoning": "High-end system optimized for competitive FPS gaming with 240Hz target",
  "alternative_profiles": [
    {"name": "balanced", "confidence": 0.75},
    {"name": "streaming", "confidence": 0.45}
  ]
}
```

**Parameters**:

| Field | Type | Description |
|-------|------|-------------|
| `hardware.cpu_cores` | int | Number of CPU cores |
| `hardware.cpu_frequency_mhz` | int | Max CPU frequency in MHz |
| `hardware.ram_gb` | int | RAM size in GB |
| `hardware.gpu_vendor` | string | GPU vendor (nvidia/amd/intel) |
| `hardware.gpu_vram_gb` | int | GPU VRAM in GB |
| `hardware.gpu_compute_units` | int | CUDA cores or stream processors |
| `hardware.storage_type` | string | Storage type (nvme/ssd/hdd) |
| `hardware.has_dedicated_gpu` | bool | Dedicated GPU present |
| `usage.primary_use` | string | Primary use case |
| `usage.games_played` | array | List of games |
| `usage.avg_session_hours` | float | Average gaming session length |
| `usage.target_fps` | int | Target FPS |
| `usage.target_resolution` | string | Target resolution |

**cURL Example**:
```bash
curl -X POST http://localhost:8080/api/v1/profile/recommend \
  -H "Content-Type: application/json" \
  -d @profile_request.json
```

---

### 3. Performance Prediction

Predict FPS and power consumption before applying optimizations.

**Endpoint**: `POST /api/v1/performance/predict`

**Request Body**:
```json
{
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
}
```

**Response**:
```json
{
  "fps_min": 92.3,
  "fps_avg": 108.5,
  "fps_max": 125.7,
  "fps_99percentile": 98.2,
  "power_consumption_watts": 320.0,
  "gpu_temp_celsius": 68.0,
  "improvement_over_current": 27.6,
  "confidence": 0.88
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8080/api/v1/performance/predict \
  -H "Content-Type: application/json" \
  -d @prediction_request.json
```

---

### 4. Community Benchmark Submission

Submit anonymized benchmark results to community database.

**Endpoint**: `POST /api/v1/community/submit`

**Request Body**:
```json
{
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
    "graphics_preset": "high",
    "fps_avg": 425.5,
    "fps_min": 380.0,
    "fps_max": 480.0,
    "fps_99percentile": 390.0,
    "power_watts": 320.0,
    "gpu_temp": 68.0,
    "cpu_temp": 72.0,
    "timestamp": "2025-11-18T12:00:00Z"
  },
  "opt_in": true
}
```

**Response**:
```json
{
  "success": true,
  "submission_id": "a7f3c9d2",
  "message": "Benchmark submitted successfully"
}
```

**Privacy**: Hardware information is anonymized using SHA256 hashing before storage.

**cURL Example**:
```bash
curl -X POST http://localhost:8080/api/v1/community/submit \
  -H "Content-Type: application/json" \
  -d @benchmark_submission.json
```

---

### 5. Community Statistics

Get aggregated community benchmark statistics.

**Endpoint**: `GET /api/v1/community/stats`

**Response**:
```json
{
  "total_submissions": 1247,
  "unique_hardware": 432,
  "games_count": 89,
  "profile_distribution": {
    "competitive": 542,
    "balanced": 389,
    "streaming": 245,
    "safe_defaults": 71
  },
  "fps_ranges": {
    "CS2": {
      "min": 180.0,
      "avg": 325.5,
      "max": 580.0
    },
    "Cyberpunk 2077": {
      "min": 45.0,
      "avg": 95.2,
      "max": 145.0
    }
  },
  "avg_power_consumption": {
    "competitive": 295.0,
    "balanced": 220.0,
    "streaming": 185.0
  }
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:8080/api/v1/community/stats
```

---

### 6. Available Profiles

List all available gaming profiles.

**Endpoint**: `GET /api/v1/profiles`

**Response**:
```json
{
  "profiles": [
    {
      "name": "competitive",
      "description": "Maximum performance for competitive gaming",
      "target_use_case": "High FPS competitive titles (CS2, Valorant)",
      "performance_impact": "high",
      "power_consumption": "high"
    },
    {
      "name": "balanced",
      "description": "Balanced performance and power efficiency",
      "target_use_case": "General gaming with good performance",
      "performance_impact": "medium",
      "power_consumption": "medium"
    },
    {
      "name": "streaming",
      "description": "Optimized for streaming and content creation",
      "target_use_case": "Streaming with OBS/encoding",
      "performance_impact": "medium",
      "power_consumption": "low"
    },
    {
      "name": "safe_defaults",
      "description": "Conservative settings for maximum stability",
      "target_use_case": "Troubleshooting and stability testing",
      "performance_impact": "low",
      "power_consumption": "low"
    }
  ]
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:8080/api/v1/profiles
```

---

## Data Models

### HardwareProfile
```python
{
  "cpu_cores": int,              # 1-128
  "cpu_frequency_mhz": int,      # 1000-6000
  "ram_gb": int,                 # 4-256
  "gpu_vendor": str,             # nvidia/amd/intel
  "gpu_vram_gb": int,            # 2-48
  "gpu_compute_units": int,      # 128-16384
  "storage_type": str,           # nvme/ssd/hdd
  "has_dedicated_gpu": bool
}
```

### UsagePattern
```python
{
  "primary_use": str,            # competitive_gaming/casual_gaming/content_creation/mixed
  "games_played": List[str],     # Game titles
  "avg_session_hours": float,    # 0.5-12.0
  "streaming": bool,
  "content_creation": bool,
  "target_fps": int,             # 30/60/120/144/240/360
  "target_resolution": str       # 1080p/1440p/4k
}
```

### GameConfig
```python
{
  "game_name": str,
  "game_type": str,              # AAA/indie/esports/simulation
  "resolution": str,             # 1080p/1440p/4k
  "graphics_preset": str,        # low/medium/high/ultra
  "ray_tracing": bool,
  "dlss_enabled": bool
}
```

---

## Error Responses

All endpoints return standard HTTP status codes:

**200 OK**: Successful request
**400 Bad Request**: Invalid input data
**404 Not Found**: Resource not found
**500 Internal Server Error**: Server error

**Error Response Format**:
```json
{
  "detail": "Error message describing the issue"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. Recommended for production:
- 100 requests/minute per IP for recommendation endpoints
- 10 submissions/hour per hardware hash for community submissions
- Unlimited for health/stats endpoints

---

## CORS Configuration

The API includes CORS middleware allowing requests from any origin. For production, configure specific allowed origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Integration Examples

### Python Client
```python
import requests

# Profile recommendation
response = requests.post(
    "http://localhost:8080/api/v1/profile/recommend",
    json={
        "hardware": {...},
        "usage": {...}
    }
)
recommendation = response.json()
print(f"Recommended profile: {recommendation['profile']}")
```

### JavaScript/TypeScript
```javascript
const response = await fetch('http://localhost:8080/api/v1/profile/recommend', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    hardware: {...},
    usage: {...}
  })
});
const recommendation = await response.json();
console.log(`Recommended profile: ${recommendation.profile}`);
```

### GUI Integration
```python
from ml_engine.cloud_api.api_server import BazziteOptimizerAPI

# Initialize API in GUI
api = BazziteOptimizerAPI()

# Get recommendation
hardware = HardwareProfile(...)
usage = UsagePattern(...)
recommendation = api.profile_optimizer.recommend_profile(hardware, usage)

# Display in GUI
self.profile_label.setText(f"Recommended: {recommendation.profile_name}")
self.confidence_bar.setValue(int(recommendation.confidence * 100))
```

---

## Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "ml_engine.cloud_api.api_server:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bazzite-optimizer-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bazzite-api
  template:
    metadata:
      labels:
        app: bazzite-api
    spec:
      containers:
      - name: api
        image: bazzite-optimizer-api:1.3.0
        ports:
        - containerPort: 8080
        env:
        - name: MODELS_DIR
          value: /models
```

---

## Support

For issues, questions, or contributions:
- GitHub: https://github.com/yourusername/bazzite-optimizer
- Documentation: See `docs/` directory
- API Tests: `python ml_engine/tests/test_api_server.py`
