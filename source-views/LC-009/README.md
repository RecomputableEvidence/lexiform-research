# LC-EXP-009 — Relational Historical Audit

**Executed bounded successor candidate to LC-EXP-008.** Python standard library only; tested on Python 3.13.5. No network, model, credentials, or GPU required. Original methods applied in the requested order: **Lens Removal, then Lens Shift**.

## What was revealed

A portable interpretation is not yet a portable relation between interpretations. LC008 can verify two endpoints separately without establishing that the second preserves the first history. Its single `EXTERNALLY_ANCHORED` label also combines ledger-tip and complete-packet matches, although those commitments bind different things.

LC009 adds two deliberately narrow operations:

1. **Scoped packet verification:** report exactly whether a caller-supplied commitment matches ledger records or the whole packet. The verifier cannot establish that the caller obtained an anchor independently.
2. **Portable append reassessment:** replay both LC008 packets; require identical expression, query stage and definitions, nondecreasing knowledge cutoff, and exact ordered evidence prefix. Report truth, root content, histogram, ledger and witness-sample changes separately. No change is a valid outcome.

This is an addition, not a claim that LC008's documented single-packet replay contract was false. It does not change the grammar, selection policy, frozen predecessor or its standing.

## Reproduce

From a new writable extraction:

```sh
python verify_manifest.py
python run_all.py
python verify_audit.py reassessment examples/changed_truth.json
python verify_audit.py reassessment examples/corroboration.json
python verify_audit.py reassessment examples/unrelated_append.json
python verify_audit.py packet examples/before_packet.json
```

`run_all.py` replays the frozen LC008 suite and then the LC009 suite. It verifies LC008's raw archive SHA-256 and manifest, and the inherited 003–007 manifests, before loading predecessor instruments. Dependencies are extracted into temporary directories; archived bytes remain unchanged. Running tests rewrites current `results/`, so verify the shipped manifest **before** running tests; changed results are new execution artifacts.

Optional:

```sh
python build_demo.py
python results/probe_008.py
```

These regenerate examples/results. The packaged probe is a path-adapted version of the examination probe, not a frozen predecessor instrument.

### Independently obtained commitments

For packets, use `--trusted-ledger-tip` or `--trusted-packet-hash`. For reassessments use `--trusted-before-packet-hash`, `--trusted-after-packet-hash`, and/or `--trusted-receipt-hash`. Each expects lowercase 64-hex SHA-256. Packet and receipt hashes use the inherited canonical JSON `sha` function, **not** the pretty-printed JSON file's raw-byte hash. The archive `.sha256` file instead hashes raw ZIP bytes. Exact boundaries are in `spec/contract.md`.

Reading an anchor from the object being checked exercises matching only; it establishes no independent trust. A supplied before-packet hash alone does not commit to the after packet. A supplied full receipt hash covers both endpoints and their declared relation. Neither authenticates the evidence source or proves a physical event.

## Fresh results

LC009: **19/19 test groups passed**, including 128 seeded append relations, changed truth, unchanged truth with changed provenance, unrelated append, knowledge-only reassessment, forks, reordered histories, truncation, context changes, forged results, scoped anchors, cross-process replay, guarded macros, expired claims and indices up to `2^64−1`.

The frozen LC008 runner passed 15 groups and reran LC007 with its inherited suites. The broader examination also freshly ran LC001 (7), embedded LC002 (16), LC003 (15), and LC004 (9); these overlapping suites are **not** summed as independent validations. Original and fresh reports are distinguished in `results/EXAMINATION.md`.

One expanded development suite had an invalid positive guard fixture and failed correctly with `guard not universal`. That run is preserved. The fixture became an explicit negative case, and a genuinely universal guard became the positive case. Final 19/19 passing results are after that disclosed amendment.

## Limits

- Full history is included twice in a reassessment receipt; both endpoints are fully replayed. No succinct proof, incremental restart, cache restoration or efficiency advantage is claimed.
- Source assertions and validity intervals remain unauthenticated. No key signatures, external witness, database persistence or consensus.
- Fixed-query append reassessment only: changed expression, definitions, query stage or backward knowledge requires another separately identified operation, not silent acceptance here. Textually different but equivalent expressions are rejected by design.
- Same inherited grammar, evidence library and packet replay instrument; LC009 is not an independent semantic grounder or cryptographic primitive.
- 8 MB CLI file limit, duplicate-key/constant rejection and selected root type checks are partial bounds, not a production parser or denial-of-service guarantee. The Python API has no file-byte bound.
- No qualification or superiority claim for Lens Removal or Lens Shift; no literal perspective-free cognition claim.

## Preservation

`history/LC-EXP-008-PORTABLE-AUDIT-001.zip` is byte-for-byte supplied predecessor SHA-256:

`7af3bd382abf3289d4282a9be3d36dd10092ad9bbe0e19b5b7d15b68a85c1ddd`

The method files are also copied unchanged. `MANIFEST.sha256` covers all distribution files except itself and Python bytecode caches. It is an integrity inventory, not a signature or validation certificate.