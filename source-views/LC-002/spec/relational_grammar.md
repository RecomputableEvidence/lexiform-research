# LC-EXP-002 / Relational treatment grammar REL-1.0.0

This is a newly introduced **bounded experiment**, not a recovered historical Codex and not a claim of general semantic understanding.

Expressions are fully parenthesized ASCII, case sensitive, and have typed operations:

```
entity ::= [A-Z][A-Z0-9]*
stage  ::= 0 | 1 | 2 | ... (non-negative decimal integer, no leading zeros)
test   ::= S(entity) | P(entity)
path   ::= R(entity,entity) | C(path,path) | J(test,path) |
           AT(stage,path) | H1(entity,entity,entity) | H2(entity,entity,entity)
```

- `R(a,b)`: directed **observed link** from `a` to `b`, whose evidence is explicitly retrieved at the active stage; not a general authorization grant.
- `C(left,right)`: a **specific composed path witness**; only valid when left.end=right.start and both have the same effective evidence stage. It does not assert that all indirect links exist or that a global relationship is transitive.
- `J(test,path)`: qualify the specific path with `S` or `P` evidence on an endpoint in that path. Unrelated entities are rejected rather than treated as irrelevant context. Strong Kleene conjunction combines the test and path witness.
- `AT(stage,path)`: explicitly set the evidence stage of its operand. Mixing stages inside one composed path is invalid, not evidence for historical continuity.
- `H1(a,b,c)`: frozen macro `C(R(a,b),R(b,c))`.
- `H2(a,b,c)`: frozen, **different version** `J(P(b),C(R(a,b),R(b,c)))`. H2 is not an automatic upgrade of H1.

Reversing link endpoints, rearranging chain order, changing a guard's scope, and replacing an immutable macro version can change meaning, yield `U`, or be invalid; the decoder must not silently repair them.

`T`, `F`, `U` refer to satisfaction of a **specified path witness**, not universal existence, safety, or legal standing. Unknown and conflicting observations retain their separate provenance reasons. Latest-stage evidence selection is a declared simplifying test convention, not a real-world continuity rule. Evidence selection is implemented independently in the two interpreters.

The shared semantic comparison output includes endpoints, active stage, `T/F/U`, per-atom evidence IDs/reasons, ordered links and guards. Reconstruction must not introduce an additional link, silently convert `U` to `F`, or omit a guard.

Both interpreters receive the same publicly specified grammar and evidence input, but use different parsing and evaluation strategies. Independence does not extend to the declared semantics, selection of test fixtures, operating system, or provenance authentication.
