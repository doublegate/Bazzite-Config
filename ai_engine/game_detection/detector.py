"""
Game Detection AI using Neural Networks

Automatically detects running games from process information
using a trained neural network classifier with CNN architecture.
"""

import logging
import json
import pickle
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import numpy as np

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
class GameDetection:
    """Detected game information"""
    game_name: str
    game_type: str  # 'fps', 'strategy', 'rpg', etc.
    confidence: float  # 0.0-1.0
    process_name: str
    recommended_profile: str


class GameCNN(nn.Module):
    """
    Convolutional Neural Network for game classification from process names

    Architecture:
    - Character-level CNN with embedding layer
    - 3 convolutional layers with increasing filters
    - Max pooling and dropout for regularization
    - Fully connected layers for classification
    """

    def __init__(self, vocab_size: int = 128, embedding_dim: int = 32,
                 num_classes: int = 50, max_length: int = 100):
        super(GameCNN, self).__init__()

        self.max_length = max_length

        # Character embedding layer
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)

        # Convolutional layers with different kernel sizes
        self.conv1 = nn.Conv1d(embedding_dim, 128, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(128, 256, kernel_size=3, padding=1)
        self.conv3 = nn.Conv1d(256, 512, kernel_size=3, padding=1)

        # Batch normalization
        self.bn1 = nn.BatchNorm1d(128)
        self.bn2 = nn.BatchNorm1d(256)
        self.bn3 = nn.BatchNorm1d(512)

        # Max pooling
        self.pool = nn.MaxPool1d(2)

        # Dropout for regularization
        self.dropout = nn.Dropout(0.5)

        # Fully connected layers
        # After 3 pooling operations: max_length // 8
        fc_input_size = 512 * (max_length // 8)
        self.fc1 = nn.Linear(fc_input_size, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, num_classes)

    def forward(self, x):
        # x shape: (batch_size, max_length)

        # Embedding: (batch_size, max_length, embedding_dim)
        x = self.embedding(x)

        # Transpose for Conv1d: (batch_size, embedding_dim, max_length)
        x = x.transpose(1, 2)

        # Conv layer 1
        x = self.conv1(x)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.pool(x)  # (batch_size, 128, max_length/2)

        # Conv layer 2
        x = self.conv2(x)
        x = self.bn2(x)
        x = F.relu(x)
        x = self.pool(x)  # (batch_size, 256, max_length/4)

        # Conv layer 3
        x = self.conv3(x)
        x = self.bn3(x)
        x = F.relu(x)
        x = self.pool(x)  # (batch_size, 512, max_length/8)

        # Flatten
        x = x.view(x.size(0), -1)

        # Fully connected layers
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)

        return x


class GameDataset(Dataset):
    """PyTorch Dataset for game process names"""

    def __init__(self, process_names: List[str], labels: List[int], max_length: int = 100):
        self.process_names = process_names
        self.labels = labels
        self.max_length = max_length

    def __len__(self):
        return len(self.process_names)

    def __getitem__(self, idx):
        # Convert process name to character indices
        process_name = self.process_names[idx].lower()

        # Character encoding (ASCII)
        encoded = [min(ord(c), 127) for c in process_name[:self.max_length]]

        # Pad to max_length
        encoded += [0] * (self.max_length - len(encoded))

        return torch.tensor(encoded, dtype=torch.long), torch.tensor(self.labels[idx], dtype=torch.long)


class GameDetector:
    """
    Neural network-based game detector

    Uses a trained CNN to classify running games from:
    - Process name patterns
    - Window titles
    - Character-level features

    Production-ready implementation with PyTorch CNN architecture.
    """

    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = model_path or Path.home() / '.local/share/bazzite-optimizer/ai-models/game_detector.pth'
        self.model = None
        self.game_database = self._load_game_database()
        self.game_to_idx = {}
        self.idx_to_game = {}
        self.max_length = 100

        if PYTORCH_AVAILABLE and self.model_path.exists():
            self._load_model()

    def _load_game_database(self) -> Dict:
        """Load known game database"""
        return {
            # FPS Games
            'csgo': ('Counter-Strike: Global Offensive', 'fps', 'competitive'),
            'cs2': ('Counter-Strike 2', 'fps', 'competitive'),
            'valorant': ('VALORANT', 'fps', 'competitive'),
            'valorant-win64-shipping': ('VALORANT', 'fps', 'competitive'),
            'apex_legends': ('Apex Legends', 'fps', 'competitive'),
            'r5apex': ('Apex Legends', 'fps', 'competitive'),
            'cod': ('Call of Duty', 'fps', 'competitive'),
            'modernwarfare': ('Call of Duty: Modern Warfare', 'fps', 'competitive'),
            'overwatch': ('Overwatch 2', 'fps', 'competitive'),
            'rainbow6': ('Rainbow Six Siege', 'fps', 'competitive'),

            # Strategy Games
            'civ6': ('Civilization VI', 'strategy', 'balanced'),
            'civilizationvi': ('Civilization VI', 'strategy', 'balanced'),
            'aoe2': ('Age of Empires II', 'strategy', 'balanced'),
            'starcraft2': ('StarCraft II', 'strategy', 'competitive'),
            'sc2': ('StarCraft II', 'strategy', 'competitive'),
            'dota2': ('Dota 2', 'moba', 'competitive'),
            'league of legends': ('League of Legends', 'moba', 'competitive'),

            # RPG/Action
            'witcher3': ('The Witcher 3', 'rpg', 'balanced'),
            'eldenring': ('Elden Ring', 'rpg', 'balanced'),
            'cyberpunk2077': ('Cyberpunk 2077', 'rpg', 'competitive'),
            'skyrim': ('The Elder Scrolls V: Skyrim', 'rpg', 'balanced'),
            'fallout4': ('Fallout 4', 'rpg', 'balanced'),

            # AAA Action
            'gtav': ('Grand Theft Auto V', 'action', 'balanced'),
            'rdr2': ('Red Dead Redemption 2', 'action', 'balanced'),
            'fortnite': ('Fortnite', 'fps', 'competitive'),
            'pubg': ('PUBG', 'fps', 'competitive'),

            # Racing
            'assettocorsa': ('Assetto Corsa', 'racing', 'competitive'),
            'forzahorizon5': ('Forza Horizon 5', 'racing', 'balanced'),

            # Simulation
            'msfs': ('Microsoft Flight Simulator', 'simulation', 'balanced'),
            'eurotrucks2': ('Euro Truck Simulator 2', 'simulation', 'balanced'),
        }

    def _build_game_mappings(self, games: List[str]):
        """Build game name to index mappings"""
        unique_games = sorted(set(games))
        self.game_to_idx = {game: idx for idx, game in enumerate(unique_games)}
        self.idx_to_game = {idx: game for game, idx in self.game_to_idx.items()}

    def _load_model(self) -> bool:
        """Load trained model from disk"""
        try:
            checkpoint = torch.load(self.model_path)

            num_classes = checkpoint['num_classes']
            self.game_to_idx = checkpoint['game_to_idx']
            self.idx_to_game = checkpoint['idx_to_game']
            self.max_length = checkpoint.get('max_length', 100)

            self.model = GameCNN(
                vocab_size=128,
                embedding_dim=32,
                num_classes=num_classes,
                max_length=self.max_length
            )
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.eval()

            logger.info(f"Loaded game detection model from {self.model_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    def detect_game(self, process_name: str, window_title: str = "") -> Optional[GameDetection]:
        """
        Detect game from process information

        Args:
            process_name: Process executable name
            window_title: Window title text (optional)

        Returns:
            GameDetection if game detected, None otherwise
        """

        # Try neural network detection if model is loaded
        if PYTORCH_AVAILABLE and self.model is not None:
            return self._detect_with_nn(process_name, window_title)

        # Fallback to database lookup
        return self._detect_with_database(process_name, window_title)

    def _detect_with_nn(self, process_name: str, window_title: str = "") -> Optional[GameDetection]:
        """Neural network-based detection"""
        try:
            # Prepare input
            process_lower = process_name.lower()
            encoded = [min(ord(c), 127) for c in process_lower[:self.max_length]]
            encoded += [0] * (self.max_length - len(encoded))

            # Convert to tensor
            input_tensor = torch.tensor([encoded], dtype=torch.long)

            # Inference
            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = F.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)

                confidence_val = confidence.item()
                predicted_idx = predicted.item()

            # Get game name from index
            if predicted_idx in self.idx_to_game:
                game_key = self.idx_to_game[predicted_idx]

                if game_key in self.game_database:
                    game_name, game_type, profile = self.game_database[game_key]

                    # Only return if confidence > threshold
                    if confidence_val > 0.5:
                        return GameDetection(
                            game_name=game_name,
                            game_type=game_type,
                            confidence=confidence_val,
                            process_name=process_name,
                            recommended_profile=profile
                        )

            return None

        except Exception as e:
            logger.error(f"Neural network detection failed: {e}")
            return self._detect_with_database(process_name, window_title)

    def _detect_with_database(self, process_name: str, window_title: str = "") -> Optional[GameDetection]:
        """Fallback database lookup"""
        process_lower = process_name.lower()

        for key, (name, game_type, profile) in self.game_database.items():
            if key in process_lower:
                return GameDetection(
                    game_name=name,
                    game_type=game_type,
                    confidence=0.85,
                    process_name=process_name,
                    recommended_profile=profile
                )

        return None

    def detect_from_system(self) -> List[GameDetection]:
        """
        Detect games from current running processes

        Returns:
            List of detected games
        """
        try:
            import psutil

            detections = []
            seen_games = set()

            for proc in psutil.process_iter(['name']):
                try:
                    detection = self.detect_game(proc.info['name'])
                    if detection and detection.game_name not in seen_games:
                        detections.append(detection)
                        seen_games.add(detection.game_name)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            return detections

        except ImportError:
            logger.warning("psutil not available")
            return []

    def train_model(self, training_data: List[Tuple[str, str]],
                   validation_split: float = 0.2,
                   epochs: int = 20,
                   batch_size: int = 32,
                   learning_rate: float = 0.001) -> Dict:
        """
        Train CNN on game process data

        Args:
            training_data: List of (process_name, game_key) tuples
            validation_split: Fraction of data for validation
            epochs: Number of training epochs
            batch_size: Batch size for training
            learning_rate: Learning rate for optimizer

        Returns:
            Training metrics dictionary
        """
        if not PYTORCH_AVAILABLE:
            logger.error("PyTorch not available. Cannot train model.")
            return {}

        logger.info(f"Training game detection CNN on {len(training_data)} samples...")

        # Prepare data
        process_names = [sample[0] for sample in training_data]
        game_keys = [sample[1] for sample in training_data]

        # Build game mappings
        self._build_game_mappings(game_keys)

        # Convert game keys to indices
        labels = [self.game_to_idx[key] for key in game_keys]

        # Train/validation split
        split_idx = int(len(process_names) * (1 - validation_split))
        train_names = process_names[:split_idx]
        train_labels = labels[:split_idx]
        val_names = process_names[split_idx:]
        val_labels = labels[split_idx:]

        # Create datasets
        train_dataset = GameDataset(train_names, train_labels, self.max_length)
        val_dataset = GameDataset(val_names, val_labels, self.max_length)

        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)

        # Initialize model
        num_classes = len(self.game_to_idx)
        self.model = GameCNN(
            vocab_size=128,
            embedding_dim=32,
            num_classes=num_classes,
            max_length=self.max_length
        )

        # Loss and optimizer
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=3)

        # Training loop
        best_val_accuracy = 0.0
        training_history = []

        for epoch in range(epochs):
            # Training phase
            self.model.train()
            train_loss = 0.0
            train_correct = 0
            train_total = 0

            for inputs, targets in train_loader:
                optimizer.zero_grad()
                outputs = self.model(inputs)
                loss = criterion(outputs, targets)
                loss.backward()
                optimizer.step()

                train_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                train_total += targets.size(0)
                train_correct += (predicted == targets).sum().item()

            # Validation phase
            self.model.eval()
            val_loss = 0.0
            val_correct = 0
            val_total = 0

            with torch.no_grad():
                for inputs, targets in val_loader:
                    outputs = self.model(inputs)
                    loss = criterion(outputs, targets)

                    val_loss += loss.item()
                    _, predicted = torch.max(outputs.data, 1)
                    val_total += targets.size(0)
                    val_correct += (predicted == targets).sum().item()

            # Calculate metrics
            train_accuracy = 100 * train_correct / train_total
            val_accuracy = 100 * val_correct / val_total
            avg_train_loss = train_loss / len(train_loader)
            avg_val_loss = val_loss / len(val_loader)

            # Learning rate scheduling
            scheduler.step(avg_val_loss)

            # Save best model
            if val_accuracy > best_val_accuracy:
                best_val_accuracy = val_accuracy
                self.save_model()

            # Log progress
            logger.info(f"Epoch {epoch+1}/{epochs} - "
                       f"Train Loss: {avg_train_loss:.4f}, Train Acc: {train_accuracy:.2f}%, "
                       f"Val Loss: {avg_val_loss:.4f}, Val Acc: {val_accuracy:.2f}%")

            training_history.append({
                'epoch': epoch + 1,
                'train_loss': avg_train_loss,
                'train_accuracy': train_accuracy,
                'val_loss': avg_val_loss,
                'val_accuracy': val_accuracy
            })

        logger.info(f"Training complete. Best validation accuracy: {best_val_accuracy:.2f}%")

        return {
            'best_val_accuracy': best_val_accuracy,
            'final_train_accuracy': train_accuracy,
            'training_history': training_history,
            'num_classes': num_classes
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
                'game_to_idx': self.game_to_idx,
                'idx_to_game': self.idx_to_game,
                'num_classes': len(self.game_to_idx),
                'max_length': self.max_length
            }, self.model_path)

            logger.info(f"Model saved to {self.model_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False


def generate_synthetic_training_data(n_samples: int = 1000) -> List[Tuple[str, str]]:
    """
    Generate synthetic training data for testing

    Args:
        n_samples: Number of training samples to generate

    Returns:
        List of (process_name, game_key) tuples
    """
    import random

    detector = GameDetector()
    game_database = detector.game_database

    training_data = []
    game_keys = list(game_database.keys())

    for _ in range(n_samples):
        # Select random game
        game_key = random.choice(game_keys)

        # Add variations of process name
        variations = [
            game_key,
            game_key.upper(),
            game_key + ".exe",
            game_key + "-win64",
            game_key + "_launcher",
            f"steam_{game_key}",
        ]

        # Add some noise
        if random.random() < 0.3:
            process_name = random.choice(variations) + "_" + str(random.randint(1, 999))
        else:
            process_name = random.choice(variations)

        training_data.append((process_name, game_key))

    return training_data


if __name__ == "__main__":
    # Example usage and training
    logging.basicConfig(level=logging.INFO)

    detector = GameDetector()

    # Generate training data
    print("Generating synthetic training data...")
    training_data = generate_synthetic_training_data(n_samples=2000)

    # Train model
    if PYTORCH_AVAILABLE:
        print("\nTraining CNN model...")
        metrics = detector.train_model(training_data, epochs=15)
        print(f"\nTraining completed:")
        print(f"  Best validation accuracy: {metrics['best_val_accuracy']:.2f}%")
        print(f"  Final training accuracy: {metrics['final_train_accuracy']:.2f}%")
    else:
        print("PyTorch not available. Install with: pip install torch")

    # Test detection
    print("\nTesting game detection:")
    test_processes = [
        "csgo.exe",
        "valorant-win64-shipping.exe",
        "eldenring.exe",
        "cyberpunk2077.exe",
        "unknown_game.exe"
    ]

    for process in test_processes:
        detection = detector.detect_game(process)
        if detection:
            print(f"  {process}: {detection.game_name} ({detection.confidence:.2%} confidence)")
        else:
            print(f"  {process}: Not detected")
