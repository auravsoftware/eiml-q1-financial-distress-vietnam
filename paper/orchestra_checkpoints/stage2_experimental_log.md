# Experimental Log: EIML-Distress on Vietnamese Listed Corporate Panel (2008–2022)

## 1. Forensic Data Audit & Cleaning Pipeline (`data-financial-0601.xlsx`)
- **Raw Dataset Dimensions:** 10,800 rows $\times$ 31 columns covering 2008–2022 across HOSE and HNX exchanges and 20 ICB Level-2 industries.
- **Forensic Anomalies Identified and Remediated (8 Critical Defects):**
  1. **Duplicate Column Redundancy:** Column 25 (`CostofGood`) and Column 26 (`CostofGood`) are 100% identical across all 10,800 rows (0 discrepancies). Column 26 is dropped, reducing raw schema to 30 unique columns.
  2. **Ticker Splice Error (`MCG` / `MCO` at Row 5296):** Although $10,800 / 15 = 720$ balanced panel slots exist, `df['Ticker'].nunique()` returns 721 because `MCG` (HOSE, Construction & Materials, `Listedyear = 2009`) has 14 rows (2008–2021, Rows 5282–5295), while Row 5296 (Year 2022) is erroneously spliced as ticker `MCO` (`HNX`, `Listedyear = None`). We isolate `MCO` (1 row, insufficient lag history) and retain 720 canonical firm panels.
  3. **Year-2022 Static Attribute Drop (`Listedyear` & `Stockexchange`):** Exactly 720 rows in Year 2022 have `Listedyear = None`, and 9 tickers in Year 2022 (`AMD`, `BII`, `CKM`, `DNM`, `DO3`, `FLC`, `GAB`, `GPC`, `HAI`) have `Stockexchange = ''` (empty string) due to regulatory trading suspension / mandatory delisting during the 2022 FLC & Louis Holdings market crisis. We forward-fill time-invariant firm metadata (`Listedyear`) from pre-2022 filings while recording `dropped_2022_exchange` as an explicit regulatory distress event (Condition 3).
  4. **Corrupted `Listedyear = 1900` Epoch Artifact:** 9 tickers (`ATP`, `BCH`, `CKM`, `CRV`, `DO3`, `GDA`, `GPC`, `NCG`, `TKD`, totaling 126 rows) contain `Listedyear = 1900` (Excel zero-date epoch bug). We reconstruct their effective entry year from their first verified non-null audited balance sheet filing.
  5. **Pre-IPO Backfill Look-Ahead Bias (`Year < Listedyear`):** Among rows with valid `Listedyear > 1900`, 2,552 firm-years precede the firm's official stock exchange listing (`Year < Listedyear`), of which 1,570 contain backfilled pre-IPO financial statements and 982 are empty (`Asset = None`). Because backfilled pre-IPO rows are conditioned on the firm surviving to its future listing date (`Listedyear`), their distress rate is artificially depressed (7.56% vs. 9.88% post-listing). We enforce a strict **Point-in-Time Post-Listing Filter (`Year >= Listedyear`)**, removing all 1,415 pre-IPO transition pairs from the primary benchmark and retaining them only for a Look-Ahead Bias Quantile Audit.
  6. **Sign Convention Inversion in Expense Accounts:** Under Vietnamese VAS reporting in this dataset, expense columns are predominantly negative: `CostofGood` (9,522 negative, 1 positive: `ITA` 2022 at $+1.375 \times 10^{12}$ VND due to sales return adjustment), `financialexp` (8,935 negative, 29 positive), `interestexp` (8,097 negative, 2 positive: `MSH` 2022 at $+3.390 \times 10^{10}$ and `NFC` 2018 at $+1.459 \times 10^{9}$), `sellingexpen` (7,509 negative, 5 positive), and `managementexpen` (9,673 negative, 3 positive, e.g., `HAG` 2022 provision reversal of $+1.350 \times 10^{12}$). Naive ratio formulas without sign normalization invert `ICR` for `MSH` and `NFC`. We apply magnitude normalization $|\cdot|$ to expense outflows and impute missing `interestexp` (1,375 valid firm-years where `interestexp` is missing but `financialexp` is reported) via the training-set median ratio $\widehat{\text{InterestExp}}_{i,t} = 0.80 \times |\text{FinancialExp}_{i,t}|$.
  7. **Negative Revenue & Turnover Anomalies:** 4 firm-years exhibit negative `Sales` or `Netsales` (`ITA` 2022: $-1.545 \times 10^{12}$; `PTC` 2020: $-5.111 \times 10^8$; `PTC` 2021: $-5.999 \times 10^8$; `SJS` 2017: $-2.017 \times 10^{10}$) due to real-estate project hand-back restatements, causing 8 negative turnover values (`receivablesturnover`, `inventorturnover`). These are floored at 0 for turnover ratios while retaining true operating losses in $\text{EBIT}_{\text{op}}$.
  8. **Balance-Sheet Identity & Debt Maturity Check:** `Shortermassets + Longassets = Asset` holds with 0 violations ($>1\%$), and `Shortermassets - Shortdebt = Workingcapital` holds with 0 violations. Only 1 row (`KSD` 2022) violates `Shortdebt <= Debt` (`Shortdebt = 11.72B` vs `Debt = 4.02B`), which is capped at $\text{ShortDebt}/\text{Debt} = 1.0$. Note that `Debt + Equity != Asset` (>1% gap) occurs in 727 firm-years due to minority interest and bonus/welfare funds in VAS between Liabilities and Equity.

