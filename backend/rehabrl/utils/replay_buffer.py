"""
rehab_rl/utils/replay_buffer.py
Prioritized Experience Replay (PER) with Sum-Tree data structure.
Based on Schaul et al. (2015) "Prioritized Experience Replay".
"""

import numpy as np
from typing import Tuple, NamedTuple


class Transition(NamedTuple):
    state: np.ndarray  # (state_dim,)
    action: int
    reward: float
    next_state: np.ndarray  # (state_dim,)
    done: bool


class SumTree:
    """
    Binary sum tree for O(log N) priority sampling.
    Leaf nodes store transition priorities; internal nodes store sums.
    The internal tree is padded to a power of two, while data indices retain
    the caller's original capacity.
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.data_capacity = capacity
        # Round up to next power of two
        self.capacity = 1
        while self.capacity < capacity:
            self.capacity <<= 1
        self.tree = np.zeros(2 * self.capacity, dtype=np.float64)
        self.n_entries = 0

    # ── Internal updates ────────────────────────────────────────────────
    def _propagate(self, idx: int, delta: float):
        parent = idx >> 1
        while parent >= 1:
            self.tree[parent] += delta
            parent >>= 1

    def _retrieve(self, idx: int, s: float) -> int:
        """Traverse tree to find leaf satisfying prefix sum = s."""
        while True:
            left = 2 * idx
            right = left + 1
            if left >= len(self.tree):
                return idx
            if s < self.tree[left]:
                idx = left
            else:
                s -= self.tree[left]
                idx = right

    # ── Public API ──────────────────────────────────────────────────────
    @property
    def total(self) -> float:
        return float(self.tree[1])

    def add(self, priority: float, data_idx: int):
        """Store priority for data at data_idx."""
        if not 0 <= data_idx < self.data_capacity:
            raise IndexError(f"data_idx {data_idx} outside buffer capacity")

        leaf = self.capacity + data_idx
        delta = priority - self.tree[leaf]
        self.tree[leaf] = priority
        self._propagate(leaf, delta)
        self.n_entries = min(self.n_entries + 1, self.data_capacity)

    def update(self, leaf_idx: int, priority: float):
        delta = priority - self.tree[leaf_idx]
        self.tree[leaf_idx] = priority
        self._propagate(leaf_idx, delta)

    def sample(self, s: float) -> Tuple[int, float, int]:
        """
        Sample a transition whose priority covers value s.
        Returns (leaf_idx, priority, data_idx).
        """
        leaf_idx = self._retrieve(1, s)
        data_idx = leaf_idx - self.capacity
        return leaf_idx, float(self.tree[leaf_idx]), data_idx


class PrioritizedReplayBuffer:
    """
    Prioritized Experience Replay buffer.

    Transitions are sampled proportional to their TD-error priority,
    corrected by importance-sampling weights to reduce bias.

    Usage:
        buf = PrioritizedReplayBuffer(capacity=20_000, alpha=0.6, beta=0.4)
        buf.push(state, action, reward, next_state, done)
        states, actions, rewards, next_states, dones, weights, idxs = buf.sample(128)
        buf.update_priorities(idxs, td_errors)
    """

    def __init__(
        self,
        capacity: int = 20_000,
        alpha: float = 0.6,  # prioritisation strength (0 = uniform)
        beta: float = 0.4,  # IS correction strength (1 = fully corrected)
        beta_inc: float = 2e-4,  # beta annealing per sample call
        eps: float = 1e-6,  # priority floor
        state_dim: int = 28,
        min_size: int = 512,
    ):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if min_size <= 0:
            raise ValueError("min_size must be positive")

        self.capacity = capacity
        self.alpha = alpha
        self.beta = beta
        self.beta_inc = beta_inc
        self.eps = eps
        self.min_size = min_size

        self.tree = SumTree(capacity)
        # Maximum raw priority. The alpha exponent is applied only when a
        # value is inserted into the tree.
        self._max_priority: float = 1.0

        # Pre-allocated arrays for efficiency
        self.states = np.zeros((capacity, state_dim), dtype=np.float32)
        self.actions = np.zeros(capacity, dtype=np.int64)
        self.rewards = np.zeros(capacity, dtype=np.float32)
        self.next_states = np.zeros((capacity, state_dim), dtype=np.float32)
        self.dones = np.zeros(capacity, dtype=np.float32)

        self.write = 0
        self.size = 0

    # ── Push ────────────────────────────────────────────────────────────
    def push(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
    ):
        idx = self.write % self.capacity
        self.states[idx] = state
        self.actions[idx] = action
        self.rewards[idx] = reward
        self.next_states[idx] = next_state
        self.dones[idx] = float(done)

        priority = self._max_priority**self.alpha
        self.tree.add(priority, idx)

        self.write = (self.write + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)

    # ── Sample ─────────────────────────────────────────────────────────
    def sample(
        self, batch_size: int
    ) -> Tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
    ]:
        """
        Returns:
          states, actions, rewards, next_states, dones  — batch tensors
          weights  — IS correction weights (normalised to [0,1])
          leaf_idxs — needed for priority updates
        """
        assert self.size >= batch_size, "Not enough transitions to sample."
        self.beta = min(1.0, self.beta + self.beta_inc)

        leaf_idxs = np.empty(batch_size, dtype=np.int64)
        data_idxs = np.empty(batch_size, dtype=np.int64)
        priorities = np.empty(batch_size, dtype=np.float64)

        total = self.tree.total
        segment = total / batch_size

        for i in range(batch_size):
            s = np.random.uniform(segment * i, segment * (i + 1))
            leaf_idx, priority, data_idx = self.tree.sample(s)
            leaf_idxs[i] = leaf_idx
            data_idxs[i] = data_idx
            priorities[i] = priority + self.eps

        probs = priorities / (total + 1e-10)
        weights = (self.size * probs) ** (-self.beta)
        weights = (weights / weights.max()).astype(np.float32)

        return (
            self.states[data_idxs],
            self.actions[data_idxs],
            self.rewards[data_idxs],
            self.next_states[data_idxs],
            self.dones[data_idxs],
            weights,
            leaf_idxs,
        )

    # ── Priority update ─────────────────────────────────────────────────
    def update_priorities(self, leaf_idxs: np.ndarray, td_errors: np.ndarray):
        """Update priorities from new TD errors after a gradient step."""
        for idx, err in zip(leaf_idxs, td_errors):
            raw_priority = float(abs(err)) + self.eps
            self._max_priority = max(self._max_priority, raw_priority)
            self.tree.update(int(idx), raw_priority**self.alpha)

    def __len__(self) -> int:
        return self.size

    @property
    def is_ready(self) -> bool:
        return self.size >= self.min_size
