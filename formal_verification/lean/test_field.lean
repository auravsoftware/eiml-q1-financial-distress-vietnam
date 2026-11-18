-- Test Linear Ordered Field in Lean 4 standard library
variable {α : Type} [LinearOrderedField α]

theorem naive_icr_tautology (P I : α) (hI : 0 < I) :
    (P + I) / I < 1 ↔ P < 0 := by
  have h1 : (P + I) / I < 1 ↔ P + I < 1 * I := div_lt_iff₀ hI
  rw [h1, one_mul]
  exact add_lt_iff_after_sub_right P I