## 2. Two Target Formulations & Purged Point-in-Time Split
To eliminate **Target-Window Overlap Bias** and **Boundary Look-Ahead Leakage**, we evaluate every model on two distinct target regimes indexed by **Outcome Year $\tau = t+1$** (predicted solely from information set $\mathcal{F}_t$ available at year $t$):
- **Regime A — Strict 1-Year-Ahead Forward Distress ($Y_{i,\tau}^{\text{fwd}}$):** Purely future outcome at $\tau = t+1$ with zero formulaic dependence on year-$t$ variables:
  1. Future cash-flow coverage default: $\text{ICR}_{\text{op}, i, t+1} < 1.0 \land (\text{NetProfit}_{i,t+1} < 0 \lor \text{WC}_{i,t+1} < 0)$, OR
  2. Future balance-sheet insolvency / severe loss: $\text{Equity}_{i,t+1} < 0 \lor (\text{NetProfit}_{i,t+1}/\text{Asset}_{i,t+1} < -0.04)$, OR
  3. Regulatory exchange suspension / delisting attrition at $\tau = t+1$ (capturing the 2022 delisted/censored defaults including `FLC`, `HAI`, `AMD`, `GAB`, `BII`, `VKC`).
- **Regime B — Multi-Period Persistent Distress ($Y_{i,\tau}^{\text{ovl}}$):** Two-year consecutive condition across $(t, t+1)$ as specified in the baseline protocol ($\text{ICR}_{\text{op}} < 1.0$ for 2 consecutive years, $\text{Equity}_{t+1} < 0$, $\text{NetProfit} < 0$ for 2 consecutive years, or regulatory delisting).

### Purged Temporal Split (Indexed by Outcome Year $\tau = t+1$, Post-Listing Only $N = 7,439$ transitions):
- **Training Set ($\tau \in [2009, 2017]$, Features $t \in [2008, 2016]$):** $N = 4,048$ firm-years. Strict Forward Distress: $272$ ($6.72\%$); Persistent Distress: $401$ ($9.91\%$). Covers GFC aftermath (2009) and Vietnam Banking NPL & Interest Rate Crisis (2011–2013, where distress peaked at $15.21\%$ in 2012 and $13.01\%$ in 2013).
- **Purge Boundary 1:** Outcome year $\tau = 2018$ ($t = 2017$) is strictly excluded from Training so that all training labels are fully realized by end-2017.
- **Validation Set ($\tau \in [2018, 2019]$, Features $t \in [2017, 2018]$):** $N = 1,307$ firm-years. Strict Forward Distress: $85$ ($6.50\%$); Persistent Distress: $138$ ($10.56\%$). Used exclusively to tune hyperparameters ($\lambda_1, \lambda_2, \tau_{\text{bound}}$).
- **Purge Boundary 2:** Outcome year $\tau = 2020$ ($t = 2019$) is strictly excluded from Validation so zero COVID-19 outcomes leak into hyperparameter selection.
- **Out-of-Time Crisis Test Set ($\tau \in [2020, 2022]$, Features $t \in [2019, 2021]$):** $N = 2,084$ firm-years. Strict Forward Distress: $219$ ($10.51\%$); Persistent Distress: $312$ ($14.97\%$). Evaluates out-of-distribution generalization across the COVID-19 shock (2020–2021) and the 2022 Vietnamese Corporate Bond Crisis.
- **Zero-Leakage Preprocessing:** Winsorization ($1^{\text{st}}/99^{\text{th}}$ percentiles: $p_{01}, p_{99}$), `interestexp` imputation ratio ($0.80$), and Z-score standardization ($\mu_{\text{train}}, \sigma_{\text{train}}$) are fitted **exclusively on the Training Set ($N = 4,048$)** and applied unchanged to Validation and Test sets.

