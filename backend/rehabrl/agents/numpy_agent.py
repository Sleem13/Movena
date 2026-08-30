"""
rehab_rl/agents/numpy_agent.py
Self-contained Double Dueling DQN agent — pure NumPy, no PyTorch required.
Same interface as DQNAgent so the Trainer/App can swap between them.
"""

import os
import numpy as np
from typing import Optional, List, Dict

from rehabrl.config import Config
from rehabrl.models.numpy_networks import build_numpy_dqn
from rehabrl.utils.replay_buffer import PrioritizedReplayBuffer


class NumpyDQNAgent:
    """
    Double Dueling DQN agent implemented entirely in NumPy.

    Algorithm:
      1. ε-greedy action selection with valid-action masking
      2. Store (s, a, r, s', done) in Prioritised Experience Replay
      3. Sample mini-batch; compute Double DQN targets
      4. Compute Huber loss; backpropagate through Dueling network
      5. Adam gradient update (manual)
      6. Soft-update target network: θ_target ← τ·θ_online + (1-τ)·θ_target
    """

    checkpoint_extension = ".npy"

    def __init__(self, cfg: Optional[Config] = None, seed: int = 42):
        self.cfg = cfg or Config()
        self.mcfg = self.cfg.model
        self.tcfg = self.cfg.training
        self.rng = np.random.default_rng(seed)

        # ── Networks ─────────────────────────────────────────────────────
        self.online_net, self.target_net = build_numpy_dqn(
            state_dim=self.mcfg.state_dim,
            n_actions=self.mcfg.n_actions,
            hidden_dims=self.mcfg.hidden_dims,
            seed=seed,
        )

        # ── Replay buffer ─────────────────────────────────────────────────
        self.buffer = PrioritizedReplayBuffer(
            capacity=self.tcfg.buffer_size,
            alpha=self.tcfg.per_alpha,
            beta=self.tcfg.per_beta_start,
            beta_inc=(self.tcfg.per_beta_end - self.tcfg.per_beta_start)
            / max(1, self.tcfg.n_episodes * self.tcfg.max_steps),
            state_dim=self.mcfg.state_dim,
            min_size=max(self.tcfg.min_buffer, self.tcfg.batch_size),
        )

        # ── Exploration ───────────────────────────────────────────────────
        self.epsilon = self.tcfg.eps_start
        self.total_steps = 0
        self.episodes = 0
        self.adam_t = 0  # Adam global step counter

        # ── Diagnostics ───────────────────────────────────────────────────
        self.losses: List[float] = []
        self.q_values: List[float] = []

    # ── Action selection ──────────────────────────────────────────────────────

    def act(
        self,
        state: np.ndarray,
        valid_actions: Optional[List[int]] = None,
        training: bool = True,
    ) -> int:
        """ε-greedy with optional action masking for valid recovery-stage actions."""
        if training and self.rng.random() < self.epsilon:
            if valid_actions:
                return int(self.rng.choice(valid_actions))
            return int(self.rng.integers(self.mcfg.n_actions))

        q_vals = self.online_net.forward(state.reshape(1, -1)).flatten()

        if valid_actions is not None:
            mask = np.full(self.mcfg.n_actions, -np.inf)
            mask[valid_actions] = q_vals[valid_actions]
            return int(np.argmax(mask))
        return int(np.argmax(q_vals))

    def act_with_info(
        self,
        state: np.ndarray,
        valid_actions: Optional[List[int]] = None,
    ) -> tuple:
        """Returns (action, q_values_array) — useful for inspection/UI."""
        q_vals = self.online_net.forward(state.reshape(1, -1)).flatten()
        if valid_actions is not None:
            mask = np.full(self.mcfg.n_actions, -np.inf)
            mask[valid_actions] = q_vals[valid_actions]
            return int(np.argmax(mask)), q_vals
        return int(np.argmax(q_vals)), q_vals

    # ── Memory ────────────────────────────────────────────────────────────────

    def remember(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
    ):
        self.buffer.push(state, action, reward, next_state, done)
        self.total_steps += 1

    # ── Learning step ─────────────────────────────────────────────────────────

    def learn(self) -> Optional[float]:
        """
        One gradient update step.
        Returns the scalar loss (or None if buffer not ready).
        """
        if not self.buffer.is_ready:
            return None

        (states, actions, rewards, next_states, dones, is_weights, leaf_idxs) = (
            self.buffer.sample(self.tcfg.batch_size)
        )

        B = len(states)

        # ── Current Q-values ─────────────────────────────────────────────
        Q_all = self.online_net.forward(states)  # (B, N)
        Q_current = Q_all[np.arange(B), actions]  # (B,)

        # ── Double DQN target ─────────────────────────────────────────────
        # Online net chooses the next action; target net evaluates it
        Q_next_online = self.online_net.forward(next_states)
        next_actions = Q_next_online.argmax(axis=1)  # (B,)

        Q_next_target = self.target_net.forward(next_states)
        Q_next = Q_next_target[np.arange(B), next_actions]  # (B,)

        target = rewards + self.tcfg.gamma * Q_next * (1.0 - dones)  # (B,)

        # ── Huber loss with IS weights ────────────────────────────────────
        td_errors = (target - Q_current).astype(np.float32)  # (B,)
        huber_loss = np.where(
            np.abs(td_errors) < 1.0,
            0.5 * td_errors**2,
            np.abs(td_errors) - 0.5,
        )
        loss = float((is_weights * huber_loss).mean())

        # ── Gradient of loss w.r.t Q-values ──────────────────────────────
        # dL/dQ_a = −is_weight * huber_grad  (zero for non-selected actions)
        huber_grad = np.where(
            np.abs(td_errors) < 1.0,
            -td_errors,
            -np.sign(td_errors),
        )
        grad_Q = np.zeros((B, self.mcfg.n_actions), dtype=np.float32)
        grad_Q[np.arange(B), actions] = (is_weights * huber_grad) / B

        # ── Backward + Adam update ────────────────────────────────────────
        self.online_net.backward(grad_Q)
        self.adam_t += 1
        self.online_net.adam_update(self.adam_t, lr=self.tcfg.lr)

        # ── Soft target update (Polyak averaging) ─────────────────────────
        self.target_net.polyak_copy_from(self.online_net, tau=self.tcfg.tau)

        # ── Update PER priorities ─────────────────────────────────────────
        self.buffer.update_priorities(leaf_idxs, np.abs(td_errors))

        # ── ε decay ──────────────────────────────────────────────────────
        self.epsilon = max(self.tcfg.eps_end, self.epsilon * self.tcfg.eps_decay)

        self.losses.append(loss)
        self.q_values.append(float(Q_current.mean()))
        return loss

    def end_episode(self):
        self.episodes += 1

    # ── Persistence ───────────────────────────────────────────────────────────

    def save(self, path: str):
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        payload = {
            "online": self.online_net.get_weights(),
            "target": self.target_net.get_weights(),
            "epsilon": self.epsilon,
            "total_steps": self.total_steps,
            "episodes": self.episodes,
            "adam_t": self.adam_t,
            "losses": self.losses[-2000:],
            "q_values": self.q_values[-2000:],
        }
        # Passing a file handle prevents np.save from silently appending
        # another ".npy" suffix to caller-provided checkpoint paths.
        with open(path, "wb") as checkpoint_file:
            np.save(checkpoint_file, payload, allow_pickle=True)

    def load(self, path: str):
        data = np.load(path, allow_pickle=True).item()
        self.online_net.set_weights(data["online"])
        self.target_net.set_weights(data["target"])
        self.epsilon = data.get("epsilon", self.tcfg.eps_end)
        self.total_steps = data.get("total_steps", 0)
        self.episodes = data.get("episodes", 0)
        self.adam_t = data.get("adam_t", 0)
        self.losses = list(data.get("losses", []))
        self.q_values = list(data.get("q_values", []))

    # ── Diagnostics ───────────────────────────────────────────────────────────

    def get_stats(self) -> Dict:
        n = min(100, max(1, len(self.losses)))
        return {
            "backend": "numpy",
            "device": "cpu",
            "episodes": self.episodes,
            "total_steps": self.total_steps,
            "epsilon": round(self.epsilon, 4),
            "buffer_size": len(self.buffer),
            "mean_loss": round(float(np.mean(self.losses[-n:])), 5)
            if self.losses
            else 0.0,
            "mean_q": round(float(np.mean(self.q_values[-n:])), 4)
            if self.q_values
            else 0.0,
            "lr": self.tcfg.lr,
            "n_params": self.online_net.n_params,
        }
