#!/usr/bin/env python3
"""
Integration Tests for ML Pipeline
Tests end-to-end data collection → training → prediction workflow
"""

import unittest
import tempfile
import os
import time
import pandas as pd
import numpy as np
from pathlib import Path

# Import components
from ml_engine.data_collection.benchmark_collector import RealDataCollector, SystemSnapshot
from ml_engine.evaluation.model_optimizer import ModelOptimizer, ModelEvaluator
from ml_engine.models.model_trainer import ModelTrainer


class TestMLPipelineIntegration(unittest.TestCase):
    """Test complete ML pipeline from data collection to prediction"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_data_file = os.path.join(cls.temp_dir, "test_data.csv")

    def setUp(self):
        """Set up before each test"""
        self.collector = RealDataCollector(
            collection_interval=0.1,  # Fast collection for tests
            output_dir=self.temp_dir
        )

    def test_01_data_collection_workflow(self):
        """Test complete data collection workflow"""
        print("\n🧪 Testing data collection workflow...")

        # Start session
        session_id = self.collector.start_session(
            game_name="Test Game",
            profile_name="balanced"
        )
        self.assertIsNotNone(session_id)

        # Simulate gaming for 1 second (10 snapshots at 0.1s interval)
        time.sleep(1.0)

        # Stop session
        summary = self.collector.stop_session()

        # Verify summary
        self.assertIn('total_snapshots', summary)
        self.assertGreater(summary['total_snapshots'], 5)  # At least 5 snapshots
        self.assertIn('output_file', summary)
        self.assertTrue(os.path.exists(summary['output_file']))

        # Verify CSV structure
        df = pd.read_csv(summary['output_file'])
        expected_columns = ['timestamp', 'cpu_usage', 'gpu_usage', 'ram_usage']
        for col in expected_columns:
            self.assertIn(col, df.columns)

        print(f"✅ Collected {len(df)} data points successfully")

    def test_02_data_export_for_training(self):
        """Test exporting collected data for ML training"""
        print("\n🧪 Testing ML data export...")

        # Create multiple test sessions
        for profile in ['competitive', 'balanced', 'streaming']:
            session_id = self.collector.start_session(
                game_name=f"Test Game - {profile}",
                profile_name=profile
            )
            time.sleep(0.5)
            self.collector.stop_session()

        # Export for ML training
        training_data = self.collector.export_for_ml_training(
            output_file=self.test_data_file,
            min_session_duration=0  # Include all sessions for tests
        )

        self.assertIsNotNone(training_data)
        self.assertGreater(len(training_data), 0)

        # Verify training data structure
        df = pd.read_csv(self.test_data_file)
        self.assertIn('profile_name', df.columns)
        self.assertIn('game_name', df.columns)

        # Verify all profiles present
        profiles = df['profile_name'].unique()
        self.assertIn('competitive', profiles)
        self.assertIn('balanced', profiles)
        self.assertIn('streaming', profiles)

        print(f"✅ Exported {len(df)} training samples with {len(profiles)} profiles")

    def test_03_model_training_workflow(self):
        """Test complete model training workflow"""
        print("\n🧪 Testing model training workflow...")

        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 300

        # Create synthetic dataset with clear patterns
        data = []
        for profile in ['competitive', 'balanced', 'streaming']:
            for _ in range(n_samples // 3):
                if profile == 'competitive':
                    sample = {
                        'cpu_usage': np.random.uniform(80, 100),
                        'gpu_usage': np.random.uniform(90, 100),
                        'ram_usage': np.random.uniform(60, 80),
                        'cpu_temp': np.random.uniform(70, 85),
                        'gpu_temp': np.random.uniform(75, 90),
                        'power_watts': np.random.uniform(300, 400),
                        'fps': np.random.uniform(200, 300),
                        'profile_name': profile
                    }
                elif profile == 'balanced':
                    sample = {
                        'cpu_usage': np.random.uniform(50, 70),
                        'gpu_usage': np.random.uniform(60, 80),
                        'ram_usage': np.random.uniform(40, 60),
                        'cpu_temp': np.random.uniform(55, 70),
                        'gpu_temp': np.random.uniform(60, 75),
                        'power_watts': np.random.uniform(200, 300),
                        'fps': np.random.uniform(100, 150),
                        'profile_name': profile
                    }
                else:  # streaming
                    sample = {
                        'cpu_usage': np.random.uniform(60, 80),
                        'gpu_usage': np.random.uniform(50, 70),
                        'ram_usage': np.random.uniform(50, 70),
                        'cpu_temp': np.random.uniform(50, 65),
                        'gpu_temp': np.random.uniform(55, 70),
                        'power_watts': np.random.uniform(250, 350),
                        'fps': np.random.uniform(60, 120),
                        'profile_name': profile
                    }
                data.append(sample)

        df = pd.DataFrame(data)

        # Split features and target
        feature_columns = ['cpu_usage', 'gpu_usage', 'ram_usage', 'cpu_temp', 'gpu_temp', 'power_watts']
        X = df[feature_columns]
        y = df['profile_name']

        # Train model
        trainer = ModelTrainer()
        trainer.train_profile_classifier(X, y)

        # Verify model is trained
        self.assertIsNotNone(trainer.profile_classifier)

        # Test prediction
        test_sample = [[95, 98, 70, 80, 85, 350]]  # Should predict 'competitive'
        prediction = trainer.profile_classifier.predict(test_sample)
        self.assertEqual(prediction[0], 'competitive')

        print(f"✅ Model trained and prediction verified: {prediction[0]}")

    def test_04_hyperparameter_optimization(self):
        """Test hyperparameter optimization workflow"""
        print("\n🧪 Testing hyperparameter optimization...")

        # Generate small synthetic dataset
        np.random.seed(42)
        n_samples = 100

        data = []
        for profile in ['competitive', 'balanced']:
            for _ in range(n_samples // 2):
                if profile == 'competitive':
                    sample = {
                        'cpu_usage': np.random.uniform(80, 100),
                        'gpu_usage': np.random.uniform(90, 100),
                        'profile_name': profile
                    }
                else:
                    sample = {
                        'cpu_usage': np.random.uniform(40, 60),
                        'gpu_usage': np.random.uniform(50, 70),
                        'profile_name': profile
                    }
                data.append(sample)

        df = pd.DataFrame(data)
        X = df[['cpu_usage', 'gpu_usage']]
        y = df['profile_name']

        # Run optimization (limited grid for speed)
        optimizer = ModelOptimizer()

        # Test with randomized search (faster)
        results = optimizer.optimize_profile_classifier(
            X, y,
            method='random',
            cv_folds=2,  # Reduced for speed
            n_iter=5  # Limited iterations for tests
        )

        # Verify results structure
        self.assertIn('best_params', results)
        self.assertIn('best_score', results)
        self.assertIn('cv_results', results)

        # Verify best score is reasonable
        self.assertGreater(results['best_score'], 0.5)  # At least 50% accuracy

        print(f"✅ Optimization complete - Best score: {results['best_score']:.3f}")

    def test_05_model_evaluation_workflow(self):
        """Test model evaluation workflow"""
        print("\n🧪 Testing model evaluation workflow...")

        # Generate synthetic test data
        np.random.seed(42)
        n_samples = 150

        data = []
        for profile in ['competitive', 'balanced', 'streaming']:
            for _ in range(n_samples // 3):
                base_cpu = {'competitive': 90, 'balanced': 60, 'streaming': 70}[profile]
                base_gpu = {'competitive': 95, 'balanced': 70, 'streaming': 60}[profile]

                sample = {
                    'cpu_usage': base_cpu + np.random.uniform(-10, 10),
                    'gpu_usage': base_gpu + np.random.uniform(-10, 10),
                    'profile_name': profile
                }
                data.append(sample)

        df = pd.DataFrame(data)
        X = df[['cpu_usage', 'gpu_usage']]
        y = df['profile_name']

        # Train a simple model
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_train, y_train)

        # Evaluate
        evaluator = ModelEvaluator()

        # Test confusion matrix (save to temp file)
        cm_path = os.path.join(self.temp_dir, 'test_cm.png')
        evaluator.plot_confusion_matrix(
            model, X_test, y_test,
            class_names=['competitive', 'balanced', 'streaming'],
            save_path=cm_path
        )
        self.assertTrue(os.path.exists(cm_path))

        # Test feature importance
        fi_path = os.path.join(self.temp_dir, 'test_fi.png')
        evaluator.plot_feature_importance(
            model, ['cpu_usage', 'gpu_usage'],
            save_path=fi_path
        )
        self.assertTrue(os.path.exists(fi_path))

        print("✅ Model evaluation visualizations generated successfully")

    def test_06_end_to_end_pipeline(self):
        """Test complete end-to-end ML pipeline"""
        print("\n🧪 Testing end-to-end ML pipeline...")

        # Step 1: Data Collection
        print("   Step 1: Collecting data...")
        for i in range(3):
            profile = ['competitive', 'balanced', 'streaming'][i % 3]
            self.collector.start_session(
                game_name=f"E2E Test Game {i}",
                profile_name=profile
            )
            time.sleep(0.3)
            self.collector.stop_session()

        # Step 2: Export Training Data
        print("   Step 2: Exporting training data...")
        e2e_data_file = os.path.join(self.temp_dir, "e2e_training_data.csv")
        self.collector.export_for_ml_training(
            output_file=e2e_data_file,
            min_session_duration=0
        )
        self.assertTrue(os.path.exists(e2e_data_file))

        # Step 3: Load and Preprocess
        print("   Step 3: Loading and preprocessing...")
        df = pd.read_csv(e2e_data_file)
        self.assertGreater(len(df), 0)

        # Step 4: Train Model (if enough data)
        if len(df) >= 10:
            print("   Step 4: Training model...")
            feature_columns = ['cpu_usage', 'gpu_usage', 'ram_usage']
            X = df[feature_columns]
            y = df['profile_name']

            trainer = ModelTrainer()
            trainer.train_profile_classifier(X, y)

            # Step 5: Test Prediction
            print("   Step 5: Testing prediction...")
            test_sample = df[feature_columns].iloc[0:1]
            prediction = trainer.profile_classifier.predict(test_sample)
            self.assertIsNotNone(prediction)

            print(f"✅ End-to-end pipeline complete - Prediction: {prediction[0]}")
        else:
            print("   ⚠️  Insufficient data for training, skipping steps 4-5")
            print("   ✅ Data collection and export pipeline verified")

    @classmethod
    def tearDownClass(cls):
        """Clean up test files"""
        import shutil
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)
        print(f"\n🧹 Cleaned up test directory: {cls.temp_dir}")


if __name__ == '__main__':
    print("="* 70)
    print("INTEGRATION TESTS: ML Pipeline")
    print("="* 70)
    print("Testing: Data Collection → Training → Optimization → Evaluation")
    print("="* 70)

    # Run tests with verbose output
    unittest.main(verbosity=2)
