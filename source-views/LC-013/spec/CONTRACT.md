# LC-EXP-013 candidate contract and predecessor delta

Inherit the `LC-EXP-012` semantic grammar, validation, permissions, eligible graph, three-valued connectives and history-preserving REASSESS/REWRITE, whose unchanged documentation is frozen within `history/LC-EXP-012-CONTESTED-STANDING-001.zip`. The **following scoped changes** define this successor only:

1. **Typed pending relation:** a scoped pending `CORRECTS` or `SUPERSEDES` relationship targeting a relevant claim is a potential defeat and conservatively forces scalar `U` in its queried ATOM proposition. Pending `DISPUTES` and `ADDS_CONTEXT` retain relationship-level `U`, and remain visible in a target ATOM's `pending` list, but **do not** independently force the proposition's scalar `U`. This does not authenticate any link.
2. **Target-scoped provenance:** `qualifiers` and relationship-derived `support` in a queried `ATOM` aggregate only links with eligible source and target and whose **target belongs to the queried proposition**. Claim `source_id` support includes only eligible claims within the queried proposition. A relation to another proposition must not alter a queried ATOM's projection. `LINK` and composed operators preserve their prior declared aggregation semantics.
3. All three matching evaluators change consistently. The finite-set oracle is still bounded to at most 10 eligible claims, and all arms inherit the same stipulated semantics. Neither source identity nor argumentation result establishes the truth of observations.

**Invariants:** original archive and internal history untouched, typed event fields and validation unchanged, proposition truth for admitted/withheld correction edges unchanged, append-only reassessment and full projection rewrite parity retained, no change to observed LC012 results retroactively.

**Evidence basis:** `evidence/probe_observed.json` plus `tests/test_lc013.py`. Full test execution and any residual errors must be read from fresh local receipts; no assertions about universal correctness, independent empirical validation or causal impact of Lens Shift.
