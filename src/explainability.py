#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Explainable AI (Integrated Gradients & Marginal Sensitivity Attribution) and
2022 Corporate Bond Crisis Case Study Analyzer (FLC, HAI, AMD, GAB, BII, VKC).
"""

import json
import os
import pickle
import numpy as np
import yaml


def compute_integrated_gradients(model, X_sample, baseline_vec=None, steps=20):
    if baseline_vec is None:
        baseline_vec = np.zeros((1, X_sample.shape[1]), dtype=np.float64)
    alphas = np.linspace(0.0, 1.0, steps)
    eps = 1e-4
    n, d = X_sample.shape
    avg_grads = np.zeros((n, d), dtype=np.float64)

    for a in alphas:
        X_interp = baseline_vec + a * (X_sample - baseline_vec)
        base_p = model.predict_proba(X_interp)
        for j in range(d):
            X_plus = X_interp.copy()
            X_plus[:, j] += eps
            p_plus = model.predict_proba(X_plus)
            avg_grads[:, j] += (p_plus - base_p) / eps

    avg_grads /= steps
    attributions = (X_sample - baseline_vec) * avg_grads
    return attributions, avg_grads


def run_explainability(config_path: str = "/home/antigravity/09_PAPER_Q1_BOND/configs/config.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    proc_dir = cfg["project"]["processed_dir"]
    results_dir = cfg["project"]["results_dir"]
    tables_dir = os.path.join(results_dir, "tables")
    models_dir = os.path.join(results_dir, "models")
    os.makedirs(tables_dir, exist_ok=True)

    with open(os.path.join(proc_dir, "train_val_test_splits.pkl"), "rb") as f:
        payload = pickle.load(f)
    with open(os.path.join(models_dir, "baselines.pkl"), "rb") as f:
        baselines = pickle.load(f)
    with open(os.path.join(models_dir, "eiml_models.pkl"), "rb") as f:
        eiml_models = pickle.load(f)

    np_splits = payload["numpy_splits"]
    rec_test = payload["records_splits"]["test"]
    feature_names = payload["scaler_params"]["feature_names"]
    mono_signs = payload["scaler_params"]["monotonic_signs"]

    X_test = np_splits["test"]["X"]
    mlp_model = baselines["y_fwd"]["Unconstrained_MLP"]
    einn_model = eiml_models["y_fwd"]["Proposed_EINN"]

    ig_mlp, grad_mlp = compute_integrated_gradients(mlp_model, X_test)
    ig_einn, grad_einn = compute_integrated_gradients(einn_model, X_test)

    mean_abs_mlp = np.mean(np.abs(ig_mlp), axis=0)
    mean_abs_einn = np.mean(np.abs(ig_einn), axis=0)
    mean_abs_mlp /= np.sum(mean_abs_mlp)
    mean_abs_einn /= np.sum(mean_abs_einn)

    feature_ranking = []
    for j, fn in enumerate(feature_names):
        sgn = mono_signs[j]
        if sgn > 0:
            viol_mlp = float(np.mean(grad_mlp[:, j] < -1e-5)) * 100.0
            viol_einn = float(np.mean(grad_einn[:, j] < -1e-5)) * 100.0
        elif sgn < 0:
            viol_mlp = float(np.mean(grad_mlp[:, j] > 1e-5)) * 100.0
            viol_einn = float(np.mean(grad_einn[:, j] > 1e-5)) * 100.0
        else:
            viol_mlp, viol_einn = 0.0, 0.0

        feature_ranking.append({
            "feature": fn,
            "monotonic_axiom": int(sgn),
            "einn_importance_share_pct": round(float(mean_abs_einn[j]) * 100.0, 2),
            "mlp_importance_share_pct": round(float(mean_abs_mlp[j]) * 100.0, 2),
            "mlp_gradient_sign_violation_pct": round(viol_mlp, 2),
            "einn_gradient_sign_violation_pct": round(viol_einn, 2),
        })

    feature_ranking.sort(key=lambda x: -x["einn_importance_share_pct"])

    # Case study on 2021 -> 2022 Bond & Delisting Crisis Issuers
    crisis_watch = {"FLC", "HAI", "AMD", "GAB", "BII", "VKC"}
    case_studies_2022 = []
    p_einn_ovl = eiml_models["y_ovl"]["Proposed_EINN"].predict_proba(X_test)
    p_einn_fwd = einn_model.predict_proba(X_test)
    p_mlp_fwd = mlp_model.predict_proba(X_test)

    for idx, r in enumerate(rec_test):
        if r["outcome_year_tau"] == 2022 and r["ticker"] in crisis_watch:
            case_studies_2022.append({
                "ticker": r["ticker"],
                "feature_year_t": r["feature_year_t"],
                "outcome_year_tau": r["outcome_year_tau"],
                "icb2": r["icb2"],
                "debt_to_asset_2021": round(r["x_raw"][4], 4),
                "shortdebt_to_debt_2021": round(r["x_raw"][5], 4),
                "icr_op_2021": round(r["x_raw"][6], 4),
                "roa_2021": round(r["x_raw"][8], 4),
                "altman_z_double_prime_2021": round(r["z_double_prime"], 4),
                "einn_forward_risk_prob": round(float(p_einn_fwd[idx]), 4),
                "einn_persistent_risk_prob": round(float(p_einn_ovl[idx]), 4),
                "unconstrained_mlp_prob": round(float(p_mlp_fwd[idx]), 4),
                "actual_2022_outcome": "Regulatory Delisting / Suspension / Bond Default",
            })

    out_json = {
        "xai_feature_attribution_ranking": feature_ranking,
        "crisis_2022_early_warning_case_studies": case_studies_2022,
    }
    out_path = os.path.join(tables_dir, "xai_and_case_studies.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_json, f, indent=2, ensure_ascii=False)

    print(f"[Explainability] XAI & 2022 Crisis Case Studies saved to: {out_path}")
    return out_json


if __name__ == "__main__":
    run_explainability()
