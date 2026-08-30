"""
rehab_rl/models/networks.py
Deep Neural Network architectures for the Rehabilitation RL Agent.

Implements:
  1. StateEncoder      — embeds categorical + continuous patient features
  2. DuelingQNetwork   — Dueling Double DQN (Wang et al., 2016)
  3. ActorCriticNet    — Shared-backbone PPO Actor-Critic (bonus model)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Tuple

from rehabrl.config import ModelConfig


# ─── Utility layers ────────────────────────────────────────────────────────────


class NoisyLinear(nn.Module):
    """
    Factorised Noisy Linear layer (Fortunato et al., 2017).
    Replaces ε-greedy exploration with learned stochastic weights.
    """

    def __init__(self, in_features: int, out_features: int, sigma_init: float = 0.5):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.sigma_init = sigma_init

        # Learnable parameters
        self.weight_mu = nn.Parameter(torch.empty(out_features, in_features))
        self.weight_sigma = nn.Parameter(torch.empty(out_features, in_features))
        self.bias_mu = nn.Parameter(torch.empty(out_features))
        self.bias_sigma = nn.Parameter(torch.empty(out_features))

        # Noise buffers (not parameters)
        self.register_buffer("weight_eps", torch.empty(out_features, in_features))
        self.register_buffer("bias_eps", torch.empty(out_features))

        self.reset_parameters()
        self.reset_noise()

    def reset_parameters(self):
        mu_range = 1.0 / self.in_features**0.5
        self.weight_mu.data.uniform_(-mu_range, mu_range)
        self.weight_sigma.data.fill_(self.sigma_init / self.in_features**0.5)
        self.bias_mu.data.uniform_(-mu_range, mu_range)
        self.bias_sigma.data.fill_(self.sigma_init / self.out_features**0.5)

    @staticmethod
    def _f(x: torch.Tensor) -> torch.Tensor:
        return x.sign() * x.abs().sqrt()

    def reset_noise(self):
        eps_i = self._f(torch.randn(self.in_features))
        eps_j = self._f(torch.randn(self.out_features))
        self.weight_eps.copy_(eps_j.outer(eps_i))
        self.bias_eps.copy_(eps_j)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.training:
            w = self.weight_mu + self.weight_sigma * self.weight_eps
            b = self.bias_mu + self.bias_sigma * self.bias_eps
        else:
            w, b = self.weight_mu, self.bias_mu
        return F.linear(x, w, b)


class ResidualBlock(nn.Module):
    """Residual MLP block with LayerNorm and GELU activation."""

    def __init__(self, dim: int, dropout: float = 0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim, dim),
            nn.LayerNorm(dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(dim, dim),
            nn.LayerNorm(dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return F.gelu(x + self.net(x))


# ─── State Encoder ─────────────────────────────────────────────────────────────


class StateEncoder(nn.Module):
    """
    Encodes the 28-dim patient state into a rich latent embedding.

    Architecture:
      Input (28)  ──►  Projection (128)  ──►  2× ResidualBlock  ──►  Embedding (128)

    The one-hot categorical features (injury type, recovery stage) are handled
    by the linear projection; no separate embedding table is needed since the
    state vector is already encoded.
    """

    def __init__(
        self, state_dim: int = 28, embed_dim: int = 128, dropout: float = 0.15
    ):
        super().__init__()
        self.embed_dim = embed_dim

        self.projection = nn.Sequential(
            nn.Linear(state_dim, embed_dim),
            nn.LayerNorm(embed_dim),
            nn.GELU(),
        )
        self.blocks = nn.Sequential(
            ResidualBlock(embed_dim, dropout),
            ResidualBlock(embed_dim, dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: (B, state_dim)  →  embedding: (B, embed_dim)"""
        h = self.projection(x)
        return self.blocks(h)


# ─── Dueling Q-Network ──────────────────────────────────────────────────────────


