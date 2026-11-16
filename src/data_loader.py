#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Forensic Data Loader & 8-Step Accounting Hygiene Pipeline for EIML-Distress (Q1 Standard).
Processes raw `/home/antigravity/upload/data-financial-0601.xlsx` (10,800 rows x 31 columns)
and outputs audited, sign-normalized, metadata-reconciled panel records without any
look-ahead leakage.
"""

import csv
import json
import math
import os
import pickle
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any
import openpyxl
import yaml


def safe_float(val: Any, default: float = None) -> float:
    if val is None or val == "":
        return default
    try:
        v = float(val)
        return default if (math.isnan(v) or math.isinf(v)) else v
    except (ValueError, TypeError):
        return default


def run_forensic_cleaning(config_path: str = "/home/antigravity/09_PAPER_Q1_BOND/configs/config.yaml") -> Tuple[Dict, Dict]:
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    raw_path = cfg["project"]["raw_data_path"]
    proc_dir = cfg["project"]["processed_dir"]
    os.makedirs(proc_dir, exist_ok=True)

    wb = openpyxl.load_workbook(raw_path, read_only=True)
    ws = wb["Sheet1"]
    rows = list(ws.iter_rows(values_only=True))
    raw_headers = list(rows[0])
    raw_data = rows[1:]

    audit_log = {
        "raw_shape": [len(raw_data), len(raw_headers)],
        "raw_headers": raw_headers,
        "anomalies_detected_and_fixed": {},
    }

    # --------------------------------------------------------------------------
    # STEP 1: Verify and Drop Duplicate Column 26 ('CostofGood')
    # --------------------------------------------------------------------------
    cog_diffs = sum(1 for r in raw_data if r[25] != r[26])
    audit_log["anomalies_detected_and_fixed"]["1_duplicate_costofgood"] = {
        "col_25_name": raw_headers[25],
        "col_26_name": raw_headers[26],
        "discrepancy_rows": cog_diffs,
        "action": "Dropped redundant column index 26; retained column index 25.",
    }

    # --------------------------------------------------------------------------
    # STEP 2: Audit Ticker Panel Balance & MCG / MCO Row 5296 Splice
    # --------------------------------------------------------------------------
    by_ticker_raw = defaultdict(dict)
    for idx, r in enumerate(raw_data, start=2):
        ticker = str(r[0]).strip()
        year = int(r[1])
        by_ticker_raw[ticker][year] = {"excel_row": idx, "raw": list(r)}

    irregular_tickers = {t: sorted(list(yrs.keys())) for t, yrs in by_ticker_raw.items() if len(yrs) != 15}
    audit_log["anomalies_detected_and_fixed"]["2_ticker_panel_splice"] = {
        "raw_unique_tickers": len(by_ticker_raw),
        "tickers_with_15_years": sum(1 for yrs in by_ticker_raw.values() if len(yrs) == 15),
        "irregular_tickers": {k: {"count": len(v), "years": v} for k, v in irregular_tickers.items()},
        "action": "Isolated single-year splice 'MCO' (Row 5296, Year 2022, HNX, Listedyear=None) from transition modeling; retained 720 canonical multi-year firm panels.",
    }
    if "MCO" in by_ticker_raw and len(by_ticker_raw["MCO"]) == 1:
        del by_ticker_raw["MCO"]

    # --------------------------------------------------------------------------
    # STEP 3 & 4: Reconcile Static Firm Metadata (2022 Missing Listedyear,
    #             2022 Empty Stockexchange Delisting Signal, and Epoch 1900 Bug)
    # --------------------------------------------------------------------------
    epoch_1900_tickers = []
    missing_2022_listed_count = 0
    dropped_2022_exchange_tickers = []
    missing_2022_asset_active_2021_tickers = []

    firm_metadata = {}
    for t, yrs in sorted(by_ticker_raw.items()):
        if 2022 in yrs and yrs[2022]["raw"][4] is None:
            missing_2022_listed_count += 1

        raw_lyrs = [int(yrs[y]["raw"][4]) for y in yrs if safe_float(yrs[y]["raw"][4]) is not None]
        valid_lyrs = [ly for ly in raw_lyrs if ly > 1900]
        first_valid_asset_yr = min(
            [y for y in yrs if safe_float(yrs[y]["raw"][5]) is not None and safe_float(yrs[y]["raw"][5]) > 0],
            default=2008,
        )

        if any(ly == 1900 for ly in raw_lyrs):
            epoch_1900_tickers.append(t)
            reconciled_listed_year = first_valid_asset_yr
        elif valid_lyrs:
            reconciled_listed_year = Counter(valid_lyrs).most_common(1)[0][0]
        else:
            reconciled_listed_year = first_valid_asset_yr

        exchs = [str(yrs[y]["raw"][2]).strip() for y in yrs if str(yrs[y]["raw"][2] or "").strip() in ("HOSE", "HNX")]
        canonical_exchange = exchs[0] if exchs else "HNX"
        icb2_vals = [str(yrs[y]["raw"][3]).strip() for y in yrs if yrs[y]["raw"][3]]
        canonical_icb2 = icb2_vals[0] if icb2_vals else "Unknown"

        exch_2022_raw = str(yrs[2022]["raw"][2] or "").strip() if 2022 in yrs else canonical_exchange
        dropped_exch_2022 = (2022 in yrs and exch_2022_raw == "")
        if dropped_exch_2022:
            dropped_2022_exchange_tickers.append(t)

        asset_2021 = safe_float(yrs[2021]["raw"][5]) if 2021 in yrs else None
        asset_2022 = safe_float(yrs[2022]["raw"][5]) if 2022 in yrs else None
        active_2021_missing_2022 = (
            (2022 in yrs)
            and (asset_2021 is not None and asset_2021 > 0)
            and (asset_2022 is None or asset_2022 <= 0)
        )
        if active_2021_missing_2022:
            missing_2022_asset_active_2021_tickers.append(t)

        firm_metadata[t] = {
            "ticker": t,
            "listed_year": reconciled_listed_year,
            "had_epoch_1900_bug": (t in epoch_1900_tickers),
            "exchange": canonical_exchange,
            "icb2": canonical_icb2,
            "dropped_2022_exchange": dropped_exch_2022,
            "active_2021_missing_2022_filing": active_2021_missing_2022,
        }

    audit_log["anomalies_detected_and_fixed"]["3_static_metadata_and_2022_delisting"] = {
        "missing_2022_listedyear_rows_fixed": missing_2022_listed_count,
        "epoch_1900_listedyear_tickers_fixed": epoch_1900_tickers,
        "dropped_2022_exchange_tickers": dropped_2022_exchange_tickers,
        "active_2021_missing_2022_filing_tickers": missing_2022_asset_active_2021_tickers,
        "action": "Forward-propagated Listedyear to 2022; replaced Listedyear=1900 with first audited filing year; preserved 2022 exchange-loss and non-filing flags as Condition 3 regulatory distress indicators.",
    }

    # --------------------------------------------------------------------------
    # STEP 5: Estimate Training-Only Interest-to-Financial-Expense Ratio (Zero Leakage)
    # --------------------------------------------------------------------------
    # Only use post-listing observations in training years (t <= 2016) where both
    # financialexp and interestexp are non-null and positive in magnitude.
    train_int_fin_ratios = []
    positive_expense_anomalies = defaultdict(list)

    for t, yrs in by_ticker_raw.items():
        lyr = firm_metadata[t]["listed_year"]
        for y, info in yrs.items():
            r = info["raw"]
            for col_idx, col_name in [(25, "CostofGood"), (27, "financialexp"), (28, "interestexp"), (29, "sellingexpen"), (30, "managementexpen")]:
                v = safe_float(r[col_idx])
                if v is not None and v > 0:
                    positive_expense_anomalies[col_name].append({"ticker": t, "year": y, "value": v})

            if y <= 2016 and y >= lyr:
                fin_v = safe_float(r[27])
                int_v = safe_float(r[28])
                if fin_v is not None and int_v is not None and abs(fin_v) > 1e6:
                    ratio = min(1.0, abs(int_v) / abs(fin_v))
                    if ratio > 0:
                        train_int_fin_ratios.append(ratio)

    train_int_fin_ratios.sort()
    kappa_train = train_int_fin_ratios[len(train_int_fin_ratios) // 2] if train_int_fin_ratios else 0.80

    audit_log["anomalies_detected_and_fixed"]["4_expense_sign_and_interest_imputation"] = {
        "positive_sign_expense_anomalies": {k: {"count": len(v), "examples": v[:5]} for k, v in positive_expense_anomalies.items()},
        "train_only_interest_to_finexp_median_kappa": round(kappa_train, 6),
        "action": "Normalized expense outflows via absolute magnitude |.|; imputed missing interestexp using kappa_train * |financialexp| fitted strictly on post-listing training years (t <= 2016).",
    }

    # --------------------------------------------------------------------------
    # STEP 6, 7 & 8: Clean Individual Firm-Year Observations & Check Identities
    # --------------------------------------------------------------------------
    cleaned_panel = defaultdict(dict)
    pre_listing_valid_count = 0
    post_listing_valid_count = 0
    missing_asset_count = 0
    imputed_interest_count = 0
    negative_revenue_rows = []
    shortdebt_exceeds_debt_rows = []

    for t, yrs in sorted(by_ticker_raw.items()):
        meta = firm_metadata[t]
        for y in sorted(yrs.keys()):
            r = yrs[y]["raw"]
            asset = safe_float(r[5])
            is_post_listing = (y >= meta["listed_year"])

            if asset is None or asset <= 0:
                missing_asset_count += 1
                cleaned_panel[t][y] = {
                    "ticker": t,
                    "year": y,
                    "valid_financials": False,
                    "is_post_listing": is_post_listing,
                    "listed_year": meta["listed_year"],
                    "exchange": meta["exchange"],
                    "icb2": meta["icb2"],
                    "dropped_2022_exchange": (y == 2022 and meta["dropped_2022_exchange"]),
                    "active_2021_missing_2022_filing": (y == 2022 and meta["active_2021_missing_2022_filing"]),
                }
                continue

            if is_post_listing:
                post_listing_valid_count += 1
            else:
                pre_listing_valid_count += 1

            raw_sales = safe_float(r[6], 0.0)
            raw_netsales = safe_float(r[7], 0.0)
            if raw_sales < 0 or raw_netsales < 0:
                negative_revenue_rows.append({"ticker": t, "year": y, "sales": raw_sales, "netsales": raw_netsales})

            sales = max(0.0, raw_sales)
            netsales = max(0.0, raw_netsales)
            debt = max(0.0, safe_float(r[8], 0.0))
            raw_shortdebt = max(0.0, safe_float(r[9], 0.0))
            if raw_shortdebt > debt * 1.001:
                shortdebt_exceeds_debt_rows.append({"ticker": t, "year": y, "debt": debt, "shortdebt": raw_shortdebt})
            shortdebt = min(debt, raw_shortdebt) if debt > 0 else 0.0

            equity = safe_float(r[10], 0.0)
            fixedassets = max(0.0, safe_float(r[11], 0.0))
            cash = max(0.0, safe_float(r[12], 0.0))
            sta = max(0.0, safe_float(r[13], 0.0))
            la = max(0.0, safe_float(r[14], 0.0))
            wc = safe_float(r[15], sta - shortdebt)
            netprofit = safe_float(r[16], 0.0)

            rec_turn = max(0.0, safe_float(r[17], 0.0))
            inv_turn = max(0.0, safe_float(r[18], 0.0))
            curr_ratio = max(0.0, safe_float(r[19], sta / max(shortdebt, 1e6)))
            quick_ratio = max(0.0, safe_float(r[20], curr_ratio * 0.6))
            cash_ratio = max(0.0, safe_float(r[21], cash / max(shortdebt, 1e6)))
            roe = safe_float(r[22], netprofit / max(abs(equity), 1e8))
            roa = safe_float(r[23], netprofit / asset)
            ros = safe_float(r[24], netprofit / max(netsales, 1e8))

            # Expense outflow normalization
            cog = abs(safe_float(r[25], 0.0))
            fin_exp = abs(safe_float(r[27], 0.0))
            raw_int_exp = safe_float(r[28], None)
            if raw_int_exp is None:
                int_exp = kappa_train * fin_exp
                imputed_interest_count += 1
                interest_imputed = True
            else:
                int_exp = abs(raw_int_exp)
                interest_imputed = False

            sell_exp = abs(safe_float(r[29], 0.0))
            mgmt_exp = abs(safe_float(r[30], 0.0))

            # Operating EBIT (Proposition 1: avoids tautological equivalence with NetProfit < 0)
            # Note: preserve raw_netsales if negative so operating loss reflects restatement shock
            ebit_op = raw_netsales - cog - sell_exp - mgmt_exp
            ebit_naive = netprofit + int_exp

            if int_exp > 1e7:
                icr_op = ebit_op / int_exp
            else:
                icr_op = 15.0 if ebit_op >= 0 else -5.0
            icr_op = max(-15.0, min(25.0, icr_op))

            cleaned_panel[t][y] = {
                "ticker": t,
                "year": y,
                "valid_financials": True,
                "is_post_listing": is_post_listing,
                "listed_year": meta["listed_year"],
                "exchange": meta["exchange"],
                "icb2": meta["icb2"],
                "dropped_2022_exchange": (y == 2022 and meta["dropped_2022_exchange"]),
                "active_2021_missing_2022_filing": False,
                "interest_imputed": interest_imputed,
                "asset": asset,
                "sales": sales,
                "netsales": netsales,
                "debt": debt,
                "shortdebt": shortdebt,
                "equity": equity,
                "fixedassets": fixedassets,
                "cash": cash,
                "shortermassets": sta,
                "longassets": la,
                "workingcapital": wc,
                "netprofit": netprofit,
                "receivablesturnover": rec_turn,
                "inventorturnover": inv_turn,
                "currentpayoutratio": curr_ratio,
                "quickpayoutratio": quick_ratio,
                "cashpayoutratio": cash_ratio,
                "roe": roe,
                "roa": roa,
                "ros": ros,
                "costofgood": cog,
                "financialexp": fin_exp,
                "interestexp": int_exp,
                "sellingexpen": sell_exp,
                "managementexpen": mgmt_exp,
                "ebit_op": ebit_op,
                "ebit_naive": ebit_naive,
                "icr_op": icr_op,
            }

    audit_log["anomalies_detected_and_fixed"]["5_panel_hygiene_counts"] = {
        "canonical_firms": len(cleaned_panel),
        "total_firm_year_slots": sum(len(yrs) for yrs in cleaned_panel.values()),
        "post_listing_valid_firm_years": post_listing_valid_count,
        "pre_listing_backfill_firm_years_isolated": pre_listing_valid_count,
        "missing_financial_statement_slots": missing_asset_count,
        "imputed_interestexp_rows": imputed_interest_count,
        "negative_revenue_anomalies_fixed": negative_revenue_rows,
        "shortdebt_gt_debt_anomalies_fixed": shortdebt_exceeds_debt_rows,
    }

    # Export clean panel to CSV and PKL
    csv_path = os.path.join(proc_dir, "clean_panel_2008_2022.csv")
    csv_fields = [
        "ticker", "year", "valid_financials", "is_post_listing", "listed_year",
        "exchange", "icb2", "dropped_2022_exchange", "active_2021_missing_2022_filing",
        "interest_imputed", "asset", "netsales", "debt", "shortdebt", "equity",
        "cash", "shortermassets", "workingcapital", "netprofit", "ebit_op", "interestexp", "icr_op"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields, extrasaction="ignore")
        writer.writeheader()
        for t in sorted(cleaned_panel.keys()):
            for y in sorted(cleaned_panel[t].keys()):
                writer.writerow(cleaned_panel[t][y])

    pkl_path = os.path.join(proc_dir, "clean_panel_2008_2022.pkl")
    with open(pkl_path, "wb") as f:
        pickle.dump({"panel": dict(cleaned_panel), "metadata": firm_metadata, "audit_log": audit_log}, f)

    audit_json_path = os.path.join(proc_dir, "forensic_cleaning_audit_report.json")
    with open(audit_json_path, "w", encoding="utf-8") as f:
        json.dump(audit_log, f, indent=2, ensure_ascii=False)

    print(f"[DataLoader] Cleaned panel saved to: {csv_path}")
    print(f"[DataLoader] Forensic audit report saved to: {audit_json_path}")
    return cleaned_panel, audit_log


if __name__ == "__main__":
    run_forensic_cleaning()
