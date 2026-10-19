# LC-EXP-011 — Claim-Relationship Semantics and Compositional Generalization

Executable **successor experiment** to the preserved LexiFORM LC001–LC010 lineage. LC010 is carried as an unmodified historical ZIP, not modified or integrated as an executable dependency of the new semantics.

## Run

Requires Python **3.10+**, standard library only, CPU-only. From the extracted folder:

```sh
python verify_manifest.py
python run_all.py
python benchmark.py
```

The final command writes `results/benchmark_latest.json` (intentionally *not* covered by the immutable manifest because timings change). Original measured results are stored separately in `results/benchmark_observed.json`.

## What this proves and does not prove

- Synthetic claim-relationship evaluation is reproducible across a recursively evaluated list-form lexicon, a conventional typed AST, and a third independently coded oracle.
- Chronology alone does not authorize a later claim to displace an overlapping earlier claim. Relationship admission, scope, and provenance are explicit.
- 512 unique seeded compositions test supplied-grammar generalization; they do **not** constitute discovery of new meanings, independent decipherability, or neural model reasoning.
- Deterministic `REWRITE` is tested separately from history-preserving `REASSESS`.
- A small preliminary CPU comparison shows no performance advantage over the typed comparator.
- Synthetic evidence cannot establish physical truth, actual observer authority, completeness of history, universal semantics, or production security.

See `spec/CONTRACT.md` and `results/EXAMINATION.md` for findings, limitations and comparison. All original LC010 members are separately preserved in `history/LC-EXP-010-RELATIONAL-CONTINUITY-001.zip`.
