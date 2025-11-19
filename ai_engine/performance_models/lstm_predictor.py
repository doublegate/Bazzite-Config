"""
LSTM-based Performance Prediction

Uses LSTM neural networks with attention mechanism for time-series
performance prediction based on historical gaming sessions.
"""

import logging
import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# PyTorch imports with fallback
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import Dataset, DataLoader
    import torch.optim as optim
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    logger.warning("PyTorch not available. Install with: pip install torch")


@dataclass
class PerformanceSequence:
    """Time-series performance data"""
    timestamps: List[float]
    fps_values: List[float]
    cpu_usage: List[float]
    gpu_usage: List[float]
    power_watts: List[float]
    gpu_temp: Optional[List[float]] = None


class AttentionLayer(nn.Module):
    """
    Attention mechanism for LSTM

    Learns to focus on important time steps in the sequence
    """

    def __init__(self, hidden_size: int):
        super(AttentionLayer, self).__init__()
        self.attention_weights = nn.Linear(hidden_size, 1)

    def forward(self, lstm_outputs):
        # lstm_outputs shape: (batch_size, seq_length, hidden_size)

        # Calculate attention scores
        scores = self.attention_weights(lstm_outputs)  # (batch, seq_len, 1)
        scores = scores.squeeze(-1)  # (batch, seq_len)

        # Apply softmax to get attention weights
        attention_weights = F.softmax(scores, dim=1)  # (batch, seq_len)

        # Apply attention weights to lstm outputs
        # Expand dims for broadcasting: (batch, seq_len, 1)
        attention_weights = attention_weights.unsqueeze(-1)

        # Weighted sum: (batch, hidden_size)
        context_vector = torch.sum(lstm_outputs * attention_weights, dim=1)

        return context_vector, attention_weights.squeeze(-1)


class PerformanceLSTM(nn.Module):
    """
    Bidirectional LSTM with Attention for FPS prediction

    Architecture:
    - Input normalization
    - 2-layer Bidirectional LSTM
    - Attention mechanism
    - Fully connected output layers
    """

    def __init__(self, input_size: int = 5, hidden_size: int = 128,
                 num_layers: int = 2, output_horizon: int = 10, dropout: float = 0.3):
        super(PerformanceLSTM, self).__init__()

        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.output_horizon = output_horizon

        # Bidirectional LSTM
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=True
        )

        # Attention layer (applied to bidirectional outputs)
        self.attention = AttentionLayer(hidden_size * 2)  # *2 for bidirectional

        # Output layers
        self.fc1 = nn.Linear(hidden_size * 2, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, output_horizon)  # Predict next N time steps

        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(hidden_size * 2)

    def forward(self, x):
        # x shape: (batch_size, sequence_length, input_size)

        # LSTM forward pass
        lstm_out, (hidden, cell) = self.lstm(x)
        # lstm_out shape: (batch, seq_len, hidden_size * 2)

        # Apply layer normalization
        lstm_out = self.layer_norm(lstm_out)

        # Apply attention
        context, attention_weights = self.attention(lstm_out)
        # context shape: (batch, hidden_size * 2)

        # Fully connected layers
        out = F.relu(self.fc1(context))
        out = self.dropout(out)
        out = F.relu(self.fc2(out))
        out = self.dropout(out)
        out = self.fc3(out)  # (batch, output_horizon)

        return out, attention_weights


class PerformanceDataset(Dataset):
    """PyTorch Dataset for performance time series"""

    def __init__(self, sequences: List[PerformanceSequence],
                 sequence_length: int = 60, output_horizon: int = 10):
        self.sequence_length = sequence_length
        self.output_horizon = output_horizon
        self.samples = []

        # Process sequences into training samples
        for seq in sequences:
            if len(seq.fps_values) < sequence_length + output_horizon:
                continue

            # Create sliding windows
            for i in range(len(seq.fps_values) - sequence_length - output_horizon + 1):
                # Input features: fps, cpu, gpu, power, temp
                features = np.column_stack([
                    seq.fps_values[i:i+sequence_length],
                    seq.cpu_usage[i:i+sequence_length],
                    seq.gpu_usage[i:i+sequence_length],
                    seq.power_watts[i:i+sequence_length],
                    seq.gpu_temp[i:i+sequence_length] if seq.gpu_temp else [0] * sequence_length
                ])

                # Target: next N fps values
                target = seq.fps_values[i+sequence_length:i+sequence_length+output_horizon]

                self.samples.append((features, target))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        features, target = self.samples[idx]
        return (
            torch.tensor(features, dtype=torch.float32),
            torch.tensor(target, dtype=torch.float32)
        )


