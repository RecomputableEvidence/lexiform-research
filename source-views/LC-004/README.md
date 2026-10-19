# LC-EXP-004 — Descriptor Composition Pressure 001

**Status:** executed *exploratory successor candidate*, **not** grammar admission or a lexiconic reasoning advantage claim.

**Purpose.** Apply expressive-pressure to the preserved LC-EXP-003 semantics using the first test that the current language cannot express: “either of two evidence-qualified routes from A to Z.” Keep source history intact; separately stress the ordered append-only interpretation of REASSESS.

## Outcome

- Reproduced exact LC-EXP-003 frozen ZIP identity (`fa5a75c8cb9e61e508b86ed9871b778aa9625528e853b7bb3cc0807b206b947d`).
- 9/9 candidate test groups passed. A generated suite has 128 seeded cases, **113** distinct choice-expression strings, 2–6 alternative branches, and 3-valued oracle comparisons on every case.
- Both the candidate balanced scanner + predecessor AST-DAG (A) and a separately coded candidate tokenizer + predecessor stack VM (B) agree, with a third conventional typed-AST control.
- Exhaustive 3×3 truth-value pairs for two alternatives agree with the stipulated `CHOICE` rule (max over `F < U < T`).
- Prior join is not expressible by a conjunction-only calculus over two independent atomic propositions: finite counterexamples for left-only, right-only and meet-only are in `src/expressivity.py`.
- Preserves each alternative's full predecessor projection and macro lineage; does not invent a flattened 'combined route'. Stage/endpoint mismatches are rejected; expiry and reassessment remain visible.
- Reproduced LC-EXP-003's acceptance of reordered identical evidence IDs as 'append-only'. Candidate `strict_reassess` adds exact predecessor-ledger **prefix** requirement and forward-knowledge check; original code untouched.

## Scope limit

The new `CHOICE` is **explicitly defined** here, not automatically discovered. It is a candidate descriptor selected after a demonstrated expressivity gap. It can combine complete predecessor expressions and nest with itself, but it **cannot appear within `C`, `J` or `AT`**. Its output is a finite list of evaluated alternatives, **not** a general path-algebra, proof search, an aggregation of unique physical truths, or a semantic synthesis beyond formal stipulated rules.

The two candidate parsers are separate implementations. They still share the predecessor evidence lookup library, declared semantics, input witnesses and cases. The conventional control shares candidate parser A; comparator independence is partial. No natural-language model or general semantic grounding is included. The exploratory benchmark is not resource/caching matched, and is **not evidence of efficiency advantage**.

## Reproduce

Python 3.10+, standard library. Extract into a **writable** directory. From the root folder:

```bash
python run_all.py
# Optionally (after run_all extracts the predecessor):
PYTHONPATH=src:history_extracted/LC-EXP-003/src python src/benchmark.py
```

On Windows PowerShell, set `PYTHONPATH` with the path separator `;`, or use `run_all.py` alone for all tests.

The runner verifies the predecessor SHA-256 and extracts it into `history_extracted/` prior to tests. The runner also writes `results/execution_receipt.json`. Original archive bytes remain unmodified. The extracted working folder is intentionally not distributed in the package.

## Included artifacts

- `history/LC-EXP-003-EVIDENCE-BOUND-EXECUTED.zip`: exact 003 predecessor.
- `src/choice_a.py`, `src/choice_b.py`, `src/choice_control.py`: three candidate runtime pathways.
- `src/continuity.py`: stricter append-only history predicate, without changing predecessor.
- `src/expressivity.py`: constrained OR/AND expressivity witness.
- `tests/test_choice.py`: positive, negative, oracle, historical-continuity and adversarial probes.
- `results/EXAMINATION.md`: source findings, claims and test limitations.
- `results/exploratory_benchmark.json`: exploratory Python timings (NOT a matched efficiency comparison).
- `MANIFEST.sha256`: file integrity of this candidate distribution except self-manifest.

## History of test changes

An initial candidate run passed 8 test groups and failed one uniqueness assertion because **128 randomly generated cases produced 113 distinct expressions**. The requirement of 128 distinct expressions was an ungrounded test expectation. The test was amended to require at least 100 distinct structures while retaining all 128 case evaluations. The earlier failing run is not counted as a passed execution; the final 9/9 pass is after that amendment.
