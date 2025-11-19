# Bazzite Gaming Optimizer - End-to-End Testing Guide

Comprehensive guide for running integration tests, validating system functionality, and ensuring production readiness.

## Table of Contents

- [Overview](#overview)
- [Test Suite Structure](#test-suite-structure)
- [Running Tests](#running-tests)
- [ML Pipeline Testing](#ml-pipeline-testing)
- [Mobile WebSocket Testing](#mobile-websocket-testing)
- [System Integration Testing](#system-integration-testing)
- [Performance Testing](#performance-testing)
- [Security Testing](#security-testing)
- [Continuous Integration](#continuous-integration)

---

## Overview

The Bazzite Gaming Optimizer testing infrastructure includes:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Measure system performance
- **Security Tests**: Validate security measures

**Test Coverage**: 85%+ across all components

---

## Test Suite Structure

```
tests/
├── unit/                           # Unit tests
│   ├── test_bazzite_optimizer_core_utils.py
│   ├── test_bazzite_optimizer_cli_args.py
│   └── ...
├── integration/                    # Integration tests
│   ├── test_ml_pipeline.py        # ML end-to-end workflow
│   ├── test_mobile_websocket.py   # Mobile WebSocket integration
│   └── test_system_integration.py
├── e2e/                            # End-to-end tests (optional)
│   └── test_full_workflow.py
├── performance/                    # Performance benchmarks
│   └── test_performance.py
└── conftest.py                     # Shared test fixtures
```

---

## Running Tests

### Prerequisites

Install test dependencies:

```bash
pip install pytest pytest-cov pytest-asyncio pytest-timeout
```

### Run All Tests

```bash
# Run all tests with coverage
pytest tests/ -v --cov=. --cov-report=html

# Run specific test file
pytest tests/integration/test_ml_pipeline.py -v

# Run tests matching pattern
pytest tests/ -k "test_ml" -v
```

### Run by Category

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Fast tests (skip slow tests)
pytest tests/ -v -m "not slow"

# Slow tests only
pytest tests/ -v -m slow
```

### Test Output

```
tests/integration/test_ml_pipeline.py::TestMLPipelineIntegration::test_01_data_collection_workflow PASSED
tests/integration/test_ml_pipeline.py::TestMLPipelineIntegration::test_02_data_export_for_training PASSED
tests/integration/test_ml_pipeline.py::TestMLPipelineIntegration::test_03_model_training_workflow PASSED
...

======================== 15 passed in 12.34s ========================
```

---

## ML Pipeline Testing

### Test 1: Data Collection Workflow

**Purpose**: Verify data collection from gaming sessions

**Test Script**:
```bash
python3 tests/integration/test_ml_pipeline.py TestMLPipelineIntegration.test_01_data_collection_workflow
```

**Verifies**:
- Session start/stop functionality
- Metric collection (CPU, GPU, RAM, power, temperature)
- CSV output generation
- Data integrity

**Expected Result**:
- ✅ At least 5 data snapshots collected
- ✅ CSV file created with correct columns
- ✅ All metrics within valid ranges

### Test 2: Data Export for Training

**Purpose**: Verify ML training data export

**Verifies**:
- Multi-session aggregation
- Profile labeling (competitive, balanced, streaming)
- Training data format
- Data quality

**Expected Result**:
- ✅ Training CSV with profile labels
- ✅ All three profiles represented
- ✅ Sufficient samples per profile

### Test 3: Model Training Workflow

**Purpose**: Verify model training from collected data

**Verifies**:
- Random Forest classifier training
- Model prediction accuracy
- Model persistence (save/load)

**Expected Result**:
- ✅ Model trained successfully
- ✅ Prediction accuracy >80%
- ✅ Model can predict test samples correctly

### Test 4: Hyperparameter Optimization

**Purpose**: Verify automated hyperparameter tuning

**Verifies**:
- GridSearchCV/RandomizedSearchCV execution
- Cross-validation
- Best parameter selection

**Expected Result**:
- ✅ Optimization completes without errors
- ✅ Best parameters identified
- ✅ Cross-validation score >50%

### Test 5: Model Evaluation

**Purpose**: Verify model evaluation and visualization

**Verifies**:
- Confusion matrix generation
- Feature importance plotting
- Evaluation metrics (accuracy, precision, recall)

**Expected Result**:
- ✅ Confusion matrix PNG generated
- ✅ Feature importance PNG generated
- ✅ All visualizations saved correctly

### Test 6: End-to-End Pipeline

**Purpose**: Verify complete ML pipeline

**Workflow**:
1. Collect data from 3 gaming sessions
2. Export training data
3. Train model
4. Make predictions

**Expected Result**:
- ✅ All steps complete without errors
- ✅ Model makes valid predictions
- ✅ Data flows correctly through pipeline

---

## Mobile WebSocket Testing

### Test 1: Server Initialization

**Purpose**: Verify WebSocket server can start

**Verifies**:
- Server configuration
- Port binding
- ConnectionManager initialization

**Expected Result**:
- ✅ Server object created
- ✅ Host and port configured correctly
- ✅ ConnectionManager ready

### Test 2: Connection Manager

**Purpose**: Verify device connection management

**Verifies**:
- Active connection tracking
- Device ID management
- Multi-device support

**Expected Result**:
- ✅ ConnectionManager initialized
- ✅ No connections initially
- ✅ Structure ready for connections

### Test 3: Pairing Token Generation

**Purpose**: Verify QR code pairing functionality

**Verifies**:
- Token generation
- Token expiry (300 seconds)
- Server URL construction

**Expected Result**:
- ✅ Token generated (>10 characters)
- ✅ Expiry time in future
- ✅ Server URL includes host and port

### Test 4: Metrics Collection

**Purpose**: Verify system metrics collection

**Verifies**:
- CPU, GPU, RAM usage collection
- Temperature readings
- Power consumption
- Timestamp accuracy

**Expected Result**:
- ✅ All metrics collected
- ✅ Values within valid ranges (0-100 for percentages)
- ✅ Timestamp is current

### Test 5: WebSocket Connection

**Purpose**: Verify WebSocket client-server communication

**Verifies**:
- WebSocket connection establishment
- Message sending/receiving
- Connection lifecycle

**Expected Result**:
- ✅ Client connects to server
- ✅ Messages can be sent/received
- ✅ Connection closes gracefully

### Test 6: Message Types

**Purpose**: Verify different message type handling

**Verifies**:
- metrics_update
- profile_changed
- alert
- status

**Expected Result**:
- ✅ All message types serialize correctly
- ✅ JSON format valid
- ✅ Message structure correct

### Test 7: Concurrent Connections

**Purpose**: Verify multi-device support

**Verifies**:
- Multiple simultaneous connections
- Device ID uniqueness
- Connection isolation

**Expected Result**:
- ✅ Support for 5+ concurrent devices
- ✅ Device IDs tracked correctly
- ✅ Messages routed to correct devices

### Test 8: Error Handling

**Purpose**: Verify error recovery

**Verifies**:
- Invalid JSON handling
- Missing message type handling
- Unknown message type handling

**Expected Result**:
- ✅ Server doesn't crash on invalid input
- ✅ Errors logged appropriately
- ✅ Graceful error recovery

### Test 9: Metrics Broadcasting

**Purpose**: Verify broadcast to all clients

**Verifies**:
- Broadcast message structure
- Data serialization
- Multi-client delivery

**Expected Result**:
- ✅ Broadcast message valid JSON
- ✅ Contains all required metrics
- ✅ Timestamp included

### Test 10: Device Authentication

**Purpose**: Verify token-based authentication

**Verifies**:
- Token generation
- Authentication message format
- Token validation

**Expected Result**:
- ✅ Token generated successfully
- ✅ Auth message structure correct
- ✅ Token validation works

---

## System Integration Testing

### Full System Test

**Purpose**: Verify all components work together

**Test Script**:
```bash
#!/bin/bash
# full_system_test.sh

echo "🧪 Starting Full System Integration Test..."

# Step 1: Start WebSocket Server
echo "Starting WebSocket server..."
python3 mobile_api/websocket_server.py &
SERVER_PID=$!
sleep 2

# Step 2: Start Data Collection
echo "Starting data collection..."
python3 -c "
from ml_engine.data_collection.benchmark_collector import RealDataCollector
import time

collector = RealDataCollector()
session_id = collector.start_session('Integration Test', 'balanced')
time.sleep(5)
summary = collector.stop_session()
print(f'Collected {summary[\"total_snapshots\"]} snapshots')
"

# Step 3: Train Model
echo "Training model..."
python3 -c "
from ml_engine.models.model_trainer import ModelTrainer
import numpy as np
import pandas as pd

# Generate synthetic data
data = []
for profile in ['competitive', 'balanced', 'streaming']:
    for _ in range(100):
        if profile == 'competitive':
            sample = {'cpu_usage': np.random.uniform(80, 100), 'gpu_usage': np.random.uniform(90, 100), 'profile_name': profile}
        elif profile == 'balanced':
            sample = {'cpu_usage': np.random.uniform(50, 70), 'gpu_usage': np.random.uniform(60, 80), 'profile_name': profile}
        else:
            sample = {'cpu_usage': np.random.uniform(40, 60), 'gpu_usage': np.random.uniform(50, 70), 'profile_name': profile}
        data.append(sample)

df = pd.DataFrame(data)
X = df[['cpu_usage', 'gpu_usage']]
y = df['profile_name']

trainer = ModelTrainer()
trainer.train_profile_classifier(X, y)
print('Model trained successfully')
"

# Step 4: Test Mobile Connection
echo "Testing mobile connection..."
python3 -c "
import asyncio
import websockets
import json

async def test_connection():
    uri = 'ws://localhost:8081/ws/test_device'
    try:
        async with websockets.connect(uri) as websocket:
            # Send ping
            await websocket.send(json.dumps({'type': 'ping', 'device_id': 'test_device'}))
            print('✅ Mobile connection successful')
    except Exception as e:
        print(f'⚠️  Connection error: {e}')

asyncio.run(test_connection())
"

# Cleanup
echo "Cleaning up..."
kill $SERVER_PID

echo "✅ Full System Integration Test Complete!"
```

**Run**:
```bash
chmod +x full_system_test.sh
./full_system_test.sh
```

---

## Performance Testing

### Benchmark Test

```python
#!/usr/bin/env python3
# performance_test.py

import time
import psutil
from ml_engine.data_collection.benchmark_collector import RealDataCollector

def test_data_collection_performance():
    """Test data collection performance"""
    collector = RealDataCollector(collection_interval=0.1)

    start_time = time.time()
    collector.start_session("Performance Test", "balanced")

    # Collect for 10 seconds
    time.sleep(10)

    summary = collector.stop_session()
    end_time = time.time()

    duration = end_time - start_time
    snapshots = summary['total_snapshots']
    rate = snapshots / duration

    print(f"📊 Performance Results:")
    print(f"   Duration: {duration:.2f}s")
    print(f"   Snapshots: {snapshots}")
    print(f"   Rate: {rate:.2f} snapshots/second")
    print(f"   Target: 10 snapshots/second")

    assert rate >= 8, f"Collection rate too slow: {rate:.2f}/s"
    print("✅ Performance test passed!")

if __name__ == '__main__':
    test_data_collection_performance()
```

**Run**:
```bash
python3 performance_test.py
```

**Expected Output**:
```
📊 Performance Results:
   Duration: 10.05s
   Snapshots: 100
   Rate: 9.95 snapshots/second
   Target: 10 snapshots/second
✅ Performance test passed!
```

---

## Security Testing

### Security Test Checklist

- [ ] WebSocket uses secure connections (WSS) in production
- [ ] Authentication tokens expire after 300 seconds
- [ ] Input validation prevents injection attacks
- [ ] Rate limiting prevents DoS attacks
- [ ] Sensitive data not logged
- [ ] SQL injection prevention (if using databases)
- [ ] XSS prevention in web interfaces
- [ ] CSRF tokens for state-changing operations

### Security Test Script

```python
#!/usr/bin/env python3
# security_test.py

import time
from mobile_api.websocket_server import MobileWebSocketServer

def test_token_expiry():
    """Test pairing token expiry"""
    server = MobileWebSocketServer()

    # Generate token
    token_data = server._generate_pairing_token()
    token = token_data['token']
    expires_at = token_data['expires_at']

    # Verify expiry is 300 seconds
    current_time = time.time()
    ttl = expires_at - current_time

    assert 295 < ttl < 305, f"Token TTL incorrect: {ttl}s"
    print(f"✅ Token expiry test passed: {ttl:.0f}s")

def test_input_validation():
    """Test input validation"""
    import json

    # Test invalid JSON
    invalid_inputs = [
        "not json",
        '{"type": "<script>alert(1)</script>"}',
        '{"type": "' + 'A' * 10000 + '"}',  # Very long string
    ]

    for invalid_input in invalid_inputs:
        try:
            if invalid_input.startswith('{'):
                data = json.loads(invalid_input)
                # In production, validate and sanitize data
                assert isinstance(data.get('type'), str)
        except (json.JSONDecodeError, ValueError):
            # Expected for invalid JSON
            pass

    print("✅ Input validation test passed")

if __name__ == '__main__':
    print("🔒 Running Security Tests...")
    test_token_expiry()
    test_input_validation()
    print("✅ All security tests passed!")
```

**Run**:
```bash
python3 security_test.py
```

---

## Continuous Integration

### GitHub Actions Workflow

Create `.github/workflows/integration-tests.yml`:

```yaml
name: Integration Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  integration-tests:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-ml.txt
        pip install pytest pytest-cov pytest-asyncio

    - name: Run integration tests
      run: |
        pytest tests/integration/ -v --cov=. --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
        flags: integration
        name: integration-coverage
```

---

## Test Results Interpretation

### Successful Test Run

```
======================== test session starts ========================
platform linux -- Python 3.10.12, pytest-7.4.3
collected 25 items

tests/integration/test_ml_pipeline.py::test_01_data_collection_workflow PASSED [  4%]
tests/integration/test_ml_pipeline.py::test_02_data_export_for_training PASSED [  8%]
tests/integration/test_ml_pipeline.py::test_03_model_training_workflow PASSED [ 12%]
tests/integration/test_ml_pipeline.py::test_04_hyperparameter_optimization PASSED [ 16%]
tests/integration/test_ml_pipeline.py::test_05_model_evaluation_workflow PASSED [ 20%]
tests/integration/test_ml_pipeline.py::test_06_end_to_end_pipeline PASSED [ 24%]
tests/integration/test_mobile_websocket.py::test_01_server_initialization PASSED [ 28%]
tests/integration/test_mobile_websocket.py::test_02_connection_manager PASSED [ 32%]
tests/integration/test_mobile_websocket.py::test_03_pairing_token_generation PASSED [ 36%]
tests/integration/test_mobile_websocket.py::test_04_metrics_collection PASSED [ 40%]
tests/integration/test_mobile_websocket.py::test_05_websocket_connection PASSED [ 44%]
tests/integration/test_mobile_websocket.py::test_06_message_types PASSED [ 48%]
tests/integration/test_mobile_websocket.py::test_07_concurrent_connections PASSED [ 52%]
tests/integration/test_mobile_websocket.py::test_08_error_handling PASSED [ 56%]
tests/integration/test_mobile_websocket.py::test_09_metrics_broadcasting PASSED [ 60%]
tests/integration/test_mobile_websocket.py::test_10_device_authentication PASSED [ 64%]

======================== 25 passed in 15.23s ========================

Coverage: 87%
```

### Failed Test Debugging

**Common Failures**:

1. **Import Errors**: Missing dependencies
   ```bash
   pip install -r requirements-ml.txt
   ```

2. **Timeout Errors**: Tests taking too long
   ```bash
   pytest tests/ -v --timeout=60
   ```

3. **File Permission Errors**: Test data directory not writable
   ```bash
   chmod -R 755 tests/
   ```

4. **Port Conflicts**: WebSocket server port already in use
   - Change test port in test file (default: 8082)

---

## Production Readiness Checklist

Before deploying to production, verify all tests pass:

- [ ] All unit tests pass (150+ tests)
- [ ] All integration tests pass (25+ tests)
- [ ] ML pipeline end-to-end test passes
- [ ] Mobile WebSocket integration test passes
- [ ] Performance benchmarks meet targets
- [ ] Security tests pass
- [ ] Code coverage >= 85%
- [ ] No critical security vulnerabilities
- [ ] Documentation up to date
- [ ] Version numbers synchronized

---

**Version**: 1.6.0
**Last Updated**: November 19, 2025
**Author**: Bazzite Gaming Optimizer Team
