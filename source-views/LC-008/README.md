# LC-EXP-008 — Portable Historical Audit Packets

**Status:** separately executed, bounded experimental successor to LC-EXP-007; **not** a production release, authenticated evidence store, semantic-learning system, or demonstrated lexicon-specific efficiency advantage.

## The concrete gap

LC-007 can revisit older audit states using in-memory revision handles, but those handles cannot be examined independently in a fresh process. This successor exports a *complete, bounded historical audit packet* and independently replays its semantic conclusion and selected witnesses from the frozen conventional typed evaluator. It does not claim to make the replay compact, incremental or free of trust assumptions.

## What is new

- `src/portable_audit.py` exports a historical snapshot and its LC-007 selected witnesses **without requiring a full-graph export**. A packet includes the exact historical evidence records, append-chain tip, fixed H1/H2 definitions, expression and query/knowledge stages, root claim, and sampled witness paths. Witness indices are decimal strings to preserve large counts across JSON implementations.
- Offline verification recomputes a fresh chain from genesis and globally checks evidence ID uniqueness. It separately re-evaluates the source expression using LC-005's conventional stack-based `TypedAudit`, compares root values/histograms/content IDs, and independently reconstructs each selected witness. It does **not** rely on LC-007's stored audit handle or incremental engine during replay.
- `verify_packet.py` is a separate command-line process. All executable dependencies are recovered from **hash-verified, unchanged predecessor ZIPs**. An optional `--trusted-tip` or `--trusted-packet-hash` must be supplied independently of the packet to establish an external commitment match. Without one, verified results are labeled `UNANCHORED`.
- The original LC-007 ZIP is embedded without changing a byte. It embeds the LC-006/005/004/003 lineage, which this successor also verifies against the predecessor manifests before loading.
- The supplied Lens Removal and Lens Shift v0.1.4 source documents are preserved in `methods/` as exact original bytes. The operational findings are about LexiFORM, **not claims of empirical validation of either method**.

## Run from the extracted LC-008 directory

Requires Python 3.10+ standard library only; no network, API, model weights, administrative permissions, or GPU.

```bash
python run_all.py           # checks 003–007 manifests; reruns 007 and inherited tests; executes 15 successor tests
python build_demo.py        # writes historical T and later U example packets
python verify_packet.py examples/historical_T.json
python verify_packet.py examples/later_U.json
python run_benchmark.py     # illustrative packet size and CPU replay timings, no matched comparator
```

If an externally trusted LC-007 chain tip for the exact historical snapshot exists, supply it:

```bash
python verify_packet.py examples/historical_T.json --trusted-tip YOUR_INDEPENDENTLY_OBTAINED_64_HEX_TIP
```

The demonstration's tip can be used to exercise the command, but reading the tip **from the packet being checked is not an independently obtained anchor**. A packet may be entirely internally consistent yet forged as an alternative history. In that case unanchored verification cannot distinguish it from a genuine source ledger.

`run_all.py`, `build_demo.py`, and `run_benchmark.py` intentionally regenerate files in `results/` and `examples/`; on rerun, reissue `MANIFEST.sha256` if repackaging. They do not change the frozen predecessor ZIP. `verify_packet.py` requires only the selected packet plus this package; it does not use the original live engine.

## Scope and actual test observations

- The legacy LC-007 runner passed **10/10** test groups; it reports **25** inherited groups. The independent LC-001 package was also executed during the broad source examination with **7/7** groups passing.
- LC-008 passed **15/15** new groups including cross-process verification, stale and future observations, preserved historical `T` alongside later contradictory `U`, macro and guard lineage, 64-segment `2^64` syntactic witness addressing, witness tampering, duplicate evidence IDs, cross-ledger swaps and unanchored consistent alternative histories.
- Synthetic benchmark with complete records and two witnesses per packet: **8** segments / **32** rows = **19,136 bytes** and **4.30 ms** replay; **32** / **128** = **73,178 bytes** and **18.83 ms**; **64** / **256** = **145,378 bytes** and **38.22 ms**. Five repeated CPU runs per size; observed medians, not guarantees. These times exclude process startup and dependency extraction. This package makes no matched performance or portability-security superiority claim.

Full reproducible receipts and findings are in `results/EXAMINATION.md`, `results/execution_receipt.json`, and `results/benchmark_008.json`.

## Trust model and explicit nonclaims

- The input evidence rows are *declared assertions*, not authenticated observations. Their stated validity windows do not establish physical persistence.
- SHA-256 links and packet hashes check internal consistency against an **independently trusted commitment**, if one exists. They are not signatures. Both of two conflicting self-consistent histories can be accepted without an anchor.
- The verifier and exporter share the fixed inherited grammar, evidence semantics and binary distributions. A distinct `TypedAudit` implementation limits shared code paths but does not establish independent interpretation of an unknown language.
- Replay intentionally ships every historical record; its storage, serialization, audit reconstruction, graph evaluation, and dependency extraction have significant nonconstant costs. This is not a durable append-only database, succinct proof system, portable in-memory cache checkpoint, or production-safe adversarial parser.
- Cross-context dependency reuse, externally verifiable source authenticity, independent semantic grounding, third-party software attestation, formal security verification and generalization remain open.
- `MAX_RECORDS=10000`, `MAX_EXPRESSION_CHARS=100000`, and `MAX_WITNESSES=32` impose some operational bounds but do not establish a general denial-of-service defense or production security qualification.

## Successor relation

Predecessor: `LC-EXP-007-APPEND-BOUND-AUDIT-001.zip`, embedded **unaltered** in `history/`, SHA-256 `b47645864323e90e95ce0408d1602cc36ef801dcbc78c244bfdf0d5954d4ac00`.

This successor's new code and packets do not rewrite the LC-007 execution, history, tests, results, chain scheme or claims. LC-007's open issue `F007-03 PROCESS_LOCAL_HISTORY` is addressed only in the **portable full-replay audit inspection** sense; compact recovery and authentication remain open. See `results/EXAMINATION.md` for the detailed change ledger and reservations.
