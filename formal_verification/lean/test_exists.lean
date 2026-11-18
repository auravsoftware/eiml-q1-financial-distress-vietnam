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
  let r : FinancialReport := {
    netSales := 1000,
    cogs := 800,
    sellingExp := 150,
    adminExp := 100,
    finExp := 50,
    otherProfit := 300,
    tax := 20
  }
  let I : Int := 60
  refine ⟨r, I, ?_⟩
  dsimp [ebitOp, netProfit]
  omega

