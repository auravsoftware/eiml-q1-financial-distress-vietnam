#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Baseline Model Training Pipeline (Classical & Unconstrained Machine Learning).
Trains and saves checkpoints for:
1. Altman Z''-Score (1995 Emerging Markets Calibrated)
2. Ohlson O-Score (1980 Calibrated)
3. Multivariable Logistic Regression (L2-penalized SGD)
4. Support Vector Machine (RBF Kernel Approximation / Random Fourier Features)
5. Random Forest (Bootstrap Feature-Subspace Decision Trees - Barboza et al., 2017)
6. Unconstrained GBDT (Gradient Boosted Decision Stumps/Trees)
7. Unconstrained Deep MLP (2-Layer Tanh Network without Economic Constraints)
"""

import os
import pickle
import numpy as np
import yaml


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30.0, 30.0)))


class LogisticRegressionBaseline:
    def __init__(self, n_features, pos_weight=2.0, lr=0.003, l2=0.005):
        self.w = np.zeros(n_features, dtype=np.float64)
        self.b = -2.2
        self.pos_weight = pos_weight
        self.lr = lr
        self.l2 = l2

    def fit(self, X, y, epochs=35):
        for _ in range(epochs):
            for i in range(X.shape[0]):
                p = float(sigmoid(np.dot(self.w, X[i]) + self.b))
                err = (p - y[i]) * (self.pos_weight if y[i] == 1 else 1.0)
                self.w -= self.lr * (err * X[i] + self.l2 * self.w)
                self.b -= self.lr * err
        return self

    def predict_proba(self, X):
        return sigmoid(X @ self.w + self.b)


class RBFSVMApproximation:
    """Random Fourier Features RBF-SVM with logistic calibration."""
    def __init__(self, n_features, n_components=48, gamma=0.08, seed=42):
        rng = np.random.default_rng(seed)
        self.omega = rng.normal(0.0, np.sqrt(2.0 * gamma), size=(n_features, n_components))
        self.phase = rng.uniform(0.0, 2.0 * np.pi, size=n_components)
        self.scale = np.sqrt(2.0 / n_components)
        self.clf = LogisticRegressionBaseline(n_components, pos_weight=2.0, lr=0.003, l2=0.008)

    def _transform(self, X):
        return self.scale * np.cos(X @ self.omega + self.phase)

    def fit(self, X, y):
        Z = self._transform(X)
        self.clf.fit(Z, y, epochs=35)
        return self

    def predict_proba(self, X):
        return self.clf.predict_proba(self._transform(X))


class ObliqueTreeStumpEnsemble:
    """Fast Pure-NumPy Depth-2 Tree Ensemble for Random Forest and Unconstrained/Monotonic GBDT."""
    def __init__(self, n_estimators=40, mode="rf", mono_signs=None, seed=42):
        self.n_estimators = n_estimators
        self.mode = mode
        self.mono_signs = mono_signs
        self.seed = seed
        self.trees = []
        self.base_logit = -2.0

    def _fit_single_stump(self, X, target, feat_indices, mono_signs=None):
        best_j, best_thr, best_l, best_r, best_gain = 0, 0.0, 0.0, 0.0, -1e18
        total_mean = float(np.mean(target))
        for j in feat_indices:
            xj = X[:, j]
            sgn = mono_signs[j] if mono_signs is not None else 0
            for q in np.linspace(0.1, 0.9, 9):
                thr = float(np.quantile(xj, q))
                mask_l = xj <= thr
                nl = int(mask_l.sum())
                nr = len(xj) - nl
                if nl < 12 or nr < 12:
                    continue
                vl = float(np.mean(target[mask_l]))
                vr = float(np.mean(target[~mask_l]))
                if sgn > 0 and vr < vl:
                    continue
                if sgn < 0 and vr > vl:
                    continue
                # Variance reduction gain
                gain = nl * (vl - total_mean) ** 2 + nr * (vr - total_mean) ** 2
                if gain > best_gain:
                    best_gain = gain
                    best_j, best_thr, best_l, best_r = int(j), thr, vl, vr
        return best_j, best_thr, best_l, best_r

    def fit(self, X, y):
        rng = np.random.default_rng(self.seed)
        n, d = X.shape
        pos_rate = np.clip(np.mean(y), 0.01, 0.99)
        self.base_logit = float(np.log(pos_rate / (1.0 - pos_rate)))

        if self.mode == "rf":
            for _ in range(self.n_estimators):
                idx = rng.integers(0, n, size=n)
                Xb, yb = X[idx], y[idx].astype(np.float64)
                feat_sub1 = rng.choice(d, size=max(5, int(np.sqrt(d))), replace=False)
                j1, thr1, vl1, vr1 = self._fit_single_stump(Xb, yb, feat_sub1, None)
                mask_l = Xb[:, j1] <= thr1
                feat_sub2 = rng.choice(d, size=max(5, int(np.sqrt(d))), replace=False)
                j2_l, thr2_l, vll, vlr = self._fit_single_stump(Xb[mask_l], yb[mask_l], feat_sub2, None)
                j2_r, thr2_r, vrl, vrr = self._fit_single_stump(Xb[~mask_l], yb[~mask_l], feat_sub2, None)
                # Add slight bootstrap leaf noise if unconstrained RF
                self.trees.append((j1, thr1, j2_l, thr2_l, vll, vlr, j2_r, thr2_r, vrl, vrr))
        else:
            f_pred = np.full(n, self.base_logit, dtype=np.float64)
            lr_boost = 0.15
            all_feats = list(range(d))
            for _ in range(self.n_estimators):
                p = sigmoid(f_pred)
                w_hess = np.maximum(p * (1.0 - p), 1e-4)
                pseudo_res = (y - p) / np.sqrt(w_hess)
                j1, thr1, vl1, vr1 = self._fit_single_stump(X, pseudo_res, all_feats, self.mono_signs)
                mask_l = X[:, j1] <= thr1
                j2_l, thr2_l, vll, vlr = self._fit_single_stump(X[mask_l], pseudo_res[mask_l], all_feats, self.mono_signs)
                j2_r, thr2_r, vrl, vrr = self._fit_single_stump(X[~mask_l], pseudo_res[~mask_l], all_feats, self.mono_signs)
                vll, vlr, vrl, vrr = vll * lr_boost, vlr * lr_boost, vrl * lr_boost, vrr * lr_boost
                step = np.where(
                    mask_l,
                    np.where(X[:, j2_l] <= thr2_l, vll, vlr),
                    np.where(X[:, j2_r] <= thr2_r, vrl, vrr),
                )
                f_pred += step
                self.trees.append((j1, thr1, j2_l, thr2_l, vll, vlr, j2_r, thr2_r, vrl, vrr))
        return self

    def predict_proba(self, X):
        n = X.shape[0]
        if self.mode == "rf":
            probs = np.zeros(n, dtype=np.float64)
            for j1, thr1, j2_l, thr2_l, vll, vlr, j2_r, thr2_r, vrl, vrr in self.trees:
                mask_l = X[:, j1] <= thr1
                probs += np.where(
                    mask_l,
                    np.where(X[:, j2_l] <= thr2_l, vll, vlr),
                    np.where(X[:, j2_r] <= thr2_r, vrl, vrr),
                )
            return np.clip(probs / max(1, len(self.trees)), 1e-6, 1.0 - 1e-6)
        else:
            f_pred = np.full(n, self.base_logit, dtype=np.float64)
            for j1, thr1, j2_l, thr2_l, vll, vlr, j2_r, thr2_r, vrl, vrr in self.trees:
                mask_l = X[:, j1] <= thr1
                f_pred += np.where(
                    mask_l,
                    np.where(X[:, j2_l] <= thr2_l, vll, vlr),
                    np.where(X[:, j2_r] <= thr2_r, vrl, vrr),
                )
            return sigmoid(f_pred)


class UnconstrainedMLP:
    def __init__(self, n_features, hidden_dim=16, pos_weight=2.0, lr=0.004, l2=0.0005, seed=42):
        rng = np.random.default_rng(seed)
        self.W1 = rng.normal(0.0, 0.35, size=(hidden_dim, n_features))
        self.b1 = np.zeros(hidden_dim, dtype=np.float64)
        self.W2 = rng.normal(0.0, 0.35, size=hidden_dim)
        self.b2 = -2.0
        self.pos_weight = pos_weight
        self.lr = lr
        self.l2 = l2

    def fit(self, X, y, epochs=25):
        for _ in range(epochs):
            for i in range(X.shape[0]):
                xi, yi = X[i], y[i]
                h = np.tanh(self.W1 @ xi + self.b1)
                p = float(sigmoid(np.dot(self.W2, h) + self.b2))
                dz = (p - yi) * (self.pos_weight if yi == 1 else 1.0)
                dh = dz * self.W2 * (1.0 - h ** 2)
                self.W2 -= self.lr * (dz * h + self.l2 * self.W2)
                self.W1 -= self.lr * (np.outer(dh, xi) + self.l2 * self.W1)
                self.b1 -= self.lr * dh
                self.b2 -= self.lr * dz
        return self

    def predict_proba(self, X):
        H = np.tanh(X @ self.W1.T + self.b1)
        return sigmoid(H @ self.W2 + self.b2)


def run_baseline_training(config_path: str = "/home/antigravity/09_PAPER_Q1_BOND/configs/config.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    proc_dir = cfg["project"]["processed_dir"]
    models_dir = os.path.join(cfg["project"]["results_dir"], "models")
    os.makedirs(models_dir, exist_ok=True)

    with open(os.path.join(proc_dir, "train_val_test_splits.pkl"), "rb") as f:
        payload = pickle.load(f)

    np_splits = payload["numpy_splits"]
    X_train = np_splits["train"]["X"]
    d = X_train.shape[1]

    trained_baselines = {}
    for target_key in ["y_fwd", "y_ovl"]:
        y_train = np_splits["train"][target_key]
        print(f"[TrainBaseline] Training classical & black-box baselines for target '{target_key}'...")

        lr_model = LogisticRegressionBaseline(d).fit(X_train, y_train)
        svm_model = RBFSVMApproximation(d).fit(X_train, y_train)
        rf_model = ObliqueTreeStumpEnsemble(n_estimators=45, mode="rf").fit(X_train, y_train)
        gbdt_model = ObliqueTreeStumpEnsemble(n_estimators=50, mode="gbdt", mono_signs=None).fit(X_train, y_train)
        mlp_model = UnconstrainedMLP(d).fit(X_train, y_train)

        trained_baselines[target_key] = {
            "LogisticRegression": lr_model,
            "RBF_SVM": svm_model,
            "RandomForest": rf_model,
            "Unconstrained_GBDT": gbdt_model,
            "Unconstrained_MLP": mlp_model,
        }

    out_path = os.path.join(models_dir, "baselines.pkl")
    with open(out_path, "wb") as f:
        pickle.dump(trained_baselines, f)
    print(f"[TrainBaseline] Saved all trained baseline models to: {out_path}")
    return trained_baselines


if __name__ == "__main__":
    run_baseline_training()
