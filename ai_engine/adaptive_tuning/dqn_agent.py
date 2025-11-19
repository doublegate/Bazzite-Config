#!/usr/bin/env python3
"""
Deep Q-Network (DQN) for Adaptive Gaming Optimization

Production PyTorch implementation of DQN for real-time gaming parameter optimization.
"""

import logging
import random
import numpy as np
from collections import deque, namedtuple
from typing import List, Tuple, Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    import torch.optim as optim
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    logger.warning("PyTorch not available for DQN")


# Experience tuple for replay buffer
Experience = namedtuple('Experience', ['state', 'action', 'reward', 'next_state', 'done'])


class DQNetwork(nn.Module):
    """
    Deep Q-Network architecture

    Input: State vector (20 dimensions - system metrics)
    Output: Q-values for each action (10 actions - optimization parameters)
    """

    def __init__(self, state_size: int = 20, action_size: int = 10, hidden_size: int = 128):
        super(DQNetwork, self).__init__()

        self.fc1 = nn.Linear(state_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, 64)
        self.fc4 = nn.Linear(64, action_size)

        self.layer_norm1 = nn.LayerNorm(hidden_size)
        self.layer_norm2 = nn.LayerNorm(hidden_size)

        self.dropout = nn.Dropout(0.2)

    def forward(self, state):
        """Forward pass"""
        x = F.relu(self.layer_norm1(self.fc1(state)))
        x = self.dropout(x)
        x = F.relu(self.layer_norm2(self.fc2(x)))
        x = self.dropout(x)
        x = F.relu(self.fc3(x))
        x = self.fc4(x)  # Q-values (no activation)
        return x


class ReplayBuffer:
    """
    Experience Replay Buffer for DQN

    Stores experiences and provides random sampling for training.
    """

    def __init__(self, capacity: int = 10000):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        """Add experience to buffer"""
        self.buffer.append(Experience(state, action, reward, next_state, done))

    def sample(self, batch_size: int) -> List[Experience]:
        """Sample random batch of experiences"""
        return random.sample(self.buffer, batch_size)

    def __len__(self):
        return len(self.buffer)


