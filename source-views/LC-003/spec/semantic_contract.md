# LC-EXP-003 / Evidence-bound semantic contract 1.0.0

The subject is a narrow, declared **path-witness calculus**. `T`, `F`, `U` express satisfaction of **named conditions using the available claims**; they are **not** certifications of real-world truth, current authority, or continuity.

## Four separate clocks/identities

An evidence record has a unique ID, an atom `R(A,B)`/`P(B)`/`S(A)`, a declared value `T/F/U`, `observed_stage` (availability of the declaration), `valid_from`, `valid_until` (exclusive, or null), a nonempty source label, and an explicit `persistence_policy`.

- `query_stage` is the stage **about which** an interpretation is requested.
- `knowledge_stage` is the latest stage of material **available to** this interpretation.
- `observed_stage` identifies when a given assertion/observation became available; it need not equal the stage about which it speaks. Retrospective assertion is distinguishable by `observed_stage > query_stage` in the trace.
- `[valid_from, valid_until)` is the source's **claimed** applicability interval. `open_asserted` must be explicit for a null endpoint. None of this verifies temporal standing in the physical world.

Lookup is eligible iff `observed_stage <= knowledge_stage` AND `valid_from <= query_stage` AND (`valid_until is null` OR `query_stage < valid_until`). Within eligible rows for a given atom, select those having the highest `observed_stage`. Conflicting selected values produce `U(conflict)`, without discarding IDs; absent or ineligible evidence produces `U` with a reason. This is one **stipulated selection policy**, not a universal epistemology. An eligible newer record displaces older eligible ones, but older records are not removed from the ledger.

Input checks reject malformed atom, duplicate ID, negative/Boolean/nonintegral clock, missing source, unknown truth status, improper validity interval, unspecified persistence policy, and changes to an admitted macro version's definition. Ledger records are frozen; the serialized digest binds their canonical order. This is *local integrity*, not cryptographic authorship.

## Relational grammar

Inherited from LC-EXP-002: `R(a,b)`, `C(path,path)`, `J(test,path)`, `AT(stage,path)`, `H1(a,b,c)`, `H2(a,b,c)`; `test` is `S(entity)` or `P(entity)`. Directed endpoints and effective `query_stage` must match in a composed path. `AT` changes **query_stage** for its subtree, not **knowledge_stage**. Unmatched scope/guard and incompatible endpoints are rejected.

`H1` v1 and `H2` v2 are admitted only with *their original LC-EXP-002 expressions*. Expanded evaluation is allowed but invocation, version, parameters, registry digest, and expansion lineage are separately preserved in the result envelope. Interpretations may have equal projections and distinct histories.

## Operations

- `REWRITE`: typed rule `C(C(x,y),z) → C(x,C(y,z))`, only for well-typed contiguous, stage-aligned path witnesses. The rule relies on associativity of concatenation and the chosen 3-valued conjunction. Both engines check the relevant projection on the supplied evidence. A hash-bound receipt retains predecessor and successor expressions separately; it is not a universal formal proof.
- `REASSESS`: original expression remains identical; query time is fixed; the successor ledger **must append**, never remove/rewrite previous record IDs. Knowledge cutoff and evidence may change. Both previous and new traces and their hashes remain available. A reassessment may produce the same outcome (an evidentiary update is not forced to be a truth change).
- `COMPUTATIONAL REUSE`: in-process typed DAG hash-consing and context-bound memoization. Key includes node, ledger digest, query stage, knowledge stage, registry digest and contract version. Cached values are defensive copies. This is **not** persistent reuse across processes and does **not** establish novel semantics.

## Independence ceiling

Engine A executes an expanded typed AST over a hash-consed DAG. Engine B uses postfix instructions on a stack. A conventional typed-AST comparator shares the same grammar and immutable evidence index. All use the same indexed selection library, stipulated semantics, and fixtures; this is *partial implementation independence*, not independent evidence judgment or source authenticity. No LLM/neural participant is part of this experiment.
