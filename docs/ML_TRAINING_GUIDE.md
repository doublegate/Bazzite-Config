# Machine Learning Training Guide

## Overview

The Bazzite Optimizer uses machine learning models to provide intelligent profile recommendations and performance predictions. This guide covers training, evaluation, and deployment of ML models.

## Models Overview

### 1. Profile Optimizer (scikit-learn)
- **Algorithm**: Random Forest Classifier (100 estimators)
- **Purpose**: Recommend optimal gaming profile based on hardware and usage
- **Features**: 15 (hardware specs + usage patterns)
- **Classes**: 4 (competitive, balanced, streaming, safe_defaults)
- **Training Data**: Synthetic + community benchmarks

### 2. Performance Predictor (scikit-learn)
- **Algorithm**: Random Forest + Gradient Boosting Ensemble
- **Purpose**: Predict FPS, power consumption, temperature
- **Features**: 17 (hardware + game config + system state)
- **Targets**: 3 (FPS, power, temperature)
- **Training Data**: Synthetic + real benchmarks

---

## Training the Models

### Quick Start

```bash
# Train all models
python -m ml_engine.models.model_trainer

# Train specific model
python -c "
from ml_engine.models.model_trainer import ModelTrainer
trainer = ModelTrainer()
trainer.train_profile_optimizer()
"
```

### Profile Optimizer Training

```python
from ml_engine.models.profile_optimizer import ProfileOptimizer
from pathlib import Path

# Initialize optimizer
optimizer = ProfileOptimizer()

# Option 1: Train on synthetic data (for testing)
optimizer.train(use_synthetic_data=True, n_samples=1000)

# Option 2: Train on community data
data_file = Path.home() / '.local/share/bazzite-optimizer/community-data/profile_benchmarks.json'
optimizer.train_from_community_data(data_file)

# Save model
models_dir = Path.home() / '.local/share/bazzite-optimizer/ml-models'
optimizer.save_model(models_dir)
```

### Performance Predictor Training

```python
from ml_engine.models.performance_predictor import PerformancePredictor

# Initialize predictor
predictor = PerformancePredictor()

# Train on synthetic data
predictor.train(use_synthetic_data=True, n_samples=2000)

# Save model
predictor.save_model(models_dir)
```

---

## Training Data Format

### Profile Benchmarks (`profile_benchmarks.json`)

```json
{
  "submissions": [
    {
      "hardware_hash": "a7f3c9d2",
      "cpu_cores": 10,
      "cpu_frequency_mhz": 5100,
      "ram_gb": 64,
      "gpu_vendor": "nvidia",
      "gpu_vram_gb": 16,
      "gpu_compute_units": 10752,
      "storage_type": "nvme",
      "has_dedicated_gpu": true,
      "primary_use": "competitive_gaming",
      "target_fps": 240,
      "avg_session_hours": 4.0,
      "profile": "competitive",
      "fps_improvement": 18.5,
      "power_watts": 285,
      "timestamp": "2025-11-18T12:00:00Z"
    }
  ]
}
```

### Performance Benchmarks (`performance_benchmarks.json`)

```json
{
  "benchmarks": [
    {
      "hardware_hash": "a7f3c9d2",
      "cpu_cores": 10,
      "cpu_freq": 5100,
      "gpu_vram": 16,
      "profile": "competitive",
      "game_name": "CS2",
      "resolution": "1080p",
      "graphics_preset": "high",
      "ray_tracing": false,
      "fps_avg": 425.5,
      "fps_min": 380.0,
      "fps_max": 480.0,
      "power_watts": 320.0,
      "gpu_temp": 68.0,
      "timestamp": "2025-11-18T12:00:00Z"
    }
  ]
}
```

---

## Model Evaluation

### Cross-Validation

```python
from ml_engine.models.model_trainer import ModelTrainer

trainer = ModelTrainer()

# Train with 5-fold cross-validation
metrics = trainer.train_profile_optimizer(cv_folds=5)

print(f"Accuracy: {metrics['accuracy']:.3f}")
print(f"Precision: {metrics['precision']:.3f}")
print(f"Recall: {metrics['recall']:.3f}")
print(f"F1 Score: {metrics['f1_score']:.3f}")
```

### Performance Metrics

**Profile Optimizer**:
- Accuracy: >0.85 on validation set
- Precision per class: >0.80
- Recall per class: >0.75
- F1 Score: >0.80

**Performance Predictor**:
- FPS R² Score: >0.75
- Power R² Score: >0.70
- Temperature R² Score: >0.65
- Mean Absolute Error: <10% of actual values

---

## Feature Engineering

### Profile Optimizer Features

```python
features = [
    'cpu_cores',              # 1-128
    'cpu_frequency_mhz',      # 1000-6000
    'ram_gb',                 # 4-256
    'gpu_vram_gb',            # 2-48
    'gpu_compute_units',      # 128-16384
    'has_dedicated_gpu',      # 0/1
    'storage_nvme',           # 0/1
    'storage_ssd',            # 0/1
    'gpu_nvidia',             # 0/1
    'gpu_amd',                # 0/1
    'target_fps',             # 30-360
    'avg_session_hours',      # 0.5-12
    'streaming',              # 0/1
    'content_creation',       # 0/1
    'resolution_score'        # 1-3 (1080p=1, 1440p=2, 4k=3)
]
```

### Performance Predictor Features

