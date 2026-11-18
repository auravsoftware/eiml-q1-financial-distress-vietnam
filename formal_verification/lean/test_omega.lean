theorem naive_icr_tautology_algebraic (P I : Int) (hI : 0 < I) :
    P + I < I ↔ P < 0 := by
  omega

