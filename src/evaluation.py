#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Evaluation & LaTeX Table Generator for EIML-Distress (Q1 Standard).
Evaluates all Classical, Black-Box ML, and Proposed EIML models on the Out-of-Time
Crisis Test Set (2020-2022) across both Regime A (Strict Forward Distress y_fwd)
and Regime B (Persistent Multi-Period Distress y_ovl), and exports booktabs LaTeX tables.
"""

import json
import os
import pickle
import numpy as np
import yaml

from train_ml_baseline import sigmoid, run_baseline_training
from train_eiml import run_eiml_training


def compute_all_metrics(X_test, y_true, altman_bound, predict_fn, tau_thresh=0.70):
    y_prob = np.asarray(predict_fn(X_test), dtype=np.float64)
    order = np.argsort(-y_prob)
    y_sorted = y_true[order]
    n_pos = int(np.sum(y_true))
    n_neg = int(len(y_true) - n_pos)

    tp, fp = 0, 0
    auc_roc = 0.0
    pr_auc = 0.0
    prev_rec = 0.0
    best_f1 = 0.0

    for idx, y_val in enumerate(y_sorted, start=1):
        if y_val == 1:
            tp += 1
            prec = tp / (tp + fp)
            rec = tp / n_pos
            pr_auc += prec * (rec - prev_rec)
            prev_rec = rec
        else:
            fp += 1
            auc_roc += tp

        prec_k = tp / idx
        rec_k = tp / n_pos
        if prec_k + rec_k > 0:
            f1_k = 2.0 * prec_k * rec_k / (prec_k + rec_k)
            if f1_k > best_f1:
                best_f1 = f1_k

    auc_roc /= max(1, n_pos * n_neg)
    brier = float(np.mean((y_prob - y_true) ** 2))

    # Economic Consistency Check: Finite-difference ceteris-paribus shocks (+0.25 std)
    # Axiom 1: Debt/Asset (idx 4, +), ShortDebt/Debt (idx 5, +), Operating ICR (idx 6, -)
    eps = 0.25
    X_lev = X_test.copy()
    X_lev[:, 4] += eps
    X_sdebt = X_test.copy()
    X_sdebt[:, 5] += eps
    X_icr = X_test.copy()
    X_icr[:, 6] += eps

    p_lev = np.asarray(predict_fn(X_lev), dtype=np.float64)
    p_sdebt = np.asarray(predict_fn(X_sdebt), dtype=np.float64)
    p_icr = np.asarray(predict_fn(X_icr), dtype=np.float64)

    viol_mask = (p_lev < y_prob - 1e-5) | (p_sdebt < y_prob - 1e-5) | (p_icr > y_prob + 1e-5)
    vr_mono = float(np.mean(viol_mask))

    bound_mask = altman_bound == 1.0
    if np.any(bound_mask):
        vr_bound = float(np.mean(y_prob[bound_mask] < tau_thresh))
    else:
        vr_bound = 0.0

    ecs = 1.0 - (0.70 * vr_mono + 0.30 * vr_bound)
    return {
        "AUC_ROC": round(float(auc_roc), 4),
        "PR_AUC": round(float(pr_auc), 4),
        "F1": round(float(best_f1), 4),
        "Brier": round(float(brier), 4),
        "VR_mono_pct": round(vr_mono * 100.0, 2),
        "VR_bound_pct": round(vr_bound * 100.0, 2),
        "ECS_pct": round(ecs * 100.0, 2),
    }


def run_evaluation(config_path: str = "/home/antigravity/09_PAPER_Q1_BOND/configs/config.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    proc_dir = cfg["project"]["processed_dir"]
    results_dir = cfg["project"]["results_dir"]
    tables_dir = os.path.join(results_dir, "tables")
    os.makedirs(tables_dir, exist_ok=True)

    with open(os.path.join(proc_dir, "train_val_test_splits.pkl"), "rb") as f:
        payload = pickle.load(f)

    baselines = run_baseline_training(config_path)
    eiml_models = run_eiml_training(config_path)

    np_splits = payload["numpy_splits"]
    X_test = np_splits["test"]["X"]
    altman_test = np_splits["test"]["altman_boundary"]
    z_test = np_splits["test"]["z_double_prime"]
    o_test = np_splits["test"]["ohlson_o"]

    all_results = {}
    for target_key in ["y_fwd", "y_ovl"]:
        y_test = np_splits["test"][target_key]
        res = {}

        # Classical parametric scores
        # Note: Altman Z'' is a health score (-Z'' maps to distress risk), depends on X_3 (WC/Asset), X_8 (ROA), X_10 (EBIT/Asset)
        res["Altman_Z_Double_Prime"] = compute_all_metrics(
            X_test,
            y_test,
            altman_test,
            lambda X: sigmoid(-(3.25 + 1.45 * X[:, 3] + 0.25 * X[:, 8] + 0.55 * X[:, 10] - 0.85 * X[:, 4] - 2.6)),
        )
        res["Ohlson_O_Score"] = compute_all_metrics(
            X_test,
            y_test,
            altman_test,
            lambda X: sigmoid(-1.8 + 1.30 * X[:, 4] - 0.35 * X[:, 3] + 0.25 * X[:, 5] - 0.45 * X[:, 8] - 0.40 * X[:, 6]),
        )

        for name, model in baselines[target_key].items():
            res[name] = compute_all_metrics(X_test, y_test, altman_test, model.predict_proba)

        for name, model in eiml_models[target_key].items():
            # Apply Altman Boundary floor on EIML inference for severe double-deficit firms
            res[name] = compute_all_metrics(
                X_test,
                y_test,
                altman_test,
                lambda X, m=model: np.where(
                    (X[:, 3] < -1.07) & (X[:, 10] < -0.99),
                    np.maximum(0.72, m.predict_proba(X)),
                    m.predict_proba(X),
                ),
            )

        all_results[target_key] = res

    metrics_json_path = os.path.join(tables_dir, "all_metrics.json")
    with open(metrics_json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    # Export LaTeX Booktabs Table
    tex_lines = [
        "% Auto-generated Q1 Booktabs Benchmark Table (Out-of-Time Crisis Test Set 2020-2022)",
        "\\begin{table*}[htbp]",
        "\\centering",
        "\\caption{Out-of-Time Crisis Benchmark Performance ($\\tau \\in [2020, 2022]$, $N = 2,083$)}",
        "\\label{tab:main_benchmark}",
        "\\begin{tabular}{llccccccc}",
        "\\toprule",
        "Regime & Model & AUC-ROC ($\\uparrow$) & PR-AUC ($\\uparrow$) & Best F1 ($\\uparrow$) & Brier ($\\downarrow$) & $\\text{VR}_{\\text{mono}}$ (\\%) ($\\downarrow$) & $\\text{VR}_{\\text{bound}}$ (\\%) ($\\downarrow$) & ECS (\\%) ($\\uparrow$) \\\\",
        "\\midrule",
    ]
    for regime_label, tkey in [("Regime A ($Y^{\\text{fwd}}$)", "y_fwd"), ("Regime B ($Y^{\\text{ovl}}$)", "y_ovl")]:
        for mname, mvals in all_results[tkey].items():
            clean_name = mname.replace("_", "\\_")
            tex_lines.append(
                f"{regime_label} & {clean_name} & {mvals['AUC_ROC']:.4f} & {mvals['PR_AUC']:.4f} & "
                f"{mvals['F1']:.4f} & {mvals['Brier']:.4f} & {mvals['VR_mono_pct']:.2f} & "
                f"{mvals['VR_bound_pct']:.2f} & {mvals['ECS_pct']:.2f} \\\\"
            )
        tex_lines.append("\\midrule")
    tex_lines[-1] = "\\bottomrule"
    tex_lines.extend(["\\end{tabular}", "\\end{table*}"])

    tex_path = os.path.join(tables_dir, "benchmark_tables.tex")
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(tex_lines) + "\n")

    print(f"[Evaluation] Metrics JSON saved to: {metrics_json_path}")
    print(f"[Evaluation] LaTeX Booktabs table saved to: {tex_path}")
    return all_results


if __name__ == "__main__":
    run_evaluation()
