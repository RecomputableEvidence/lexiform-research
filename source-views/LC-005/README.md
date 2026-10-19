# LC-EXP-005 — Lazy Compositional Witness Graphs (Candidate)

**Status:** executed, reproducible experimental branch. **Not** an admitted semantic innovation or evidence of efficiency superiority. **Not** the historical 2025 Lexicon Codex.

## Motivation

LC-EXP-004's `CHOICE` applies only to complete relational expressions. It cannot compose alternatives serially (`C(CHOICE(...),...)`) or scope guards and temporal operators across alternatives. Eager distribution can create exponentially many syntactic witnesses. LC-EXP-005 tests a graph representation whose node count grows with the expression DAG rather than the number of expanded witnesses.

## Defined semantics

Three values `F < U < T`; `C` combines contiguous paths by meet (min); `CHOICE` combines same-start/end/stage alternatives by join (max). These operations also compose **histograms of individual witness values** without enumerating all witnesses. The histogram counts distinguishable *syntactic derivations*, not independent evidence or reliable physical route counts.

- `R(A,B)` reads an indexed evidence claim at a designated query/knowledge stage using the unchanged LC-003 ledger semantics.
- `C(left,right)` preserves stage, endpoint compatibility, and branch provenance, with Cartesian-product semantics summarized by multiplying three-valued histograms.
- `CHOICE(left,right)` preserves ordered branch decisions, with histogram addition; no fabricated cross-branch physical route.
- `J(P(X),path)` or `J(S(X),path)` requires X to occur on **every possible witness** under the expression; otherwise the whole input is rejected rather than implicitly weakening guard scope.
- `AT(stage,path)` changes the scoped query stage, without merging evidence from mixed explicit stages.
- `H1` and `H2` reuse pinned LC-003 versions and retain the invocation/version/expansion in MACRO graph nodes.

Every cached evaluation is bound to expression, ledger SHA-256, knowledge stage, query stage, registry SHA-256. Returned results are defensive deep copies. Evidence authenticity remains a separate assumption and is **not** attested.

## Engines and controls

- `LazyGraph`: scanner-parser A + hash-consed witness graph with per-node three-valued derivation histogram, branch-directed witness selection.
- `TypedDP`: independently tokenized conventional typed expression + bottom-up dynamic programming for identical abstract meanings (aggregate control; no full graph).
- `TypedAudit`: independently tokenized, stack-executed conventional typed evaluator producing the **same full witness DAG and evidence details**. This is the audit-matched performance comparator, not a distinct epistemic grounder.
- `EagerOracle`: enumerates every concrete witness, capped at 4096, for small test cases to check the lazy graph's combinatorial results.

All share LC-003's evidence-selection library and the same stipulated grammar. Two implementations agreeing is not fully independent semantic validation.

## Observed results

- LC-004 predecessor: SHA-256 `90fd1a44eaa018fe2f713333b526fec56dc5241b956c80876915081701d9bba7` (embedded exactly).
- Embedded LC-003 original: SHA-256 `fa5a75c8cb9e61e508b86ed9871b778aa9625528e853b7bb3cc0807b206b947d`.
- Candidate conformance: 13/13 test groups PASS. Includes 128 seeded inputs, independently enumerated oracles, scope/temporal rejection, macros, expired evidence, cache mutation, REWRITE and REASSESS receipts.
- At 64 two-route segments, 256 distinct evidence edge claims support `2^64` distinct *possible route derivations*, stored with 511 graph nodes. The first/last derivations reconstruct distinct paths and preserve different evidence IDs; no full witness enumeration occurred.
- A separate synthetic 64-choice duplication test stores `2^64` derivations with 191 nodes; **not** distinct physical evidence.
- Archived REWRITE and REASSESS receipts independently re-compute from included records and definition registry; ordered ledger-prefix integrity is required.
- On this Python CPU benchmark, cold 64-segment latency: 27.033 ms LazyGraph vs 27.873 ms TypedAudit vs 3.692 ms TypedDP aggregate. The audit-matched implementations are close and do **not** demonstrate uniquely lexiconic speedup. Details in `results/benchmark.json`; CPU microbenchmark noise applies.

## Excluded claims / limitations

No automatic semantic discovery, general natural-language understanding, neural training, universal future decipherment, compression advantage over alternative representations, independent observational authenticity, or proven end-to-end scaling superiority. The three-valued max/min algebra is conventional and the typed audit comparator applies the same graph technique. Counts of possible derivations must never be reported as observations or verified real-world routes. The selected scalar semantics do not yet represent dependence between witness evidence sources or probability of independent alternatives. Source and result graphs are stored in separate REWRITE/REASSESS receipts, but these receipts are bounded auditable assertions—not institutionally authorized determinations.

## Reproduction (Python 3.10+ standard library)

Extract ZIP to a writable directory and run:

```bash
python run_all.py
# Windows PowerShell:
$env:PYTHONPATH = "src;history_003_extracted/LC-EXP-003/src"
python src/verify_receipts.py
python src/benchmark.py
```

On Linux/macOS use `PYTHONPATH=src:history_003_extracted/LC-EXP-003/src` before the last two commands. `run_all.py` verifies and extracts exact nested predecessors in a temporary working tree and runs tests; it never modifies archived predecessors.

Manifest: `MANIFEST.sha256` hashes every packaged file apart from itself. A separate archive-level SHA-256 freeze accompanies the deliverable.
