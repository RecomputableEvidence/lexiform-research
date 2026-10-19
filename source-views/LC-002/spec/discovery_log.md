# Candidate-alphabet pressure log — v1.0.0

**This is a design rationale, not a claim that machine-driven alphabet discovery has been achieved.** The pilot begins with the smallest distinctions the episode and conformance challenges reveal; symbols are explicit experiment choices, not discoveries of universal semantic atoms.

| Need / pressure | Chosen feature | Could existing features express it? | New ambiguity/cost | Adversarial control |
|---|---|---|---|---|
| Distinguish sealed status from inspection outcome | Two atomic predicates `S`, `P` | Not with a single opaque Boolean without losing missing-condition identity | Predicates domain-specific; not universal | Unknown `P` cannot turn into false `S` |
| Conjunctive authorization | Binary `&` | Hard-coding a monolithic eligibility predicate would hide the compositional structure | Three-valued AND logic must be fixed | Missing/false independent truth-table cases |
| Test semantic equivalence under changing scope | `!`, `|` | Equivalent reformulations cannot be expressed through `&` alone | Added operators and proof obligations | De Morgan valid; negation-scope mutant rejected |
| Test direction-sensitive composition | `>` | No; `&` and `|` are commutative | Material implication semantics explicitly declared | Operand order reversed must change meaning under some valuation |
| Share repeated structure | Parameterized, versioned `G1(x)` | Yes, by restating the expanded expression | Registry expansion, version management, extra checks | `G1` and `G2` produce different results under selected valuation |
| Keep history when evidence changes | Stage-indexed immutable evidence events and `REASSESS` | Not a valid expression rewrite | Snapshot selection and provenance costs | Earlier stage intact after later conflicting state |
| Independent reconstruction | Independent A/B bounded reconstructions | Evaluator value alone cannot expose premise qualifications | Additional provenance lookup | Unknown and false remain different |

**Deferred because not yet required:** quantifiers, higher-order definitions, universal grounding, actual temporal operators inside expressions, multimodal codecs, learned parsing, evidence authentication, self-describing bootstraps. Adding one of these requires a new grammar version and new conformance tests. The time semantics presently live in evidence snapshots, **not** in the symbolic expression language. This is an observed limitation and an explicit next pressure point.

**Proposed grammar discovery cycle:** (1) gather irreducible failed distinctions, (2) propose one primitive or compositional rule, (3) compare with compositions of existing primitives, (4) freeze new version with provenance of pressure cases, (5) run an independent, preregistered challenge set, (6) retain failures, regressions and added evaluation cost. No grammar-learning algorithm is implemented yet.
