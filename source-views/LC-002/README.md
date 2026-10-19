# LC-EXP-002 — Version-Bound Relational Composition (new successor)

**Status:** executable bounded successor experiment; **not** the 2025 Lexicon Codex; not a trained LLM.

## Provenance

- Frozen predecessor `LC-EXP-001.zip` SHA-256: `1014aa4b0948ec04f0f859905a3af3dad35034368e5016300a7c29215079e9e8`.
- Prior independently preserved external examination: `LC-EXP-001-INDEPENDENT-EXAM-001.zip`; findings triggered two hardening repairs. The predecessor archive is not overwritten or repackaged as historical evidence.
- This successor carries the v1 files for regression purposes, including the original grammar/spec, while **modifying only the successor copies** of `src/interpreter_a.py` and `src/interpreter_b.py` to repair cache return aliasing and mutable definition binding.
- This successor introduces a **new** relational treatment grammar in `spec/relational_grammar.md`, with two independently implemented interpretation/evaluation pathways and explicit staged evidence.

## Verified experiments

- Predecessor suite on patched code: 7 groups, all pass; 220 deterministic generated boolean expressions × 81 valuations = 17,820 valuation checks.
- Successor suite: 9 groups, all pass; 120 deterministic generated relational expressions × 81 valuations = 9,720 valuation checks.
- Explicitly scripted pressure: 17 named probes, all passed as expected (see `results/pressure_run.json`).
- Within-treatment scaling at 2, 4, 8, 16, and 32 path links is recorded in `results/relational_scale.json`.
- `results/EXAMINATION.md` describes capabilities and retained open limitations.

## Reproduce (Python 3.10+; standard library)

From this folder, in a disposable extracted copy:

```sh
python tests/test_conformance.py
python tests/test_successor.py
python src/pressure.py
python src/relational_scale.py
python verify_manifest.py  # execute before rerunning scripts if comparing to frozen distribution
```

Test and benchmark scripts may rewrite `results/` files in your extracted copy; verify the shipped manifest before executing them. For immutable comparison, compare the source ZIP checksum and freeze receipt first.

## Scope

`R(a,b)` tests an observed directed relationship with explicit evidence; `C` composes a *specific path witness* with matching endpoints at the **same stage**; `J` attaches guard evidence on a node present in the path; `AT` scopes a query to a declared stage. `H1` / `H2` are distinct frozen versioned compound definitions. Unknown, conflicting evidence, and non-contiguous paths are not silently corrected. These operations are not proof of a universal lexicon or improvement over optimized symbolic representations.

**No neural model, self-deciphering key, multimodal transfer, cryptographic attestation, general language understanding, adaptive learning, or demonstrated efficiency superiority is present.**
