# LexiFORM PXP-002 follow-through — local executed pressure examination

**Status:** `FROZEN_TEST_EXECUTED / BOUNDED_SYNTHETIC_CONFORMANCE / NO_REPOSITORY_ADMISSION`  
**Research object:** PXP-002-LEXIFORM-EXEC-PRESSURE-001  
**Source:** user-preserved Package 1, exact LC-EXP-012 and LC-EXP-013 originals.

## Executive finding

The new **19-case** static scope matrix was frozen *before executing against either archived implementation* (`PREREGISTRATION.json`, SHA-256 `d0824aa2b49bced75bf6ae7cd32ec2c3ff73fa114bf0195083f2981b135949c1`). Recovered source ZIP SHA-256 and each native manifest verified. Baseline unit tests executed on the original source: **LC012: 26/26 PASS; LC013: 33/33 PASS**. The new matrix then evaluated both original versions on the same cases, with LC013 receiving the source-derived outcome checks: **19/19 PASS**. LC012 is *not retroactively scored* under LC013's amended contract.

A fresh second extraction of both exact archives, rerunning original suites and all matrix cases with the same implementations and outputs checked against saved projections, also **PASS**. This is same-implementation recomputation, not an independently written oracle or external model examination. Existing original test scripts and execution outputs were not changed in the source ZIPs.

## What changed

Of 19 controlled cases, five had a changed projection between historical LC012 and amended LC013; 14 had identical projections. These differences are not blanket claims that all older LC012 test outcomes were failures. They specifically pressure LC013's stated scope repair.

| Case | LC012 observed | LC013 observed | Material scope distinction |
| --- | --- | --- | --- |
| C03: targeted pending DISPUTES | `U` | `T` | Pending non-defeating dispute remains visible in `pending` without forcing scalar uncertainty |
| C04: targeted pending ADDS_CONTEXT | `U` | `T` | Pending context relation also does not defeat current claim |
| C06: unrelated admitted context | scalar `T`, but foreign qualifier/support included | scalar `T`, foreign qualifier/support absent | Exact ATOM projection is target-scoped |
| C09: unrelated admitted correction | scalar `T`, foreign evidence included | scalar `T`, foreign evidence absent | No cross-proposition support inheritance |
| C11: unrelated pending guarded correction | scalar `T`, foreign guard evidence included | scalar `T`, foreign guard evidence absent | Knowledge of a distinct predicate does not add support to queried proposition |

**Important controls:** C01 retains pending correction on an unrelated proposition without blocking current scalar `T` in either version; C02 retains a targeted *potentially defeating* pending correction and gives `U` in both. Targeted pending `SUPERSEDES` with policy claims likewise gives `U`. Context and knowledge cutoffs, admitted and withheld reviews, already-admitted disputes/context, and separated support were independently exercised as static fixtures. The tests use the actual program's `T/F/U` and typed projection fields, not invented universal authority labels.

**Preserved lineage:** LC013 embeds byte-identical LC012 ZIP (SHA-256 `748902021e2339691a79c1830164c02aa6382781d62a4e16f4339f3681c097ff`). LC013 retained the same `src/contract.py`, `src/engine.py`, `src/expressions.py`, `src/fixtures.py`, and `tests/test_lc012.py` as LC012, while changing `src/lexicon.py`, `src/typed_baseline.py`, and `src/oracle.py`. This establishes a narrow sourced code delta; not causal proof of methodology efficacy.

## Scope and controls

- All cases are synthetic inputs under the declared LC013 policy. No external observations, third-party authority attestation, formal proof of global correctness, or independent empirical semantics are established.
- The lexicon, typed baseline, and finite oracle implement a shared stipulated policy; their agreement is meaningful code-path triangulation, not three independent scientific authorities.
- New test specifications and adjudication were authored by this assistant. There was no blinded external examiner. Post-run reproduction tooling and its bindings are labeled separately from the frozen test protocol.
- LC012's original contract continues to describe LC012; LC013 is a separately identified successor with an explicitly amended policy. Nothing here retroactively rewrites LC012 preregistration or outcomes.
- Independent source-object identity is supported by SHA-256/ZIP CRC and manifests, not independent creator/server attestations.
- No Perplexity API requests were made; no money spent in this local gate. No repository mutation or public release.

## Next scientific dependency

A discriminating follow-on should target a failure not already solved by LC013's contract: e.g., competing conditional guards and relevant pending defeating links under a time-varying policy, with **an oracle frozen independently of the candidate implementation**. Only build it if it advances an identified uncertainty. Shared World's admission×permission four-cell question remains a separate controller experiment; it must not be imported into LexiFORM without an explicit bridge hypothesis.

## Portable contents and reproduction

- `LC-EXP-012-CONTESTED-STANDING-001.zip` and `LC-EXP-013-SCOPED-RELATIONSHIP-001.zip`: byte-exact recovered input archives, with LC013 embedding its LC012 predecessor.
- `PREREGISTRATION.json`: pre-run test scope, source digests, objective outcome policy and stop rule.
- `pressure_matrix.py`: 19 deterministic fixture cases and source-derived LC013 checks, hash-bound in prereg.
- `LC012_pressure_results.json`, `LC013_pressure_results.json`: archived per-case projections, complete unfiltered outcomes.
- `PAIRWISE_COMPARISON.json`: machine-readable full projection differences.
- `LC-EXP-01*_manifest_run.log` and `LC-EXP-01*_baseline_run.log`: local execution stdout/stderr.
- `RECOMPUTATION_RECEIPT.json`: fresh second extraction, same-implementation reproduction result.
- `reproduce_offline.py`: post-execution portable reproduction utility, not part of original preregistration.
- `EXTERNAL_INPUT_BINDING_POST_RUN.json`: hashes of the earlier PXP proposal/exam, explicitly bound after test.
- `SHA256SUMS.txt`: sealed hashes of all files in release packet other than itself.

From an extracted directory containing both ZIPs and scripts, run:

```powershell
py -3 .\reproduce_offline.py
```

This launches local Python test code. It uses only the standard library and should have no API/network or paid calls. Inspect the source first if your environment requires trusted-code approval. The output claim is same-implementation replay, not independent semantic correctness.
