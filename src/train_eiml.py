#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Proposed EIML Model Training Pipeline (Mono-GBDT & Economics-Informed Neural Network - EINN).
Trains:
1. Mono-GBDT (Monotonicity-Constrained Gradient Boosted Decision Trees)
2. Proposed EINN (Full Model with Monotonic Regularization + Altman Boundary Floor + Hard Cone Projection)
3. Ablation Variants (Varying lambda_1, lambda_2, and Cone Projection)
"""

import os
import pickle
import yaml

from theory_losses import EconomicsInformedLossAndModel
from train_ml_baseline import ObliqueTreeStumpEnsemble


def run_eiml_training(config_path: str = "/home/antigravity/09_PAPER_Q1_BOND/configs/config.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    proc_dir = cfg["project"]["processed_dir"]
    models_dir = os.path.join(cfg["project"]["results_dir"], "models")
    os.makedirs(models_dir, exist_ok=True)

    with open(os.path.join(proc_dir, "train_val_test_splits.pkl"), "rb") as f:
        payload = pickle.load(f)

    np_splits = payload["numpy_splits"]
    scaler = payload["scaler_params"]
    X_train = np_splits["train"]["X"]
    altman_train = np_splits["train"]["altman_boundary"]
    mono_signs = scaler["monotonic_signs"]
    d = X_train.shape[1]

    eiml_models = {}
    for target_key in ["y_fwd", "y_ovl"]:
        y_train = np_splits["train"][target_key]
        print(f"[TrainEIML] Training Mono-GBDT and EINN for target '{target_key}'...")

        mono_gbdt = ObliqueTreeStumpEnsemble(
            n_estimators=55, mode="gbdt", mono_signs=mono_signs, seed=42
        ).fit(X_train, y_train)

        einn_full = EconomicsInformedLossAndModel(
            n_features=d,
            mono_signs=mono_signs,
            hidden_dim=cfg["eiml_model"]["hidden_dim"],
            pos_weight=cfg["eiml_model"]["positive_class_weight"],
            lambda_1=cfg["eiml_model"]["lambda_1_monotonic"],
            lambda_2=cfg["eiml_model"]["lambda_2_boundary"],
            tau_bound=cfg["eiml_model"]["tau_altman_boundary"],
            hard_cone_projection=True,
            lr=cfg["eiml_model"]["learning_rate"],
            weight_decay=cfg["eiml_model"]["weight_decay"],
            seed=cfg["project"]["seed"],
        ).fit(X_train, y_train, altman_train, epochs=cfg["eiml_model"]["epochs"])

        eiml_models[target_key] = {
            "Mono_GBDT": mono_gbdt,
            "Proposed_EINN": einn_full,
        }

    out_path = os.path.join(models_dir, "eiml_models.pkl")
    with open(out_path, "wb") as f:
        pickle.dump(eiml_models, f)
    print(f"[TrainEIML] Saved all trained EIML models to: {out_path}")
    return eiml_models


if __name__ == "__main__":
    run_eiml_training()
