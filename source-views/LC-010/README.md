# LC-EXP-010 — Declared Relational Continuity and Witness Scope

**Executed candidate successor, not a substitute for the original Claude-delivered LC-EXP-009 runnable ZIP.** No model, network access, GPU, package installation or credentials required. Python 3.10+ standard library. Tested on Python 3.13.5 on Linux.

## Provenance

The file `history/LC-EXP-009-RECONSTRUCTED-RUNNABLE.zip` is a fresh runnable reconstruction of LC-EXP-009 from the user-supplied *reading export*. It contains 39 hash-matched members, including byte-identical original predecessor LC-EXP-008. Its new ZIP hash is `d2068668386340be540c2b943bebef4078a124e50a54e0692e5d310970af813b`. **It is not the unavailable original Claude ZIP** reportedly hashed `b5fa927aa61cc397d8e5b55d7c4c181724bcbeffda8c9f3c59588213be8615a9`.

## Revealed gap and added contract

LC009 proves a declared pairwise relation between two portable audit packets. It does not define a continuous sequence of relations across many independent receipts. A collection of individually valid pair receipts can be reordered or spliced together without a common valid intermediate packet.

LC010 adds a typed, bounded **chain of pairwise relation receipts**, linked by exact endpoint-packet identity and domain-separated content commitments. Optional externally supplied tip and starting hash can be checked but never treated as self-authenticating. The new interpretation summaries differentiate **sampled witness content**, **sampled supporting IDs**, and **audit-envelope/ledger commitment changes**. These are distinct from LC009's `sample_selection_changed` field, which compares sampled indices.

## Reproduce

After extraction, from `LC-EXP-010-RELATIONAL-CONTINUITY-001`:

```shell
python verify_manifest.py
python run_all.py
python verify_chain.py examples/three_stage_chain.json
python build_example.py  # re-creates example and results; run only after verifying the frozen manifest
```

`run_all.py` verifies frozen predecessor identity and nested manifests before running LC010 tests. It does not automatically rerun LC009's suite; that was run separately in clean extraction and its execution log is included in `results/`.

Reconstruction tests and LC010 tests were independently executed under a clean extraction and their output was preserved in `results`. The original failed test pass is also retained; subsequent corrections did not modify LC009.

`verify_chain.py` optionally accepts `--trusted-start-packet-hash` and `--trusted-chain-tip`. An anchor read from the packet itself is not independent evidence of authenticity. See `spec/contract.md` and `results/EXAMINATION.md` for exact boundaries.
