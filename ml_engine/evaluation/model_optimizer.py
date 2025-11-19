#!/usr/bin/env python3
"""
ML Model Hyperparameter Optimization & Evaluation

Automated hyperparameter tuning and comprehensive model evaluation
for all ML models in the Bazzite Optimizer suite.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime

import numpy as np
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class ModelOptimizer:
    """
    Hyperparameter optimization for ML models

    Features:
    - Grid search for exhaustive parameter tuning
    - Random search for large parameter spaces
    - Cross-validation with stratified splits
    - Automated best parameter selection
    - Performance metrics logging
    """

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path.home() / '.local/share/bazzite-optimizer/ml-optimization'
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.optimization_history = []

    def optimize_profile_classifier(self, X_train, y_train,
                                    method: str = 'grid',
                                    cv_folds: int = 5) -> Dict:
        """
        Optimize RandomForestClassifier for profile recommendation

        Args:
            X_train: Training features
            y_train: Training labels
            method: 'grid' or 'random' search
            cv_folds: Cross-validation folds

        Returns:
            Optimization results with best parameters
        """
        from sklearn.ensemble import RandomForestClassifier

        logger.info("Optimizing Profile Classifier hyperparameters...")

        # Define parameter grid
        param_grid = {
            'n_estimators': [50, 100, 200, 300],
            'max_depth': [10, 20, 30, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2', None],
            'class_weight': ['balanced', 'balanced_subsample', None]
        }

        # Reduce for random search
        if method == 'random':
            param_grid['n_estimators'] = [50, 100, 150, 200, 250, 300]
            param_grid['max_depth'] = [5, 10, 15, 20, 25, 30, None]

        # Initialize base classifier
        base_clf = RandomForestClassifier(random_state=42, n_jobs=-1)

        # Perform search
        if method == 'grid':
            search = GridSearchCV(
                base_clf, param_grid,
                cv=cv_folds,
                scoring='accuracy',
                n_jobs=-1,
                verbose=1
            )
        else:  # random
            search = RandomizedSearchCV(
                base_clf, param_grid,
                n_iter=50,
                cv=cv_folds,
                scoring='accuracy',
                n_jobs=-1,
                verbose=1,
                random_state=42
            )

        # Fit
        search.fit(X_train, y_train)

        # Results
        results = {
            'model_type': 'RandomForestClassifier',
            'optimization_method': method,
            'best_params': search.best_params_,
            'best_score': float(search.best_score_),
            'cv_folds': cv_folds,
            'timestamp': datetime.now().isoformat()
        }

        # Save results
        self._save_optimization_results('profile_classifier', results)

        logger.info(f"Best parameters: {search.best_params_}")
        logger.info(f"Best CV score: {search.best_score_:.4f}")

        return results

    def optimize_performance_regressor(self, X_train, y_train,
                                       target_name: str = 'fps',
                                       method: str = 'grid',
                                       cv_folds: int = 5) -> Dict:
        """
        Optimize GradientBoostingRegressor for performance prediction

        Args:
            X_train: Training features
            y_train: Training target (FPS, power, or temp)
            target_name: Name of target variable
            method: 'grid' or 'random' search
            cv_folds: Cross-validation folds

        Returns:
            Optimization results
        """
        from sklearn.ensemble import GradientBoostingRegressor

        logger.info(f"Optimizing Performance Regressor for {target_name}...")

        # Parameter grid
        param_grid = {
            'n_estimators': [100, 200, 300],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'max_depth': [3, 5, 7, 9],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'subsample': [0.8, 0.9, 1.0],
            'max_features': ['sqrt', 'log2', None]
        }

        # Reduce for random search
        if method == 'random':
            param_grid['learning_rate'] = [0.001, 0.01, 0.05, 0.1, 0.15, 0.2]
            param_grid['max_depth'] = [3, 4, 5, 6, 7, 8, 9, 10]

        # Initialize base regressor
        base_reg = GradientBoostingRegressor(random_state=42)

        # Perform search
        if method == 'grid':
            search = GridSearchCV(
                base_reg, param_grid,
                cv=cv_folds,
                scoring='r2',
                n_jobs=-1,
                verbose=1
            )
        else:  # random
            search = RandomizedSearchCV(
                base_reg, param_grid,
                n_iter=50,
                cv=cv_folds,
                scoring='r2',
                n_jobs=-1,
                verbose=1,
                random_state=42
            )

        # Fit
        search.fit(X_train, y_train)

        # Results
        results = {
            'model_type': 'GradientBoostingRegressor',
            'target': target_name,
            'optimization_method': method,
            'best_params': search.best_params_,
            'best_score': float(search.best_score_),
            'cv_folds': cv_folds,
            'timestamp': datetime.now().isoformat()
        }

        # Save results
        self._save_optimization_results(f'performance_regressor_{target_name}', results)

        logger.info(f"Best parameters: {search.best_params_}")
        logger.info(f"Best R² score: {search.best_score_:.4f}")

        return results

    def _save_optimization_results(self, model_name: str, results: Dict):
        """Save optimization results to file"""
        output_file = self.output_dir / f"{model_name}_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        self.optimization_history.append(results)

        logger.info(f"Saved optimization results to {output_file}")


class ModelEvaluator:
    """
    Comprehensive model evaluation and reporting

    Features:
    - Classification metrics (accuracy, precision, recall, F1)
    - Regression metrics (MSE, MAE, R²)
    - Cross-validation scores
    - Confusion matrices
    - Feature importance analysis
    - Performance visualization
    """

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path.home() / '.local/share/bazzite-optimizer/ml-evaluation'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def evaluate_classifier(self, model, X_test, y_test,
                           class_names: List[str],
                           model_name: str = "classifier") -> Dict:
        """
        Comprehensive classifier evaluation

        Args:
            model: Trained classifier
            X_test: Test features
            y_test: Test labels
            class_names: List of class names
            model_name: Model identifier

        Returns:
            Evaluation metrics
        """
        logger.info(f"Evaluating {model_name}...")

        # Predictions
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test) if hasattr(model, 'predict_proba') else None

        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, target_names=class_names, output_dict=True)
        conf_matrix = confusion_matrix(y_test, y_pred)

        results = {
            'model_name': model_name,
            'accuracy': float(accuracy),
            'classification_report': report,
            'confusion_matrix': conf_matrix.tolist(),
            'class_names': class_names,
            'timestamp': datetime.now().isoformat()
        }

        # Print summary
        print(f"\n{'='*60}")
        print(f"{model_name} Evaluation")
        print(f"{'='*60}")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"\nPer-Class Metrics:")
        for class_name in class_names:
            metrics = report[class_name]
            print(f"  {class_name}:")
            print(f"    Precision: {metrics['precision']:.4f}")
            print(f"    Recall: {metrics['recall']:.4f}")
            print(f"    F1-Score: {metrics['f1-score']:.4f}")

        # Plot confusion matrix
        self._plot_confusion_matrix(conf_matrix, class_names, model_name)

        # Save results
        output_file = self.output_dir / f"{model_name}_evaluation.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        return results

    def evaluate_regressor(self, model, X_test, y_test,
                          target_name: str = "target",
                          model_name: str = "regressor") -> Dict:
        """
        Comprehensive regressor evaluation

        Args:
            model: Trained regressor
            X_test: Test features
            y_test: Test target
            target_name: Name of target variable
            model_name: Model identifier

        Returns:
            Evaluation metrics
        """
        logger.info(f"Evaluating {model_name} for {target_name}...")

        # Predictions
        y_pred = model.predict(X_test)

        # Metrics
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        # Mean Absolute Percentage Error
        mape = np.mean(np.abs((y_test - y_pred) / (y_test + 1e-8))) * 100

        results = {
            'model_name': model_name,
            'target': target_name,
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'r2': float(r2),
            'mape': float(mape),
            'timestamp': datetime.now().isoformat()
        }

        # Print summary
        print(f"\n{'='*60}")
        print(f"{model_name} Evaluation - {target_name}")
        print(f"{'='*60}")
        print(f"R² Score: {r2:.4f}")
        print(f"RMSE: {rmse:.2f}")
        print(f"MAE: {mae:.2f}")
        print(f"MAPE: {mape:.2f}%")

        # Plot predictions vs actual
        self._plot_predictions(y_test, y_pred, target_name, model_name)

        # Save results
        output_file = self.output_dir / f"{model_name}_{target_name}_evaluation.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        return results

    def analyze_feature_importance(self, model, feature_names: List[str],
                                   model_name: str = "model",
                                   top_n: int = 15) -> Dict:
        """
        Analyze and visualize feature importance

        Args:
            model: Trained model with feature_importances_
            feature_names: List of feature names
            model_name: Model identifier
            top_n: Number of top features to display

        Returns:
            Feature importance dict
        """
        if not hasattr(model, 'feature_importances_'):
            logger.warning(f"{model_name} does not have feature_importances_ attribute")
            return {}

        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]

        # Create importance dict
        importance_dict = {
            feature_names[i]: float(importances[i])
            for i in indices[:top_n]
        }

        # Print top features
        print(f"\n{'='*60}")
        print(f"{model_name} - Top {top_n} Features")
        print(f"{'='*60}")
        for i, idx in enumerate(indices[:top_n], 1):
            print(f"{i:2d}. {feature_names[idx]:30s}: {importances[idx]:.4f}")

        # Plot feature importances
        self._plot_feature_importance(importances, feature_names, model_name, top_n)

        # Save
        output_file = self.output_dir / f"{model_name}_feature_importance.json"
        with open(output_file, 'w') as f:
            json.dump(importance_dict, f, indent=2)

        return importance_dict

    def _plot_confusion_matrix(self, conf_matrix, class_names, model_name):
        """Plot confusion matrix"""
        plt.figure(figsize=(10, 8))
        plt.imshow(conf_matrix, interpolation='nearest', cmap=plt.cm.Blues)
        plt.title(f'{model_name} - Confusion Matrix')
        plt.colorbar()

        tick_marks = np.arange(len(class_names))
        plt.xticks(tick_marks, class_names, rotation=45)
        plt.yticks(tick_marks, class_names)

        # Add text annotations
        thresh = conf_matrix.max() / 2
        for i, j in np.ndindex(conf_matrix.shape):
            plt.text(j, i, format(conf_matrix[i, j], 'd'),
                    ha="center", va="center",
                    color="white" if conf_matrix[i, j] > thresh else "black")

        plt.ylabel('True label')
        plt.xlabel('Predicted label')
        plt.tight_layout()

        output_file = self.output_dir / f"{model_name}_confusion_matrix.png"
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"Saved confusion matrix to {output_file}")

    def _plot_predictions(self, y_true, y_pred, target_name, model_name):
        """Plot predictions vs actual values"""
        plt.figure(figsize=(10, 6))

        plt.scatter(y_true, y_pred, alpha=0.5)
        plt.plot([y_true.min(), y_true.max()],
                [y_true.min(), y_true.max()],
                'r--', lw=2, label='Perfect prediction')

        plt.xlabel(f'Actual {target_name}')
        plt.ylabel(f'Predicted {target_name}')
        plt.title(f'{model_name} - Predictions vs Actual')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        output_file = self.output_dir / f"{model_name}_{target_name}_predictions.png"
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"Saved predictions plot to {output_file}")

    def _plot_feature_importance(self, importances, feature_names, model_name, top_n):
        """Plot feature importance"""
        indices = np.argsort(importances)[::-1][:top_n]

        plt.figure(figsize=(12, 8))
        plt.title(f'{model_name} - Top {top_n} Feature Importances')
        plt.bar(range(top_n), importances[indices])
        plt.xticks(range(top_n), [feature_names[i] for i in indices], rotation=45, ha='right')
        plt.ylabel('Importance')
        plt.tight_layout()

        output_file = self.output_dir / f"{model_name}_feature_importance.png"
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"Saved feature importance plot to {output_file}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("ML Model Optimizer & Evaluator")
    print("Run this module through ModelTrainer for actual optimization")