class DuelingQNetwork(nn.Module):
    """
    Dueling Double Deep Q-Network (Wang et al., 2016).

    Separates the Q-value into:
      Q(s,a) = V(s)  +  A(s,a)  −  mean_a A(s,a)

    This allows the network to learn state values independently of
    action advantages — crucial for rehabilitation where many actions
    have similar outcomes at a given recovery stage.

    Architecture:
      StateEncoder  →  Shared trunk  →  ┬─ Value head   V(s)     (1)
                                        └─ Advantage head A(s,a)  (N_actions)
    """

    def __init__(self, cfg: ModelConfig):
        super().__init__()
        self.n_actions = cfg.n_actions

        # Shared state encoder
        embed_dim = 128
        self.encoder = StateEncoder(cfg.state_dim, embed_dim, cfg.dropout)

        # Shared trunk MLP
        trunk_layers = []
        prev = embed_dim
        for hdim in cfg.hidden_dims:
            trunk_layers += [
                nn.Linear(prev, hdim),
                nn.LayerNorm(hdim),
                nn.GELU(),
                nn.Dropout(cfg.dropout),
            ]
            prev = hdim
        self.trunk = nn.Sequential(*trunk_layers)

        # Value stream: scalar state value V(s)
        self.value_head = nn.Sequential(
            nn.Linear(prev, 128),
            nn.GELU(),
            nn.Linear(128, 1),
        )

        # Advantage stream: per-action advantages A(s, a)
        self.adv_head = nn.Sequential(
            nn.Linear(prev, 128),
            nn.GELU(),
            nn.Linear(128, cfg.n_actions),
        )

        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.orthogonal_(m.weight, gain=np.sqrt(2))
                nn.init.zeros_(m.bias)

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        state: (B, state_dim) float32
        returns: Q-values (B, n_actions)
        """
        h = self.encoder(state)
        h = self.trunk(h)

        V = self.value_head(h)  # (B, 1)
        A = self.adv_head(h)  # (B, n_actions)
        Q = V + (A - A.mean(dim=1, keepdim=True))  # dueling aggregation
        return Q

    def get_action(self, state: torch.Tensor) -> int:
        """Greedy action selection (argmax Q)."""
        with torch.no_grad():
            q = self.forward(state.unsqueeze(0))
            return int(q.argmax(dim=1).item())

    def get_q_values(self, state: torch.Tensor) -> np.ndarray:
        """Return Q-values as numpy array for analysis."""
        with torch.no_grad():
            return self.forward(state.unsqueeze(0)).squeeze(0).cpu().numpy()

    @property
    def n_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


# ─── Actor-Critic Network (PPO) ─────────────────────────────────────────────────


class ActorCriticNet(nn.Module):
    """
    Shared-backbone Actor-Critic for Proximal Policy Optimization (PPO).

    Encoder → Shared trunk → ┬─ Actor head  (policy logits)
                              └─ Critic head (state value)
    """

    def __init__(self, cfg: ModelConfig):
        super().__init__()
        embed_dim = 128

        self.encoder = StateEncoder(cfg.state_dim, embed_dim, cfg.dropout)

        shared_layers = []
        prev = embed_dim
        for hdim in cfg.hidden_dims[:2]:
            shared_layers += [nn.Linear(prev, hdim), nn.Tanh()]
            prev = hdim
        self.shared = nn.Sequential(*shared_layers)

        self.actor = nn.Linear(prev, cfg.n_actions)
        self.critic = nn.Linear(prev, 1)

        self._init_weights()

    def _init_weights(self):
        nn.init.orthogonal_(self.actor.weight, gain=0.01)
        nn.init.orthogonal_(self.critic.weight, gain=1.0)
        for m in self.modules():
            if isinstance(m, nn.Linear) and m not in (self.actor, self.critic):
                nn.init.orthogonal_(m.weight, gain=np.sqrt(2))
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, state: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Returns (logits, value)."""
        h = self.shared(self.encoder(state))
        return self.actor(h), self.critic(h)

    def get_action_and_value(
        self, state: torch.Tensor, action: torch.Tensor = None
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        logits, value = self.forward(state)
        dist = torch.distributions.Categorical(logits=logits)
        if action is None:
            action = dist.sample()
        log_prob = dist.log_prob(action)
        entropy = dist.entropy()
        return action, log_prob, entropy, value.squeeze(-1)

    @property
    def n_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


# ─── Model factory ─────────────────────────────────────────────────────────────


def build_dqn(cfg: ModelConfig) -> Tuple[DuelingQNetwork, DuelingQNetwork]:
    """Build online and target DQN networks (identical architecture)."""
    online = DuelingQNetwork(cfg)
    target = DuelingQNetwork(cfg)
    target.load_state_dict(online.state_dict())
    target.requires_grad_(False)
    return online, target


def build_actor_critic(cfg: ModelConfig) -> ActorCriticNet:
    return ActorCriticNet(cfg)
