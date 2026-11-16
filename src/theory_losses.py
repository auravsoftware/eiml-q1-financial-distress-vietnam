#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Economics-Informed Machine Learning (EIML) Loss Functions, Monotonic Cone Projection,
and Readiness Verification Suite for Q1 Corporate Distress Modeling.
"""

import json
import os
import pickle
import numpy as np
import yaml


class EconomicsInformedLossAndModel:
    """
    NumPy-vectorized Economics-Informed Neural Network (EINN) with:
    1. Weighted Binary Cross-Entropy / Focal Loss (L_data)
    2. Analytical Jacobian Monotonicity Regularization (R_mono)
    3. Altman Double-Deficit Insolvency Boundary Penalty (R_bound)
    4. Hard Positive-Cone Weight Projection (Guarantees VR_mono == 0.00%)
    """

    def __init__(
        self,
        n_features: int,
        mono_signs: list,
        hidden_dim: int = 16,
        pos_weight: float = 2.0,
        lambda_1: float = 2.5,
        lambda_2: float = 1.8,
        tau_bound: float = 0.70,
        hard_cone_projection: bool = True,
        lr: float = 0.0035,
        weight_decay: float = 0.001,
        seed: int = 42,
    ):
        self.n_features = n_features
        self.mono_signs = np.array(mono_signs, dtype=np.float64)
        self.hidden_dim = hidden_dim
        self.pos_weight = pos_weight
        self.lambda_1 = lambda_1
        self.lambda_2 = lambda_2
        self.tau_bound = tau_bound
        self.hard_cone_projection = hard_cone_projection
        self.lr = lr
        self.weight_decay = weight_decay

        rng = np.random.default_rng(seed)
        self.W1 = rng.normal(0.0, 0.25, size=(hidden_dim, n_features))
        self.b1 = np.zeros(hidden_dim, dtype=np.float64)
        self.W2 = np.abs(rng.normal(0.0, 0.25, size=hidden_dim)) + 0.02
        self.b2 = -2.0

        if self.hard_cone_projection:
            self._project_weights()

    def _project_weights(self):
        self.W2 = np.maximum(0.01, self.W2)
        for j, sgn in enumerate(self.mono_signs):
            if sgn > 0:
                self.W1[:, j] = np.maximum(0.005, self.W1[:, j])
            elif sgn < 0:
                self.W1[:, j] = np.minimum(-0.005, self.W1[:, j])

    @staticmethod
    def _sigmoid(z: np.ndarray) -> np.ndarray:
        z_clip = np.clip(z, -30.0, 30.0)
        return 1.0 / (1.0 + np.exp(-z_clip))

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        H = np.tanh(X @ self.W1.T + self.b1)
        Z = H @ self.W2 + self.b2
        return self._sigmoid(Z)

    def compute_loss_breakdown(self, X: np.ndarray, y: np.ndarray, altman_bound: np.ndarray) -> dict:
        H = np.tanh(X @ self.W1.T + self.b1)
        Z = H @ self.W2 + self.b2
        p = np.clip(self._sigmoid(Z), 1e-7, 1.0 - 1e-7)

        # 1. Weighted BCE loss
        weights = np.where(y == 1, self.pos_weight, 1.0)
        l_data = -np.mean(weights * (y * np.log(p) + (1.0 - y) * np.log(1.0 - p)))

        # 2. Analytical Jacobian dp/dx_j = p(1-p) * ((1 - H^2) * W2) @ W1
        dH = (1.0 - H ** 2) * self.W2[None, :]  # (N, hidden_dim)
        grad_X = (p * (1.0 - p))[:, None] * (dH @ self.W1)  # (N, n_features)

        r_mono = 0.0
        for j, sgn in enumerate(self.mono_signs):
            if sgn > 0:
                r_mono += np.mean(np.maximum(0.0, -grad_X[:, j]))
            elif sgn < 0:
                r_mono += np.mean(np.maximum(0.0, grad_X[:, j]))

        # 3. Altman Boundary loss
        mask = altman_bound == 1.0
        if np.any(mask):
            r_bound = np.mean(np.maximum(0.0, self.tau_bound - p[mask]) ** 2)
        else:
            r_bound = 0.0

        l_total = l_data + self.lambda_1 * r_mono + self.lambda_2 * r_bound
        return {
            "L_total": float(l_total),
            "L_data": float(l_data),
            "R_mono": float(r_mono),
            "R_bound": float(r_bound),
        }

    def fit(self, X: np.ndarray, y: np.ndarray, altman_bound: np.ndarray, epochs: int = 35):
        n = X.shape[0]
        for _ in range(epochs):
            for i in range(n):
                xi = X[i]
                yi = y[i]
                bi = altman_bound[i]

                h = np.tanh(self.W1 @ xi + self.b1)
                z = float(np.dot(self.W2, h) + self.b2)
                p = float(self._sigmoid(z))

                wt = self.pos_weight if yi == 1 else 1.0
                dz = (p - yi) * wt

                if bi == 1.0 and p < self.tau_bound:
                    dz += self.lambda_2 * 2.0 * (p - self.tau_bound) * p * (1.0 - p)

                dh = dz * self.W2 * (1.0 - h ** 2)
                self.W2 -= self.lr * (dz * h + self.weight_decay * self.W2)
                self.W1 -= self.lr * (np.outer(dh, xi) + self.weight_decay * self.W1)
                self.b1 -= self.lr * dh
                self.b2 -= self.lr * dz

                if self.hard_cone_projection:
                    self._project_weights()
        return self
