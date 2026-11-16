# Economics-Informed Machine Learning (EIML) for Corporate Financial Distress Prediction in Emerging Markets

[![Q1 Paper PDF (English)](https://img.shields.io/badge/PDF-English_Q1_Manuscript_(19p)-blue)](paper/final_paper.pdf)
[![Q1 Paper PDF (Vietnamese)](https://img.shields.io/badge/PDF-Bản_Dịch_Tiếng_Việt_(20p)-green)](paper/final_paper_vi.pdf)

> **Title (EN):** *Economics-Informed Machine Learning for Corporate Financial Distress Prediction in Emerging Markets: Monotonic Structural Regularization, Forensic Panel Sanitization, and Out-of-Time Crisis Generalization*  
> **Tên đề tài (VI):** *Học máy Tích hợp Lý thuyết Kinh tế trong Dự báo Kiệt quệ Tài chính Doanh nghiệp tại Thị trường Mới nổi: Chính quy hóa Cấu trúc Đơn điệu, Làm sạch Pháp y Dữ liệu Bảng và Tổng quát hóa Ngoài mẫu trong Khủng hoảng*

---

## 📄 Full Paper & Manuscripts (Bài Báo Hoàn Chỉnh)

- **English Q1 PDF (LaTeX Compiled, 19 pages):** [`paper/final_paper.pdf`](paper/final_paper.pdf) | **LaTeX Source:** [`paper/main.tex`](paper/main.tex) | **Markdown:** [`paper/Q1_Paper_Orchestra_EIML_Full_Manuscript.md`](paper/Q1_Paper_Orchestra_EIML_Full_Manuscript.md)
- **Vietnamese Translated PDF (LaTeX T5 Vector Compiled, 20 pages):** [`paper/final_paper_vi.pdf`](paper/final_paper_vi.pdf) | **LaTeX Source:** [`paper/main_vi.tex`](paper/main_vi.tex) | **Markdown:** [`paper/Ban_Dich_Tieng_Viet_Q1_Paper_EIML.md`](paper/Ban_Dich_Tieng_Viet_Q1_Paper_EIML.md)
- **Verified Bibliography (52 Q1–Q4 Peer-Reviewed References):** [`paper/references.bib`](paper/references.bib) | [`paper/citation_map.json`](paper/citation_map.json)

---

## 🗂️ Repository Structure (Cấu Trúc Thư Mục)

```text
├── configs/
│   └── config.yaml                                  # Hyperparameters, temporal split & monotonic axiom config
├── data/
│   ├── raw/
│   │   └── data-financial-0601.xlsx                 # Original raw dataset (11,455 rows x 35 columns, 2008–2022)
│   └── processed/
│       ├── clean_panel_2008_2022.csv                # Sanitized post-forensic panel (CSV)
│       ├── clean_panel_2008_2022.pkl                # Sanitized post-forensic panel (Pickle)
│       ├── panel_features_clean.csv                 # Zero-look-ahead engineered features & dual targets (7,602 pairs)
│       ├── train_val_test_splits.pkl                # Strict chronological Train / Val / Out-of-Time Test splits
│       ├── forensic_cleaning_audit_report.json      # 7-stage forensic accounting audit log
│       └── experimental_setup_summary.json          # Dataset & split statistics summary
├── docs/
│   └── ORIGINAL_SPEC_README.md                      # Original research specification & guide
├── paper/
│   ├── main.tex                                     # Full Q1 English LaTeX manuscript
│   ├── main_vi.tex                                  # Full Q1 Vietnamese LaTeX manuscript (UTF-8 T5 font encoding)
│   ├── final_paper.pdf                              # Compiled English PDF (19 pages)
│   ├── final_paper_vi.pdf                           # Compiled Vietnamese PDF (20 pages)
│   ├── references.bib                               # 52 verified Q1–Q4 BibTeX references
│   ├── citation_map.json                            # Structured literature review mapping
│   ├── t5enc.def                                    # Vietnamese T5 vector font encoding definitions for pdflatex
│   ├── Q1_Paper_Orchestra_EIML_Full_Manuscript.md   # English full manuscript in Markdown
│   ├── Ban_Dich_Tieng_Viet_Q1_Paper_EIML.md         # Vietnamese full manuscript in Markdown
│   └── figures/
│       ├── fig1_architecture.pdf / .tex             # Figure 1: EIML & 7-stage forensic pipeline architecture
│       ├── fig2_crisis_trajectory.pdf / .tex        # Figure 2: 2008–2022 distress trajectory & macro crisis regimes
│       ├── fig3_pareto_ecs.pdf / .tex               # Figure 3: Out-of-time PR-AUC vs. ECS Pareto frontier
│       └── fig4_monotonic_response.pdf / .tex       # Figure 4: Partial response curves & Integrated Gradients XAI
├── results/
│   ├── experimental_setup_verification.json         # 7/7 Zero-Look-Ahead & pipeline verification checks
│   ├── models/
│   │   ├── baselines.pkl                            # Trained classical & unconstrained ML baselines
│   │   └── eiml_models.pkl                          # Trained Mono-GBDT & Proposed EINN models
│   └── tables/
│       ├── all_metrics.json                         # Out-of-time evaluation metrics (Regime A & Regime B)
│       ├── benchmark_tables.tex                     # Auto-generated LaTeX booktabs benchmark table
│       └── xai_and_case_studies.json                # Integrated Gradients XAI & 2022 Bond Crisis case studies
├── src/
│   ├── data_loader.py                               # 7-stage forensic accounting data cleaner
│   ├── feature_engineering.py                       # Zero-look-ahead feature & dual-regime label constructor
│   ├── verify_experimental_setup.py                 # Automated leakage & split audit script
│   ├── theory_losses.py                             # Monotonic softplus reparameterization & Merton/Altman losses
│   ├── train_ml_baseline.py                         # Classical & unconstrained ML baseline trainer
│   ├── train_eiml.py                                # Proposed EINN & Mono-GBDT trainer
│   ├── evaluation.py                                # Out-of-time predictive & Economic Consistency Score (ECS) evaluator
│   ├── explainability.py                            # Axiomatic Integrated Gradients & 2022 crisis case study auditor
│   └── generate_paper_figures.py                    # Standalone TikZ/PGFPlots vector PDF figure generator
└── requirements.txt                                 # Python dependencies
```

---

## 🔬 Key Empirical Results (Tóm Tắt Kết Quả Thực Nghiệm Ngoài Mẫu 2021–2022, $N_{\text{test}}=2,083$)

| Regime | Model | ROC-AUC $\uparrow$ | PR-AUC $\uparrow$ | F1 $\uparrow$ | Brier $\downarrow$ | $\text{VR}_{\text{mono}}$ (%) $\downarrow$ | $\text{VR}_{\text{bound}}$ (%) $\downarrow$ | ECS (%) $\uparrow$ |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Regime A ($Y_{i,t+1}^{\text{fwd}}$)** | Altman $Z''$-Score (1995) | 0.6648 | 0.2487 | 0.2901 | 0.2954 | 0.00 | 0.00 | 100.00 |
| *(1-Year Forward New Transition)* | Ohlson $O$-Score (1980) | 0.6453 | 0.2085 | 0.2602 | 0.1550 | 0.00 | 68.75 | 79.38 |
| *Base Rate: $10.99\%$* | Logistic Regression (L2) | 0.7732 | 0.3044 | 0.4139 | 0.0854 | 100.00 | 81.25 | 5.63 |
| | RBF-Kernel SVM | 0.7504 | 0.2886 | 0.3574 | 0.0877 | 95.30 | 100.00 | 3.29 |
| | Random Forest | **0.8062** | 0.3433 | 0.4199 | 0.0822 | 0.77 | 100.00 | 69.46 |
| | Unconstrained GBDT | 0.7991 | 0.3493 | **0.4201** | 0.0819 | 0.05 | 100.00 | 69.97 |
| | Unconstrained MLP | 0.7764 | 0.3021 | 0.3919 | 0.0879 | 71.96 | 68.75 | 29.00 |
| | **Mono-GBDT (Proposed)** | **0.8021** | **0.3793** | **0.4187** | **0.0798** | **0.05** | **0.00** | **99.97** |
| | **Proposed EINN (Proposed)** | **0.7870** | **0.3517** | **0.3943** | **0.0848** | **0.00** | **0.00** | **100.00** |
| **Regime B ($Y_{i,t+1}^{\text{ovl}}$)** | Altman $Z''$-Score (1995) | 0.6440 | 0.2713 | 0.3298 | 0.2917 | 0.00 | 0.00 | 100.00 |
| *(Multi-Period Persistent Distress)* | Ohlson $O$-Score (1980) | 0.6528 | 0.2713 | 0.3212 | 0.1674 | 0.00 | 68.75 | 79.38 |
| *Base Rate: $17.28\%$* | Logistic Regression (L2) | 0.9548 | 0.7351 | 0.7580 | 0.0664 | 94.10 | 37.50 | 22.88 |
| | RBF-Kernel SVM | 0.8864 | 0.6282 | 0.5808 | 0.0969 | 96.54 | 100.00 | 2.42 |
| | Random Forest | 0.9620 | 0.7746 | 0.8011 | 0.0600 | 2.21 | 93.75 | 70.33 |
| | Unconstrained GBDT | 0.9640 | 0.7820 | 0.8060 | 0.0496 | 0.00 | 100.00 | 70.00 |
| | Unconstrained MLP | 0.9557 | 0.7526 | 0.7425 | 0.0606 | 39.94 | 12.50 | 68.29 |
| | **Mono-GBDT (Proposed)** | **0.9648** | **0.7932** | **0.8076** | **0.0490** | **0.00** | **0.00** | **100.00** |
| | **Proposed EINN (Proposed)** | **0.9592** | **0.7658** | **0.7620** | **0.0590** | **0.00** | **0.00** | **100.00** |

---

## 🚀 Reproducing the Pipeline (Hướng Dẫn Chạy Lại Thực Nghiệm & Biên Dịch PDF)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run 7-stage forensic data cleaning & zero-look-ahead feature engineering
python3 src/data_loader.py
python3 src/feature_engineering.py
python3 src/verify_experimental_setup.py

# 3. Train baselines, EIML models, evaluate ECS, and run Integrated Gradients XAI
python3 src/train_ml_baseline.py
python3 src/explainability.py

# 4. Generate standalone vector PDF figures and compile English & Vietnamese PDFs
python3 src/generate_paper_figures.py
cd paper
pdflatex -interaction=nonstopmode main.tex && bibtex main && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main_vi.tex && bibtex main_vi && pdflatex -interaction=nonstopmode main_vi.tex && pdflatex -interaction=nonstopmode main_vi.tex
```
