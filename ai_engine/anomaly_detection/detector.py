"""
Variational Autoencoder for Anomaly Detection

Detects system anomalies using VAE trained on normal operating conditions.
Production-ready PyTorch implementation.
"""

import logging
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

# PyTorch imports
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    logger.warning("PyTorch not available")


@dataclass
class SystemAnomaly:
    """Detected system anomaly"""
    anomaly_type: str  # 'thermal', 'performance', 'crash_risk'
    severity: float  # 0.0-1.0
    affected_component: str
    description: str
    recommended_action: str
    timestamp: str
    reconstruction_error: Optional[float] = None


class SystemVAE(nn.Module):
    """Variational Autoencoder for system metrics anomaly detection"""

    def __init__(self, input_dim: int = 10, latent_dim: int = 4):
        super(SystemVAE, self).__init__()

        # Encoder: input -> hidden -> latent (mu, logvar)
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.Linear(64, 32),
            nn.ReLU()
        )

        self.fc_mu = nn.Linear(32, latent_dim)
        self.fc_logvar = nn.Linear(32, latent_dim)

        # Decoder: latent -> hidden -> output
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.Linear(64, input_dim),
            nn.Sigmoid()  # Normalize to [0, 1]
        )

    def encode(self, x):
        """Encode input to latent space distribution"""
        h = self.encoder(x)
        return self.fc_mu(h), self.fc_logvar(h)

    def reparameterize(self, mu, logvar):
        """Reparameterization trick for backprop through sampling"""
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z):
        """Decode latent vector to reconstruction"""
        return self.decoder(z)

    def forward(self, x):
        """Full forward pass"""
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        return self.decode(z), mu, logvar


def vae_loss(recon_x, x, mu, logvar):
    """VAE loss = reconstruction loss + KL divergence"""
    # Reconstruction loss (MSE)
    recon_loss = F.mse_loss(recon_x, x, reduction='sum')

    # KL divergence
    kld = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())

    return recon_loss + kld


