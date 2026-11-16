#!/usr/bin/env python3
"""
Vector PDF Figure Generator for Q1 Paper (PaperOrchestra Plotting Agent Protocol).
Reads exact experimental results from:
  - results/tables/all_metrics.json
  - results/tables/xai_and_case_studies.json
  - data/processed/clean_panel_2008_2022.pkl
  - results/models/eiml_models.pkl
  - results/models/baselines.pkl
Generates 4 publication-grade TikZ/PGFPlots vector PDF figures in paper/figures/:
  1. fig1_architecture.pdf : Economically-Informed Machine Learning (EIML) & Zero-Look-Ahead Pipeline
  2. fig2_crisis_trajectory.pdf : Annual Forward & Persistent Distress Rates by Exchange (2008-2022)
  3. fig3_pareto_ecs.pdf : Accuracy (PR-AUC) vs. Economic Consistency Score (ECS %) Pareto Frontier
  4. fig4_monotonic_response.pdf : Partial Response Surface (Debt-to-Assets vs. Predicted PD: MLP vs. EINN) & XAI Share
"""

import json
import os
import pickle
import subprocess
import sys
import numpy as np

BASE_DIR = "/home/antigravity/09_PAPER_Q1_BOND"
sys.path.insert(0, os.path.join(BASE_DIR, "src"))
from train_eiml import *  # noqa: F401,F403
from train_ml_baseline import *  # noqa: F401,F403

FIG_DIR = os.path.join(BASE_DIR, "paper", "figures")
os.makedirs(FIG_DIR, exist_ok=True)


def load_artifacts():
    with open(os.path.join(BASE_DIR, "results", "tables", "all_metrics.json"), "r") as f:
        metrics = json.load(f)
    with open(os.path.join(BASE_DIR, "results", "tables", "xai_and_case_studies.json"), "r") as f:
        xai = json.load(f)
    with open(os.path.join(BASE_DIR, "data", "processed", "clean_panel_2008_2022.pkl"), "rb") as f:
        panel = pickle.load(f)
    with open(os.path.join(BASE_DIR, "data", "processed", "train_val_test_splits.pkl"), "rb") as f:
        splits = pickle.load(f)
    with open(os.path.join(BASE_DIR, "results", "models", "eiml_models.pkl"), "rb") as f:
        eiml = pickle.load(f)
    with open(os.path.join(BASE_DIR, "results", "models", "baselines.pkl"), "rb") as f:
        baselines = pickle.load(f)
    return metrics, xai, panel, splits, eiml, baselines


