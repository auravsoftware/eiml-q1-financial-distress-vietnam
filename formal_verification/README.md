# Formal Mathematical Verification (Lean 4 & TLA+) for EIML Paper

This directory contains the **Formal Verification Suite** for our paper:
> **"Economically-Informed Machine Learning for Corporate Financial Distress Prediction: Eliminating Look-Ahead Bias in Emerging Markets"**

The suite uses two complementary formal verification paradigms:
1. **Deductive Theorem Proving (Lean 4)** for continuous analytical guarantees, architectural monotonicity, and algebraic tautology elimination.
2. **Model Checking (TLA+ / TLC)** for discrete temporal logic, 7-step panel hygiene, anti-look-ahead isolation, and transition safety invariants.

---

## 1. Structure

```
formal_verification/
├── README.md                      # Documentation of mathematical proofs
├── run_formal_verification.sh     # One-click automated verification runner
├── lean/
│   └── EIML_Formal.lean           # Lean 4 machine-checked theorems
└── tla/
    ├── EIML_Pipeline.tla          # TLA+ specification for 7-step panel hygiene
    ├── EIML_Pipeline.cfg          # TLC model configuration for pipeline
    ├── EIML_TemporalLogic.tla     # TLA+ specification for temporal non-leakage
    └── EIML_TemporalLogic.cfg     # TLC model configuration for temporal logic
```

---

## 2. Verified Mathematical Theorems (Lean 4)

- **Theorem 1 (Algebraic Tautology of Naive ICR):**
  $$\text{EBIT}_{\text{naive}} = \text{NetProfit} + I \implies \left(\frac{\text{EBIT}_{\text{naive}}}{I} < 1.0 \iff \text{NetProfit} < 0\right)$$
  *Proves that naive ICR is 100% algebraically degenerate.*

- **Theorem 2 (Operating EBIT Non-Degeneracy & Information Preservation):**
  $$\text{EBIT}_{\text{op}} = \text{NetSales} - C - S - A$$
  *Formally proves the existence of states where $\text{ICR}_{\text{op}} < 1$ with $\text{NetProfit} \ge 0$ (unmasking hidden operating distress like FLC/HAI/BII) and states where $\text{ICR}_{\text{op}} \ge 1$ with $\text{NetProfit} < 0$ (viable operating turnarounds).*

- **Theorem 3 (Proposed EINN Architectural Monotonicity Guarantee):**
  *By softplus weight reparameterization $\mathbf{W}^{(1)}$, strictly positive hidden layers $\mathbf{W}^{(l)} \ge 0$, monotonic activations $\psi' \ge 0$, and monotonic linear skip highway:*
  $$\forall j \in \mathcal{M}_+, \quad \frac{\partial \hat{p}}{\partial x_j} \ge 0, \qquad \forall k \in \mathcal{M}_-, \quad \frac{\partial \hat{p}}{\partial x_k} \le 0$$
  *Holds analytically across the entire input domain $\mathbb{R}^d$.*

- **Theorem 4 (Zero Violation Rate & 100% ECS Guarantee):**
  *Proves that analytical partial monotonicity directly enforces $\text{VR}_{\text{mono}} = 0.00\%$ and $\text{ECS} = 100.00\%$.*

---

## 3. Verified Temporal Invariants (TLA+ / TLC)

- **`InvZeroLookAhead`:** Proves that feature engineering and parameter estimation ($\kappa_{\text{train}}$) access strictly $\tau \le T_{\text{train}}$ and never leak out-of-time test information.
- **`InvTickerSpliceResolved`:** Proves that the $\texttt{MCO} \to \texttt{MCG}$ entity anomaly is cleanly merged without orphan records.
- **`InvPreIPOFirmlandIsolate`:** Proves that no backfilled pre-IPO observations enter the model evaluation sample.
- **`InvExpenseSignsNonNegative`:** Proves that all expense features are standardized to absolute non-negative magnitudes.
- **`InvRegimeDisentanglement`:** Proves that Regime A ($Y_{t+1}^{\text{fwd}}$) strictly evaluates forward transitions from currently solvent states, explaining the AUC discrepancy with Regime B ($Y_{t+1}^{\text{ovl}}$).
- **`InvDelistingCapture`:** Proves that regulatory delisting attrition is retained as default, eliminating survivorship bias.

---

## 4. Execution

To run the complete verification suite:

```bash
chmod +x formal_verification/run_formal_verification.sh
./formal_verification/run_formal_verification.sh
```

**Requirements:**
- Lean 4 (`elan`)
- Java 11+ (for TLC)