class AnomalyDetector:
    """
    VAE-based anomaly detector for gaming systems

    Production-ready implementation with:
    - Variational Autoencoder architecture
    - Reconstruction error thresholding
    - Real-time anomaly scoring
    - Heuristic fallback for reliability
    """

    def __init__(self, model_path: Optional[Path] = None, threshold: float = 0.05):
        self.model_path = model_path or Path.home() / '.local/share/bazzite-optimizer/ai-models/vae_anomaly.pth'
        self.model = None
        self.threshold = threshold  # Reconstruction error threshold
        self.feature_means = None
        self.feature_stds = None

        if PYTORCH_AVAILABLE and self.model_path.exists():
            self._load_model()

    def detect_anomalies(self, system_metrics: Dict) -> List[SystemAnomaly]:
        """
        Detect anomalies in system metrics

        Args:
            system_metrics: Dictionary of system metrics

        Returns:
            List of detected anomalies
        """

        if PYTORCH_AVAILABLE and self.model is not None:
            return self._detect_with_vae(system_metrics)

        # Fallback to heuristics
        return self._detect_with_heuristics(system_metrics)

    def _detect_with_vae(self, metrics: Dict) -> List[SystemAnomaly]:
        """VAE-based anomaly detection"""
        try:
            # Extract and normalize features
            features = np.array([
                metrics.get('cpu_temp', 50) / 100,
                metrics.get('gpu_temp', 50) / 100,
                metrics.get('cpu_usage', 50) / 100,
                metrics.get('gpu_usage', 50) / 100,
                metrics.get('ram_usage', 50) / 100,
                metrics.get('power_watts', 200) / 500,
                metrics.get('fps', 60) / 300,
                metrics.get('fan_speed', 50) / 100,
                metrics.get('throttling', 0),
                metrics.get('error_count', 0) / 10
            ], dtype=np.float32)

            # Normalize using training statistics
            if self.feature_means is not None:
                features_norm = (features - self.feature_means) / (self.feature_stds + 1e-8)
            else:
                features_norm = features

            # Convert to tensor and predict
            x = torch.tensor([features_norm], dtype=torch.float32)

            self.model.eval()
            with torch.no_grad():
                recon, mu, logvar = self.model(x)
                error = F.mse_loss(recon, x).item()

            anomalies = []

            # Check if reconstruction error exceeds threshold
            if error > self.threshold:
                # Analyze which features deviated most
                diff = torch.abs(recon - x)[0].numpy()
                feature_names = ['cpu_temp', 'gpu_temp', 'cpu_usage', 'gpu_usage',
                               'ram_usage', 'power', 'fps', 'fan_speed', 'throttling', 'errors']

                max_idx = np.argmax(diff)
                severity = min(1.0, error / self.threshold)

                anomalies.append(SystemAnomaly(
                    anomaly_type='performance',
                    severity=severity,
                    affected_component=feature_names[max_idx],
                    description=f"Abnormal {feature_names[max_idx]} pattern detected (error: {error:.4f})",
                    recommended_action="Check system health and recent configuration changes",
                    timestamp=datetime.now().isoformat(),
                    reconstruction_error=error
                ))

            # Also run heuristic checks for critical issues
            heuristic_anomalies = self._detect_with_heuristics(metrics)
            anomalies.extend(heuristic_anomalies)

            return anomalies

        except Exception as e:
            logger.error(f"VAE detection failed: {e}")
            return self._detect_with_heuristics(metrics)

    def _detect_with_heuristics(self, metrics: Dict) -> List[SystemAnomaly]:
        """Heuristic-based fallback detection"""
        anomalies = []
        timestamp = datetime.now().isoformat()

        # Critical thermal anomalies
        if metrics.get('cpu_temp', 0) > 85:
            anomalies.append(SystemAnomaly(
                anomaly_type='thermal',
                severity=0.9,
                affected_component='CPU',
                description=f"CPU temperature critical: {metrics['cpu_temp']}°C",
                recommended_action="Reduce CPU load or improve cooling",
                timestamp=timestamp
            ))

        if metrics.get('gpu_temp', 0) > 85:
            anomalies.append(SystemAnomaly(
                anomaly_type='thermal',
                severity=0.9,
                affected_component='GPU',
                description=f"GPU temperature critical: {metrics['gpu_temp']}°C",
                recommended_action="Reduce graphics settings or improve cooling",
                timestamp=timestamp
            ))

        # Performance anomalies
        if metrics.get('fps', 60) < 30 and metrics.get('gpu_usage', 100) < 50:
            anomalies.append(SystemAnomaly(
                anomaly_type='performance',
                severity=0.7,
                affected_component='GPU',
                description="Low FPS despite low GPU usage - possible CPU bottleneck",
                recommended_action="Check for CPU bottleneck, background processes, or driver issues",
                timestamp=timestamp
            ))

        # Power anomalies
        if metrics.get('power_watts', 0) > 450:
            anomalies.append(SystemAnomaly(
                anomaly_type='power',
                severity=0.6,
                affected_component='PSU',
                description=f"High power consumption: {metrics['power_watts']}W",
                recommended_action="Monitor PSU stability and consider power limits",
                timestamp=timestamp
            ))

        return anomalies

    def train(self, normal_data: List[Dict],
             epochs: int = 100,
             batch_size: int = 128,
             learning_rate: float = 0.001) -> Dict:
        """
        Train VAE on normal operating data

        Args:
            normal_data: List of normal system metrics
            epochs: Training epochs
            batch_size: Batch size
            learning_rate: Learning rate

        Returns:
            Training metrics
        """
        if not PYTORCH_AVAILABLE:
            logger.error("PyTorch not available")
            return {}

        logger.info(f"Training VAE on {len(normal_data)} normal samples...")

        # Prepare features
        features_list = []
        for metrics in normal_data:
            features = np.array([
                metrics.get('cpu_temp', 50) / 100,
                metrics.get('gpu_temp', 50) / 100,
                metrics.get('cpu_usage', 50) / 100,
                metrics.get('gpu_usage', 50) / 100,
                metrics.get('ram_usage', 50) / 100,
                metrics.get('power_watts', 200) / 500,
                metrics.get('fps', 60) / 300,
                metrics.get('fan_speed', 50) / 100,
                metrics.get('throttling', 0),
                metrics.get('error_count', 0) / 10
            ], dtype=np.float32)
            features_list.append(features)

        features_array = np.array(features_list)

        # Calculate normalization statistics
        self.feature_means = np.mean(features_array, axis=0)
        self.feature_stds = np.std(features_array, axis=0)

        # Normalize
        features_norm = (features_array - self.feature_means) / (self.feature_stds + 1e-8)

        # Create dataset
        dataset = torch.utils.data.TensorDataset(
            torch.tensor(features_norm, dtype=torch.float32)
        )
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        # Initialize model
        self.model = SystemVAE(input_dim=10, latent_dim=4)
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)

        # Training loop
        training_history = []

        for epoch in range(epochs):
            self.model.train()
            total_loss = 0

            for (batch,) in dataloader:
                optimizer.zero_grad()
                recon, mu, logvar = self.model(batch)
                loss = vae_loss(recon, batch, mu, logvar)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

            avg_loss = total_loss / len(dataloader)

            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")

            training_history.append({'epoch': epoch + 1, 'loss': avg_loss})

        # Save model
        self.save_model()

        logger.info("VAE training complete")
        return {
            'final_loss': avg_loss,
            'training_history': training_history
        }

    def save_model(self) -> bool:
        """Save trained model"""
        if self.model is None:
            logger.error("No model to save")
            return False

        try:
            self.model_path.parent.mkdir(parents=True, exist_ok=True)

            torch.save({
                'model_state_dict': self.model.state_dict(),
                'threshold': self.threshold,
                'feature_means': self.feature_means,
                'feature_stds': self.feature_stds
            }, self.model_path)

            logger.info(f"Model saved to {self.model_path}")
            return True

        except Exception as e:
            logger.error(f"Save failed: {e}")
            return False

    def _load_model(self) -> bool:
        """Load trained model"""
        try:
            checkpoint = torch.load(self.model_path)

            self.model = SystemVAE(input_dim=10, latent_dim=4)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.threshold = checkpoint['threshold']
            self.feature_means = checkpoint['feature_means']
            self.feature_stds = checkpoint['feature_stds']
            self.model.eval()

            logger.info(f"Model loaded from {self.model_path}")
            return True

        except Exception as e:
            logger.error(f"Load failed: {e}")
            return False


