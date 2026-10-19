# LC-EXP-001 / Frozen grammar v1.0.0

**Status:** experimental hypothesis, not recovered historical Codex.

The alphabet was chosen to express the distinctions required by the initial episode. It is not claimed to be minimal, optimal, or historically original. Candidate changes must create a new version and be tested against held-out cases. The first version uses two observed predicates `S` (sealed) and `P` (inspection passed), logical operations `!`, `&`, `|`, `>` (material implication under strong Kleene logic), and a definition family `G<version>`.

```
expr  ::= atom | negate | binary | reference
atom  ::= ("S" | "P") "(" entity ")"
negate ::= "!(" expr ")"
binary ::= ("&" | "|" | ">") "(" expr "," expr ")"
reference ::= "G" positive_integer "(" entity ")"
entity ::= ASCII letter followed by ASCII letters/digits, except operator names
```

Whitespace may appear between tokens. Entities and macro parameters are not quoted, and their names are deliberately restricted. An expression using an undefined definition version MUST fail rather than upgrade silently. Macros are immutable within an experimental run. The registry's canonical SHA-256 is recorded with every trace event. Neither parser is allowed to infer a definition that is not declared in the registry.

**Truth values:** `T`, `F`, `U`. `!U = U`; `&(F,anything)=F`, `&(T,T)=T`, all other AND cases are U; OR dual; `>(a,b) = |(!(a),b)`.

**Observations:** Every signed observation is an evidence event with an integer effective stage `0,1,2`; a snapshot at time `t` uses the latest observation whose effective stage is `<=t`. If conflicting observations exist at the same latest stage, the atom is `U` with conflict provenance. This is a closed-world-with-explicit-unknown query model, NOT a claim that unknown observations are false. Persistence of unmodified observations between snapshots is an explicit experimental assumption. Snapshot evidence provenance identifies source IDs and conflicting claims.

**Rule:** `G1(A)` is the condition for transfer authorization (not a real-world transfer policy). Only `T` establishes authorization; `F` or `U` do not. `F` is known counterevidence, while `U` is missing/conflicting evidence. The rule intentionally allows changes in authorization as the state changes.

**REWRITE:** Claims expression equivalence over *all* valuations of the atomic variables in the three-valued logic. The executable verifier enumerates all `3^n` valuations for expressions with at most 8 distinct atoms. It rejects if equivalence is unproven or fails, and does not use evidence-history transitions as rewrites.

**REASSESS:** Reevaluates the *same* expression under a later evidence snapshot. Previous snapshots and evidence remain immutable. This is NOT equivalence-preserving rewriting.

**Computational independence:** Interpreter A uses a recursive-descent parser and recursive AST evaluator; Interpreter B uses frame-stack parsing, a postfix virtual machine, and independently authored three-valued truth functions. Neither imports the other or shares a parser/AST. Both read this publicly declared grammar and registry.

**Limits:** This toy grammar has no quantifier, negated evidence, spatial references, modality encoders, no uncertain probabilities, no language learning, and no self-bootstrapping decoding key. It tests a bounded semantic kernel. It does not establish general semantic understanding or time-anchor decipherability.
