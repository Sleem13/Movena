"""
rehab_rl/models/numpy_networks.py
Pure NumPy implementation of the Dueling DQN.

Implements full forward + backward pass manually — no PyTorch required.
Educational deep dive into how neural networks actually work under the hood.

Architecture:
  StateEncoder  →  Shared Trunk  →  Value Head  V(s)   (scalar)
                                →  Adv Head    A(s,a)  (N-dim)
  Q(s,a) = V(s) + A(s,a) − mean_a A(s,a)   ← Dueling aggregation
"""

import numpy as np
from typing import List, Optional, Tuple


# ─── Single Layer ─────────────────────────────────────────────────────────────


class DenseLayer:
    """
    Fully-connected layer with ReLU or linear activation.
    Maintains its own Adam optimizer state.
    """

    def __init__(
        self,
        in_dim: int,
        out_dim: int,
        activation: str = "relu",  # "relu" | "gelu" | "linear"
        seed: int = 0,
    ):
        rng = np.random.default_rng(seed)
        scale = np.sqrt(2.0 / in_dim)  # He (Kaiming) initialisation

        self.W = (rng.standard_normal((in_dim, out_dim)) * scale).astype(np.float32)
        self.b = np.zeros(out_dim, dtype=np.float32)
        self.act = activation

        # Adam momentum & variance accumulators
        self.mW = np.zeros_like(self.W)
        self.vW = np.zeros_like(self.W)
        self.mb = np.zeros_like(self.b)
        self.vb = np.zeros_like(self.b)

        # Saved for backward pass
        self._x_in: Optional[np.ndarray] = None
        self._z: Optional[np.ndarray] = None
        self.dW: Optional[np.ndarray] = None
        self.db: Optional[np.ndarray] = None

    # ── Forward ─────────────────────────────────────────────────────────
    def forward(self, x: np.ndarray) -> np.ndarray:
        """x: (B, in_dim) → out: (B, out_dim)"""
        self._x_in = x
        self._z = x @ self.W + self.b
        return self._activate(self._z)

    def _activate(self, z: np.ndarray) -> np.ndarray:
        if self.act == "relu":
            return np.maximum(0.0, z)
        if self.act == "gelu":
            c = np.sqrt(2.0 / np.pi)
            return 0.5 * z * (1.0 + np.tanh(c * (z + 0.044715 * z**3)))
        return z  # linear

    def _activate_grad(self, grad: np.ndarray) -> np.ndarray:
        if self.act == "relu":
            return grad * (self._z > 0.0).astype(np.float32)
        if self.act == "gelu":
            c = np.sqrt(2.0 / np.pi)
            t = np.tanh(c * (self._z + 0.044715 * self._z**3))
            dt = (1.0 - t**2) * c * (1.0 + 3 * 0.044715 * self._z**2)
            g = 0.5 * (1.0 + t) + 0.5 * self._z * dt
            return grad * g
        return grad  # linear — identity

    # ── Backward ────────────────────────────────────────────────────────
    def backward(self, grad_out: np.ndarray) -> np.ndarray:
        """
        grad_out: (B, out_dim)  ← gradient of loss w.r.t. this layer's output
        Returns gradient w.r.t. this layer's input (B, in_dim).
        Accumulates dW, db for use in update().
        """
        grad_z = self._activate_grad(grad_out)  # through activation
        self.dW = self._x_in.T @ grad_z  # (in, out)
        self.db = grad_z.sum(axis=0)  # (out,)
        return grad_z @ self.W.T  # (B, in_dim)

    # ── Adam update ──────────────────────────────────────────────────────
    def adam_update(
        self,
        t: int,
        lr: float = 3e-4,
        beta1: float = 0.9,
        beta2: float = 0.999,
        eps: float = 1e-8,
        clip: float = 1.0,  # gradient clipping norm
    ):
        # Clip gradients
        gnorm = np.sqrt((self.dW**2).sum() + (self.db**2).sum())
        if gnorm > clip:
            self.dW *= clip / gnorm
            self.db *= clip / gnorm

        self.mW = beta1 * self.mW + (1 - beta1) * self.dW
        self.vW = beta2 * self.vW + (1 - beta2) * self.dW**2
        self.mb = beta1 * self.mb + (1 - beta1) * self.db
        self.vb = beta2 * self.vb + (1 - beta2) * self.db**2

        bc1 = 1 - beta1**t
        bc2 = 1 - beta2**t

        self.W -= lr * (self.mW / bc1) / (np.sqrt(self.vW / bc2) + eps)
        self.b -= lr * (self.mb / bc1) / (np.sqrt(self.vb / bc2) + eps)

    # ── Weight copy (for target network) ────────────────────────────────
    def polyak_copy_from(self, src: "DenseLayer", tau: float = 1.0):
        """θ_self ← τ·θ_src + (1−τ)·θ_self"""
        self.W = (tau * src.W + (1 - tau) * self.W).copy()
        self.b = (tau * src.b + (1 - tau) * self.b).copy()

    @property
    def n_params(self) -> int:
        return self.W.size + self.b.size


