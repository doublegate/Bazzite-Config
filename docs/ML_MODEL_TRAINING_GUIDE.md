# Bazzite Gaming Optimizer - ML Model Training Guide

Complete guide for collecting real gaming data, training machine learning models, optimizing hyperparameters, and deploying trained models for production use.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Phase 1: Data Collection](#phase-1-data-collection)
- [Phase 2: Data Preprocessing](#phase-2-data-preprocessing)
- [Phase 3: Model Training](#phase-3-model-training)
- [Phase 4: Hyperparameter Optimization](#phase-4-hyperparameter-optimization)
- [Phase 5: Model Evaluation](#phase-5-model-evaluation)
- [Phase 6: Model Deployment](#phase-6-model-deployment)
- [Advanced Topics](#advanced-topics)
- [Troubleshooting](#troubleshooting)

---

## Overview

The Bazzite Gaming Optimizer uses machine learning to:

1. **Profile Classification**: Recommend optimal gaming profile (Competitive, Balanced, Streaming) based on hardware and usage patterns
2. **Performance Prediction**: Predict FPS, power consumption, and temperatures for different configurations
3. **Anomaly Detection**: Identify system health issues using VAE autoencoder
4. **Adaptive Optimization**: Use DQN reinforcement learning to dynamically optimize settings

This guide focuses on **training models with real data** collected from your gaming sessions.

---

## Prerequisites

### Software Requirements

**Python Dependencies**:
```bash
pip install -r requirements-ml.txt
```

Key packages:
- `scikit-learn>=1.3.0` - Classical ML algorithms
- `torch>=2.0.0` - Deep learning framework
- `psutil>=5.9.0` - System metrics collection
- `GPUtil>=1.4.0` - GPU metrics (NVIDIA)
- `pandas>=2.0.0` - Data manipulation
- `numpy>=1.24.0` - Numerical computing
- `matplotlib>=3.7.0` - Visualization
- `seaborn>=0.12.0` - Statistical visualization

**Hardware Requirements**:

- **Minimum**: 16GB RAM, 4-core CPU
- **Recommended**: 32GB+ RAM, 8+ core CPU, NVIDIA GPU (for deep learning)
- **Storage**: 10GB+ free space for datasets and models

### Verify Installation

```bash
python3 -c "import sklearn; import torch; print(f'sklearn: {sklearn.__version__}, torch: {torch.__version__}')"
```

Expected output: `sklearn: 1.3.x, torch: 2.0.x`

---

## Phase 1: Data Collection

### Understanding the Data Collection System

The `RealDataCollector` class captures live system metrics during gaming sessions:

**Collected Metrics**:
- CPU: Usage (%), temperature (°C), frequency (MHz)
- GPU: Usage (%), temperature (°C), memory usage (%), power (W)
- RAM: Usage (%)
- Power: Total system power consumption (W)
- FPS: Frame rate (optional, game-specific)

### Setting Up Data Collection

**1. Start a Collection Session**:

```python
from ml_engine.data_collection.benchmark_collector import RealDataCollector

# Initialize collector
collector = RealDataCollector(
    collection_interval=2.0,  # Collect metrics every 2 seconds
    output_dir="./gaming_data"
)

# Start collecting
session_id = collector.start_session(
    game_name="Counter-Strike 2",
    profile_name="competitive",
    additional_metadata={
        "resolution": "1920x1080",
        "settings": "medium",
        "map": "dust2"
    }
)

print(f"Collection started: {session_id}")
print("Play your game normally. Press Ctrl+C when done.")
```

**2. Play Your Game**:

The collector runs in the background, capturing metrics every 2 seconds. Play normally for at least 10-15 minutes to gather meaningful data.

**3. Stop Collection**:

```python
# When done gaming
summary = collector.stop_session()
print(f"Collected {summary['total_snapshots']} data points")
print(f"Average FPS: {summary['avg_fps']:.1f}")
print(f"Average CPU: {summary['avg_cpu']:.1f}%")
print(f"Average GPU: {summary['avg_gpu']:.1f}%")
```

### Automated Collection Script

Create `collect_gaming_data.py`:

```python
#!/usr/bin/env python3
"""
Automated gaming data collection script
Run this before gaming, press Ctrl+C when done
"""

import sys
import time
import signal
from ml_engine.data_collection.benchmark_collector import RealDataCollector

collector = None

def signal_handler(sig, frame):
    print("\n\nStopping collection...")
    if collector:
        summary = collector.stop_session()
        print(f"\n✅ Collection complete!")
        print(f"   Snapshots: {summary['total_snapshots']}")
        print(f"   Duration: {summary['duration']:.1f}s")
        print(f"   Avg FPS: {summary.get('avg_fps', 'N/A')}")
        print(f"   Data saved to: {summary['output_file']}")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    game_name = input("Game name: ").strip() or "Unknown Game"
    profile_name = input("Profile (competitive/balanced/streaming): ").strip() or "balanced"

    collector = RealDataCollector(collection_interval=2.0)
    session_id = collector.start_session(game_name=game_name, profile_name=profile_name)

    print(f"\n🎮 Collection started for '{game_name}' using '{profile_name}' profile")
    print("📊 Collecting metrics every 2 seconds...")
    print("⏸️  Press Ctrl+C when done gaming\n")

    # Keep collecting until Ctrl+C
    while True:
        time.sleep(1)
```

**Usage**:

```bash
chmod +x collect_gaming_data.py
./collect_gaming_data.py

# During prompt:
Game name: Cyberpunk 2077
Profile (competitive/balanced/streaming): competitive

# Play game, then Ctrl+C when done
```

### Data Collection Best Practices

**1. Collect Diverse Data**:

- Multiple games (FPS, RPG, strategy)
- Different profiles (competitive, balanced, streaming)
- Various graphics settings (low, medium, high, ultra)
- Different workloads (idle, normal gaming, stress testing)

**2. Minimum Collection Requirements**:

- **Profile Classifier**: 50+ sessions per profile (150+ total)
- **Performance Predictor**: 100+ sessions across all configurations
- **Anomaly Detector**: 200+ normal sessions + 20+ anomalous sessions

**3. Data Quality**:

- Collect for at least 10 minutes per session
- Ensure stable gaming conditions (not alt-tabbing frequently)
- Note any anomalies (crashes, thermal throttling, etc.)

### Viewing Collected Data

```python
import pandas as pd

# Load a session
df = pd.read_csv("gaming_data/session_20251119_123456.csv")

# Basic statistics
print(df.describe())

# Plot CPU/GPU usage over time
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.plot(df['timestamp'], df['cpu_usage'], label='CPU')
plt.ylabel('CPU Usage (%)')
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(df['timestamp'], df['gpu_usage'], label='GPU', color='green')
plt.ylabel('GPU Usage (%)')
plt.xlabel('Time (s)')
plt.legend()
plt.tight_layout()
plt.show()
```

---

## Phase 2: Data Preprocessing

### Exporting Training Data

After collecting multiple sessions, export to ML training format:

```python
from ml_engine.data_collection.benchmark_collector import RealDataCollector

collector = RealDataCollector()

# Export all sessions to training format
training_data = collector.export_for_ml_training(
    output_file="training_data.csv",
    min_session_duration=600  # Only include sessions >= 10 minutes
)

print(f"Exported {len(training_data)} samples for training")
```

### Data Preprocessing Script

Create `preprocess_data.py`:

```python
#!/usr/bin/env python3
"""
Preprocess collected gaming data for ML training
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Load data
df = pd.read_csv("training_data.csv")

print(f"Loaded {len(df)} samples")
print(f"Features: {df.columns.tolist()}")

# Remove outliers (IQR method)
def remove_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    return df[(df[column] >= lower) & (df[column] <= upper)]

for col in ['cpu_usage', 'gpu_usage', 'cpu_temp', 'gpu_temp']:
    df = remove_outliers(df, col)

print(f"After outlier removal: {len(df)} samples")

# Feature engineering
df['total_usage'] = df['cpu_usage'] + df['gpu_usage']
df['thermal_load'] = (df['cpu_temp'] + df['gpu_temp']) / 2
df['power_efficiency'] = df['fps'] / (df['power_watts'] + 1)  # +1 to avoid division by zero

# Save preprocessed data
df.to_csv("training_data_preprocessed.csv", index=False)
print(f"Preprocessed data saved: {len(df)} samples, {len(df.columns)} features")
```

**Run preprocessing**:

```bash
python3 preprocess_data.py
```

---

## Phase 3: Model Training

### Training the Profile Classifier

The profile classifier recommends which gaming profile to use based on hardware and usage patterns.

**1. Prepare Training Script** (`train_profile_classifier.py`):

```python
#!/usr/bin/env python3
"""
Train Random Forest profile classifier
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from ml_engine.models.model_trainer import ModelTrainer

# Load preprocessed data
df = pd.read_csv("training_data_preprocessed.csv")

# Features for classification
feature_columns = [
    'cpu_usage', 'cpu_temp', 'cpu_freq',
    'gpu_usage', 'gpu_temp', 'gpu_memory',
    'ram_usage', 'power_watts'
]

X = df[feature_columns]
y = df['profile_name']  # Target: competitive/balanced/streaming

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")
print(f"Profile distribution: {y_train.value_counts().to_dict()}")

# Train model
trainer = ModelTrainer()
trainer.train_profile_classifier(X_train, y_train)

# Evaluate
accuracy = trainer.evaluate_profile_classifier(X_test, y_test)
print(f"\n✅ Model trained successfully!")
print(f"   Accuracy: {accuracy:.2%}")

# Save model
trainer.save_profile_classifier("models/profile_classifier_v1.6.0.pkl")
print(f"   Model saved to: models/profile_classifier_v1.6.0.pkl")
```

**2. Run Training**:

```bash
mkdir -p models
python3 train_profile_classifier.py
```

**Expected Output**:
```
Training samples: 800
Testing samples: 200
Profile distribution: {'competitive': 350, 'balanced': 300, 'streaming': 150}

Training Random Forest classifier...
✅ Model trained successfully!
   Accuracy: 94.50%
   Model saved to: models/profile_classifier_v1.6.0.pkl
```

### Training the Performance Predictor

The performance predictor estimates FPS, power consumption, and temperatures for different configurations.

**1. Create Training Script** (`train_performance_predictor.py`):

```python
#!/usr/bin/env python3
"""
Train Gradient Boosting performance predictor
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from ml_engine.models.model_trainer import ModelTrainer

# Load data
df = pd.read_csv("training_data_preprocessed.csv")

# Features
feature_columns = [
    'cpu_usage', 'cpu_freq', 'gpu_usage',
    'gpu_memory', 'ram_usage'
]

X = df[feature_columns]

# Multi-output targets
y = df[['fps', 'power_watts', 'cpu_temp', 'gpu_temp']]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Training samples: {len(X_train)}")

# Train model
trainer = ModelTrainer()
trainer.train_performance_predictor(X_train, y_train)

# Evaluate
r2_scores = trainer.evaluate_performance_predictor(X_test, y_test)
print(f"\n✅ Performance predictor trained!")
print(f"   R² Scores:")
for metric, score in r2_scores.items():
    print(f"   - {metric}: {score:.3f}")

# Save model
trainer.save_performance_predictor("models/performance_predictor_v1.6.0.pkl")
print(f"\n   Model saved to: models/performance_predictor_v1.6.0.pkl")
```

**2. Run Training**:

```bash
python3 train_performance_predictor.py
```

**Expected Output**:
```
Training samples: 800

Training Gradient Boosting regressor...
✅ Performance predictor trained!
   R² Scores:
   - fps: 0.892
   - power_watts: 0.857
   - cpu_temp: 0.823
   - gpu_temp: 0.845

   Model saved to: models/performance_predictor_v1.6.0.pkl
```

---

## Phase 4: Hyperparameter Optimization

The `ModelOptimizer` class automates hyperparameter tuning using GridSearchCV or RandomizedSearchCV.

### Optimizing Profile Classifier

**1. Create Optimization Script** (`optimize_classifier.py`):

```python
#!/usr/bin/env python3
"""
Hyperparameter optimization for profile classifier
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from ml_engine.evaluation.model_optimizer import ModelOptimizer

# Load data
df = pd.read_csv("training_data_preprocessed.csv")

feature_columns = [
    'cpu_usage', 'cpu_temp', 'cpu_freq',
    'gpu_usage', 'gpu_temp', 'gpu_memory',
    'ram_usage', 'power_watts'
]

X = df[feature_columns]
y = df['profile_name']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Initialize optimizer
optimizer = ModelOptimizer()

print("🔍 Starting hyperparameter optimization...")
print("   Method: Grid Search")
print("   Cross-validation: 5-fold\n")

# Optimize (this may take 10-30 minutes)
results = optimizer.optimize_profile_classifier(
    X_train, y_train,
    method='grid',  # Use 'random' for faster results
    cv_folds=5
)

print(f"\n✅ Optimization complete!")
print(f"\n📊 Best Parameters:")
for param, value in results['best_params'].items():
    print(f"   {param}: {value}")

print(f"\n📈 Best Cross-Validation Score: {results['best_score']:.4f}")

# Train final model with best parameters
from sklearn.ensemble import RandomForestClassifier
best_model = RandomForestClassifier(**results['best_params'], random_state=42)
best_model.fit(X_train, y_train)

# Evaluate on test set
from sklearn.metrics import accuracy_score
test_accuracy = accuracy_score(y_test, best_model.predict(X_test))
print(f"📊 Test Set Accuracy: {test_accuracy:.4f}")

# Save optimized model
import pickle
with open("models/profile_classifier_optimized_v1.6.0.pkl", 'wb') as f:
    pickle.dump(best_model, f)
print(f"\n💾 Optimized model saved!")
```

**2. Run Optimization**:

```bash
python3 optimize_classifier.py
```

**Expected Output** (abbreviated):
```
🔍 Starting hyperparameter optimization...
   Method: Grid Search
   Cross-validation: 5-fold

Fitting 5 folds for each of 144 candidates, totaling 720 fits
[Parallel processing output...]

✅ Optimization complete!

📊 Best Parameters:
   n_estimators: 200
   max_depth: 20
   min_samples_split: 5
   min_samples_leaf: 2
   max_features: sqrt

📈 Best Cross-Validation Score: 0.9523
📊 Test Set Accuracy: 0.9550

💾 Optimized model saved!
```

### Optimizing Performance Predictor

**1. Create Optimization Script** (`optimize_predictor.py`):

```python
#!/usr/bin/env python3
"""
Hyperparameter optimization for performance predictor
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from ml_engine.evaluation.model_optimizer import ModelOptimizer

# Load data
df = pd.read_csv("training_data_preprocessed.csv")

feature_columns = ['cpu_usage', 'cpu_freq', 'gpu_usage', 'gpu_memory', 'ram_usage']
X = df[feature_columns]
y = df[['fps', 'power_watts', 'cpu_temp', 'gpu_temp']]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Initialize optimizer
optimizer = ModelOptimizer()

print("🔍 Optimizing performance predictor...")
print("   Method: Randomized Search (faster)")
print("   Iterations: 50\n")

# Optimize with randomized search (faster than grid)
results = optimizer.optimize_performance_predictor(
    X_train, y_train,
    method='random',
    cv_folds=5,
    n_iter=50
)

print(f"\n✅ Optimization complete!")
print(f"\n📊 Best Parameters:")
for param, value in results['best_params'].items():
    print(f"   {param}: {value}")

print(f"\n📈 Best Cross-Validation R² Score: {results['best_score']:.4f}")

# Save results
import json
with open("optimization_results_predictor.json", 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n💾 Results saved to optimization_results_predictor.json")
```

**2. Run Optimization**:

```bash
python3 optimize_predictor.py
```

---

## Phase 5: Model Evaluation

### Comprehensive Model Evaluation

**1. Create Evaluation Script** (`evaluate_models.py`):

```python
#!/usr/bin/env python3
"""
Comprehensive model evaluation with visualizations
"""

import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from ml_engine.evaluation.model_optimizer import ModelEvaluator

# Load data
df = pd.read_csv("training_data_preprocessed.csv")

# Profile Classifier Evaluation
print("=" * 60)
print("PROFILE CLASSIFIER EVALUATION")
print("=" * 60)

feature_columns = ['cpu_usage', 'cpu_temp', 'cpu_freq', 'gpu_usage',
                   'gpu_temp', 'gpu_memory', 'ram_usage', 'power_watts']
X = df[feature_columns]
y = df['profile_name']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Load trained model
with open("models/profile_classifier_optimized_v1.6.0.pkl", 'rb') as f:
    classifier = pickle.load(f)

# Initialize evaluator
evaluator = ModelEvaluator()

# Generate confusion matrix
evaluator.plot_confusion_matrix(
    classifier, X_test, y_test,
    class_names=['competitive', 'balanced', 'streaming'],
    save_path='evaluation/classifier_confusion_matrix.png'
)
print("✅ Confusion matrix saved: evaluation/classifier_confusion_matrix.png")

# Feature importance
evaluator.plot_feature_importance(
    classifier, feature_columns,
    save_path='evaluation/classifier_feature_importance.png'
)
print("✅ Feature importance saved: evaluation/classifier_feature_importance.png")

# Performance Predictor Evaluation
print("\n" + "=" * 60)
print("PERFORMANCE PREDICTOR EVALUATION")
print("=" * 60)

feature_columns = ['cpu_usage', 'cpu_freq', 'gpu_usage', 'gpu_memory', 'ram_usage']
X = df[feature_columns]
y = df[['fps', 'power_watts', 'cpu_temp', 'gpu_temp']]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Load model
with open("models/performance_predictor_v1.6.0.pkl", 'rb') as f:
    predictor = pickle.load(f)

# Evaluate each output
predictions = predictor.predict(X_test)

for i, metric in enumerate(['fps', 'power_watts', 'cpu_temp', 'gpu_temp']):
    evaluator.plot_prediction_scatter(
        y_test.iloc[:, i], predictions[:, i],
        metric_name=metric,
        save_path=f'evaluation/predictor_{metric}_scatter.png'
    )
    print(f"✅ {metric} scatter plot saved: evaluation/predictor_{metric}_scatter.png")

print("\n" + "=" * 60)
print("EVALUATION COMPLETE")
print("=" * 60)
print("Check the 'evaluation/' directory for all visualizations")
```

**2. Run Evaluation**:

```bash
mkdir -p evaluation
python3 evaluate_models.py
```

### Interpreting Results

**Confusion Matrix**:
- Diagonal values should be high (correct predictions)
- Off-diagonal values should be low (misclassifications)
- Target: >90% accuracy for each class

**Feature Importance**:
- Shows which features most influence predictions
- Use this to identify key system metrics
- Consider removing low-importance features for efficiency

**R² Scores**:
- 1.0 = perfect predictions
- 0.8-0.9 = good model
- 0.6-0.8 = acceptable model
- <0.6 = needs improvement (more data or feature engineering)

---

## Phase 6: Model Deployment

### Integrating Trained Models

**1. Update Model Paths** in `ml_engine/models/profile_optimizer.py`:

```python
class ProfileOptimizer:
    def __init__(self, model_path='models/profile_classifier_optimized_v1.6.0.pkl'):
        self.model_path = model_path
        self.model = self.load_model()
```

**2. Test Integration**:

```python
from ml_engine.models.profile_optimizer import ProfileOptimizer

# Initialize with trained model
optimizer = ProfileOptimizer(model_path='models/profile_classifier_optimized_v1.6.0.pkl')

# Test prediction
hardware_specs = {
    'cpu_cores': 10,
    'cpu_base_freq': 3.6,
    'ram_gb': 64,
    'gpu_model': 'RTX 5080',
    'gpu_vram_gb': 16
}

recommended_profile = optimizer.recommend_profile(hardware_specs)
print(f"Recommended profile: {recommended_profile}")
```

### Production Deployment Checklist

- [ ] Verify model files are in `models/` directory
- [ ] Test model predictions with sample inputs
- [ ] Update bazzite-optimizer.py to use new models
- [ ] Benchmark inference latency (<100ms for real-time use)
- [ ] Document model version in VERSION file
- [ ] Create backup of previous models
- [ ] Test end-to-end with GUI application
- [ ] Monitor prediction accuracy in production

---

## Advanced Topics

### Continuous Learning

Implement a system to continuously improve models with new data:

```python
# collect_and_retrain.py
def continuous_learning_loop():
    while True:
        # Collect new gaming sessions
        new_data = collect_recent_sessions(days=7)

        # Append to training dataset
        append_to_training_data(new_data)

        # Retrain models monthly
        if should_retrain():
            retrain_all_models()
            evaluate_and_deploy()

        time.sleep(86400)  # Check daily
```

### Transfer Learning

Use pre-trained models as starting points:

```python
# Load existing model
base_model = load_model("models/profile_classifier_v1.6.0.pkl")

# Fine-tune on new data (e.g., new game)
fine_tuned_model = fine_tune(base_model, new_game_data, epochs=10)
```

### Ensemble Methods

Combine multiple models for better predictions:

```python
from sklearn.ensemble import VotingClassifier

# Combine multiple classifiers
ensemble = VotingClassifier([
    ('rf', random_forest_model),
    ('gb', gradient_boosting_model),
    ('svm', svm_model)
], voting='soft')

ensemble.fit(X_train, y_train)
```

---

## Troubleshooting

### Common Issues

**Issue: Low Accuracy (<80%)**

Solutions:
- Collect more diverse data (different games, profiles)
- Feature engineering (create new features from existing ones)
- Try different algorithms (XGBoost, LightGBM)
- Check for data quality issues (outliers, missing values)

**Issue: Overfitting (Training accuracy >> Test accuracy)**

Solutions:
- Increase regularization (max_depth, min_samples_split)
- Collect more training data
- Use cross-validation to validate performance
- Apply dropout for deep learning models

**Issue: Training Too Slow**

Solutions:
- Use RandomizedSearchCV instead of GridSearchCV
- Reduce parameter search space
- Use fewer cross-validation folds (3 instead of 5)
- Enable parallel processing (n_jobs=-1)

**Issue: GPU Not Detected for PyTorch**

```bash
# Verify CUDA installation
python3 -c "import torch; print(torch.cuda.is_available())"

# If False, reinstall PyTorch with CUDA support
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## Summary

**Complete ML Training Workflow**:

1. **Collect Data**: Use `RealDataCollector` during gaming sessions (50+ sessions per profile)
2. **Preprocess**: Clean data, remove outliers, engineer features
3. **Train Models**: Profile classifier (Random Forest) + Performance predictor (Gradient Boosting)
4. **Optimize**: Hyperparameter tuning with GridSearchCV/RandomizedSearchCV
5. **Evaluate**: Confusion matrices, feature importance, R² scores
6. **Deploy**: Integrate trained models into bazzite-optimizer.py
7. **Monitor**: Track prediction accuracy in production
8. **Iterate**: Continuously collect new data and retrain

**Expected Results**:

- **Profile Classifier**: 90-95% accuracy
- **Performance Predictor**: R² scores 0.85-0.90 for FPS/power/temps
- **Inference Latency**: <100ms for real-time predictions

---

**Version**: 1.6.0
**Last Updated**: November 19, 2025
**Author**: Bazzite Gaming Optimizer Team

For additional assistance, see the [FAQ](FAQ.md) or open a GitHub issue.
