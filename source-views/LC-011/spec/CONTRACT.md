# LC-EXP-011 — Frozen candidate semantics, v0.1

This is a **candidate experiment**; its expressions and adjudications are *declared synthetic semantics*, not authenticated evidence about the external world. It does not modify LC-001–LC-010.

## Objects and identity

- `claims`: immutable append-only assertions (`id`, typed subject/predicate/object, `T` or `F`, observation stage, applicability interval, context list and evidence-source ID). A recorded claim is not a validated fact.
- `links`: typed `CORRECTS`, `DISPUTES`, `SUPERSEDES`, `ADDS_CONTEXT` **claims about other claims**. A link alone does not determine truth. Its direction, endpoints, context, interval, evidence references, and date are explicit.
- `admissions`: separate declared review decisions. Link effects require a matching admission, its type-specific rule name, an evidence reference, and a knowledge stage at which the review has been recorded. Reviewers and sources are **not cryptographically authenticated**.
- `evidence`: synthetic source-referenced records. Presence does not establish physical occurrence, truth, reliability, or authority.
- `standing`: computed separately for each `(query_stage, knowledge_cutoff, context)`. `T/F/U` are values under this experiment's logic, not externally certified truth.
- `historical interpretation`: separately computed per ledger and knowledge cutoff. `REASSESS` keeps both before/after results; it is not a semantic `REWRITE`.

## Consequences of admitted links

- `CORRECTS`: when both source and target observation claims are applicable and admitted, target is excluded from the active *current* set within link's scope. This is **declared adjudication**, not proof the source is true or that the old assertion never existed.
- `DISPUTES`: source and target observation claims remain active; the target receives a dispute marker. A dispute by itself is not a refutation. Opposing active claim values produce `U`.
- `SUPERSEDES`: same action on active governing policy claims within its *explicit effective interval*. A supersession must be policy-to-policy. Earlier query stages outside the interval remain historically unaffected.
- `ADDS_CONTEXT`: context-source claim annotates the target when admitted, applicable and referring to the same subject/object. It does not alter the target truth value.
- Unadmitted relations are visible as pending when observed and applicable; withheld relations have no standing effects. An unknown relation is `U`.
- Absent claims produce `U`; a set of conflicting active `T`/`F` claims produces `U`; same-valued active claims preserve the scalar but change support and provenance.

**Limits:** this simple calculus cannot decide reliability of competing sources, verify external authority, resolve networked cross-topic revisions, infer correct supersession from a raw timestamp, or establish claims whose underlying observations were never authenticated. Admitted relationships are stipulated test facts.

## Expression grammar

Lexicon/list form uses:

- `['A', kind, predicate, subject, object]` — typed proposition;
- `['L', relation_id]` — admission standing of relationship itself, distinct from standing of its affected proposition;
- `['N', x]`, `['&', x, y, ...]`, `['|', x, y, ...]` — Kleene 3-valued negation, conjunction, disjunction;
- `['S', query_stage, knowledge_cutoff, context, x]` — explicitly scoped subexpression.

A conventional typed-AST arm uses `ATOM`, `LINK`, `NOT`, `ALL`, `ANY`, and `SCOPE` with different syntax. Both return a scalar value and seven normalized provenance sets (`active`, `displaced`, `disputed`, `qualifiers`, `admitted`, `pending`, `support`). The independently coded third-path oracle evaluates abstract expression dictionaries.

The three execution paths share the **same written semantic target, fixture author, and ledger-validation contract**. Agreement is formal interoperability under a supplied specification, not independently discovered semantics.

## Transformations

- `REWRITE`: only registered `NOT(ANY(x1,...)) -> ALL(NOT(x1),...)` using strong Kleene three-valued logic, with hash-bound expression identity and checked full result projection.
- `REASSESS`: append-only ledger and knowledge-cutoff transition; both interpretations preserved with their hashes and affected fields.
- `CLAIM_RELATIONSHIP`: separate link event + optional later admission; never interchangeable with `REWRITE`.

Append-only comparison uses canonical JSON byte prefix equality per typed ledger category; it rejects reordering/removal/substantive historical changes within those categories. The prototype **does not** implement a signed globally ordered multi-type event stream or LC010's full portable packet chain.

## Negative and null results

- Newer conflicting claim without admitted correction: `U`, even though predecessor latest-stage heuristic would choose the newer value.
- Proposed unadmitted correction: `U` in the same case.
- Corroborating observation: scalar unchanged, support set changes.
- Unrelated observation: semantic projection unchanged but ledger digest changes.
- Reverse link direction and context changes produce independently observable differences.
- Invalid source/evidence IDs, duplicate identities, negative stages, policy/observation type crossover, and mutable historical prefixes are rejected.

## Experiment status

The compiled comparison and oracle are **research controls**, not external certification. Generated combinations are syntactically new to their runtime instantiations but based on a known grammar; general semantic discovery and external linguistic grounding are unproven. Efficiency is measured separately and must compare identical output fidelity.