# ─── MLP (stack of DenseLayer) ────────────────────────────────────────────────


class MLP:
    """Simple sequential MLP. Hidden layers use GELU; output uses linear."""

    def __init__(self, sizes: List[int], seed: int = 0):
        self.layers: List[DenseLayer] = []
        for i in range(len(sizes) - 1):
            act = "gelu" if i < len(sizes) - 2 else "linear"
            self.layers.append(DenseLayer(sizes[i], sizes[i + 1], act, seed + i * 17))

    def forward(self, x: np.ndarray) -> np.ndarray:
        for layer in self.layers:
            x = layer.forward(x)
        return x

    def backward(self, grad: np.ndarray) -> np.ndarray:
        for layer in reversed(self.layers):
            grad = layer.backward(grad)
        return grad

    def adam_update(self, t: int, lr: float, **kw):
        for layer in self.layers:
            layer.adam_update(t, lr, **kw)

    def polyak_copy_from(self, src: "MLP", tau: float = 1.0):
        for sl, ol in zip(self.layers, src.layers):
            sl.polyak_copy_from(ol, tau)

    @property
    def n_params(self) -> int:
        return sum(layer.n_params for layer in self.layers)


# ─── Dueling Q-Network ────────────────────────────────────────────────────────


class DuelingQNetworkNumpy:
    """
    Dueling DQN in pure NumPy.

    Forward:
      h   = trunk(state)
      V   = val_head(h)          shape (B, 1)
      A   = adv_head(h)          shape (B, N)
      Q   = V + A − mean_a(A)

    Backward (Dueling gradients):
      ∂L/∂V_i   = Σ_j ∂L/∂Q_j          (sum across actions)
      ∂L/∂A_i   = ∂L/∂Q_i − mean_j(∂L/∂Q_j)

    Both heads share the trunk output h — their gradients are summed.
    """

    def __init__(
        self,
        state_dim: int,
        n_actions: int,
        hidden_dims: List[int] = None,
        seed: int = 42,
    ):
        hidden_dims = hidden_dims or [256, 256, 128]
        self.n_actions = n_actions

        trunk_sizes = [state_dim] + hidden_dims
        self.trunk = MLP(trunk_sizes, seed=seed)
        self.val_head = MLP([hidden_dims[-1], 128, 1], seed=seed + 1000)
        self.adv_head = MLP([hidden_dims[-1], 128, n_actions], seed=seed + 2000)

    # ── Forward ─────────────────────────────────────────────────────────
    def forward(self, x: np.ndarray) -> np.ndarray:
        """x: (B, state_dim) → Q: (B, n_actions)"""
        self._h = self.trunk.forward(x)  # (B, H)
        V = self.val_head.forward(self._h)  # (B, 1)
        A = self.adv_head.forward(self._h)  # (B, N)
        return V + (A - A.mean(axis=1, keepdims=True))

    # ── Backward ────────────────────────────────────────────────────────
    def backward(self, grad_Q: np.ndarray):
        """
        grad_Q: (B, N)  — gradient of loss w.r.t. Q-values.
        Updates internal gradients; call adam_update() afterwards.
        """
        # Dueling gradient decomposition
        grad_V = grad_Q.sum(axis=1, keepdims=True)  # (B, 1)
        grad_A = grad_Q - grad_Q.mean(axis=1, keepdims=True)  # (B, N)

        grad_h_val = self.val_head.backward(grad_V)  # (B, H)
        grad_h_adv = self.adv_head.backward(grad_A)  # (B, H)

        grad_h = grad_h_val + grad_h_adv
        self.trunk.backward(grad_h)

    # ── Adam update ──────────────────────────────────────────────────────
    def named_parameters(self):
        """Yield (name, numpy array) pairs for all learnable parameters.
        Mimics PyTorch's nn.Module.named_parameters for compatibility with UI.
        """
        # Trunk layers
        for i, layer in enumerate(self.trunk.layers):
            yield (f"trunk.layer{i}.W", layer.W)
            yield (f"trunk.layer{i}.b", layer.b)
        # Value head layers
        for i, layer in enumerate(self.val_head.layers):
            yield (f"val_head.layer{i}.W", layer.W)
            yield (f"val_head.layer{i}.b", layer.b)
        # Advantage head layers
        for i, layer in enumerate(self.adv_head.layers):
            yield (f"adv_head.layer{i}.W", layer.W)
            yield (f"adv_head.layer{i}.b", layer.b)

    @property
    def n_parameters(self) -> int:
        """Alias for total number of parameters (compatible with UI)."""
        return self.n_params

    # ── Adam update ──────────────────────────────────────────────────────
    def adam_update(self, t: int, lr: float = 3e-4):
        self.trunk.adam_update(t, lr)
        self.val_head.adam_update(t, lr)
        self.adv_head.adam_update(t, lr)

    # ── Target network update ────────────────────────────────────────────
    def polyak_copy_from(self, src: "DuelingQNetworkNumpy", tau: float = 1.0):
        self.trunk.polyak_copy_from(src.trunk, tau)
        self.val_head.polyak_copy_from(src.val_head, tau)
        self.adv_head.polyak_copy_from(src.adv_head, tau)

    # ── Serialization ────────────────────────────────────────────────────
    def get_weights(self) -> dict:
        def mlp_w(mlp):
            return [(layer.W.copy(), layer.b.copy()) for layer in mlp.layers]

        return {
            "trunk": mlp_w(self.trunk),
            "val": mlp_w(self.val_head),
            "adv": mlp_w(self.adv_head),
        }

    def set_weights(self, d: dict):
        def load(mlp, ws):
            for layer, (W, b) in zip(mlp.layers, ws):
                layer.W = W.copy()
                layer.b = b.copy()

        load(self.trunk, d["trunk"])
        load(self.val_head, d["val"])
        load(self.adv_head, d["adv"])

    @property
    def n_params(self) -> int:
        return self.trunk.n_params + self.val_head.n_params + self.adv_head.n_params


# ─── Convenience ─────────────────────────────────────────────────────────────


def build_numpy_dqn(
    state_dim: int,
    n_actions: int,
    hidden_dims: List[int],
    seed: int = 42,
) -> Tuple[DuelingQNetworkNumpy, DuelingQNetworkNumpy]:
    """Return (online, target) with identical initialisation."""
    online = DuelingQNetworkNumpy(state_dim, n_actions, hidden_dims, seed)
    target = DuelingQNetworkNumpy(state_dim, n_actions, hidden_dims, seed)
    target.polyak_copy_from(online, tau=1.0)  # exact copy
    return online, target