```python
features = [
    # Hardware (6 features)
    'cpu_cores', 'cpu_freq', 'ram_gb',
    'gpu_vram', 'gpu_cores', 'gpu_vendor_encoded',

    # Game Config (6 features)
    'game_type_encoded', 'resolution_encoded',
    'graphics_preset_encoded', 'ray_tracing',
    'dlss_enabled', 'game_complexity_score',

    # System State (4 features)
    'background_processes', 'cpu_usage',
    'ram_usage', 'current_fps',

    # Profile (1 feature)
    'profile_encoded'
]
```

---

## Synthetic Data Generation

### Profile Optimizer Synthetic Data

```python
def generate_synthetic_profile_data(n_samples=1000):
    """Generate realistic training data"""
    data = []

    for _ in range(n_samples):
        # High-end competitive setup
        if random.random() < 0.3:
            sample = {
                'cpu_cores': random.randint(8, 16),
                'cpu_frequency_mhz': random.randint(4500, 5500),
                'ram_gb': random.choice([32, 64]),
                'gpu_vram_gb': random.choice([8, 12, 16, 24]),
                'target_fps': random.choice([144, 240, 360]),
                'profile': 'competitive'
            }

        # Balanced gaming
        elif random.random() < 0.5:
            sample = {
                'cpu_cores': random.randint(4, 8),
                'cpu_frequency_mhz': random.randint(3500, 4500),
                'ram_gb': random.choice([16, 32]),
                'gpu_vram_gb': random.choice([6, 8, 12]),
                'target_fps': random.choice([60, 120, 144]),
                'profile': 'balanced'
            }

        # Add more patterns...

        data.append(sample)

    return data
```

---

## Model Persistence

### Saving Models

```python
import pickle
from pathlib import Path

# Save with pickle
models_dir = Path.home() / '.local/share/bazzite-optimizer/ml-models'
models_dir.mkdir(parents=True, exist_ok=True)

with open(models_dir / 'profile_optimizer.pkl', 'wb') as f:
    pickle.dump({
        'classifier': optimizer.classifier,
        'scaler': optimizer.scaler,
        'feature_names': optimizer.feature_names,
        'profile_mapping': optimizer.profile_mapping
    }, f)
```

### Loading Models

```python
# Load from pickle
with open(models_dir / 'profile_optimizer.pkl', 'rb') as f:
    model_data = pickle.load(f)
    optimizer.classifier = model_data['classifier']
    optimizer.scaler = model_data['scaler']
```

---

## Automated Training Pipeline

### Scheduled Retraining

```python
from ml_engine.models.model_trainer import ModelTrainer
import schedule
import time

def train_all_models():
    """Retrain all models on latest community data"""
    trainer = ModelTrainer()

    # Check if enough new data
    if trainer._has_sufficient_new_data():
        print("Retraining models with new community data...")

        # Train profile optimizer
        profile_metrics = trainer.train_profile_optimizer(cv_folds=5)
        print(f"Profile optimizer accuracy: {profile_metrics['accuracy']:.3f}")

        # Train performance predictor
        perf_metrics = trainer.train_performance_predictor(cv_folds=5)
        print(f"Performance predictor R²: {perf_metrics['fps_r2']:.3f}")

# Schedule daily retraining at 2 AM
schedule.every().day.at("02:00").do(train_all_models)

while True:
    schedule.run_pending()
    time.sleep(3600)
```

---

## Best Practices

### 1. Data Quality
- Validate all submissions before adding to training set
- Remove outliers (>3 standard deviations)
- Balance classes to prevent bias
- Use stratified sampling for train/test split

### 2. Model Versioning
- Save models with version tags
- Track training metrics for each version
- Keep last 3 model versions for rollback
- Document feature changes between versions

### 3. Monitoring
- Track prediction accuracy in production
- Log failed predictions for analysis
- Monitor model drift over time
- A/B test new models before deployment

### 4. Privacy
- Always anonymize hardware data (SHA256 hash)
- Never store personally identifiable information
- Aggregate statistics before sharing
- Provide opt-out mechanism

---

## Troubleshooting

### Low Accuracy

**Problem**: Model accuracy <70%
**Solutions**:
- Collect more diverse training data (aim for 1000+ samples per class)
- Add more features (e.g., monitor refresh rate, cooling solution)
- Try different algorithms (XGBoost, LightGBM)
- Tune hyperparameters (n_estimators, max_depth)

### Overfitting

**Problem**: High training accuracy but low validation accuracy
**Solutions**:
- Increase regularization (max_depth, min_samples_split)
- Add more training data
- Use cross-validation
- Simplify model (reduce features)

### Biased Predictions

**Problem**: Model favors one profile
**Solutions**:
- Balance training data (equal samples per class)
- Use class weights in classifier
- Collect more data for underrepresented profiles
- Review feature importance

---

## Advanced Topics

### Hyperparameter Tuning

```python
from sklearn.model_selection import GridSearchCV

# Define parameter grid
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [10, 20, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

# Grid search with cross-validation
grid_search = GridSearchCV(
    RandomForestClassifier(),
    param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1
)

grid_search.fit(X_train, y_train)
best_params = grid_search.best_params_
```

### Feature Importance

```python
# Get feature importance from Random Forest
importances = optimizer.classifier.feature_importances_
feature_importance = sorted(
    zip(optimizer.feature_names, importances),
    key=lambda x: x[1],
    reverse=True
)

# Print top 10 features
for feature, importance in feature_importance[:10]:
    print(f"{feature}: {importance:.3f}")
```

---

## Next Steps

1. Collect real community benchmark data
2. Implement automated retraining pipeline
3. Deploy to production with monitoring
4. Expand to deep learning models (see v1.4.0)
5. Add A/B testing framework

For deep learning implementations, see `docs/DEEP_LEARNING_GUIDE.md` (v1.4.0).
