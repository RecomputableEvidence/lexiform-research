# LC-EXP-001 — Compositional Meaning and Reconstruction

**Executable CPU-first vertical slice** | Frozen test grammar `LC-EXP-001-GRAMMAR-1.0.0` | Python standard library only

## Purpose

Test whether two independent implementations can interpret unfamiliar compositions, reason directly on lexiconic structure, reconstruct qualifications, and distinguish (a) **REWRITE**, an equivalent representational change, from (b) **REASSESS**, a new justified conclusion from later evidence. Test on an intentionally narrow invented transfer-policy episode. Measure against a conventional typed tree, with and without caching and definition reuse. **No training and no LLM inference are part of this version.**

This is *not* an implementation or proof of the original August 2025 Codex. The historical material remains unverified, and the grammar is an original bounded experiment developed from the October 2026 discussion.

## Reproduce

On a machine with Python 3.10 or later:

```bash
python tests/test_conformance.py
python src/experiment.py
python src/benchmark.py
```

Run commands from the package root. All scripts use standard library only. Each script resolves files relative to its own location. `test_conformance.py` returns nonzero on any test failure. The episode overwrites `results/episode_trace.json`; benchmark overwrites `results/benchmark.json`. This package contains the actual observed reports from the creation run.

## Files

- `spec/grammar.md`: version 1 frozen grammar, logic, temporal semantics, limits, and interpretation boundary.
- `spec/registry.json`: version-pinned definitions and declared primitive operators; experimental invented version 2 changes the meaning on purpose for a negative control.
- `spec/discovery_log.md`: pressure rationale and explicit non-discovery claims.
- `src/interpreter_a.py`: recursive-descent parser, AST evaluator, independent bounded reconstruction, frozen-registry guard, memoization with evidence-digest invalidation.
- `src/interpreter_b.py`: explicit frame-stack parser, independent postfix VM, separately authored 3-valued algebra and reconstruction. Does not import A.
- `src/common.py`: shared input protocol and immutable evidence-history selection. No common parser or evaluator.
- `src/baseline.py`: conventional typed AST evaluator with matching truth values, both cached and uncached.
- `src/experiment.py`: episode, finite exhaustive rewrite equivalence, audit trace, independent agreement checks.
- `src/benchmark.py`: separate warm CPU repeated-query timing and Python allocation sampling.
- `tests/test_conformance.py`: deterministic examples, mutation/failure tests, 220 generated compositions × 81 full valuations, and tamper/staleness controls.
- `results/`: records produced from actual execution, not hypothetical expected results.

## What the first successful run means

Given the *supplied grammar and definition registry*, two different parsers/evaluators agreed on `U → T → F` for the unchanged expression `G1(A)` under staged evidence. They independently reconstructed the same semantic support records (though with different prose), while a conventional typed evaluator reached the same truth values. A valid De Morgan rewrite passed the exhaustive proof check; an invalid scope-changing rewrite was rejected with a counterexample. The resulting trace is hash-linked and preserves earlier states.

This is **bounded native structure-based inference**; it does **not** demonstrate unique reasoning capacity beyond existing symbolic systems. It is interoperability under a pre-shared spec, not self-deciphering communication with an unknown civilization.

## Interpreting the benchmark fairly

The benchmark uses an identical 6,000-request toy semantic workload across these arms: conventional typed uncached; conventional typed cached; lexicon with reusable definitions and cached results; lexicon with cached definitions but no result cache; and lexicon with neither. It verifies identical truth values before each timing trial. Times are medians of five sequential trials, with per-run warmups. Memory is `tracemalloc` peak for the first 300 queries in fresh instances (Python allocations only); these are noisy numbers, not process resident sets or hardware/energy measurements.

Crucially, the conventional typed evaluator can benefit from exactly the same reuse/caching strategies. The byte comparison compares a *small expression string plus the full registry* with repeated JSON-serialized typed trees; it is not a fair lower bound on well-designed symbolic serializations (which can likewise reference precompiled definitions). It does not include neural interpretation/reconstruction, disk I/O, GPU work, registry maintenance or training. Do **not** extrapolate from these measurements to LLM throughput or model-quality advantages.

## Evidence / security limitations

- A SHA-256 audit hash chain **detects accidental modifications only when the root/digests are independently preserved and trusted**. It is not digitally signed or remotely witnessed; a party with control of the entire log can recompute the chain. The report separately anchors the full supplied evidence log digest.
- Evidence ID and source text are user-supplied test fixtures; their authenticity is not established.
- No cryptographic custody, independent holdout custodian, preregistration, or hidden sequestered test suite exists here. The random seed and generator for the **generated composition suite** are visible.
- The toy evidence semantics assume observations persist across stages until superseded. This does not establish real-world timing or safety rules.
- The exhaustive equivalence checker is complete **within the declared propositional three-valued semantics for expressions containing at most eight distinct atoms**; it is not a general theorem prover.
- Native inference here uses explicit symbols; it does not perform general open-domain semantic interpretation.

## Next strictly separated work

1. Independent blinded suite and definition evolution; enrich the alphabet only after a measured expressivity failure.
2. Introduce explicit time and event operators inside encoded expressions, then test reassessment and history as distinct operations again.
3. Add same-capability optimized typed reference, compare cost of shared structure/cache invalidation, then consider neural ingress/egress with a fixed unchanged model.
4. Separately investigate a self-grounding decoding key for the original time-anchor objective, without treating model interoperability as proof of universal decipherability.