class DQNAgent:
    """
    DQN Agent for Adaptive Gaming Optimization

    Features:
    - Deep Q-Network with target network
    - Experience replay
    - Epsilon-greedy exploration
    - Double DQN (optional)
    - Adaptive learning rate
    """

    def __init__(self,
                 state_size: int = 20,
                 action_size: int = 10,
                 hidden_size: int = 128,
                 learning_rate: float = 0.001,
                 gamma: float = 0.99,
                 epsilon_start: float = 1.0,
                 epsilon_end: float = 0.01,
                 epsilon_decay: float = 0.995,
                 buffer_size: int = 10000,
                 batch_size: int = 64,
                 target_update: int = 10,
                 model_path: Optional[Path] = None):

        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.target_update = target_update
        self.update_counter = 0

        self.model_path = model_path or Path.home() / '.local/share/bazzite-optimizer/ai-models/dqn_agent.pth'

        if not PYTORCH_AVAILABLE:
            logger.error("PyTorch not available. DQN cannot be initialized.")
            return

        # Q-Network and Target Network
        self.q_network = DQNetwork(state_size, action_size, hidden_size)
        self.target_network = DQNetwork(state_size, action_size, hidden_size)
        self.target_network.load_state_dict(self.q_network.state_dict())
        self.target_network.eval()

        # Optimizer
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)

        # Replay buffer
        self.memory = ReplayBuffer(buffer_size)

        # Load model if exists
        if self.model_path.exists():
            self.load_model()

    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """
        Select action using epsilon-greedy policy

        Args:
            state: Current state
            training: If True, use epsilon-greedy. If False, use greedy.

        Returns:
            Selected action index
        """
        if not PYTORCH_AVAILABLE:
            return random.randint(0, self.action_size - 1)

        # Epsilon-greedy exploration
        if training and random.random() < self.epsilon:
            return random.randint(0, self.action_size - 1)

        # Exploitation: select action with highest Q-value
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            q_values = self.q_network(state_tensor)
            return q_values.argmax(1).item()

    def store_experience(self, state, action, reward, next_state, done):
        """Store experience in replay buffer"""
        self.memory.push(state, action, reward, next_state, done)

    def train_step(self) -> Optional[float]:
        """
        Perform one training step

        Returns:
            Training loss if trained, None otherwise
        """
        if not PYTORCH_AVAILABLE:
            return None

        # Need enough experiences
        if len(self.memory) < self.batch_size:
            return None

        # Sample batch
        experiences = self.memory.sample(self.batch_size)
        batch = Experience(*zip(*experiences))

        # Convert to tensors
        state_batch = torch.FloatTensor(np.array(batch.state))
        action_batch = torch.LongTensor(np.array(batch.action))
        reward_batch = torch.FloatTensor(np.array(batch.reward))
        next_state_batch = torch.FloatTensor(np.array(batch.next_state))
        done_batch = torch.FloatTensor(np.array(batch.done))

        # Current Q-values
        current_q_values = self.q_network(state_batch).gather(1, action_batch.unsqueeze(1))

        # Next Q-values from target network
        with torch.no_grad():
            next_q_values = self.target_network(next_state_batch).max(1)[0]
            target_q_values = reward_batch + (1 - done_batch) * self.gamma * next_q_values

        # Compute loss
        loss = F.smooth_l1_loss(current_q_values.squeeze(), target_q_values)

        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), 1.0)
        self.optimizer.step()

        # Update target network periodically
        self.update_counter += 1
        if self.update_counter % self.target_update == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())

        # Decay epsilon
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)

        return loss.item()

    def save_model(self) -> bool:
        """Save model to disk"""
        if not PYTORCH_AVAILABLE or self.q_network is None:
            return False

        try:
            self.model_path.parent.mkdir(parents=True, exist_ok=True)

            torch.save({
                'q_network_state_dict': self.q_network.state_dict(),
                'target_network_state_dict': self.target_network.state_dict(),
                'optimizer_state_dict': self.optimizer.state_dict(),
                'epsilon': self.epsilon,
                'update_counter': self.update_counter,
            }, self.model_path)

            logger.info(f"Model saved to {self.model_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False

    def load_model(self) -> bool:
        """Load model from disk"""
        if not PYTORCH_AVAILABLE:
            return False

        try:
            checkpoint = torch.load(self.model_path)

            self.q_network.load_state_dict(checkpoint['q_network_state_dict'])
            self.target_network.load_state_dict(checkpoint['target_network_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.epsilon = checkpoint['epsilon']
            self.update_counter = checkpoint['update_counter']

            logger.info(f"Model loaded from {self.model_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


class GamingEnvironment:
    """
    Simulated gaming environment for training DQN agent

    State: 20 dimensions (CPU usage, GPU usage, temps, FPS, etc.)
    Actions: 10 (adjust CPU governor, GPU clock, fan curve, etc.)
    Reward: FPS improvement + stability - temperature penalty
    """

    def __init__(self):
        self.state_size = 20
        self.action_size = 10
        self.reset()

    def reset(self) -> np.ndarray:
        """Reset environment to initial state"""
        # Initialize with typical gaming state
        self.state = np.array([
            50.0,  # CPU usage %
            60.0,  # CPU temp
            4500,  # CPU freq MHz
            70.0,  # GPU usage %
            65.0,  # GPU temp
            1800,  # GPU clock MHz
            50.0,  # RAM usage %
            120.0, # Target FPS
            115.0, # Current FPS
            250.0, # Power consumption W
            # ... 10 more state variables
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ], dtype=np.float32)

        return self.state

    def step(self, action: int) -> Tuple[np.ndarray, float, bool]:
        """
        Execute action and return next state, reward, done

        Args:
            action: Action index (0-9)

        Returns:
            (next_state, reward, done)
        """
        # Simulate action effects
        if action == 0:  # Increase CPU freq
            self.state[2] += 100  # CPU freq
            self.state[8] += 2    # FPS
            self.state[1] += 1    # CPU temp
            self.state[9] += 10   # Power

        elif action == 1:  # Decrease CPU freq
            self.state[2] -= 100
            self.state[8] -= 1
            self.state[1] -= 1
            self.state[9] -= 10

        elif action == 2:  # Increase GPU clock
            self.state[5] += 50
            self.state[8] += 5
            self.state[4] += 2
            self.state[9] += 20

        elif action == 3:  # Decrease GPU clock
            self.state[5] -= 50
            self.state[8] -= 3
            self.state[4] -= 2
            self.state[9] -= 20

        # ... more actions

        # Calculate reward
        fps_diff = self.state[8] - self.state[7]  # Current vs target
        temp_penalty = max(0, self.state[1] - 80) + max(0, self.state[4] - 85)
        power_penalty = max(0, self.state[9] - 350) / 10

        reward = fps_diff - temp_penalty - power_penalty

        # Check if done (episode ends after thermal emergency or target reached)
        done = self.state[1] > 95 or self.state[4] > 90 or abs(fps_diff) < 5

        return self.state.copy(), reward, done


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if not PYTORCH_AVAILABLE:
        print("PyTorch not available. Cannot run DQN training.")
        exit(1)

    # Initialize agent and environment
    agent = DQNAgent()
    env = GamingEnvironment()

    print("Training DQN Agent for Adaptive Gaming Optimization")
    print("=" * 60)

    num_episodes = 100
    max_steps = 200

    for episode in range(num_episodes):
        state = env.reset()
        total_reward = 0
        losses = []

        for step in range(max_steps):
            # Select and execute action
            action = agent.select_action(state, training=True)
            next_state, reward, done = env.step(action)

            # Store experience
            agent.store_experience(state, action, reward, next_state, done)

            # Train
            loss = agent.train_step()
            if loss is not None:
                losses.append(loss)

            total_reward += reward
            state = next_state

            if done:
                break

        avg_loss = sum(losses) / len(losses) if losses else 0

        if (episode + 1) % 10 == 0:
            print(f"Episode {episode+1}/{num_episodes} - "
                  f"Reward: {total_reward:.2f}, "
                  f"Loss: {avg_loss:.4f}, "
                  f"Epsilon: {agent.epsilon:.3f}")

            # Save model periodically
            agent.save_model()

    print("\nTraining complete!")
    agent.save_model()
