# LC-EXP-007 — Append-Bound Ledger and Selective Audit

**Research status:** separately executed experimental successor, not an amendment to frozen LC-EXP-006. Python 3.10+ standard library, no neural model involved.

**Preserved predecessor:** `history/LC-EXP-006-DEPENDENCY-BOUND-REUSE-001.zip` SHA-256 `00c801c2a1068c20a370ee3de539abd064b9254ec726f69b627f3b0be454ffec`. The 006 archive includes its frozen 005 predecessor. This successor intentionally changes the *ledger commitment scheme*; LC-007 hash-chain commitments **cannot be equated** with LC-006 whole-ledger digest values, even when the same records are present.

## Executable research question

Can an append-only in-process ledger maintain a cryptographically linked historical commitment and indexed evidence lookups without rebuilding prior records, while a selective audit interface preserves exact revisitable historical interpretations without full-graph output on every evaluation?

## Implemented

- `src/persistent_ledger.py`: record validation reuses LC-003's schema; each append advances a domain-separated SHA-256 chain from a declared genesis anchor. A version-limited snapshot references a trusted in-process store. Old snapshots exclude newly added evidence. Per-atom indexed lookups preserve the established stage, validity, conflict, and nonapplicable-ID semantics.
- `verify_transition(...)`: independent receipt replay from a trusted predecessor commitment and length, **plus a maintained set of historical IDs**. Linking a delta without the historical ID set cannot demonstrate global ID uniqueness. `verify_full_replay` allows complete recomputation from exported records; this remains linear.
- `src/selective_audit.py`: composes LC-006's plan, dependency detection and node computation with per-node version history. Root-only evaluation returns an ephemeral `AuditHandle`. `full_graph(handle)` materializes the audit-complete historical DAG on demand; `witness(handle, index)` reconstructs one selected witness without full DAG serialization. Both APIs remain valid for previous revisions after later append events.
- Independent correctness oracle: the frozen predecessor's conventional `TypedAudit` full recomputation against its original `EvidenceLedger` and full witness selection. Parity checks compare content-derived root IDs, semantic graph nodes and selected witnesses; commitment hashes differ by design.
- Audit receipts distinguish proof/source identity changes from changed scalar truth and include append/recomputation counts. The old predecessor archive and predecessor failures remain unchanged.

## Reproduce

From the extracted package directory:

```sh
python run_all.py
python run_benchmark.py
python build_demo.py
```

`run_all.py` checks the embedded frozen predecessor archive SHA-256 and its internal 16-entry manifest, executes 25 predecessor tests, then runs 10 LC-007 test groups. The benchmark reruns tests as a precondition and rewrites `results/benchmark_007.json`; the demo likewise rewrites its derived report. **Rerunning changes files covered by the frozen manifest; those changes should be treated as new run artifacts, not as modifications to the frozen package.**

## Evidence results and ceilings

The test suite includes 128 seeded append updates, independent temporal lookup selection comparisons, 64-stage `2^64` compositional witness identity, independent full graph equivalence, negative forged receipts, invalid evidence, historical snapshots, unrelated updates, same-truth different-evidence transitions, and historical standing.

The microbenchmark separately measures persistent append, LC-006-style full ledger reconstruction, root-only incremental evaluation using A and B parser variants, full graph materialization, and single-witness reconstruction. Root-only A/B evaluations share the selective invalidation algorithm, so this is **not an independent optimized typed-graph speed competition**. The performance result is about eliminating specific known materialization/rebuild work, not unique lexiconic superiority.

## Explicit limits

1. **Trusted in-process store:** `AppendLedger` is a Python builder with mutable internal arrays. Public operations preserve historical append order, but Python code with direct object access can tamper with those arrays. This is **not** a tamper-resistant database or remotely authenticated ledger.
2. **Hash chain is not evidence authentication:** no key signatures, independent capture attestation, source authentication, external persistence, crash recovery, or distributed consensus. A verifier must trust an independently established anchor, prior history/ID state, and provided record bytes.
3. **Historical handles are process-local:** graph revisions live in memory. Cross-process restoration needs ledger replay and reevaluation; no compact portable historical checkpoint was demonstrated.
4. **Output costs remain:** materializing the complete graph and complete ledger replay still scale with the amount of information requested. Witness extraction traverses the selected derivation; it is not free.
5. **No fresh meaning discovered:** grammar, atom rules and evidentiary semantics remain externally declared; the result is bounded computational reuse and selective audit output, not independent semantic grounding or learning.
6. **Common-mode limitations:** both A/B parser arms share computation and evidence selection, while the typed oracle shares the underlying declared evidence semantics. Independent parity is therefore scoped, not full adversarial independence.
7. **No changed-context reuse:** a different source expression, registry, query stage or knowledge cutoff still requires a separate evaluator.

See `results/EXAMINATION.md`, `results/execution_receipt.json`, `results/benchmark_007.json`, and `results/example_transitions.json`.
