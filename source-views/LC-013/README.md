# LC-EXP-013 — Scoped Relationship Standing (bounded successor)

This is a **local post-inventory successor** of LC-EXP-012. The original LC012 ZIP is preserved byte-for-byte in `history/`; original supplied research methods and preregistration are preserved separately. This successor was **not** covered by the supplied preregistration: see `evidence/protocol_amendment.json`. Its existence and tests do not empirically qualify Lens Shift or prove external truth.

## Why a successor

LC012's evaluator interpreted every pending link to a queried target as scalar uncertainty, even when the relation was `DISPUTES` or `ADDS_CONTEXT`, both explicitly non-defeating. Added links targeting unrelated propositions also leaked their qualifiers and evidence IDs into the queried audit projection. `evidence/probe_observed.json` documents both behaviors in the predecessor.

## Tested delta

For ATOM expressions only, only pending `CORRECTS`/`SUPERSEDES` edges conservatively force scalar `U`. All kinds of pending links remain separately visible in `pending` for their target. Qualifiers and relationship-evidence support are projected by target-relation ID, while claim support retains that proposition's claims. LINK expressions and the finite argumentation graph are otherwise unchanged. Three separately coded interpreters agree on these cases.

`python -B verify_manifest.py` then `python -B run_all.py`. The manifest seals release files other than itself and mutable `results/*_latest.json`. `history/` retains the original LC012 ZIP including its observations, and `results/` records the local successor execution separately.

**Limits:** synthetically stipulated grammar, policy and authority; same author/evaluator family, no external attestation; scalar `U` still conservatively chosen for possible pending defeat, even with same-valued claims; source/condition provenance is a minimal tagged set, not a full proof graph or a global transaction ordering. This is not LC012 validation or an independent empirical comparison.
