# LC-EXP-012 — Frozen candidate semantics v0.1

**Subject:** competing, conditional and cyclic claim relationships, with historical reassessment. These semantics are **stipulated experimental choices**, not generally justified world-model semantics. This package is **not** a production adjudicator or authority certificate.

## 1. Objects and distinct standing

- **Claim:** immutable claim (`id`, kind, predicate, subject, object, `T/F`, observation stage, valid interval, context, source evidence). An asserted value is not certified fact.
- **Condition observation:** a scoped `key:T/F` fixture used only in relation guards, independently of contested claim resolution. Multiple eligible values disagreeing → `U`. Missing → `U`; neither absence nor contradiction is `F`.
- **Relationship:** a typed claim-to-claim link (`CORRECTS`, `DISPUTES`, `SUPERSEDES`, `ADDS_CONTEXT`), source and target, time/context, evidence IDs, plus guard expression. The relationship is itself an assertion.
- **Review admission:** `ADMITTED/WITHHELD` and an appropriate declared rule, reviewer identity, observation stage and evidence reference. A matching permission entry is required; **identities and authority are not externally authenticated**.
- **Claim standing:** the evaluator's derivation for `(query_stage, knowledge_cutoff, context)`. It is not the same object as the original assertion.
- **Interpretation:** scalar `T/F/U` plus audit projection (`accepted`, `defeated`, `undecided`, `attacks`, `admitted`, `pending`, `disputed`, `qualifiers`, `support`). An unchanged scalar with changed support is still a change of provenance.

## 2. Scoped permission, guard and admission

1. Claims and relationships are eligible only if `observed <= knowledge_cutoff` and `from <= query_stage < until` and the named context is present.
2. An admission requires a declared reviewer permission for the relationship kind, reviewer validity at admission time, an overlapping permitted context, matching type-specific rule and earlier accessible evidence. Execution in a query context outside the reviewer permissions does not activate the link.
3. Guards are separately evaluated using strong Kleene `T/F/U` through `CONST`, `FACT`, `NOT`, `AND`, `OR`; `FACT` draws on scoped synthetic condition observations. The guard is not allowed to inspect conclusions from its own claim-contestation graph. This prevents self-supporting circular admission through a guard **by construction of this experiment**, not by solving general nonmonotonic context semantics.
4. Only a link with admitted review and `T` guard is active. Withheld review or `F` guard makes it inactive. An unresolved admission or `U` guard is pending. A pending attack onto a queried proposition **forces `U`** conservatively; no contested correction is silently ignored.
5. `DISPUTES` adds a challenge marker, never a defeat solely by link type. `ADDS_CONTEXT` adds a qualifier and does not change truth directly. `CORRECTS` applies to observation claims and `SUPERSEDES` to policy claims, with declared scope only.

## 3. Competing revision semantics

For each eligible claim-to-claim admitted `CORRECTS` or `SUPERSEDES`, create a directed *defeat argument* `source → target`. Two admitted relationships having the same endpoints are one attack edge for the scalar calculation, but both IDs remain in provenance.

Under this **explicit policy choice**, standing for the attack graph uses the grounded (skeptical) extension of a finite abstract argumentation graph:

- Start with no accepted or defeated arguments.
- Admit arguments all of whose attackers are defeated; an admitted argument defeats each target it attacks.
- Repeat until no new acceptances are possible.
- Anything neither accepted nor defeated is `UNDECIDED`. An even correction cycle without external support is not resolved by recorded order or timestamp.

This may produce reinstatement of a previously defeated claim if its attacker is itself defeated by a justified attack. **Such reinstatement is a formal argumentation outcome, not a determination that the earlier assertion was physically true**.

For each proposition: if all accepted eligible claims share a value and there are no undecided eligible claims and no pending potentially relevant link, return that value. Otherwise return `U`. Zero accepted claims → `U`. This policy deliberately sacrifices some opportunities for a scalar answer to avoid silently resolving unsettled contestation.

The grounded extension exists for finite graphs under the declared attack relation. It is only one reasonable **candidate**, not a universal policy for all correction semantics; e.g., more intricate review institutions may demand priorities, evidence reliability weights or rule-specific defeasibility.

Reference for the formal predecessor of this *policy*, not evidence of novel meaning: Dung, *On the Acceptability of Arguments and Its Fundamental Role in Nonmonotonic Reasoning, Logic Programming and n-Person Games* (1995), <https://cse-robotics.engr.tamu.edu/dshell/cs631/papers/dung95acceptability.pdf>.

## 4. Expressions and interpreters

Abstract grammar: `ATOM(kind,predicate,subject,object)`, `LINK(relation_id)`, `NOT(x)`, `ALL(x,...)`, `ANY(x,...)`, `SCOPE(query,cutoff,context,body)`.

Three comparison pathways:

- `src/lexicon.py`: list-form descriptors, iterative IN/OUT/UNDEC acceptance propagation, per-instance scoped state reuse.
- `src/typed_baseline.py`: separate conventional typed AST and characteristic-function fixed-point evaluator, per-instance scoped state reuse.
- `src/oracle.py`: independently coded finite-set **oracle of the declared policy**, enumerating candidate complete extensions on at most ten claims. It shares the policy target and input validator assumptions; it is NOT an independently established theory of truth or a certified evaluator.

All arms return the same full audit projection. Their independent coding reduces some implementation-correlated errors but cannot eliminate common specification or synthetic-fixture errors.

## 5. Historical operations

- `REWRITE`: registered three-valued De Morgan transformation `NOT(ANY(...)) → ALL(NOT(...))`. Verify the **entire** output projection before emitting a rewrite receipt; no historical evidence mutation.
- `REASSESS`: accept only an exact append-only prefix of the six typed ledger categories; re-evaluate both historical and successor snapshots and preserve their individual hashes, cutoff and outputs. It is not a rewrite. Category-wise prefix does **not** establish a globally ordered cross-category event sequence, a physically complete record, or the LC010 portable chain semantics.

## 6. Deliberate experimental limits

The alphabet is an **experimentally chosen formal grammar**, not autonomously discovered. Synthetic review permissions are not proven institutional authority. External fact reliability, admission-policy legitimacy, condition-dependency cycles, secure source attestations, global event ordering, real-world temporal causality, independently deciphered meaning, unrestricted compositional inference and lexicon-specific performance superiority are **not established**. Some true relations can be conservatively reported `U`.

The two machine interpreters and oracle are all written by the same experiment author and inherit the same declared semantics; cross-check agreement is bounded interoperability, not independent empirical grounding. This package is NOT evidence of NGAST/Cairn model training.
