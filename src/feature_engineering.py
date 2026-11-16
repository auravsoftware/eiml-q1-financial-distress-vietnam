#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zero-Look-Ahead Feature Engineering & Purged Point-in-Time Split Builder (Q1 Standard).
Constructs the 4 Corporate Finance Pillars (18 features), classical baseline scores
(Altman Z''-Score, Ohlson O-Score), Altman Double-Deficit Boundary indicator, and
Dual Target Regimes (Strict 1-Year-Ahead Forward Distress vs. Multi-Period Persistent Distress).

Enforces all 6 Zero-Look-Ahead Guards:
1. Outcome-year indexing (tau = t + 1) with Purged Split Boundaries (Train <= 2017, Val 2018-2019, Test 2020-2022).
2. Point-in-Time Post-Listing Filter (Year_t >= Listedyear_i), isolating pre-IPO backfilled rows.
3. Right-censoring / 2022 delisting attrition capture (FLC, HAI, AMD, GAB, BII, VKC, etc.).
4. Train-only Winsorization (p01, p99) and Z-score Standardization (mu_train, sigma_train).
5. Dual target regime separation (De-overlapped Strict Forward Y_fwd vs. Persistent Y_ovl).
6. Explicit 4-month audit publication lag alignment (FY_t available April 1 of t+1).
"""

import csv
import json
import math
import os
import pickle
from collections import defaultdict
from typing import Dict, List, Tuple
import numpy as np
import yaml

from data_loader import run_forensic_cleaning


def build_features_and_splits(config_path: str = "/home/antigravity/09_PAPER_Q1_BOND/configs/config.yaml") -> Dict:
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    proc_dir = cfg["project"]["processed_dir"]
    cleaned_panel, audit_log = run_forensic_cleaning(config_path)

    feature_names = cfg["features"]["names"]
    mono_map = cfg["features"]["monotonic_constraints"]
    mono_vec = [mono_map.get(fn, 0) for fn in feature_names]

    # Step 1: Compute point-in-time firm-year ratio vectors X_{i,t}
    for t, yrs in cleaned_panel.items():
        for y in sorted(yrs.keys()):
            rec = yrs[y]
            if not rec["valid_financials"]:
                continue

            asset = rec["asset"]
            netsales = rec["netsales"]
            debt = rec["debt"]
            shortdebt = rec["shortdebt"]
            equity = rec["equity"]
            cash = rec["cash"]
            sta = rec["shortermassets"]
            wc = rec["workingcapital"]
            netprofit = rec["netprofit"]
            ebit_op = rec["ebit_op"]
            int_exp = rec["interestexp"]
            icr_op = rec["icr_op"]
            sell_exp = rec["sellingexpen"]
            mgmt_exp = rec["managementexpen"]

            # 4 Classical Ratios for Altman Z''-Score (1995 Emerging Markets)
            x1_wc_asset = max(-1.5, min(1.0, wc / asset))
            x2_re_proxy = max(-1.0, min(1.0, netprofit / asset))
            x3_ebit_asset = max(-1.0, min(1.0, ebit_op / asset))
            x4_eq_debt = max(-1.0, min(5.0, equity / max(debt, 1e8)))
            z_double_prime = 3.25 + 6.56 * x1_wc_asset + 3.26 * x2_re_proxy + 6.72 * x3_ebit_asset + 1.05 * x4_eq_debt

            # Ohlson O-Score proxy
            neg_eq = 1.0 if debt > asset else 0.0
            ohlson_o = (
                -1.32
                - 0.407 * math.log(max(asset / 1e9, 0.1))
                + 6.03 * min(2.0, debt / asset)
                - 1.43 * x1_wc_asset
                + 0.0757 * (shortdebt / max(sta, 1e8))
                - 1.72 * neg_eq
                - 2.37 * x2_re_proxy
                - 1.83 * ((ebit_op + int_exp) / max(debt, 1e8))
            )

            rec["z_double_prime"] = z_double_prime
            rec["ohlson_o"] = ohlson_o
            rec["base_features_16"] = [
                min(15.0, rec["currentpayoutratio"]),                           # 0: curr_ratio
                min(15.0, rec["quickpayoutratio"]),                             # 1: quick_ratio
                min(1.0, cash / asset),                                         # 2: cash_to_asset
                x1_wc_asset,                                                    # 3: wc_to_asset (-1)
                min(2.0, debt / asset),                                         # 4: debt_to_asset (+1)
                (shortdebt / debt) if debt > 0 else 0.0,                        # 5: shortdebt_to_debt (+1)
                icr_op,                                                         # 6: icr_op (-1)
                min(5.0, cash / max(debt, 1e8)),                                # 7: cash_to_debt
                x2_re_proxy,                                                    # 8: roa (-1)
                max(-2.0, min(2.0, rec["roe"])),                                # 9: roe
                x3_ebit_asset,                                                  # 10: ebit_to_asset (-1)
                max(-2.0, min(2.0, ebit_op / max(netsales, 1e8))),              # 11: op_margin
                min(5.0, netsales / asset),                                     # 12: asset_turnover
                min(50.0, rec["receivablesturnover"]),                          # 13: rec_turnover
                min(50.0, rec["inventorturnover"]),                             # 14: inv_turnover
                min(2.0, (sell_exp + mgmt_exp) / max(netsales, 1e8)),           # 15: opex_to_sales
            ]

    # Step 2: Construct Causal Transition Pairs (t -> tau = t + 1)
    # Strictly using information up to t (t-1 and t) to predict outcome at tau = t + 1.
    splits_post_listing = {"train": [], "val": [], "test": []}
    splits_pre_ipo_audit = []
    cohort_summary = defaultdict(lambda: {"n_post": 0, "fwd_distress": 0, "ovl_distress": 0, "n_pre_ipo": 0})

    for t, yrs in sorted(cleaned_panel.items()):
        for y in range(2008, 2022):
            cur = yrs.get(y)
            nxt = yrs.get(y + 1)
            prev = yrs.get(y - 1)
            if cur is None or not cur["valid_financials"] or nxt is None:
                continue

            tau = y + 1
            # Right-censoring / Regulatory delisting check at tau = y + 1
            if not nxt["valid_financials"]:
                # Retained ONLY if it is a verified 2022 regulatory delisting / distress non-filing
                is_censored_default = (
                    tau == 2022
                    and (nxt["dropped_2022_exchange"] or cur["netprofit"] < 0 or cur["icr_op"] < 1.0)
                )
                if not is_censored_default:
                    continue
                y_strict_fwd = 1
                y_persistent_ovl = 1
                c1_flag, c2_flag, c3_flag = False, False, True
            else:
                c3_flag = (tau == 2022 and nxt["dropped_2022_exchange"])
                # Regime B (Persistent Multi-Period Distress across (t, t+1))
                c1_ovl = (cur["icr_op"] < 1.0 and nxt["icr_op"] < 1.0)
                c2_ovl = (nxt["equity"] < 0) or (cur["netprofit"] < 0 and nxt["netprofit"] < 0)
                y_persistent_ovl = 1 if (c1_ovl or c2_ovl or c3_flag) else 0

                # Regime A (Strict 1-Year-Ahead Forward Distress at tau = t+1 ONLY, zero year-t overlap)
                c1_fwd = (nxt["icr_op"] < 1.0 and (nxt["netprofit"] < 0 or nxt["workingcapital"] < 0))
                c2_fwd = (nxt["equity"] < 0) or (nxt["netprofit"] / nxt["asset"] < -0.04)
                y_strict_fwd = 1 if (c1_fwd or c2_fwd or c3_flag) else 0
                c1_flag, c2_flag = c1_fwd, c2_fwd

            # Dynamic trajectory lags (t-1 -> t, strictly causal at decision time t)
            if prev is not None and prev["valid_financials"]:
                d_debt_asset = max(-1.0, min(1.0, cur["base_features_16"][4] - prev["base_features_16"][4]))
                d_icr_op = max(-10.0, min(10.0, cur["base_features_16"][6] - prev["base_features_16"][6]))
                altman_boundary = 1.0 if (
                    cur["workingcapital"] < 0 and cur["ebit_op"] < 0
                    and prev["workingcapital"] < 0 and prev["ebit_op"] < 0
                ) else 0.0
            else:
                d_debt_asset = 0.0
                d_icr_op = 0.0
                altman_boundary = 1.0 if (cur["workingcapital"] < 0 and cur["ebit_op"] < 0) else 0.0

            x_raw_18 = cur["base_features_16"] + [d_debt_asset, d_icr_op]

            transition_record = {
                "ticker": t,
                "feature_year_t": y,
                "decision_date": f"{y+1}-04-01",  # 4-month audit lag after Dec 31, t
                "outcome_year_tau": tau,
                "listed_year": cur["listed_year"],
                "is_post_listing": cur["is_post_listing"],
                "exchange": cur["exchange"],
                "icb2": cur["icb2"],
                "x_raw": x_raw_18,
                "y_fwd": y_strict_fwd,
                "y_ovl": y_persistent_ovl,
                "altman_boundary": altman_boundary,
                "z_double_prime": cur["z_double_prime"],
                "ohlson_o": cur["ohlson_o"],
                "c3_delisting_attrition": int(c3_flag),
            }

            if not cur["is_post_listing"]:
                splits_pre_ipo_audit.append(transition_record)
                cohort_summary[f"{y}->{tau}"]["n_pre_ipo"] += 1
            else:
                if tau <= 2017:
                    sp = "train"
                elif tau <= 2019:
                    sp = "val"
                else:
                    sp = "test"
                splits_post_listing[sp].append(transition_record)
                cohort_summary[f"{y}->{tau}"]["n_post"] += 1
                cohort_summary[f"{y}->{tau}"]["fwd_distress"] += y_strict_fwd
                cohort_summary[f"{y}->{tau}"]["ovl_distress"] += y_persistent_ovl

    # Step 3: Fit Winsorization (p01, p99) and Z-Score Scaler STRICTLY on Training Set (tau <= 2017)
    n_features = len(feature_names)
    scaler_params = {
        "feature_names": feature_names,
        "monotonic_signs": mono_vec,
        "p01": [],
        "p99": [],
        "mean": [],
        "std": [],
    }

    for j in range(n_features):
        col_train = sorted([r["x_raw"][j] for r in splits_post_listing["train"]])
        p01 = col_train[int(0.01 * len(col_train))]
        p99 = col_train[int(0.99 * len(col_train))]
        col_win = [max(p01, min(p99, v)) for v in col_train]
        m = sum(col_win) / len(col_win)
        s = math.sqrt(sum((v - m) ** 2 for v in col_win) / len(col_win)) or 1.0

        scaler_params["p01"].append(p01)
        scaler_params["p99"].append(p99)
        scaler_params["mean"].append(m)
        scaler_params["std"].append(s)

        for sp_list in list(splits_post_listing.values()) + [splits_pre_ipo_audit]:
            for r in sp_list:
                if "x_norm" not in r:
                    r["x_norm"] = [0.0] * n_features
                v_clipped = max(p01, min(p99, r["x_raw"][j]))
                r["x_norm"][j] = (v_clipped - m) / s

    # Build NumPy arrays for immediate model training
    numpy_splits = {}
    for sp in ["train", "val", "test"]:
        recs = splits_post_listing[sp]
        numpy_splits[sp] = {
            "X": np.array([r["x_norm"] for r in recs], dtype=np.float64),
            "X_raw": np.array([r["x_raw"] for r in recs], dtype=np.float64),
            "y_fwd": np.array([r["y_fwd"] for r in recs], dtype=np.int64),
            "y_ovl": np.array([r["y_ovl"] for r in recs], dtype=np.int64),
            "altman_boundary": np.array([r["altman_boundary"] for r in recs], dtype=np.float64),
            "z_double_prime": np.array([r["z_double_prime"] for r in recs], dtype=np.float64),
            "ohlson_o": np.array([r["ohlson_o"] for r in recs], dtype=np.float64),
            "tickers": [r["ticker"] for r in recs],
            "feature_years": np.array([r["feature_year_t"] for r in recs], dtype=np.int64),
            "outcome_years": np.array([r["outcome_year_tau"] for r in recs], dtype=np.int64),
            "icb2": [r["icb2"] for r in recs],
        }

    # Save ready-to-train splits and feature CSV
    splits_pkl_path = os.path.join(proc_dir, "train_val_test_splits.pkl")
    payload = {
        "numpy_splits": numpy_splits,
        "records_splits": splits_post_listing,
        "pre_ipo_isolated_records": splits_pre_ipo_audit,
        "scaler_params": scaler_params,
        "cohort_summary": dict(cohort_summary),
        "forensic_audit": audit_log,
    }
    with open(splits_pkl_path, "wb") as f:
        pickle.dump(payload, f)

    features_csv_path = os.path.join(proc_dir, "panel_features_clean.csv")
    csv_cols = [
        "split", "ticker", "feature_year_t", "decision_date", "outcome_year_tau",
        "listed_year", "exchange", "icb2", "y_fwd", "y_ovl", "altman_boundary",
        "z_double_prime", "ohlson_o", "c3_delisting_attrition"
    ] + feature_names
    with open(features_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_cols)
        writer.writeheader()
        for sp in ["train", "val", "test"]:
            for r in splits_post_listing[sp]:
                row_dict = {
                    "split": sp,
                    "ticker": r["ticker"],
                    "feature_year_t": r["feature_year_t"],
                    "decision_date": r["decision_date"],
                    "outcome_year_tau": r["outcome_year_tau"],
                    "listed_year": r["listed_year"],
                    "exchange": r["exchange"],
                    "icb2": r["icb2"],
                    "y_fwd": r["y_fwd"],
                    "y_ovl": r["y_ovl"],
                    "altman_boundary": r["altman_boundary"],
                    "z_double_prime": round(r["z_double_prime"], 4),
                    "ohlson_o": round(r["ohlson_o"], 4),
                    "c3_delisting_attrition": r["c3_delisting_attrition"],
                }
                for j, fn in enumerate(feature_names):
                    row_dict[fn] = round(r["x_norm"][j], 6)
                writer.writerow(row_dict)

    setup_summary = {
        "splits_overview": {
            sp: {
                "n_samples": int(len(splits_post_listing[sp])),
                "feature_years_t": [int(min(r["feature_year_t"] for r in splits_post_listing[sp])), int(max(r["feature_year_t"] for r in splits_post_listing[sp]))],
                "outcome_years_tau": [int(min(r["outcome_year_tau"] for r in splits_post_listing[sp])), int(max(r["outcome_year_tau"] for r in splits_post_listing[sp]))],
                "strict_forward_distress_count": int(sum(r["y_fwd"] for r in splits_post_listing[sp])),
                "strict_forward_distress_rate_pct": round(100.0 * sum(r["y_fwd"] for r in splits_post_listing[sp]) / len(splits_post_listing[sp]), 2),
                "persistent_distress_count": int(sum(r["y_ovl"] for r in splits_post_listing[sp])),
                "persistent_distress_rate_pct": round(100.0 * sum(r["y_ovl"] for r in splits_post_listing[sp]) / len(splits_post_listing[sp]), 2),
                "altman_boundary_severe_cases": int(sum(r["altman_boundary"] for r in splits_post_listing[sp])),
            }
            for sp in ["train", "val", "test"]
        },
        "pre_ipo_isolated_transitions": {
            "n_samples": len(splits_pre_ipo_audit),
            "persistent_distress_rate_pct": round(100.0 * sum(r["y_ovl"] for r in splits_pre_ipo_audit) / max(1, len(splits_pre_ipo_audit)), 2),
        },
        "scaler_fitted_on_train_only": {
            fn: {
                "monotonic_constraint": mono_vec[j],
                "p01_train": round(scaler_params["p01"][j], 4),
                "p99_train": round(scaler_params["p99"][j], 4),
                "mean_train": round(scaler_params["mean"][j], 4),
                "std_train": round(scaler_params["std"][j], 4),
            }
            for j, fn in enumerate(feature_names)
        },
    }

    summary_json_path = os.path.join(proc_dir, "experimental_setup_summary.json")
    with open(summary_json_path, "w", encoding="utf-8") as f:
        json.dump(setup_summary, f, indent=2, ensure_ascii=False)

    print(f"[FeatureEngineering] Splits saved to: {splits_pkl_path}")
    print(f"[FeatureEngineering] Clean feature matrix CSV saved to: {features_csv_path}")
    print(f"[FeatureEngineering] Experimental setup summary saved to: {summary_json_path}")
    return payload


if __name__ == "__main__":
    build_features_and_splits()