class LSTMPerformancePredictor:
    """
    LSTM-based performance predictor for time-series forecasting

    Production-ready implementation with:
    - Bidirectional LSTM layers
    - Attention mechanism for interpretability
    - Multi-step ahead prediction (1-30 seconds)
    - Comprehensive training and evaluation
    """

    def __init__(self, model_path: Optional[Path] = None,
                 sequence_length: int = 60, output_horizon: int = 10):
        self.model_path = model_path or Path.home() / '.local/share/bazzite-optimizer/ai-models/lstm_performance.pth'
        self.sequence_length = sequence_length  # seconds of history
        self.output_horizon = output_horizon    # seconds to predict
        self.model = None
        self.feature_means = None
        self.feature_stds = None

        if PYTORCH_AVAILABLE and self.model_path.exists():
            self._load_model()

    def _normalize_features(self, features: np.ndarray, fit: bool = False) -> np.ndarray:
        """Normalize features to zero mean and unit variance"""
        if fit or self.feature_means is None:
            self.feature_means = np.mean(features, axis=(0, 1), keepdims=True)
            self.feature_stds = np.std(features, axis=(0, 1), keepdims=True) + 1e-8

        return (features - self.feature_means) / self.feature_stds

    def _denormalize_fps(self, normalized_fps: np.ndarray) -> np.ndarray:
        """Denormalize FPS predictions"""
        if self.feature_means is not None:
            # FPS is the first feature (index 0)
            return normalized_fps * self.feature_stds[0, 0, 0] + self.feature_means[0, 0, 0]
        return normalized_fps

    def predict_next_fps(self, history: PerformanceSequence,
                        horizon: Optional[int] = None) -> List[float]:
        """
        Predict FPS for next N seconds

        Args:
            history: Historical performance data
            horizon: Prediction horizon (overrides default if provided)

        Returns:
            Predicted FPS values for next horizon seconds
        """

        if not PYTORCH_AVAILABLE or self.model is None:
            return self._fallback_prediction(history, horizon or self.output_horizon)

        try:
            # Ensure we have enough history
            if len(history.fps_values) < self.sequence_length:
                return self._fallback_prediction(history, horizon or self.output_horizon)

            # Prepare input features (last sequence_length points)
            features = np.column_stack([
                history.fps_values[-self.sequence_length:],
                history.cpu_usage[-self.sequence_length:],
                history.gpu_usage[-self.sequence_length:],
                history.power_watts[-self.sequence_length:],
                history.gpu_temp[-self.sequence_length:] if history.gpu_temp else [0] * self.sequence_length
            ])

            # Normalize
            features_normalized = self._normalize_features(features.reshape(1, *features.shape))

            # Convert to tensor
            input_tensor = torch.tensor(features_normalized, dtype=torch.float32)

            # Inference
            self.model.eval()
            with torch.no_grad():
                predictions, attention_weights = self.model(input_tensor)
                predictions = predictions.cpu().numpy()[0]  # (output_horizon,)

            # Denormalize predictions
            predicted_fps = self._denormalize_fps(predictions).tolist()

            # If different horizon requested, interpolate
            if horizon and horizon != self.output_horizon:
                predicted_fps = self._interpolate_predictions(predicted_fps, horizon)

            return predicted_fps

        except Exception as e:
            logger.error(f"LSTM prediction failed: {e}")
            return self._fallback_prediction(history, horizon or self.output_horizon)

    def _fallback_prediction(self, history: PerformanceSequence, horizon: int) -> List[float]:
        """Fallback prediction using exponential moving average"""
        if not history.fps_values:
            return [60.0] * horizon

        # Use exponential moving average of last 30 points
        recent_fps = history.fps_values[-30:]
        if len(recent_fps) == 0:
            return [60.0] * horizon

        # Calculate EMA
        alpha = 0.3
        ema = recent_fps[0]
        for fps in recent_fps[1:]:
            ema = alpha * fps + (1 - alpha) * ema

        # Add slight decay for future prediction
        predictions = []
        current = ema
        for i in range(horizon):
            predictions.append(current)
            # Slight regression to mean (assume 60 FPS baseline)
            current = 0.95 * current + 0.05 * 60.0

        return predictions

    def _interpolate_predictions(self, predictions: List[float], target_horizon: int) -> List[float]:
        """Interpolate predictions to different horizon"""
        if len(predictions) == target_horizon:
            return predictions

        # Linear interpolation
        x_original = np.linspace(0, 1, len(predictions))
        x_target = np.linspace(0, 1, target_horizon)
        return np.interp(x_target, x_original, predictions).tolist()

    def train(self, training_sequences: List[PerformanceSequence],
             validation_split: float = 0.2,
             epochs: int = 50,
             batch_size: int = 64,
             learning_rate: float = 0.001,
             early_stopping_patience: int = 10) -> Dict:
        """
        Train LSTM model on performance sequences

        Args:
            training_sequences: List of performance sequences
            validation_split: Fraction for validation
            epochs: Number of training epochs
            batch_size: Batch size
            learning_rate: Learning rate
            early_stopping_patience: Epochs to wait before early stopping

        Returns:
            Training metrics dictionary
        """
        if not PYTORCH_AVAILABLE:
            logger.error("PyTorch not available. Cannot train model.")
            return {}

        logger.info(f"Training LSTM on {len(training_sequences)} sequences...")

        # Create dataset
        full_dataset = PerformanceDataset(
            training_sequences,
            self.sequence_length,
            self.output_horizon
        )

        if len(full_dataset) == 0:
            logger.error("No training samples generated. Check sequence lengths.")
            return {}

        # Normalize features
        all_features = np.array([sample[0].numpy() for sample in full_dataset])
        self._normalize_features(all_features, fit=True)

        # Train/validation split
        train_size = int(len(full_dataset) * (1 - validation_split))
        val_size = len(full_dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(
            full_dataset, [train_size, val_size]
        )

        # Data loaders
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)

        # Initialize model
        self.model = PerformanceLSTM(
            input_size=5,  # fps, cpu, gpu, power, temp
            hidden_size=128,
            num_layers=2,
            output_horizon=self.output_horizon,
            dropout=0.3
        )

        # Loss and optimizer
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=5
        )

        # Training loop
        best_val_loss = float('inf')
        patience_counter = 0
        training_history = []

        for epoch in range(epochs):
            # Training phase
            self.model.train()
            train_loss = 0.0

            for features, targets in train_loader:
                optimizer.zero_grad()

                # Normalize features
                features_norm = self._normalize_features(features.numpy())
                features_norm = torch.tensor(features_norm, dtype=torch.float32)

                predictions, _ = self.model(features_norm)

                # Normalize targets (FPS values)
                targets_norm = (targets - self.feature_means[0, 0, 0]) / self.feature_stds[0, 0, 0]

                loss = criterion(predictions, targets_norm)
                loss.backward()

                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)

                optimizer.step()
                train_loss += loss.item()

            avg_train_loss = train_loss / len(train_loader)

            # Validation phase
            self.model.eval()
            val_loss = 0.0
            val_mae = 0.0

            with torch.no_grad():
                for features, targets in val_loader:
                    features_norm = self._normalize_features(features.numpy())
                    features_norm = torch.tensor(features_norm, dtype=torch.float32)

                    predictions, _ = self.model(features_norm)

                    targets_norm = (targets - self.feature_means[0, 0, 0]) / self.feature_stds[0, 0, 0]

                    loss = criterion(predictions, targets_norm)
                    val_loss += loss.item()

                    # Calculate MAE in original scale
                    pred_original = self._denormalize_fps(predictions.numpy())
                    mae = np.mean(np.abs(pred_original - targets.numpy()))
                    val_mae += mae

            avg_val_loss = val_loss / len(val_loader)
            avg_val_mae = val_mae / len(val_loader)

            # Learning rate scheduling
            scheduler.step(avg_val_loss)

            # Early stopping and model saving
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                patience_counter = 0
                self.save_model()
            else:
                patience_counter += 1

            # Log progress
            logger.info(f"Epoch {epoch+1}/{epochs} - "
                       f"Train Loss: {avg_train_loss:.4f}, "
                       f"Val Loss: {avg_val_loss:.4f}, "
                       f"Val MAE: {avg_val_mae:.2f} FPS")

            training_history.append({
                'epoch': epoch + 1,
                'train_loss': avg_train_loss,
                'val_loss': avg_val_loss,
                'val_mae': avg_val_mae
            })

            # Early stopping
            if patience_counter >= early_stopping_patience:
                logger.info(f"Early stopping triggered at epoch {epoch+1}")
                break

        logger.info(f"Training complete. Best validation loss: {best_val_loss:.4f}")

        return {
            'best_val_loss': best_val_loss,
            'final_train_loss': avg_train_loss,
            'final_val_mae': avg_val_mae,
            'training_history': training_history,
            'epochs_trained': epoch + 1
        }

    def save_model(self) -> bool:
        """Save trained model to disk"""
        if self.model is None:
            logger.error("No model to save")
            return False

        try:
            self.model_path.parent.mkdir(parents=True, exist_ok=True)

            torch.save({
                'model_state_dict': self.model.state_dict(),
                'sequence_length': self.sequence_length,
                'output_horizon': self.output_horizon,
                'feature_means': self.feature_means,
                'feature_stds': self.feature_stds
            }, self.model_path)

            logger.info(f"Model saved to {self.model_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False

    def _load_model(self) -> bool:
        """Load trained model from disk"""
        try:
            checkpoint = torch.load(self.model_path)

            self.sequence_length = checkpoint['sequence_length']
            self.output_horizon = checkpoint['output_horizon']
            self.feature_means = checkpoint['feature_means']
            self.feature_stds = checkpoint['feature_stds']

            self.model = PerformanceLSTM(
                input_size=5,
                hidden_size=128,
                num_layers=2,
                output_horizon=self.output_horizon,
                dropout=0.3
            )
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.eval()

            logger.info(f"Loaded LSTM model from {self.model_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


def generate_synthetic_performance_data(n_sequences: int = 100,
                                       seq_length: int = 150) -> List[PerformanceSequence]:
    """
    Generate synthetic performance data for testing

    Args:
        n_sequences: Number of sequences to generate
        seq_length: Length of each sequence

    Returns:
        List of performance sequences
    """
    import random

    sequences = []

    for _ in range(n_sequences):
        # Base FPS with trend and noise
        base_fps = random.uniform(60, 240)
        trend = random.uniform(-0.1, 0.1)  # FPS trend over time

        fps_values = []
        cpu_usage = []
        gpu_usage = []
        power_watts = []
        gpu_temp = []

        for t in range(seq_length):
            # FPS with trend and random fluctuations
            fps = base_fps + trend * t + random.gauss(0, 10)
            fps = max(30, min(360, fps))  # Clamp to reasonable range
            fps_values.append(fps)

            # CPU usage correlated with FPS
            cpu = random.uniform(30, 80) + (240 - fps) * 0.1
            cpu_usage.append(min(100, max(0, cpu)))

            # GPU usage strongly correlated with FPS
            gpu = random.uniform(60, 95) + (fps - 120) * 0.1
            gpu_usage.append(min(100, max(0, gpu)))

            # Power consumption
            power = 150 + gpu * 2 + random.gauss(0, 20)
            power_watts.append(max(100, min(450, power)))

            # GPU temperature
            temp = 50 + gpu * 0.4 + random.gauss(0, 3)
            gpu_temp.append(max(40, min(95, temp)))

        sequences.append(PerformanceSequence(
            timestamps=list(range(seq_length)),
            fps_values=fps_values,
            cpu_usage=cpu_usage,
            gpu_usage=gpu_usage,
            power_watts=power_watts,
            gpu_temp=gpu_temp
        ))

    return sequences


if __name__ == "__main__":
    # Example usage and training
    logging.basicConfig(level=logging.INFO)

    predictor = LSTMPerformancePredictor(sequence_length=60, output_horizon=10)

    # Generate training data
    print("Generating synthetic training data...")
    training_data = generate_synthetic_performance_data(n_sequences=200, seq_length=200)

    # Train model
    if PYTORCH_AVAILABLE:
        print("\nTraining LSTM model...")
        metrics = predictor.train(training_data, epochs=30, batch_size=32)
        print(f"\nTraining completed:")
        print(f"  Best validation loss: {metrics['best_val_loss']:.4f}")
        print(f"  Final validation MAE: {metrics['final_val_mae']:.2f} FPS")
        print(f"  Epochs trained: {metrics['epochs_trained']}")

        # Test prediction
        print("\nTesting FPS prediction:")
        test_sequence = training_data[0]
        predicted_fps = predictor.predict_next_fps(test_sequence, horizon=10)
        print(f"  Current FPS: {test_sequence.fps_values[-1]:.1f}")
        print(f"  Predicted next 10s: {[f'{fps:.1f}' for fps in predicted_fps]}")
    else:
        print("PyTorch not available. Install with: pip install torch")
