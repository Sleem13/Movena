"""
rehab_rl/agents/dqn_agent.py
Double Dueling DQN agent with Prioritized Experience Replay.

Key features:
  • Double DQN       — action selection by online net, evaluation by target net
  • Dueling heads    — separate value / advantage streams (in networks.py)
  • PER              — prioritised sampling by TD error
  • Soft target update — Polyak averaging every step
  • ε-greedy decay   — with action masking for valid stage actions
"""

import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Optional, List, Tuple, Dict

# Allow running from project root
from rehabrl.config import Config
from rehabrl.models.networks import build_dqn
from rehabrl.utils.replay_buffer import PrioritizedReplayBuffer


def cuda_is_available() -> bool:
    """Return whether the installed PyTorch runtime can use CUDA."""
    return torch.cuda.is_available()


def resolve_torch_device(requested: str | None = "auto") -> torch.device:
    """Resolve an explicit device or automatically select CUDA with CPU fallback."""
    if requested in {None, "auto"}:
        return torch.device("cuda" if cuda_is_available() else "cpu")

    device = torch.device(requested)
    if device.type == "cuda" and not cuda_is_available():
        raise RuntimeError("CUDA was requested but no CUDA device is available")
    return device


class DQNAgent:
    """
    Rehabilitation RL Agent using Double Dueling DQN with PER.

    The agent learns a policy π(s) → a that maximises cumulative
    discounted reward over the patient's recovery trajectory.
    """

    checkpoint_extension = ".pt"

    def __init__(self, cfg: Optional[Config] = None, device: str = "auto"):
        self.cfg = cfg or Config()
        self.mcfg = self.cfg.model
        self.tcfg = self.cfg.training
        self.device = resolve_torch_device(device)

        # ── Networks ────────────────────────────────────────────────────
        self.online_net, self.target_net = build_dqn(self.mcfg)
        self.online_net.to(self.device)
        self.target_net.to(self.device)
        self.target_net.eval()

        # ── Optimiser ────────────────────────────────────────────────────
        self.optimizer = optim.Adam(
            self.online_net.parameters(),
            lr=self.tcfg.lr,
            eps=1e-5,
        )
        self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer,
            T_max=self.tcfg.n_episodes,
            eta_min=self.tcfg.lr * 0.1,
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

        # ── Metrics ───────────────────────────────────────────────────────
        self.losses: List[float] = []
        self.q_values: List[float] = []

    # ── Action selection ──────────────────────────────────────────────────────

    def act(
        self,
        state: np.ndarray,
        valid_actions: Optional[List[int]] = None,
        training: bool = True,
    ) -> int:
        """
        ε-greedy action selection with optional action masking.
        During evaluation (training=False) always acts greedily.
        """
        if training and np.random.random() < self.epsilon:
            if valid_actions:
                return int(np.random.choice(valid_actions))
            return int(np.random.randint(self.mcfg.n_actions))

        state_t = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        self.online_net.eval()
        with torch.no_grad():
            q_vals = self.online_net(state_t).squeeze(0).cpu().numpy()
        self.online_net.train()

        # Mask invalid actions with -∞
        if valid_actions is not None:
            mask = np.full(self.mcfg.n_actions, -np.inf)
            mask[valid_actions] = q_vals[valid_actions]
            q_vals = mask

        return int(np.argmax(q_vals))

    def act_with_info(
        self,
        state: np.ndarray,
        valid_actions: Optional[List[int]] = None,
    ) -> Tuple[int, np.ndarray]:
        """Returns (action, q_values_array) for inspection."""
        state_t = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        self.online_net.eval()
        with torch.no_grad():
            q_vals = self.online_net(state_t).squeeze(0).cpu().numpy()
        self.online_net.train()

        if valid_actions is not None:
            mask = np.full(self.mcfg.n_actions, -np.inf)
            mask[valid_actions] = q_vals[valid_actions]
            action = int(np.argmax(mask))
        else:
            action = int(np.argmax(q_vals))
        return action, q_vals

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
        Sample a mini-batch from PER and perform one gradient step.
        Returns the mean loss (or None if buffer not ready).
        """
        if not self.buffer.is_ready:
            return None

        (states, actions, rewards, next_states, dones, is_weights, leaf_idxs) = (
            self.buffer.sample(self.tcfg.batch_size)
        )

        # Convert to tensors
        states_t = torch.FloatTensor(states).to(self.device)
        actions_t = torch.LongTensor(actions).to(self.device)
        rewards_t = torch.FloatTensor(rewards).to(self.device)
        next_states_t = torch.FloatTensor(next_states).to(self.device)
        dones_t = torch.FloatTensor(dones).to(self.device)
        weights_t = torch.FloatTensor(is_weights).to(self.device)

        # ── Current Q-values ─────────────────────────────────────────────
        current_q = (
            self.online_net(states_t).gather(1, actions_t.unsqueeze(1)).squeeze(1)
        )

        # ── Double DQN target ─────────────────────────────────────────────
        with torch.no_grad():
            # Online net selects action, target net evaluates it
            next_actions = self.online_net(next_states_t).argmax(dim=1)
            next_q_target = (
                self.target_net(next_states_t)
                .gather(1, next_actions.unsqueeze(1))
                .squeeze(1)
            )
            target_q = rewards_t + self.tcfg.gamma * next_q_target * (1 - dones_t)

        # ── PER-weighted Huber loss ───────────────────────────────────────
        td_errors = (target_q - current_q).detach().cpu().numpy()
        loss = (weights_t * nn.HuberLoss(reduction="none")(current_q, target_q)).mean()

        # ── Gradient step ─────────────────────────────────────────────────
        self.optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.online_net.parameters(), self.tcfg.grad_clip)
        self.optimizer.step()

        # ── Update priorities ─────────────────────────────────────────────
        self.buffer.update_priorities(leaf_idxs, np.abs(td_errors))

        # ── Soft target update ────────────────────────────────────────────
        self._soft_update()

        # ── Epsilon decay ─────────────────────────────────────────────────
        self.epsilon = max(self.tcfg.eps_end, self.epsilon * self.tcfg.eps_decay)

        loss_val = float(loss.item())
        q_mean = float(current_q.mean().item())
        self.losses.append(loss_val)
        self.q_values.append(q_mean)
        return loss_val

    def _soft_update(self):
        """Polyak averaging: θ_target ← τ·θ_online + (1-τ)·θ_target."""
        tau = self.tcfg.tau
        for p_target, p_online in zip(
            self.target_net.parameters(), self.online_net.parameters()
        ):
            p_target.data.copy_(tau * p_online.data + (1 - tau) * p_target.data)

    def end_episode(self):
        """Call at the end of each episode."""
        self.episodes += 1
        if self.losses:
            self.scheduler.step()

    # ── Save / Load ───────────────────────────────────────────────────────────

    def save(self, path: str):
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        torch.save(
            {
                "online_state_dict": self.online_net.state_dict(),
                "target_state_dict": self.target_net.state_dict(),
                "optimizer": self.optimizer.state_dict(),
                "epsilon": self.epsilon,
                "total_steps": self.total_steps,
                "episodes": self.episodes,
                "losses": self.losses[-1000:],
                "q_values": self.q_values[-1000:],
            },
            path,
        )

    def load(self, path: str):
        ckpt = torch.load(path, map_location=self.device, weights_only=True)
        self.online_net.load_state_dict(ckpt["online_state_dict"])
        self.target_net.load_state_dict(ckpt["target_state_dict"])
        self.optimizer.load_state_dict(ckpt["optimizer"])
        self.epsilon = ckpt.get("epsilon", self.tcfg.eps_end)
        self.total_steps = ckpt.get("total_steps", 0)
        self.episodes = ckpt.get("episodes", 0)
        self.losses = ckpt.get("losses", [])
        self.q_values = ckpt.get("q_values", [])

    # ── Diagnostics ───────────────────────────────────────────────────────────

    def get_stats(self) -> Dict:
        recent = 100
        return {
            "backend": "pytorch",
            "device": str(self.device),
            "episodes": self.episodes,
            "total_steps": self.total_steps,
            "epsilon": round(self.epsilon, 4),
            "buffer_size": len(self.buffer),
            "mean_loss": round(float(np.mean(self.losses[-recent:])), 4)
            if self.losses
            else 0.0,
            "mean_q": round(float(np.mean(self.q_values[-recent:])), 4)
            if self.q_values
            else 0.0,
            "lr": round(self.optimizer.param_groups[0]["lr"], 6),
            "n_params": self.online_net.n_parameters,
        }
