structure FinancialReport where
  netSales : Int
  cogs : Int
  sellingExp : Int
  adminExp : Int
  finExp : Int
  otherProfit : Int
  tax : Int

def ebitOp (r : FinancialReport) : Int :=
  r.netSales - r.cogs - r.sellingExp - r.adminExp

def netProfit (r : FinancialReport) : Int :=
  ebitOp r - r.finExp + r.otherProfit - r.tax

theorem ebit_op_detects_hidden_distress :
    ∃ (r : FinancialReport) (I : Int),
      0 < I ∧
      ebitOp r < I ∧
      netProfit r ≥ 0 := by
  refine ⟨⟨1000, 800, 150, 100, 50, 300, 20⟩, 60, ?_⟩
  refine ⟨by decide, by decide, by decide⟩

theorem ebit_op_detects_viable_turnaround :
    ∃ (r : FinancialReport) (I : Int),
      0 < I ∧
      ebitOp r ≥ I ∧
      netProfit r < 0 := by
  refine ⟨⟨2000, 1200, 200, 200, 100, -500, 0⟩, 100, ?_⟩
  refine ⟨by decide, by decide, by decide⟩