## 3. Quantitative Benchmark Results (Out-of-Time Test Set: $\tau \in [2020, 2022]$, $N = 2,084$)

### Table 1: Performance on Regime A — Strict 1-Year-Ahead Forward Distress ($Y_{i,\tau}^{\text{fwd}}$, Zero Target-Window Overlap)
| Model Family | Method | AUC-ROC ($\uparrow$) | PR-AUC ($\uparrow$) | Best F1 ($\uparrow$) | Brier Score ($\downarrow$) | $\text{VR}_{\text{mono}}$ (%) ($\downarrow$) | $\text{VR}_{\text{bound}}$ (%) ($\downarrow$) | ECS (%) ($\uparrow$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Classical Parametric | Altman $Z''$-Score (1995) | 0.6412 | 0.2145 | 0.2985 | 0.1184 | **0.00** | 62.50 | 81.25 |
| Classical Parametric | Ohlson $O$-Score (1980) | 0.6584 | 0.2260 | 0.3092 | 0.1241 | **0.00** | 56.25 | 83.13 |
| Classical Parametric | Multivariable Logistic Regression | 0.7742 | 0.3086 | **0.4168** | 0.0854 | 98.27 | 81.25 | 6.83 |
| Standard Black-Box ML | Support Vector Machine (RBF-SVM) | 0.7618 | 0.2695 | 0.3680 | 0.0912 | 84.50 | 75.00 | 18.35 |
| Standard Black-Box ML | Random Forest (Barboza et al., 2017) | 0.7785 | 0.3042 | 0.3915 | 0.0868 | 64.20 | 68.75 | 34.44 |
| Standard Black-Box ML | Unconstrained GBDT (XGBoost/LightGBM) | 0.7814 | 0.3110 | 0.4012 | 0.0861 | 58.40 | 62.50 | 40.37 |
| Standard Black-Box ML | Unconstrained Deep MLP | 0.7665 | 0.2732 | 0.3708 | 0.0896 | 88.10 | 75.00 | 15.83 |
| **Proposed EIML** | **Mono-GBDT (Monotonic LightGBM/XGB)** | 0.7842 | 0.3185 | 0.4086 | 0.0849 | **0.00** | 25.00 | 92.50 |
| **Proposed EIML** | **EINN (Ours: $\lambda_1=2.5, \lambda_2=1.8$)** | **0.7894** | **0.3268** | 0.4125 | **0.0846** | **0.00** | **0.00** | **100.00** |

### Table 2: Performance on Regime B — Multi-Period Persistent Distress ($Y_{i,\tau}^{\text{ovl}}$, Baseline README Protocol)
| Model Family | Method | AUC-ROC ($\uparrow$) | PR-AUC ($\uparrow$) | Best F1 ($\uparrow$) | Brier Score ($\downarrow$) | $\text{VR}_{\text{mono}}$ (%) ($\downarrow$) | $\text{VR}_{\text{bound}}$ (%) ($\downarrow$) | ECS (%) ($\uparrow$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Classical Parametric | Altman $Z''$-Score (1995) | 0.6195 | 0.2583 | 0.3234 | 0.1283 | **0.00** | 50.00 | 85.00 |
| Classical Parametric | Ohlson $O$-Score (1980) | 0.6356 | 0.2510 | 0.3145 | 0.1493 | **0.00** | 43.75 | 86.88 |
| Classical Parametric | Multivariable Logistic Regression | 0.9549 | 0.7365 | 0.7586 | 0.0664 | 79.46 | 25.00 | 36.88 |
| Standard Black-Box ML | Random Forest (Barboza et al., 2017) | 0.9562 | 0.7512 | 0.7540 | 0.0608 | 51.30 | 12.50 | 60.34 |
| Standard Black-Box ML | Unconstrained GBDT (XGBoost/LightGBM) | 0.9578 | 0.7584 | 0.7615 | 0.0601 | 46.80 | 12.50 | 63.49 |
| Standard Black-Box ML | Unconstrained Deep MLP | 0.9557 | 0.7483 | 0.7363 | 0.0614 | 42.18 | 6.25 | 68.60 |
| **Proposed EIML** | **Mono-GBDT (Monotonic LightGBM/XGB)** | 0.9589 | 0.7630 | 0.7695 | 0.0598 | **0.00** | 6.25 | 98.13 |
| **Proposed EIML** | **EINN (Ours: $\lambda_1=2.5, \lambda_2=1.8$)** | **0.9597** | **0.7664** | **0.7742** | **0.0595** | **0.00** | **0.00** | **100.00** |

### Table 3: Look-Ahead Bias & Data Hygiene Ablation Audit (Evaluated with EINN on Out-of-Time Test)
| Pipeline Configuration | Bias / Leakage Mechanism Present | Apparent AUC-ROC | Apparent PR-AUC | Inflation vs. Strict Baseline ($\Delta$ AUC) | Methodological Validity |
| :--- | :--- | :---: | :---: | :---: | :--- |
| 1. Random 5-Fold Cross-Validation | Future macro cycles (2020–2022) leaked into training folds | 0.8415 | 0.4120 | **+0.0521 ( Severely Biased)** | Invalid (Violates temporal causality) |
| 2. Contemporaneous Target ($X_t \to Y_t$) | Predicts distress using same-year financial statements | 0.9782 | 0.8840 | **+0.1888 (Tautological)** | Invalid (100% Look-Ahead Bias) |
| 3. Overlapping Target Window ($X_t \to Y_{(t,t+1)}^{\text{ovl}}$) | Year-$t$ condition shared between $X_t$ and 2-year label $Y_{(t,t+1)}$ | 0.9597 | 0.7664 | **+0.1703 (Window Overlap)** | Valid only for conditional persistence |
| 4. Unpurged Split Boundary ($t=2019$ in Val) | 2020 COVID-19 outcome ($Y_{2020}$) leaked into Val hyperparameter tuning | 0.7968 | 0.3390 | **+0.0074 (Boundary Leakage)** | Biased model selection |
| 5. Pre-IPO Backfill Included ($N_{\text{train}}=5,463$) | Includes 1,415 pre-listing rows conditioned on future IPO survival | 0.7812 | 0.3140 | **-0.0082 (Survivorship Dilution)** | Biased base rate ($7.56\%$ pre-IPO) |
| 6. Dropping 2022 Censored/Delisted Firms | Drops 28 non-filing firms in 2022 (`FLC`, `HAI`, `BII`, `VKC`, etc.) | 0.7790 | 0.3055 | **-0.0104 (Attrition Bias)** | Misses true 2022 bond/stock defaults |
| **7. Proposed Strict Point-in-Time Purged ($Y_{i,\tau}^{\text{fwd}}$)** | **Zero Look-Ahead, Post-Listing Only, Purged Boundaries, Censoring-Aware** | **0.7894** | **0.3268** | **Baseline (0.0000)** | **Gold-Standard Q1 Protocol** |

### Table 4: Ablation Study on Theory-Informed Regularization ($\lambda_1$ Monotonicity & $\lambda_2$ Altman Boundary on Regime A)
| Configuration | $\lambda_1$ (Monotonicity) | $\lambda_2$ (Altman Boundary) | Cone Projection | AUC-ROC ($\uparrow$) | PR-AUC ($\uparrow$) | Brier ($\downarrow$) | $\text{VR}_{\text{mono}}$ (%) ($\downarrow$) | $\text{VR}_{\text{bound}}$ (%) ($\downarrow$) | ECS (%) ($\uparrow$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| ① Base MLP (Unconstrained) | 0.0 | 0.0 | No | 0.7665 | 0.2732 | 0.0896 | 88.10 | 75.00 | 15.83 |
| ② + Soft Monotonic Penalty Only | 1.0 | 0.0 | No | 0.7790 | 0.3064 | 0.0865 | 14.25 | 62.50 | 71.28 |
| ③ + Strong Soft Monotonic Penalty | 2.5 | 0.0 | No | 0.7848 | 0.3195 | 0.0853 | 2.40 | 56.25 | 81.45 |
| ④ + Soft Boundary Penalty Only | 0.0 | 1.8 | No | 0.7712 | 0.2890 | 0.0881 | 82.40 | 0.00 | 42.32 |
| ⑤ + Soft Mono + Boundary ($\mathcal{R}_{\text{mono}} + \mathcal{R}_{\text{bound}}$) | 2.5 | 1.8 | No | 0.7860 | 0.3212 | 0.0852 | 0.77 | 0.00 | 99.46 |
| **⑥ Full EINN (Soft Loss + Hard Cone Projection)** | **2.5** | **1.8** | **Yes** | **0.7894** | **0.3268** | **0.0846** | **0.00** | **0.00** | **100.00** |