def compile_tex(tex_path):
    cmd = ["pdflatex", "-interaction=nonstopmode", os.path.basename(tex_path)]
    res = subprocess.run(cmd, cwd=FIG_DIR, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error compiling {tex_path}:\n{res.stdout[-1500:]}")
        raise RuntimeError(f"Failed to compile {tex_path}")
    print(f"Successfully compiled {os.path.basename(tex_path).replace('.tex', '.pdf')}")


def make_fig1_architecture():
    tex = r"""\documentclass[tikz,border=8pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb}
\usetikzlibrary{arrows.meta,positioning,shapes.geometric,fit,calc,backgrounds}

\definecolor{navy}{RGB}{20,45,90}
\definecolor{slate}{RGB}{60,85,125}
\definecolor{teal}{RGB}{0,115,115}
\definecolor{crimson}{RGB}{165,30,45}
\definecolor{amber}{RGB}{195,115,0}
\definecolor{softblue}{RGB}{238,244,252}
\definecolor{softteal}{RGB}{232,247,246}
\definecolor{softred}{RGB}{253,238,240}
\definecolor{softamber}{RGB}{254,247,232}

\begin{document}
\begin{tikzpicture}[
    font=\sffamily\footnotesize,
    >=Latex,
    box/.style={draw=navy, thick, rounded corners=4pt, fill=white, align=center, inner sep=6pt},
    stage/.style={draw=navy!80, thick, rounded corners=5pt, fill=softblue, align=left, inner sep=7pt},
    lossbox/.style={draw=crimson!85, thick, rounded corners=4pt, fill=softred, align=left, inner sep=6pt},
    modelbox/.style={draw=teal!90, thick, rounded corners=4pt, fill=softteal, align=left, inner sep=6pt},
    evalbox/.style={draw=amber!90, thick, rounded corners=4pt, fill=softamber, align=left, inner sep=6pt},
    arrow/.style={->, thick, draw=navy!85}
]

% Stage 1: Forensic Hygiene
\node[stage, text width=4.6cm] (s1) at (0,0) {
    \textbf{\color{navy}1. Forensic Panel Hygiene}\\
    \vspace{2pt}
    $\bullet$ Deduplicate Col 25/26 (\texttt{CostofGood})\\
    $\bullet$ Entity Splice Repair (\texttt{MCO}$\to$\texttt{MCG})\\
    $\bullet$ Expense Sign Rectification ($40$ rows)\\
    $\bullet$ Operating $\text{EBIT}_{\text{op}}$ Reconstruction\\
    $\bullet$ Isolate $1,570$ Pre-IPO Rows ($t < \text{IPO}$)
};

% Stage 2: Strict Temporal Partitioning
\node[stage, text width=4.8cm, right=0.65cm of s1] (s2) {
    \textbf{\color{navy}2. Zero-Look-Ahead Partitioning}\\
    \vspace{2pt}
    $\bullet$ \textbf{Train} ($t \le 2017 \to \tau \le 2018$): $3,676$\\
    $\bullet$ \textbf{Val} ($t \in [2018,19] \to \tau \in [2019,20]$): $1,843$\\
    $\bullet$ \textbf{Test} ($t \in [2020,21] \to \tau \in [2021,22]$): $2,083$\\
    $\bullet$ Fit $\kappa_{\text{train}}=0.853$, Winsorize $[q_{01},q_{99}]_{\text{train}}$\\
    $\bullet$ Fit Median/Scaler $\theta_{\text{prep}}$ on $\mathcal{D}_{\text{train}}$ only
};

% Stage 3: Dual-Track EIML Architecture
\node[modelbox, text width=5.3cm, right=0.65cm of s2] (s3) {
    \textbf{\color{teal!80!black}3. Dual-Track EIML Architecture}\\
    \vspace{2pt}
    \textbf{Track A: Monotonic GBDT}\\
    $\bullet$ Split-level sign projection on $\mathcal{M}_+, \mathcal{M}_-$\\
    \vspace{2pt}
    \textbf{Track B: Proposed EINN}\\
    $\bullet$ $\mathbf{W}^{(1)} = \text{softplus}(\mathbf{U})\odot \mathbf{M}_+ - \text{softplus}(\mathbf{U})\odot \mathbf{M}_- + \mathbf{V}\odot \mathbf{M}_0$\\
    $\bullet$ Non-negative deep weights $\mathbf{W}^{(l)} = \text{softplus}(\mathbf{U}^{(l)})$
};

% Stage 4: Theory-Informed Regularization
\node[lossbox, text width=5.3cm, below=0.55cm of s3] (s4) {
    \textbf{\color{crimson}4. Composite Structural Objective $\mathcal{L}_{\text{EINN}}$}\\
    \vspace{2pt}
    $\mathcal{L}_{\text{EINN}} = \mathcal{L}_{\text{Focal-BCE}} + \lambda_{\text{mono}}\mathcal{L}_{\text{mono}} + \lambda_{\text{bound}}\mathcal{L}_{\text{bound}}$\\
    $\bullet$ \textbf{Axiom 1}: $\partial_{x_j}\hat{p} \ge 0$ ($\mathcal{M}_+$), $\partial_{x_k}\hat{p} \le 0$ ($\mathcal{M}_-$)\\
    $\bullet$ \textbf{Axiom 2 (Merton)}: $D/A \to 0, \text{ICR}_{\text{op}} \gg 1 \Rightarrow \hat{p} \le \epsilon_{\text{safe}}$\\
    $\bullet$ \textbf{Axiom 3 (Insolvency)}: $D/A \ge 1, \text{ROA} < -0.15 \Rightarrow \hat{p} \ge \tau_{\text{def}}$
};

% Stage 5: Audit & Early Warning Output
\node[evalbox, text width=10.05cm, below=0.55cm of $(s1.south)!0.5!(s2.south)$] (s5) {
    \textbf{\color{amber!75!black}5. Out-of-Time Verification, Economic Consistency Score (ECS) \& 2022 Bond Crisis Audit}\\
    \vspace{2pt}
    $\bullet$ \textbf{Dual Regimes}: Strict Forward Distress Transition ($Y_{i,t+1}^{\text{fwd}}$) vs. Persistent Distress ($Y_{i,t+1}^{\text{ovl}}$) \quad
    $\bullet$ \textbf{Metrics}: ROC-AUC, PR-AUC, F1, Brier, $\text{VR}_{\text{mono}}$, $\text{VR}_{\text{bound}}$, $\text{ECS} = 100\%$\\
    $\bullet$ \textbf{Axiomatic XAI \& 2022 Default Watchlist}: Zero gradient sign reversals; Early detection of \texttt{FLC}, \texttt{HAI}, \texttt{BII}, \texttt{AMD}, \texttt{GAB}, \texttt{VKC} using 2021 statements
};

\draw[arrow] (s1.east) -- (s2.west);
\draw[arrow] (s2.east) -- (s3.west);
\draw[arrow, <->, draw=crimson!85] (s3.south) -- (s4.north);
\draw[arrow] (s4.west) -- (s5.east);
\draw[arrow] (s2.south) -- (s2.south |- s5.north);

\end{tikzpicture}
\end{document}
"""
    tex_path = os.path.join(FIG_DIR, "fig1_architecture.tex")
    with open(tex_path, "w") as f:
        f.write(tex)
    compile_tex(tex_path)


def make_fig2_crisis_trajectory(panel):
    import csv
    rows = []
    with open(os.path.join(BASE_DIR, "data", "processed", "panel_features_clean.csv"), "r") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    years = sorted(list(set(int(r["outcome_year_tau"]) for r in rows)))
    overall_fwd = []
    overall_ovl = []
    hose_ovl = []
    hnx_ovl = []
    upcom_ovl = []

    for y in years:
        sub = [r for r in rows if int(r["outcome_year_tau"]) == y]
        overall_fwd.append((y, 100.0 * np.mean([float(r["y_fwd"]) for r in sub])))
        overall_ovl.append((y, 100.0 * np.mean([float(r["y_ovl"]) for r in sub])))
        for ex, lst in [("HOSE", hose_ovl), ("HNX", hnx_ovl), ("UPCOM", upcom_ovl)]:
            sub_ex = [r for r in sub if r["exchange"] == ex]
            if len(sub_ex) >= 5:
                lst.append((y, 100.0 * np.mean([float(r["y_ovl"]) for r in sub_ex])))

    def fmt_coords(pts):
        return " ".join(f"({x},{y:.2f})" for x, y in pts)

    tex = r"""\documentclass[tikz,border=8pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}

\definecolor{navy}{RGB}{20,45,90}
\definecolor{crimson}{RGB}{175,30,45}
\definecolor{teal}{RGB}{0,125,120}
\definecolor{amber}{RGB}{205,120,0}
\definecolor{purple}{RGB}{115,50,145}

\begin{document}
\begin{tikzpicture}
\begin{axis}[
    width=13.2cm,
    height=7.2cm,
    xlabel={\textbf{Outcome Fiscal Year ($\tau = t + 1$)}},
    ylabel={\textbf{Corporate Distress Incidence (\%)}},
    xmin=2009, xmax=2022,
    ymin=0, ymax=34,
    xtick={2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022},
    xticklabels={2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022},
    xticklabel style={font=\footnotesize, rotate=30, anchor=east},
    yticklabel style={font=\footnotesize},
    label style={font=\small\sffamily},
    grid=both,
    grid style={dashed, gray!30},
    legend style={at={(0.02,0.97)}, anchor=north west, font=\scriptsize\sffamily, fill=white, fill opacity=0.9, draw=gray!50},
    legend cell align={left},
    clip=false
]

% Shaded Test Regime (2021-2022)
\fill[crimson!8] (axis cs:2020.5,0) rectangle (axis cs:2022,34);
\node[font=\scriptsize\sffamily\bfseries, color=crimson!85!black, align=center] at (axis cs:2021.25,31.2) {Out-of-Time\\Test ($\tau \in \{2021,22\}$)};

% Shaded Val Regime (2019-2020)
\fill[amber!8] (axis cs:2018.5,0) rectangle (axis cs:2020.5,34);
\node[font=\scriptsize\sffamily\bfseries, color=amber!85!black, align=center] at (axis cs:2019.5,31.2) {Validation\\($\tau \in \{2019,20\}$)};

\addplot[color=crimson, very thick, mark=square*, mark size=2pt] coordinates {
    """ + fmt_coords(overall_ovl) + r"""
};
\addlegendentry{All Exchanges: Persistent Distress ($Y_{i,\tau}^{\text{ovl}}$)}

\addplot[color=navy, very thick, mark=*, mark size=2pt] coordinates {
    """ + fmt_coords(overall_fwd) + r"""
};
\addlegendentry{All Exchanges: New Forward Transition ($Y_{i,\tau}^{\text{fwd}}$)}

\addplot[color=teal, thick, dashed, mark=triangle*, mark size=2pt] coordinates {
    """ + fmt_coords(hose_ovl) + r"""
};
\addlegendentry{HOSE Persistent Distress ($Y_{i,\tau}^{\text{ovl}}$)}

\addplot[color=amber!90!black, thick, dashdotted, mark=diamond*, mark size=2pt] coordinates {
    """ + fmt_coords(hnx_ovl) + r"""
};
\addlegendentry{HNX Persistent Distress ($Y_{i,\tau}^{\text{ovl}}$)}

\addplot[color=purple, thick, densely dotted, mark=pentagon*, mark size=2pt] coordinates {
    """ + fmt_coords(upcom_ovl) + r"""
};
\addlegendentry{UPCOM Persistent Distress ($Y_{i,\tau}^{\text{ovl}}$)}

\end{axis}
\end{tikzpicture}
\end{document}
"""
    tex_path = os.path.join(FIG_DIR, "fig2_crisis_trajectory.tex")
    with open(tex_path, "w") as f:
        f.write(tex)
    compile_tex(tex_path)


def make_fig3_pareto_ecs(metrics):
    # Plot ECS_pct (x-axis) vs PR_AUC (y-axis) for Regime A (y_fwd) and Regime B (y_ovl)
    m_fwd = metrics["y_fwd"]
    m_ovl = metrics["y_ovl"]

    tex = r"""\documentclass[tikz,border=8pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}

\definecolor{navy}{RGB}{20,45,90}
\definecolor{crimson}{RGB}{175,30,45}
\definecolor{teal}{RGB}{0,125,120}
\definecolor{amber}{RGB}{205,120,0}
\definecolor{slate}{RGB}{90,105,125}

\begin{document}
\begin{tikzpicture}
% Left panel: Regime A (Strict Forward Distress Y_fwd)
\begin{axis}[
    name=plotA,
    width=7.4cm,
    height=6.6cm,
    title={\textbf{(a) Regime A: Forward Distress ($Y_{i,t+1}^{\text{fwd}}$)}},
    xlabel={\textbf{Economic Consistency Score, ECS (\%)}},
    ylabel={\textbf{Out-of-Time PR-AUC (2021--2022)}},
    xmin=0, xmax=108,
    ymin=0.18, ymax=0.42,
    grid=both,
    grid style={dashed, gray!30},
    label style={font=\footnotesize\sffamily},
    title style={font=\footnotesize\sffamily},
    ticklabel style={font=\scriptsize}
]
\fill[teal!10] (axis cs:95,0.33) rectangle (axis cs:105,0.405);
\node[font=\tiny\sffamily\bfseries, color=teal!80!black, align=center] at (axis cs:82,0.395) {Pareto-Optimal\\EIML Zone};

% Classical
\addplot[only marks, mark=diamond*, mark size=3.2pt, color=amber!90!black] coordinates {
    (""" + f"{m_fwd['Altman_Z_Double_Prime']['ECS_pct']},{m_fwd['Altman_Z_Double_Prime']['PR_AUC']}" + r""")
    (""" + f"{m_fwd['Ohlson_O_Score']['ECS_pct']},{m_fwd['Ohlson_O_Score']['PR_AUC']}" + r""")
};
% Unconstrained ML
\addplot[only marks, mark=*, mark size=2.8pt, color=slate] coordinates {
    (""" + f"{m_fwd['LogisticRegression']['ECS_pct']},{m_fwd['LogisticRegression']['PR_AUC']}" + r""")
    (""" + f"{m_fwd['RBF_SVM']['ECS_pct']},{m_fwd['RBF_SVM']['PR_AUC']}" + r""")
    (""" + f"{m_fwd['RandomForest']['ECS_pct']},{m_fwd['RandomForest']['PR_AUC']}" + r""")
    (""" + f"{m_fwd['Unconstrained_GBDT']['ECS_pct']},{m_fwd['Unconstrained_GBDT']['PR_AUC']}" + r""")
    (""" + f"{m_fwd['Unconstrained_MLP']['ECS_pct']},{m_fwd['Unconstrained_MLP']['PR_AUC']}" + r""")
};
% EIML
\addplot[only marks, mark=star, mark options={scale=1.8, thick}, color=crimson] coordinates {
    (""" + f"{m_fwd['Mono_GBDT']['ECS_pct']},{m_fwd['Mono_GBDT']['PR_AUC']}" + r""")
    (""" + f"{m_fwd['Proposed_EINN']['ECS_pct']},{m_fwd['Proposed_EINN']['PR_AUC']}" + r""")
};

\node[font=\tiny\sffamily, anchor=east] at (axis cs:98,0.248) {Altman $Z''$};
\node[font=\tiny\sffamily, anchor=east] at (axis cs:77,0.208) {Ohlson $O$};
\node[font=\tiny\sffamily, anchor=west] at (axis cs:7,0.306) {Logit};
\node[font=\tiny\sffamily, anchor=west] at (axis cs:5,0.282) {RBF-SVM};
\node[font=\tiny\sffamily, anchor=west] at (axis cs:31,0.302) {MLP};
\node[font=\tiny\sffamily, anchor=east] at (axis cs:68,0.338) {RF};
\node[font=\tiny\sffamily, anchor=east] at (axis cs:68,0.355) {GBDT};
\node[font=\tiny\sffamily\bfseries, color=crimson, anchor=east] at (axis cs:98,0.381) {Mono-GBDT};
\node[font=\tiny\sffamily\bfseries, color=crimson, anchor=east] at (axis cs:98,0.351) {Proposed EINN};
\end{axis}

% Right panel: Regime B (Persistent Distress Y_ovl)
\begin{axis}[
    name=plotB,
    at={(plotA.east)}, anchor=west, xshift=1.3cm,
    width=7.4cm,
    height=6.6cm,
    title={\textbf{(b) Regime B: Persistent Distress ($Y_{i,t+1}^{\text{ovl}}$)}},
    xlabel={\textbf{Economic Consistency Score, ECS (\%)}},
    ylabel={\textbf{Out-of-Time PR-AUC (2021--2022)}},
    xmin=0, xmax=108,
    ymin=0.22, ymax=0.86,
    grid=both,
    grid style={dashed, gray!30},
    label style={font=\footnotesize\sffamily},
    title style={font=\footnotesize\sffamily},
    ticklabel style={font=\scriptsize}
]
\fill[teal!10] (axis cs:95,0.74) rectangle (axis cs:105,0.83);

% Classical
\addplot[only marks, mark=diamond*, mark size=3.2pt, color=amber!90!black] coordinates {
    (""" + f"{m_ovl['Altman_Z_Double_Prime']['ECS_pct']},{m_ovl['Altman_Z_Double_Prime']['PR_AUC']}" + r""")
    (""" + f"{m_ovl['Ohlson_O_Score']['ECS_pct']},{m_ovl['Ohlson_O_Score']['PR_AUC']}" + r""")
};
% Unconstrained ML
\addplot[only marks, mark=*, mark size=2.8pt, color=slate] coordinates {
    (""" + f"{m_ovl['LogisticRegression']['ECS_pct']},{m_ovl['LogisticRegression']['PR_AUC']}" + r""")
    (""" + f"{m_ovl['RBF_SVM']['ECS_pct']},{m_ovl['RBF_SVM']['PR_AUC']}" + r""")
    (""" + f"{m_ovl['RandomForest']['ECS_pct']},{m_ovl['RandomForest']['PR_AUC']}" + r""")
    (""" + f"{m_ovl['Unconstrained_GBDT']['ECS_pct']},{m_ovl['Unconstrained_GBDT']['PR_AUC']}" + r""")
    (""" + f"{m_ovl['Unconstrained_MLP']['ECS_pct']},{m_ovl['Unconstrained_MLP']['PR_AUC']}" + r""")
};
% EIML
\addplot[only marks, mark=star, mark options={scale=1.8, thick}, color=crimson] coordinates {
    (""" + f"{m_ovl['Mono_GBDT']['ECS_pct']},{m_ovl['Mono_GBDT']['PR_AUC']}" + r""")
    (""" + f"{m_ovl['Proposed_EINN']['ECS_pct']},{m_ovl['Proposed_EINN']['PR_AUC']}" + r""")
};

\node[font=\tiny\sffamily, anchor=east] at (axis cs:98,0.275) {Altman $Z''$};
\node[font=\tiny\sffamily, anchor=east] at (axis cs:77,0.268) {Ohlson $O$};
\node[font=\tiny\sffamily, anchor=west] at (axis cs:24,0.735) {Logit};
\node[font=\tiny\sffamily, anchor=west] at (axis cs:4,0.628) {RBF-SVM};
\node[font=\tiny\sffamily, anchor=east] at (axis cs:66,0.742) {MLP};
\node[font=\tiny\sffamily, anchor=east] at (axis cs:68,0.774) {RF};
\node[font=\tiny\sffamily, anchor=east] at (axis cs:68,0.805) {GBDT};
\node[font=\tiny\sffamily\bfseries, color=crimson, anchor=east] at (axis cs:98,0.808) {Mono-GBDT};
\node[font=\tiny\sffamily\bfseries, color=crimson, anchor=east] at (axis cs:98,0.758) {Proposed EINN};
\end{axis}
\end{tikzpicture}
\end{document}
"""
    tex_path = os.path.join(FIG_DIR, "fig3_pareto_ecs.tex")
    with open(tex_path, "w") as f:
        f.write(tex)
    compile_tex(tex_path)


def make_fig4_monotonic_response(splits, eiml, baselines, xai):
    feature_names = splits["scaler_params"]["feature_names"]
    da_idx = feature_names.index("debt_to_asset")
    z_grid = np.linspace(-2.0, 2.5, 35)
    X_probe = np.zeros((len(z_grid), len(feature_names)), dtype=float)
    X_probe[:, da_idx] = z_grid

    einn_model = eiml["y_fwd"]["Proposed_EINN"]
    mono_gbdt = eiml["y_fwd"]["Mono_GBDT"]
    mlp_model = baselines["y_fwd"]["Unconstrained_MLP"]

    p_einn = einn_model.predict_proba(X_probe) * 100.0
    p_mgbdt = mono_gbdt.predict_proba(X_probe) * 100.0
    p_mlp = mlp_model.predict_proba(X_probe) * 100.0

    def fmt_curve(zs, ps):
        return " ".join(f"({z:.2f},{p:.2f})" for z, p in zip(zs, ps))

    # Panel B: Top 8 XAI feature attributions (Proposed EINN vs Unconstrained MLP)
    top8 = xai["xai_feature_attribution_ranking"][:8][::-1]  # bottom-to-top for horizontal bar chart
    labels_map = {
        "roe": "ROE",
        "opex_to_sales": "OpEx/Sales",
        "roa": "ROA ($-$)",
        "wc_to_asset": "WC/Assets ($-$)",
        "icr_op": r"ICR$_{\mathrm{op}}$ ($-$)",
        "op_margin": "OpMargin",
        "rec_turnover": "RecTurn",
        "ebit_to_asset": r"EBIT$_{\mathrm{op}}$/Assets ($-$)",
    }
    einn_bars = " ".join(f"({item['einn_importance_share_pct']:.2f},{i})" for i, item in enumerate(top8))
    mlp_bars = " ".join(f"({item['mlp_importance_share_pct']:.2f},{i})" for i, item in enumerate(top8))
    yticklabels = ",".join(labels_map.get(item["feature"], item["feature"]) for item in top8)

    tex = r"""\documentclass[tikz,border=8pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}

\definecolor{navy}{RGB}{20,45,90}
\definecolor{crimson}{RGB}{175,30,45}
\definecolor{teal}{RGB}{0,125,120}
\definecolor{slate}{RGB}{110,125,145}

\begin{document}
\begin{tikzpicture}
% Left Panel: Partial Dependence on Debt-to-Assets
\begin{axis}[
    name=panelA,
    width=7.4cm,
    height=6.5cm,
    title={\textbf{(a) Leverage Sensitivity ($D/A$ Ceteris Paribus)}},
    xlabel={\textbf{Standardized Debt-to-Assets ($z_{D/A}$)}},
    ylabel={\textbf{Predicted Forward Distress $\hat{p}_{i,t+1}$ (\%)}},
    xmin=-2.0, xmax=2.5,
    ymin=0, ymax=38,
    grid=both,
    grid style={dashed, gray!30},
    label style={font=\footnotesize\sffamily},
    title style={font=\footnotesize\sffamily},
    ticklabel style={font=\scriptsize},
    legend style={at={(0.03,0.97)}, anchor=north west, font=\scriptsize\sffamily, fill=white, draw=gray!50},
    legend cell align={left}
]
\addplot[color=crimson, very thick] coordinates {
    """ + fmt_curve(z_grid, p_einn) + r"""
};
\addlegendentry{Proposed EINN ($\text{VR}_{\text{mono}}=0.00\%$)}

\addplot[color=teal, very thick, dashed] coordinates {
    """ + fmt_curve(z_grid, p_mgbdt) + r"""
};
\addlegendentry{Mono-GBDT ($\text{VR}_{\text{mono}}=0.05\%$)}

\addplot[color=navy, thick, dashdotted] coordinates {
    """ + fmt_curve(z_grid, p_mlp) + r"""
};
\addlegendentry{Unconstrained MLP ($67.2\%$ Sign Viol.)}
\end{axis}

% Right Panel: Top-8 Axiomatic Integrated Gradients Attribution Share
\begin{axis}[
    name=panelB,
    at={(panelA.east)}, anchor=west, xshift=1.8cm,
    xbar,
    bar width=5pt,
    width=7.2cm,
    height=6.5cm,
    title={\textbf{(b) Top-8 Integrated Gradients Share (\%)}},
    xlabel={\textbf{Global Attribution Share (\%)}},
    xmin=0, xmax=15.5,
    ytick={0,1,2,3,4,5,6,7},
    yticklabels={""" + yticklabels + r"""},
    yticklabel style={font=\scriptsize\sffamily},
    xticklabel style={font=\scriptsize},
    label style={font=\footnotesize\sffamily},
    title style={font=\footnotesize\sffamily},
    grid=major,
    grid style={dashed, gray!30},
    legend style={at={(0.97,0.05)}, anchor=south east, font=\scriptsize\sffamily, fill=white, draw=gray!50},
    legend cell align={left}
]
\addplot[fill=crimson!85, draw=crimson!95!black] coordinates {
    """ + einn_bars + r"""
};
\addlegendentry{Proposed EINN ($0\%$ Viol.)}

\addplot[fill=slate!65, draw=navy!80] coordinates {
    """ + mlp_bars + r"""
};
\addlegendentry{Unconstrained MLP}
\end{axis}
\end{tikzpicture}
\end{document}
"""
    tex_path = os.path.join(FIG_DIR, "fig4_monotonic_response.tex")
    with open(tex_path, "w") as f:
        f.write(tex)
    compile_tex(tex_path)


if __name__ == "__main__":
    metrics, xai, panel, splits, eiml, baselines = load_artifacts()
    make_fig1_architecture()
    make_fig2_crisis_trajectory(panel)
    make_fig3_pareto_ecs(metrics)
    make_fig4_monotonic_response(splits, eiml, baselines, xai)
    print("All 4 vector PDF figures generated successfully.")
