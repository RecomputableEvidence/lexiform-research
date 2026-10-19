# LexiFORM

**Executable research in compositional, evidence-qualified relational semantics.**

LexiFORM is an **independent NGAST research line**, not a component, release, or performance claim of Fork. The repository preserves an experimental progression; no language-model training, general semantic understanding, external truth authentication, or deployment authority is inferred from that progression.

## Start with the evidence

- [`registry/experiments.json`](registry/experiments.json) — exact archive identities, version boundaries and the current qualification of each result.
- [`archives/`](archives/) — original 13 unmodified executable research ZIPs. **These**, not editable convenience views, are the exact preserved source objects.
- [`source-views/`](source-views/) — readable extracted code, tests and specs; may intentionally omit results, historical nested archives and large fixtures. Do not use these as substitute frozen packages.
- [`examinations/`](examinations/) — separately identified examination archives, including the PXP-002 followthrough on LC012/013.
- [`docs/BOUNDARIES.md`](docs/BOUNDARIES.md) — evidence limitations and publication scope.
- [`docs/NEXT_EXPERIMENT.md`](docs/NEXT_EXPERIMENT.md) — independent oracle trial candidate; **not executed or admitted**.
- [`examinations/LC012-RECOMPUTATION-AUDIT-INCOMING/`](examinations/LC012-RECOMPUTATION-AUDIT-INCOMING/README.md) — a separate verification-branch submission with a conflicting LC012 sequence label; the supplied ZIP is incomplete and not a new admitted source archive.

## Reproduce archive identity (Python 3.10+ standard library)

```sh
python tools/verify_sources.py
```

This verifies **13/13 archive SHA-256 identities, ZIP CRC, and 288/288 internal manifest entries** against the preserved source population. It does not execute the original experiment tests or validate their real-world meaning. A **separate** selected-entrypoint replay is documented in [`examinations/BASELINE_REPRODUCTION_001/`](examinations/BASELINE_REPRODUCTION_001/): 12/13 completed with PASS; LC009 did not complete within that specific 12-second local limit. **Later**, [LC009 Replay 002](examinations/LC009-REPLAY-002/README.md) ran the exact LC009 reconstructed runnable and frozen predecessor chain to completion, with 19/19 current tests passing. Both observations are preserved.

To rerun a single original experiment in temporary extraction, choose an experiment explicitly:

```sh
python tools/reproduce_one.py --experiment LC-EXP-013
```

External dependencies and test entrypoints vary across history; consult each archived README and inspect executable code before running. The script does not sandbox arbitrary Python. Network access is not intentionally used by the experiment packages, but Python execution remains under the operator’s security controls.

## Historical sequence

| Identity | Focus | Historical qualifier |
|---|---|---|
| [LC-001](archives/LC-EXP-001.zip) | Compositional meaning and reconstruction | BOUNDED_EXECUTED |
| [LC-002](archives/LC-EXP-002-EXECUTED-SUCCESSOR.zip) | Version-bound relational composition | BOUNDED_EXECUTED_SUCCESSOR |
| [LC-003](archives/LC-EXP-003-EVIDENCE-BOUND-EXECUTED.zip) | Evidence-bound semantic continuity | BOUNDED_EXECUTED_SUCCESSOR |
| [LC-004](archives/LC-EXP-004-DESCRIPTOR-PRESSURE-001.zip) | Descriptor expressivity pressure | EXPLORATORY_EXECUTED_CANDIDATE |
| [LC-005](archives/LC-EXP-005-LAZY-COMPOSITION-001.zip) | Lazy compositional witness graphs | EXECUTED_CANDIDATE |
| [LC-006](archives/LC-EXP-006-DEPENDENCY-BOUND-REUSE-001.zip) | Dependency-bound semantic reuse | BOUNDED_EXECUTED |
| [LC-007](archives/LC-EXP-007-APPEND-BOUND-AUDIT-001.zip) | Append-bound audit | BOUNDED_EXECUTED |
| [LC-008](archives/LC-EXP-008-PORTABLE-AUDIT-001.zip) | Portable historical audit | BOUNDED_EXECUTED |
| [LC-009](archives/LC-EXP-009-RECONSTRUCTED-RUNNABLE.zip) | Relational historical audit — runnable reconstruction | RECONSTRUCTED_RUNNABLE |
| [LC-010](archives/LC-EXP-010-RELATIONAL-CONTINUITY-001.zip) | Declared relational continuity | EXECUTED_SUCCESSOR_CANDIDATE |
| [LC-011](archives/LC-EXP-011-CLAIM-RELATIONSHIP-001.zip) | Claim-relationship semantics | EXECUTED_SUCCESSOR_CANDIDATE |
| [LC-012](archives/LC-EXP-012-CONTESTED-STANDING-001.zip) | Contested standing | EXECUTED_SUCCESSOR_WITH_KNOWN_DEFECT |
| [LC-013](archives/LC-EXP-013-SCOPED-RELATIONSHIP-001.zip) | Scoped relationship standing | EXECUTED_POST_PREREG_SUCCESSOR |

**Important:** LC-009 is a *runnable reconstruction*, **not** the original externally produced LC009 archive. LC-013 is a separately identified post-preregistration successor to LC-012. Earlier negative results and their original limits remain intact. The original 2025 time-anchor/Codex conception is historically distinct from these executable experiments.

## Authorship and citation

Project lead: Ryan Feller, [ORCID 0009-0000-7863-5792](https://orcid.org/0009-0000-7863-5792). See [`CITATION.cff`](CITATION.cff). This repository is not a DOI registration, ORCID Work entry, external peer review, or proof of intellectual-property entitlement for all possible embedded contributions.

## Open-source release boundary

**MIT license authorized:** The owner has expressly confirmed rights to the LexiFORM code, datasets, logs and historical archives under their control and authorized MIT for that material. See [publication authorization](docs/PUBLICATION_AUTHORIZATION_20261018.md) and [release gates](docs/RELEASE_GATES.md). This does not grant rights to separately owned third-party content. Preservation and source disclosure do not establish semantic correctness or reproducibility beyond the executed tests.

## Program separation

Fork, Shared World, model-weight training, Temporal Operations, RUNS Forge, and FractureEngine are separate projects. Cross-reference is not inheritance, endorsement, integration, or mutual verification.

## Project status

`RIGHTS_APPROVED_BASELINE_v0.1.2`. The public repository exists; the LC001–LC013 archive population is published only once the remote Git commit is pushed and verified. The snapshot registry and earlier addenda retain their original preparation-time metadata; they are not retroactive publication receipts. No DOI, ORCID Work registration, peer review or deployment is asserted by this release.

## Publish to the already-created GitHub repository

The existing public repository has a README and an MIT license. This exact, hash-bound baseline can be pushed into it after local preflight using [the non-force existing-repository publisher](tools/publish_existing_repo.py):

```powershell
py -3 .\tools\publish_existing_repo.py
py -3 .\tools\publish_existing_repo.py --publish --confirmed-rights
```

The first command is read-only verification. The second **publishes the historical archives**, verifies the remote commit, and then creates a versioned annotated tag. See [`scripts/README.md`](scripts/README.md). Do not invoke the older repository-creation flow.