def generate_synthetic_normal_data(n_samples: int = 1000) -> List[Dict]:
    """Generate synthetic normal operating data for training"""
    import random

    data = []
    for _ in range(n_samples):
        data.append({
            'cpu_temp': random.uniform(45, 75),
            'gpu_temp': random.uniform(50, 75),
            'cpu_usage': random.uniform(30, 80),
            'gpu_usage': random.uniform(60, 95),
            'ram_usage': random.uniform(40, 75),
            'power_watts': random.uniform(200, 350),
            'fps': random.uniform(60, 240),
            'fan_speed': random.uniform(40, 80),
            'throttling': 0,
            'error_count': 0
        })

    return data


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    detector = AnomalyDetector()

    # Generate and train on normal data
    if PYTORCH_AVAILABLE:
        print("Generating normal training data...")
        normal_data = generate_synthetic_normal_data(n_samples=2000)

        print("\nTraining VAE...")
        metrics = detector.train(normal_data, epochs=50)
        print(f"Training complete. Final loss: {metrics['final_loss']:.4f}")

        # Test anomaly detection
        print("\nTesting anomaly detection:")
        test_cases = [
            {'cpu_temp': 70, 'gpu_temp': 65, 'cpu_usage': 60, 'gpu_usage': 85, 'ram_usage': 50, 'power_watts': 280, 'fps': 144, 'fan_speed': 60},
            {'cpu_temp': 95, 'gpu_temp': 90, 'cpu_usage': 100, 'gpu_usage': 100, 'ram_usage': 90, 'power_watts': 450, 'fps': 20, 'fan_speed': 100},
        ]

        for i, test_metrics in enumerate(test_cases, 1):
            anomalies = detector.detect_anomalies(test_metrics)
            print(f"\nTest case {i}:")
            if anomalies:
                for anomaly in anomalies:
                    print(f"  [{anomaly.severity:.2f}] {anomaly.anomaly_type}: {anomaly.description}")
            else:
                print("  No anomalies detected")
    else:
        print("PyTorch not available")
