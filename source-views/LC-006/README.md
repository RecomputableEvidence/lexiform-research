# LC-EXP-006 — Dependency-Bound Semantic Reuse

**Status:** Executed bounded experiment. **Not** a new trained AI, independent semantic discovery, or proof of lexicon-specific speed/interpretation advantage.

The frozen LC-EXP-005 predecessor archive is preserved byte-for-byte under `history/`. LC-EXP-006 is an additional separately identified experiment. Its focus is **whether graph computations can be reused following append-only evidence enrichment while preserving the complete LC-005 witness/evidence graph**.

## Implemented contract

- Full node plan compiled once from fixed expression, fixed grammar registry, fixed query stage, fixed knowledge cutoff.
- Each evidence-dependent node records the atom it looks up, its stage, and reverse parent dependencies.
- An append is permitted only if its ledger exactly preserves the predecessor's ordered records as a prefix; input row identifiers and validity metadata remain checked by LC-003.
- New unrelated evidence does not cause a lookup or node recomputation.
- New evidence for a used atom causes a fresh evidence lookup. If the **entire structured selection result** is unchanged, graph nodes remain reused. If selection metadata changes (even with unchanged `T/F/U` value), the affected node and ancestors are recomputed.
- Every materialized result binds the **new complete ledger SHA-256**, fixed macro-registry digest, query/knowledge stages and source expression. Earlier outputs/transition receipts remain intact.
- Changes in source expression, grammar registry, query stage, or knowledge cutoff **reject reuse**; construct a new evaluator rather than importing a stale cache across contexts.
- Evidence authenticity, cross-ledger trust, retroactive physical validity, probability of alternative derivations, and the historical Lexicon Codex are outside scope.

**Important:** Reusing symbolic evaluation under a fixed knowledge cutoff is not the same as preserving a conclusion's real-world standing. The caller must choose the proper query/knowledge context and supply appropriate evidence. `R(A,B)` can be true as a past-state query and unknown in the present without contradiction.

## Independent and shared portions

- `BoundReuse(..., 'A')` uses predecessor scanner/parser A.
- `BoundReuse(..., 'B')` uses predecessor typed token parser B. Both intentionally share LC-006's dependency-update algorithm.
- **Oracle:** a newly created predecessor `TypedAudit` evaluator processes the entire input from scratch and returns the same full witness graph. Its parser and full recomputation are separate, but evidence-selection rules are shared.
- `LazyGraph` full rebuild is also benchmarked. No arm is granted weaker accuracy or an aggregate-only output.

## Running on Windows, Linux or macOS

Python 3.10+ standard library; no GPU, cloud usage, model download, external dependencies, or privileged symlink permissions.

```sh
python run_all.py
python run_benchmark.py
```

Each runner checks the frozen LC-005 predecessor archive, extracts it to a disposable temporary folder, runs its 13 tests, and then runs the successor or benchmark. `run_all.py` also verifies all 19 entries of the predecessor's internal manifest before running its tests. The original archived ZIP is never modified. `run_benchmark.py` writes measured output into `results/benchmark_006.json`, so re-running benchmarks after download will intentionally modify that derived results file; regenerate the package manifest if repackaging.

## Results and claim ceilings

- Predecessor: 13/13 existing test groups passed.
- Successor: 12/12 new test groups passed, including 128 fixed-seed append comparisons to a separately implemented full TypedAudit evaluator; cold/warm full graph identity is required.
- 64-segment graph: `2^64` syntactic derivations remain represented as 511 materialized result nodes with indexable witnesses. These are **not** independent observations.
- Full-audit graph append benchmark: incremental evaluator around 7–8 ms vs conventional full rebuild around 25–29 ms per update in this measured Python CPU run. Typed incremental control is comparable to the lexicon incremental arm, **so no uniquely lexiconic advantage**.
- Rebuilding the immutable ledger/index remains separately measured, about 1.4 ms per append at 64 segments in these synthetic fixtures. Full graph copying, ordered-prefix comparison and ledger rebuild are not sublinear.

See `results/EXAMINATION.md`, `results/benchmark_006.json`, `results/example_transitions.json`, `results/execution_receipt.json`, and `MANIFEST.sha256`.

### What still needs research

1. Reusable semantic dependencies when the **query/knowledge context changes**, rather than always rebuilding.
2. Efficient canonical ledger persistence or authenticated append structures without scanning and rebuilding the full ledger for every addition.
3. Output modes that selectively materialize proof paths while retaining independent audit replay, rather than copying all 511 graph nodes every time.
4. Matched independently engineered incremental typed-graph comparisons and measurement of end-to-end cost, including encoding, state management, and verification.
5. How novel semantic distinctions are established and grounded, rather than simply composed through already supplied formal rules.
