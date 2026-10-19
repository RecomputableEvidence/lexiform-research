# Lens Shift Method Specification v0.1.4-CANDIDATE

**Artifact ID:** `LENS-SHIFT-METHOD-SPEC-v0.1.4-CANDIDATE`  
**Predecessor:** `LENS-SHIFT-METHOD-SPEC-v0.1.3-CANDIDATE`  
**Predecessor source filename:** `LENS-SHIFT-METHOD-SPEC-v0.1.3-CANDIDATE(20261011-175147).md`  
**Predecessor raw UTF-8 SHA-256:** `2d53a5bb00cffecdaa6f416a4f000842d03915c46347664a072fef21c77cc92c`  
**Revision basis:** October 13, 2026 subject-first operational-use correction  
**Status:** `PROVISIONAL_RESEARCH_METHOD_SPECIFICATION`  
**Validation standing:** `NOT_YET_EMPIRICALLY_QUALIFIED`  
**Freeze standing:** `NOT_FROZEN`  
**Successor relation:** `SUBJECT_FIRST_OPERATIONAL_PRESENTATION_REPAIR`  
**Predecessor preservation rule:** v0.1.3 and its prior lineage retain their historical text, identity, execution results, validation standing, and claims. This successor does not retrofit its clauses into prior executions.  
**Successor scope:** separates internal deconstruction/classification/reconstruction work from user-visible method evaluation; prevents recurring self-examination from displacing the requested subject; specifies subject-first output and authorization conditions; preserves optional empirical qualification as a separate requested task. All other prior clauses are retained unless amended by the explicit v0.1.4 provisions below.  
**Standing effect:** specification revision alone confers no empirical validation or claimed superiority.
---

## 1. Purpose

Lens Shift is a modular research and operational examination method for deliberately varying the analytical representation of a bounded subject and observing whether controlled changes in perspective, distinction, relationship, transition structure, contextual framing, sequencing, or resource allocation produce recognizable and reproducible structural effects.

Lens Shift is not defined as:

- a model capability;
- model-weight learning;
- unrestricted recursive prompting;
- a correctness oracle;
- an authority mechanism;
- proof that multiple perspectives inherently improve an answer;
- proof that an examined artifact is valid;
- proof of Lens Shift's own utility.

Lens Shift is an externalized, portable methodological object. Its effectiveness, efficiency, transferability, and utility are external empirical questions.

Lens Shift is designed for revision through preserved succession. A current constraint, lens, classification, comparator, threshold, or operational rule is not presumed permanent merely because it is presently useful or admissible. Change MUST occur through an inspectable successor relation rather than by rewriting predecessor history.

The method therefore distinguishes preservation from immobilization:

\[
preserve(previous\ standing) \not\Rightarrow freeze(future\ standing)
\]

and treats responsible evolution as part of the method rather than an exception to it.

---

## 2. Core Research Proposition

Given a bounded subject \(S\), a registered manipulation configuration \(M\), resource budget \(Q\), and contextual configuration \(C\):

\[
R = f(S,M,Q,C)
\]


For v0.1.2, every execution also has a temporal coordinate or bounded interval \(T\). Where subject, context, evidence, authority, dependency, or runtime state can change materially over time, the execution record MUST bind that temporal state:

\[
R_T = f(S,M,Q,C,T)
\]

This does not assert that time itself caused an effect. It prevents an observation made under one temporal state from silently inheriting standing in another.

Controlled variation of one declared variable should, where materially relevant, produce a recognizable change in the resulting representation:

\[
x \rightarrow x'
\]

\[
\Delta R = f(S,x',Q,C) - f(S,x,Q,C)
\]

A candidate Lens Shift primitive is supported only to the extent that the resulting effect is:

1. observable;
2. representable;
3. appropriately directed;
4. reproducible within declared tolerance;
5. distinguishable from mere wording variation;
6. absent or materially reduced where the manipulated property is irrelevant.

---

## 3. Primary Design Principle

Lens Shift seeks **reproducible structural sensitivity**, not deterministic prose.

The target is not:

\[
same\ input \Rightarrow same\ words
\]

The target is:

\[
controlled\ manipulation_X \Rightarrow recognizable\ effect\ class_X
\]

Different executions may use different language while still exhibiting the same structural response.

---

## 4. Three-Layer Analytical Model

Lens Shift explicitly separates:

### 4.1 Transformation Layer

What the manipulation changes in the representation, inspection procedure, or analytical emphasis.

### 4.2 Detection Layer

How the system determines whether the predicted structural signature appeared.

### 4.3 Decision Layer

How a detected effect becomes a finding, materiality determination, disposition, or repair candidate.

The canonical chain is:

\[
S
\xrightarrow{Transformation}
R'
\xrightarrow{Detection}
E
\xrightarrow{Decision}
(F,M,D)
\]

where:

- \(S\) = bounded subject;
- \(R'\) = transformed or inspected representation;
- \(E\) = detected structural effect;
- \(F\) = finding;
- \(M\) = materiality determination;
- \(D\) = disposition.

These layers MUST remain distinct.

A failed detector does not prove the transformation had no effect.  
A permissive detector must not manufacture an effect that the transformation did not produce.  
A detected effect does not automatically become material.

---

## 5. Evidentiary Object Separation

The following objects MUST remain distinct:

1. Method specification
2. Manipulation class
3. Lens contract
4. Subject
5. Execution
6. Observation
7. Detected effect
8. Finding
9. Materiality determination
10. Disposition
11. Repair
12. Successor subject
13. Effect record
14. Utility claim
15. Evidence-basis state
16. Claim ceiling
17. Qualification vector
18. Amendment or supersession relation
19. Re-examination trigger

No object inherits stronger standing merely from adjacency, derivation, or inclusion.

In particular:

\[
Observation \neq Effect
\]

\[
Effect \neq Finding
\]

\[
Finding \neq Materiality
\]

\[
Materiality \neq Disposition
\]

\[
Disposition \neq Repair
\]

\[
Repair \neq Successor\ Validity
\]

---

## 6. Manipulation Classes

The umbrella term **Manipulation Class** replaces the earlier phrase “Lens Shift primitive classes.”

Registered manipulation classes MAY include:

### 6.1 `LENS`

Changes analytical perspective or inspection emphasis.

### 6.2 `DISTINCTION`

Separates propositions, meanings, objects, or states that might otherwise collapse.

### 6.3 `RELATIONSHIP`

Changes the declared relation between objects.

Examples:

\[
A \rightarrow B
\]

\[
A \parallel B
\]

\[
A \not\Rightarrow B
\]

### 6.4 `TRANSITION`

Changes state progression or temporal structure.

### 6.5 `MECHANISM`

Changes how one state, observation, or event may produce another.

### 6.6 `CONTEXT`

Adds, removes, or changes a declared contextual layer.

### 6.7 `SEQUENCE`

Changes ordering of otherwise equivalent operations.

### 6.8 `RESOURCE_BUDGET`

Changes visible token budget, compute allocation, time, or reviewer effort where observable.

Each manipulation class is independently testable.

---

## 7. Lens Contract

A **lens** is a registered analytical operation intended to increase sensitivity to a declared class of structure while preserving declared invariants.

Each candidate lens MUST have both:

1. a human-readable method description; and
2. a machine-testable Lens Contract.

Minimum Lens Contract fields:

```yaml
lens_id:
lens_version:
name:
target_construct:
unit_of_analysis:
inspection_question:
transformation_operator:
preserved_invariants: []
required_input_schema:
positive_fixture_conditions: []
negative_fixture_conditions: []
expected_positive_signature: []
expected_null_signature: []
effect_detector:
effect_threshold:
false_activation_rule:
tolerance_policy:
known_confounds: []
required_context: []
temporal_scope:
evidence_requirement:
minimum_candidate_budget:
incompatible_conditions: []
sequence_dependencies: []
materiality_rule:
default_claim_ceiling:
reexamination_triggers: []
output_fields: []
validation_status:
```

A change in wording alone is insufficient to establish a distinct lens.

---

## 8. Lens Qualification States

A candidate lens may receive one or more of the following bounded experimental states:

### `EXPECTED_EFFECT`

The target construct is present and the predicted structural signature appears.

### `VALID_NULL`

The target construct is absent or immaterial and no material differential effect appears.

### `FAILED_DISCRIMINATION`

The target construct is intentionally present but the lens fails to expose the expected effect.

### `FALSE_ACTIVATION`

The lens produces the target signature where the relevant construct is absent.

### `FUNCTIONAL_REDUNDANCY`

The lens repeatedly produces no independent material contribution beyond another registered lens.

### `ORDER_DEPENDENT`

The lens's measurable contribution depends materially on prior or subsequent execution order.

### `STRUCTURAL_REPRODUCTION`

The structural signature reproduces within declared tolerance.

### `MATERIALITY_DIVERGENCE`

Reviewers or runs agree on the structural signature but disagree materially on consequence.

### `DISPOSITION_DIVERGENCE`

Materiality may be agreed, but disposition differs.

### `COST_INSTABILITY`

The structural result is stable while resource usage varies beyond declared tolerance.

### `REPLICATION_BLOCKED`

Execution cannot support the intended replication claim because required conditions were unavailable or violated.

### `INSUFFICIENT_EVIDENCE`

The execution record cannot support classification.

These states describe bounded observations; they do not define permanent standing.

---

## 9. Material Difference

A **material difference** is a detected structural effect that alters at least one preregistered relevant property of interpretation, evidence, decision, state, boundary, or disposition.

Candidate structural effect classes include:

```text
UNSUPPORTED_CLAIM_REMOVED
AMBIGUITY_EXPOSED
TEMPORAL_BOUNDARY_ADDED
AUTHORITY_INHERITANCE_BLOCKED
DEPENDENCY_SURFACED
CONTRADICTION_DETECTED
SEMANTIC_COLLAPSE_REVERSED
STATE_TRANSITION_CORRECTED
EVIDENCE_REQUIREMENT_ADDED
UNCERTAINTY_PRESERVED
DISPOSITION_CHANGED
NO_MATERIAL_DIFFERENCE
```

Stylistic variation alone MUST NOT count as material.

---

## 10. Typed Materiality Model

Materiality MUST NOT be reduced to a single untyped Boolean where the experiment depends on cross-execution comparison.

Minimum materiality record:

```yaml
materiality_scope:
affected_claim_ids: []
affected_decision_ids: []
effect_severity:
reversibility:
confidence_class:
evidence_sufficiency:
adjudicator_identity:
adjudication_basis:
materiality_outcome:
```

Materiality classes MAY include:

### `SEMANTIC_MATERIALITY`

Meaning, scope, contradiction, authority, identity, or temporal status changes.

### `EVIDENTIARY_MATERIALITY`

Necessary evidence is absent, invalid, stale, conflicting, or misattributed.

### `DECISION_MATERIALITY`

The admissible disposition changes.

### `OPERATIONAL_MATERIALITY`

A required state transition, control, or repair changes.

### `NONMATERIAL_STRUCTURAL_EFFECT`

A real typed effect exists but does not alter a relevant outcome.

This permits the method to preserve low-level sensitivity without promoting every detected difference into consequence.

---

## 11. Null Behavior

`NO_MATERIAL_DIFFERENCE` is a valid result.

A primitive can be **qualified for a stated scope** only after it demonstrates both:

\[
sensitivity
\]

when the target property is present, and:

\[
appropriate\ invariance
\]

when it is absent or irrelevant.

Positive and negative fixtures SHOULD both be included in qualification experiments.

---

## 12. Reproducibility Model

Reproducibility is multidimensional:

\[
Reproducibility =
(
signature\ agreement,
effect\ class\ agreement,
materiality\ agreement,
decision\ agreement,
cost\ stability
)
\]

A lens MAY therefore be:

- structurally reproducible;
- materially unresolved;
- dispositionally divergent;
- cost-unstable;

without collapsing those results into a single pass/fail label.

---

## 13. Comparator Taxonomy

Experiments seeking causal attribution SHOULD declare one or more comparators.

### `BASELINE_REVIEW`

Does ordinary review detect the same effect?

### `ATTENTION_CONTROL`

Does comparable analytical attention explain the apparent gain?

### `SHAM_LENS`

Does a non-target transformation produce a similar apparent effect?

### `ALTERNATIVE_LENS`

Does another lens provide equivalent or independent contribution?

### `RESOURCE_MATCHED_CONTROL`

Is the gain due to Lens Shift rather than additional visible resource allocation?

### `ORDER_COUNTERBALANCED_CONTROL`

Does the effect survive order manipulation?

### `INDEPENDENT_REPLICATION`

Does the effect survive reviewer/model separation?

No comparator is assumed necessary for every operational use, but stronger causal claims require stronger controls.

Where a comparator supports attribution, qualification, or superiority claims, comparator identity and role MUST be established independently of the observed outcome. Similarity or difference discovered after execution does not itself create valid comparator standing.

\[
observed\ difference \not\Rightarrow valid\ comparator
\]

\[
observed\ similarity \not\Rightarrow failed\ comparator
\]

---

## 14. Sequence as an Experimental Variable

Lens order MUST NOT be assumed neutral.

Candidate comparisons include:

\[
A \rightarrow B
\]

\[
B \rightarrow A
\]

\[
A \parallel B
\]

Candidate results include:

```text
NO_ORDER_EFFECT
PREPARATORY_DEPENDENCY
ANCHORING_EFFECT
CONTAMINATION_EFFECT
COMPLEMENTARY_ORDER_EFFECT
NONDETERMINED
```


A contamination effect is not limited to execution order. It MAY arise when participant-facing instructions, role labels, hidden hypotheses, expected contrasts, comparator identity, desired response characteristics, prior outputs, grading criteria, or experiment structure become available to a participant or evaluator whose valid role depends on not having that information.

Historical presence of a concept in the method specification does not by itself establish experimental contamination. Contamination is relation-specific: the relevant question is whether information crossed a boundary that the declared experimental role required to remain unexposed.

---

## 15. Observable Output-Budget Economy

Token economy is part of the Lens Shift research object, but claims MUST be bounded to what the runtime exposes.

For an execution:

```yaml
input_tokens_if_available:
declared_output_budget:
observed_output_tokens_if_available:
total_observable_tokens_if_available:
latency_if_available:
retry_count:
provider_runtime_settings:
hidden_reasoning_usage: UNAVAILABLE_IF_NOT_EXPOSED
material_findings:
confirmed_findings:
false_activations:
effect_classes:
```

Initial experiments SHOULD describe this as **Observable Output-Budget Economy** unless total resource use is actually observable.

Candidate metrics:

### Material Finding Yield

\[
MFY =
\frac{confirmed\ material\ findings}
{observable\ tokens}
\]

### Marginal Finding Yield

\[
MFY_{\Delta Q} =
\frac{\Delta confirmed\ findings}
{\Delta observable\ tokens}
\]

### Minimum Effective Budget

The smallest tested visible output budget at which the required structural signature remains reproducible within declared tolerance.

### Compression Retention

\[
CR_q =
\frac{StructuralAccuracy_q}
{StructuralAccuracy_{reference}}
\]

subject to false-activation constraints.

### Compression Loss

\[
CL_q = 1 - CR_q
\]

### Saturation

A bounded condition in which additional observable resource repeatedly produces no material new structural effect under declared coverage.

Saturation MUST NOT be interpreted as completeness.

---

## 16. Execution Profiles

These profiles are configurations of one method and are not independently validated merely by inclusion.

### `LS-COMPACT`

Minimum viable lens application under constrained visible output budget.

### `LS-SELECTIVE`

One or more deliberately selected lenses applied to a known examination problem.

### `LS-PRESSURE`

Multiple materially distinct lenses applied adversarially.

### `LS-REPAIR-REPRESSURE`

Pressure followed by bounded repair and renewed pressure.

### `LS-INDEPENDENT`

Equivalent subject examined independently without cross-contamination.

### `LS-EXPERIMENTAL`

Preregistered manipulation of lenses, sequences, budgets, fixtures, or contextual variables.

---

## 17. Temporal Execution Model

Every execution and pressure epoch is a bounded historical event:

1. it begins;
2. it persists for a bounded interval;
3. it ends.

Historical execution does not imply continuing authority.

A successor execution does not retroactively alter the identity or standing of its predecessor.

Present standing is not permanent standing. A state that is material, useful, unsafe, unavailable, inadmissible, ineffective, or unknown at one time MAY have different standing under later conditions.

Accordingly:

\[
WORKS_{t_1,C_1} \not\Rightarrow WORKS_{t_2,C_2}
\]

\[
FAILS_{t_1,C_1} \not\Rightarrow FAILS_{t_2,C_2}
\]

\[
UNKNOWN_{t_1} \neq IMPOSSIBLE
\]

\[
NOT\_YET \neq NEVER
\]

A later successful execution does not erase an earlier valid failure under different bounded conditions. A later failure does not erase an earlier valid success. The historical record SHOULD preserve both and the transition evidence between them.

Where standing changes, the successor record SHOULD identify which of the following changed materially:

```text
SUBJECT
IMPLEMENTATION
DEPENDENCY
ENVIRONMENT
EVIDENCE
AUTHORITY
OBJECTIVE
RESOURCE_BUDGET
RUNTIME
KNOWLEDGE_STATE
OTHER_DECLARED_CONDITION
```

The method MUST NOT treat present ignorance as evidence that a future state cannot exist, nor present capability as evidence that the capability will remain valid indefinitely.

---

## 18. Repair Semantics

A repair MUST NOT erase or overwrite the original issue.

A repair record SHOULD preserve:

```yaml
predecessor_subject_id:
predecessor_execution_id:
finding_id:
repair_intent:
repair_delta_artifact:
successor_subject_id:
reexecution_configuration:
repressure_result:
```

Post-repair classifications MAY include:

```text
FINDING_NOT_REPRODUCED
FINDING_MITIGATED
FINDING_RELOCATED
NOVEL_FAILURE_INTRODUCED
INSUFFICIENT_EVIDENCE
```

`LS-REPAIR-REPRESSURE` may establish that a declared signature ceased or changed under the successor state. It does not establish broad successor validity.

A constraint or rule MAY be retained, narrowed, conditionalized, amended, superseded, or retired when new evidence or changed conditions support that transition. Such a change is not required to be labeled a defect repair if the predecessor rule was valid for its historical conditions.

The transition record SHOULD preserve:

```yaml
predecessor_rule_or_constraint:
historical_basis:
pressure_or_change_condition:
successor_pathway:
preserved_invariants: []
newly_admitted_conditions: []
newly_withheld_conditions: []
reexamination_basis:
```

Preserving why a boundary existed is distinct from requiring that boundary to remain forever.

---

## 19. Representation and Operationalization Boundary

Lens Shift distinguishes:

\[
description
\neq
simulation
\neq
decision\ criterion
\neq
executable\ transition
\]

Representation of an undesirable state does not automatically authorize construction of the mechanism required to realize it.

Where recognition is sufficient, Lens Shift SHOULD prefer recognition models over realization models.

A declared inadmissible condition may be represented as:

\[
S_{inadmissible} \notin \mathcal{A}
\]

without requiring a fully encoded transition path into that condition.


An inadmissible state MAY also declare a re-examination pathway without weakening its current disposition:

\[
S_{inadmissible,T_1}
\xrightarrow{new\ evidence\ or\ changed\ conditions}
REEXAMINE
\]

A pathway is not an authorization. It records the conditions under which current withholding may be reconsidered. This prevents a temporary boundary from being silently hardened into an unsupported permanent prohibition.

---

## 20. Compression Principle

Lens Shift MAY grow in representational capability while shrinking in storage requirements.

Desired progression:

\[
prose
\rightarrow
typed\ observation
\rightarrow
stable\ distinction
\rightarrow
validated\ relationship
\rightarrow
compact\ recomputable\ representation
\]

Compression is acceptable only when supporting evidence remains recoverable, traceable, or recomputable.

---

## 21. Canonical Schemas

The method SHOULD use versioned machine-readable schemas for at least:

- lens registry entries;
- manipulation registry entries;
- subject manifests;
- execution records;
- observations;
- detected effects;
- findings;
- materiality decisions;
- dispositions;
- repairs;
- effect records;
- normalization ledgers;
- grading records;
- pre-execution commitment manifests;
- post-execution receipts.
- evidence-basis records;
- claim-ceiling records;
- role-exposure / contamination records;
- comparator provenance records;
- amendment / supersession records;
- re-examination triggers;
- qualification-vector records;
- recursive-execution lineage and termination records;
- fixed-point comparison records;
- method-snapshot identity-binding records;
- external dependency resolution and integrity records.

Schema validation does not establish semantic correctness.

---

## 22. Identity, Canonicalization, and Hashing

Where the research depends on preservation or replay, identity SHOULD be content-addressed.

The implementation SHOULD declare:

- canonicalization procedure;
- hash algorithm;
- text encoding;
- newline normalization;
- secret/redaction handling;
- whether metadata is included in identity;
- artifact-specific hash boundaries.

Separate hashes SHOULD be available, where applicable, for:

```text
subject
context surface
prompt surface
lens registry
manipulation registry
output schema
fixture
ground truth
grader rubric
run manifest
raw result
normalized result
grade
analysis
```

`HASH_MATCH` does not imply semantic correctness.

Where an execution materially relies on immutable method identity for preservation, replay, comparison, replication, qualification, epoch binding, recursive lineage, or successor-differential analysis, the identity binding MUST include:

```yaml
method_spec_id:
method_spec_hash:
hash_algorithm:
canonicalization_rule_id:
canonicalization_rule_version:
hash_boundary:
text_encoding:
newline_normalization:
redaction_handling:
epoch_binding_record_if_applicable:
```

These fields MAY be carried by an immutable epoch-binding record if the execution references that record explicitly and recomputably.

A changed hash establishes difference within the declared hash boundary. It does not itself establish semantic or material difference.

\[
Changed\ Hash 
ot\Rightarrow Material\ Difference
\]

---

## 23. Normalization Provenance

Raw results are immutable historical objects.

Normalized results are derived artifacts.


Evidence referenced by an execution SHOULD be typed at the point of use. Minimum evidence-basis states are:

```text
DIRECT
DERIVED
ASSERTED
INFERRED
MISSING
UNKNOWN
UNAVAILABLE
REDACTED
CONFLICTING
FAILED_TO_OBSERVE
```

These states are not interchangeable.

In particular:

\[
FAILED\_TO\_OBSERVE \neq OBSERVED\_ABSENT
\]

A filename, label, comment, interface badge, self-description, or unverified metadata SHOULD default to `ASSERTED` unless independently supported. `ASSERTED`, `MISSING`, `UNKNOWN`, `UNAVAILABLE`, `REDACTED`, `CONFLICTING`, or `FAILED_TO_OBSERVE` MAY support a finding about uncertainty, provenance, or evidence sufficiency; they MUST NOT alone establish a positive claim about an external state.

Normalization MUST be versioned and SHOULD preserve:

```yaml
source_output_hash:
normalizer_id:
normalizer_version:
transformations_applied: []
human_intervention:
normalized_output_hash:
normalization_status:
```

Normalization MUST NOT silently repair substantive model behavior.

---

## 24. Grader Independence

Grading provenance SHOULD include:

```yaml
grader_id:
grader_version:
grader_type:
grader_blindness:
grading_rubric_id:
grading_input_hashes: []
adjudication_path:
conflict_status:
```

Where feasible, deterministic structural validation SHOULD precede subjective adjudication.

Participant, executor, comparator, normalizer, grader, adjudicator, and decision-authority roles MUST NOT be assumed equivalent. Where role separation materially affects validity, the execution record SHOULD declare which information each role could access and when.

A role may be performed by the same human or machine only when the declared design permits that overlap. Identity overlap does not itself invalidate an execution; undisclosed overlap that violates a required independence condition does.

---

## 25. Stop Conditions

A preregistered experiment or pressure cycle SHOULD declare stopping rules.

Possible stop conditions include:

- required replication count reached;
- planned sample exhausted;
- predefined saturation condition reached;
- unacceptable false-activation threshold exceeded;
- resource ceiling reached;
- protocol defect discovered;
- unresolved adjudication divergence blocks valid continuation;
- execution environment no longer matches preregistration.

Stopping due to protocol defect MUST NOT authorize silent redesign of completed observations.

---

## 26. Threat Model

Lens Shift experiments SHOULD consider at least:

- prompt injection inside subjects;
- evaluator gaming;
- collusive or non-independent graders;
- context leakage across runs;
- benchmark overfitting;
- registry tampering;
- normalization drift;
- strategic verbosity;
- treatment leakage;
- cache contamination;
- fixture memorization;
- hidden provider/runtime changes;
- model snapshot drift.

Threat-model presence does not imply threat occurrence.

---

## 27. Regular Operational Use

Lens Shift is intended to become callable methodology rather than permanent conversational overhead.

Candidate operational path:

\[
ordinary\ operation
\rightarrow
trigger
\rightarrow
profile\ selection
\rightarrow
Lens\ Shift
\rightarrow
result
\rightarrow
optional\ evidence\ record
\]

Routine use SHOULD select the smallest profile reasonably capable of answering the examination question.

### 27.1 Subject-First Operational Contract (v0.1.4 amendment)

When a user supplies a substantive subject and invokes Lens Shift as the means of analysis, the **subject and its findings** are the deliverable. Lens Shift is an enabling process, not an alternative subject, and its observed procedural effect is not an obligatory report section.

The LLM SHOULD use analytical decomposition, classification, cross-perspective inspection, and reconstruction to improve the subject-level result. This instruction describes intended analytical operations; it does not assert that an externally unverifiable hidden reasoning sequence has been instrumented or empirically qualified.

In routine subject-first operation, the response MUST:

1. Preserve the user's objective, subject identity, relevant constraints, and useful question as the controlling target.
2. Deconstruct the subject into materially distinct components, evidence, relations, dependencies, alternatives, and failure conditions as needed to analyze it.
3. Classify source-supported facts, estimates, assumptions, competing explanations, uncertainties, and decisions without promoting one state into another.
4. Reconstruct an integrated account of **the subject**, including findings, consequential tradeoffs, executable decisions or next tests where useful.
5. Suppress method-centric narration, self-referential recursion reports, plateau declarations, effect celebrations, methodological approval requests, and unsolicited claims about Lens Shift's performance.
6. Avoid treating the final response's polish, structure, or length as proof of the internal analysis process's utility.

The method's possible contribution during analysis MAY be left implicit. There is no requirement to ask for the user's approval of an observed analytical effect before presenting a substantive subject-level finding. This does NOT supersede authorization required for external actions, disclosure, consequential decisions, data access, or other independently controlled transitions.

No method-level validity, robustness, fixed-point, causal-effect, or superiority claim follows solely because a subject-level answer appears useful.

### 27.2 Analytical Focus and Repetition Boundary (v0.1.4 amendment)

An analytical gap or unresolved finding MUST NOT automatically redirect work into repeated analysis of the method itself. A gap should trigger a subject-relevant operation when one is useful: obtain evidence, test an alternative, identify a necessary instrument, quantify uncertainty, preserve a limit, or deliver the best bounded result.

Recursion is allowed when it provides new material information about the **subject** or is explicitly the requested subject. If additional passes yield no material subject-level gain within the available budget, normal operational use SHOULD conclude or change to an appropriate subject-relevant action, without declaring a validated fixed point.

Where the user explicitly requests a method qualification experiment, the experimental reporting clauses remain applicable. Routine subject analysis MUST NOT be silently converted into such an experiment.

---

## 28. Portability Requirement

Lens Shift MUST NOT depend on any one model having previously participated in its development.

A conforming execution package SHOULD contain enough information for another suitable reviewer—human or machine—to instantiate the method without access to the originating conversation.

Therefore:

\[
Lens\ Shift \neq learned\ model\ state
\]

---

## 29. Claim Ladder

### Level 1 — `EXECUTION_EXISTENCE`

Lens Shift was executed.

### Level 2 — `OBSERVED_EFFECT`

A measurable difference occurred.

### Level 3 — `REPRODUCIBLE_EFFECT`

A declared manipulation repeatedly produced a recognizable structural effect.

### Level 4 — `ATTRIBUTABLE_EFFECT`

Relevant controls support attribution of the effect to the Lens Shift manipulation rather than obvious competing explanations.

### Level 5 — `TRANSFER`

The effect survives declared changes in wording, fixtures, reviewers, models, or domains.

### Level 6 — `UTILITY`

The attributable effect produces sufficient practical benefit relative to cost.

No lower level implies a higher level.

The Claim Ladder is a claim-admissibility structure, not a scalar quality score, conformance score, or universal maturity ranking.

For multidimensional qualification, v0.1.2 additionally permits a qualification vector:

\[
Q = (E,S,R,A,I,D)
\]

where:

- \(E\) = execution-record completeness;
- \(S\) = structural discrimination;
- \(R\) = reproducibility;
- \(A\) = attribution/control adequacy;
- \(I\) = independent replication;
- \(D\) = domain/scope qualification.

Each dimension MUST retain its own evidence and standing. Strength in one dimension MUST NOT be used to fill an unmeasured dimension.

\[
METHOD\_CONFORMANCE \neq LENS\_QUALIFICATION
\]

---

## 30. Failure Is Admissible Evidence

Material adverse findings include:

- no discriminating effect;
- baseline review matching or exceeding Lens Shift;
- attention control matching or exceeding Lens Shift;
- high false activation;
- token inefficiency;
- sequence contamination;
- functional redundancy;
- reviewer instability;
- normalization instability;
- failure under paraphrase;
- failure outside familiar domains;
- uncontrolled materiality judgments;
- nonconvergence.

Such findings MUST be preserved.

Preservation of failure does not make failure permanent. A future successor MAY produce a different result under changed conditions, but the earlier failure remains valid as a bounded historical observation unless independently shown to have been erroneous.

Likewise, preservation of success does not guarantee continuing success. Previously successful behavior MAY require re-examination after material changes in dependencies, environment, authority, runtime, evidence, implementation, or knowledge state.

---

## 31. Initial Research Objective

The first research objective remains narrow:

> Determine whether one preregistered lens can produce a predefined structural signature under positive fixtures, remain appropriately inactive under negative fixtures, exhibit a detectable difference from baseline and attention-matched review, and expose a measurable visible-output-budget response, while preserving a complete execution surface sufficient for independent inspection.

The first feasibility pilot is defined separately as:

`LENS-SHIFT-EXP-001A-PROTOCOL-FEASIBILITY-v0.1-CANDIDATE`

---

## 32. Current Standing

This artifact establishes a repaired candidate methodological identity only.

It does not establish:

```text
EFFECTIVENESS
UTILITY
SUPERIORITY
GENERALIZATION
OPTIMAL_LENS_SET
OPTIMAL_SEQUENCE
OPTIMAL_TOKEN_BUDGET
MODEL_INDEPENDENCE
HUMAN_REPRODUCIBILITY
CAUSAL_ATTRIBUTION
SAFE_AUTONOMOUS_DECISION_USE
```

Those remain experimental questions.


This successor also does not establish that any present rule, constraint, lens, comparator, threshold, or explanatory model will remain useful indefinitely. The method's current architecture is itself subject to future pressure, amendment, supersession, and retirement through preserved successor records.

---

## 33. Minimum Admissible Execution Record

A result represented as a recorded Lens Shift execution MUST preserve, at minimum:

```yaml
execution_id:
method_spec_id:
method_spec_hash:
epoch_id_if_applicable:
subject_id:
subject_version_or_hash:
subject_boundary:
inspection_boundary:
objective:
execution_time_or_interval:
context_state:
manipulation_class:
lens_id:
lens_version:
preserved_invariants: []
expected_signature:
detector_or_evaluator:
evidence_basis: []
effect_class:
finding_state:
materiality_state:
disposition:
unresolved_conditions: []
claim_ceiling:
known_limitations: []
```

Where a field is not applicable, the execution SHOULD say so explicitly rather than silently omit a materially relevant boundary.

Conformance to this record structure does not establish semantic correctness, empirical utility, safety, compliance, or qualification.

---

## 34. Claim Ceiling

Every execution SHOULD declare the strongest claim supported by its actual evidence.

`claim_ceiling` constrains interpretation of the result and MUST NOT be inferred upward from formatting, confidence language, artifact complexity, naming, dashboard status, or institutional context.

A result MAY have a lower claim ceiling than the method's theoretical capability.

Absence of a detected effect MUST be represented as bounded non-detection unless the design independently supports a stronger absence claim.

No execution, finding, repair, successor artifact, filename, summary, dashboard, or disposition MAY imply standing above the evidence actually established.

---

## 35. Finding-Reference Integrity

Observation, effect, finding, materiality, disposition, repair, and successor-validity claims MUST remain referentially traceable.

A materiality determination or disposition SHOULD reference the antecedent finding or explicit null state from which it proceeds.

A repair SHOULD reference the finding or condition it intends to alter.

A successor-validity claim MUST identify its independent validation basis and MUST NOT inherit validity solely because an antecedent finding was mitigated or ceased to reproduce.

The canonical relation is:

\[
O \rightarrow E \rightarrow F \rightarrow M \rightarrow D
\]

Transitions MAY terminate, remain unresolved, or produce explicit null states. They MUST NOT be silently skipped when the omitted relation is material to the claim.

---

## 36. Experimental Role and Exposure Boundary

For experimental uses, the protocol SHOULD distinguish at least:

```text
METHOD_SPECIFICATION
EXPERIMENT_PROTOCOL
PARTICIPANT_FACING_INSTRUCTION
PARTICIPANT_ROLE
COMPARATOR_ASSIGNMENT
EXECUTOR
NORMALIZER
EVALUATOR
GRADER
ADJUDICATOR
DECISION_AUTHORITY
POST_EXECUTION_INTERPRETATION
```

Each role SHOULD declare relevant information exposure where blindness, independence, or contamination control matters.

Information that may contaminate one role may be entirely legitimate in another. Therefore, contamination MUST be assessed against the declared boundary, not inferred merely because a concept existed somewhere in the broader lineage.

Participant-facing material that reveals a hidden role, comparator assignment, expected contrast, hypothesis, desired effect, grading criterion, or experimental structure MAY invalidate claims that depend on that information remaining concealed.

---

## 37. Comparator Standing

A comparator used for causal, incremental-value, transfer, or superiority claims MUST have standing independent of the result it helps evaluate.

Comparator standing SHOULD be bound before outcome adjudication where feasible and SHOULD preserve:

```yaml
comparator_id:
comparator_type:
assignment_basis:
assignment_time:
subject_relation:
resource_relation:
information_exposure:
expected_difference_or_invariance:
known_confounds: []
```

A post hoc observation that two outputs differ does not establish that they were valid experimental comparators.

A post hoc observation that two outputs converge does not establish that the comparator failed.

---

## 38. Re-examination Pathways

A present constraint SHOULD be understood as a bounded disposition with a basis, not automatically as a permanent law.

Where useful, a constraint MAY declare:

```yaml
current_disposition:
historical_basis:
protected_invariant:
reexamination_triggers: []
required_new_evidence: []
successor_authority_required:
expiration_or_review_condition:
```

Possible successor outcomes include:

```text
RETAINED
NARROWED
CONDITIONALIZED
AMENDED
SUPERSEDED
RETIRED
INSUFFICIENT_EVIDENCE_TO_CHANGE
```

A pathway does not weaken the current constraint. It prevents the system from confusing "withheld now" with "forbidden forever."

---

## 39. Amendment and Supersession Semantics

A successor MAY replace a predecessor rule without declaring the predecessor erroneous when the relevant conditions have changed.

The minimum historical relationship is:

\[
predecessor\ standing
+
change\ evidence
\rightarrow
successor\ standing
\]

not:

\[
successor\ standing
\rightarrow
rewrite(predecessor)
\]

The record SHOULD distinguish:

- correction of an earlier error;
- repair of a defect;
- adaptation to changed conditions;
- replacement by a better mechanism;
- scope narrowing;
- scope expansion;
- retirement due to irrelevance;
- reactivation of a previously unsuccessful or unavailable approach.

The same idea or mechanism MAY legitimately move between these states over time.

---

## 40. Non-Monopoly Principle

No Lens Shift mechanism, lens, finding class, temporal model, evidence rule, comparator, or successful explanatory pattern acquires universal explanatory standing merely because it performed well in a bounded domain.

\[
local\ success \not\Rightarrow universal\ authority
\]

The method SHOULD remain open to multiple materially distinct explanations and mechanisms where the evidence does not justify collapse.

A lens that repeatedly identifies one class of hidden failure MAY itself become a source of blindness if every future failure is forced into that class.

Therefore:

- Lens Shift MUST NOT become a correctness oracle by repeated usefulness;
- a successful lens MUST remain challengeable by alternative lenses and ordinary review;
- an explanatory model SHOULD state its bounded scope;
- unresolved competing explanations SHOULD remain unresolved until evidence distinguishes them.

---

## 41. Process-Outcome Discipline

Lens Shift is evaluated through the relationship between process and resulting outcomes, not through specification sophistication alone.

The preferred empirical loop is:

\[
Condition
\rightarrow
Process
\rightarrow
Observed\ Effect
\rightarrow
Outcome
\rightarrow
Replication
\rightarrow
Bounded\ Claim
\]

Across executions, the research object MAY be represented as:

\[
Lens \times Domain \times Task \times Comparator \times Operator \times Time
\rightarrow
Performance
\]

Performance MAY include:

```text
TRUE_MATERIAL_FINDING_YIELD
FALSE_ACTIVATION_RATE
VALID_NULL_RATE
FAILED_DISCRIMINATION_RATE
INTER_RATER_AGREEMENT
REPRODUCTION_RATE
ATTRIBUTION_STRENGTH
DECISION_QUALITY
COST_PER_CONFIRMED_FINDING
ORDER_EFFECT
CONTAMINATION_RATE
TRANSFER_PERFORMANCE
DOWNSTREAM_REPAIR_OUTCOME
```

The objective is not to prove the current theory of Lens Shift. The objective is to discover the method's actual operating envelope, including conditions in which baseline review, another method, or no intervention performs better.

### 41.1 Separate Subject Utility From Method Qualification (v0.1.4 amendment)

Method-effect experiments, comparative claims, external validation, and grading are **separate research activities** that MAY be undertaken when requested or independently warranted. Their existence does not make method-effect reporting a prerequisite for routine subject-first use.

Operational analyses MUST report subject findings at the evidentiary level they support, regardless of whether the method's general utility has been qualified. An empirical claim about the method itself still requires the relevant comparator and evidence under §§ 2–15, 29, and 41. A verified subject measurement is not a verified methodological effect; a useful subject-level decision is not a method-level superiority result.

---

## 42. Evolution Loop

Lens Shift does not impose a terminal boundary between design and learning.

A permissible lineage is:

\[
D_0
\rightarrow
E_0
\rightarrow
O_0
\rightarrow
D_1
\rightarrow
E_1
\rightarrow
O_1
\rightarrow \cdots
\]

where:

- \(D_n\) = current design;
- \(E_n\) = execution under that design;
- \(O_n\) = resulting observation set.

A successor design MUST NOT require erasure of the predecessor in order to advance.

\[
D_{n+1} \neq rewrite(D_n)
\]

The preferred discipline is:

> Tighten where ambiguity prevents interpretable execution. Execute where experience can produce evidence. Amend where evidence or changed conditions reveal a better path. Preserve the transition.

This principle does not require constant change. It requires that change, stasis, retirement, and reactivation each remain evidence-governed possibilities.

---

## 43. Successor Change Ledger

Relative to `LENS-SHIFT-METHOD-SPEC-v0.1.2-CANDIDATE`, this successor:

1. preserves v0.1.2 as a separate historical artifact;
2. preserves all v0.1.2 temporal-standing, pathway, evidence-state, claim-ceiling, role/exposure, comparator, qualification-vector, non-monopoly, process/outcome, evolution-loop, and epoch-binding semantics unless explicitly amended;
3. adds bounded recursive-execution lineage and termination records;
4. distinguishes preregistered, declared-before-depth, adaptive-operational, post-hoc-disclosed, and epoch-amended continuation rules;
5. requires continuation/depth preregistration where recursive sequences materially support reproducibility, attribution, qualification, transfer, or utility claims;
6. requires an epoch split or explicit segmentation when such a continuation rule or bound changes;
7. adds explicit fixed-point equivalence semantics and prohibits treating fixed-point status as completeness;
8. strengthens method-snapshot identity by binding hashes to canonicalization, encoding, normalization, redaction, and hash-boundary metadata when immutable identity matters;
9. preserves `HASH_MATCH` as an identity statement rather than semantic authority;
10. preserves changed hash as representational difference rather than automatic materiality;
11. distinguishes declared external dependencies from dependencies actually resolved and used;
12. adds dependency-resolution, integrity-verification, substitution, and scope records;
13. constrains claim ceilings when materially relied-upon dependencies are unresolved or insufficiently verified;
14. preserves silent dependency substitution as inadmissible;
15. leaves empirical and qualification standing unchanged.

### Validation standing after successor

```text
METHOD_SPECIFICATION = v0.1.3-CANDIDATE
PREDECESSOR = v0.1.2-CANDIDATE
PREDECESSOR_SHA256 = 4202cb8ee2063d37476e70cecfb92e978f4eabd0bd1dd50c6b1df09d0bb3df81
SUCCESSOR_PROPOSAL = LENS-SHIFT-v0.1.3-SUCCESSOR-PROPOSAL-002
SUCCESSOR_PROPOSAL_SHA256 = 73819aaa77c90afa155fb48acd9be8dd7d1d458932e8b59e074e995c5b093220
EMPIRICAL_QUALIFICATION = NOT_YET_ESTABLISHED_FOR_v0.1.3
UTILITY = UNESTABLISHED
SUPERIORITY = UNESTABLISHED
GENERALIZATION = UNESTABLISHED
CAUSAL_ATTRIBUTION = UNESTABLISHED
SUCCESSOR_FREEZE = NOT_FROZEN
```

Specification evolution does not itself advance empirical standing.

---

## 44. Epoch Binding Without Lineage Immobilization

Empirical interpretation requires stable experimental targets. Method evolution requires continued successor freedom. These are compatible.

An experiment, replay, pressure run, or qualification epoch MAY bind to an immutable method snapshot:

```yaml
epoch_id:
bound_method_spec_id:
bound_method_hash:
bound_lens_versions: []
bound_protocol_id:
binding_time:
allowed_runtime_variation:
prohibited_mid_epoch_changes: []
```

Once execution begins, the bound snapshot MUST NOT be silently altered for that epoch.

However:

\[
freeze(epoch\ target) \neq freeze(method\ lineage)
\]

A successor method MAY be developed concurrently or afterward. It does not retroactively change the method actually used by the bound epoch.

If a protocol defect or new insight requires changing the method during an epoch, the current epoch SHOULD be closed, blocked, or explicitly segmented according to its stopping rules. A new epoch MAY then bind the successor.

This preserves both:

1. **experimental interpretability** — the process actually tested remains stable and identifiable; and
2. **evolutionary continuity** — the broader method remains free to change through successor artifacts.

The method therefore does not choose between rigor and evolution. It binds each claim to the version that produced it while allowing later versions to continue the lineage.

---

## 45. Bounded Recursive-Execution Traceability and Termination

Recursion is an optional execution pattern, not a privileged analytical mode.

A recursive execution occurs when a prior execution, finding, repair, successor proposal, method clause, method snapshot, or other explicitly declared predecessor object is re-represented as a new bounded subject.

When recursion is used, the execution SHOULD preserve:

```yaml
recursive_application:
  root_execution_id:
  parent_execution_id:
  recursion_depth:
  maximum_depth_if_declared:
  recursive_subject_relation:
  continuation_rule:
  continuation_rule_status:
  continuation_rule_amendment_id_if_any:
  fixed_point_rule_if_used:
  prior_effect_classes: []
  current_effect_classes: []
  stop_reason:
```

Candidate `recursive_subject_relation` values MAY include:

```text
EXECUTION_AS_SUBJECT
FINDING_AS_SUBJECT
REPAIR_AS_SUBJECT
SUCCESSOR_PROPOSAL_AS_SUBJECT
METHOD_CLAUSE_AS_SUBJECT
METHOD_SNAPSHOT_AS_SUBJECT
OTHER_DECLARED_RELATION
```

Candidate `continuation_rule_status` values MAY include:

```text
PREREGISTERED
DECLARED_BEFORE_DEPTH
ADAPTIVE_OPERATIONAL
POST_HOC_DISCLOSED
AMENDED_BY_EPOCH_SPLIT
```

For ordinary exploratory or operational use, continuation MAY be adaptive if the adaptive status is disclosed.

For a recursive execution used materially to support a claim of reproducibility, attribution, qualification, transfer, or utility:

1. the continuation rule MUST be declared before the relevant recursion sequence begins;
2. the maximum recursion depth MUST be declared before the relevant recursion sequence begins;
3. a changed continuation rule or maximum depth MUST close or explicitly segment the current recursive epoch;
4. the amendment, reason, prior bound, successor bound, and affected claims MUST be recorded.

Candidate stop reasons MAY include:

```text
MAXIMUM_DEPTH_REACHED
NO_NEW_MATERIAL_EFFECT_CLASS
DECLARED_FIXED_POINT_REACHED
RESOURCE_CEILING_REACHED
PROTOCOL_DEFECT
EVIDENCE_EXHAUSTED
CONTINUATION_NO_LONGER_MATERIAL
MANUAL_BOUNDED_STOP
OTHER_DECLARED_REASON
```

`MANUAL_BOUNDED_STOP` is admissible for exploratory or operational execution when its non-preregistered character is disclosed.

No recursive child inherits the evidentiary standing, qualification state, authority, or claim ceiling of its parent merely from the recursive relation.

### 45.1 Fixed-point comparison

`DECLARED_FIXED_POINT_REACHED` MUST NOT be inferred from prose similarity or reviewer intuition alone.

A declared fixed point exists only when the current execution satisfies an explicit equivalence relation against a specified parent, root, or normalized representation.

The fixed-point record MUST identify:

```yaml
fixed_point_comparison:
  comparison_target:
  equivalence_relation:
  normalization_version_if_any:
  compared_fields: []
  tolerance_policy:
  unresolved_difference_treatment:
  comparison_result:
```

Compared fields MAY include:

```text
effect_class
materiality_outcome
disposition
evidence_basis_states
material_finding_ids
claim_ceiling
normalized_structural_representation
```

A fixed-point result is a bounded stop state.

\[
Declared\ Fixed\ Point \not\Rightarrow Completeness
\]

---

## 46. External Executable Dependency Resolution and Integrity

A method specification MAY define normative contract surfaces whose executable schemas, registries, validators, fixtures, graders, normalizers, canonicalizers, or experiment protocols are maintained as separate artifacts.

Declared dependency and resolved dependency are distinct states.

Where an execution depends on an external artifact, the execution package SHOULD preserve:

```yaml
external_dependency:
  dependency_id:
  dependency_type:
  declared_version:
  declared_content_hash_if_available:
  required_for:
  dependency_scope:
  availability_state:
  supplied_location_or_reference:
  resolution_time:
  resolved_artifact_id:
  resolved_version:
  resolved_content_hash:
  resolution_status:
  integrity_verification_status:
  substitution_policy:
```

Candidate `dependency_type` values MAY include:

```text
LENS_REGISTRY
MANIPULATION_REGISTRY
SCHEMA
VALIDATOR
FIXTURE_SET
GRADER_RUBRIC
EXPERIMENT_PROTOCOL
NORMALIZER
CANONICALIZATION_RULE
OTHER_DECLARED_DEPENDENCY
```

Candidate `resolution_status` values MAY include:

```text
DECLARED
RESOLVED
HASH_VERIFIED
VERSION_MATCHED
SUBSTITUTED
UNRESOLVED
UNAVAILABLE
NOT_REQUIRED
```

A dependency that is materially relied upon by a result but not resolved, or not integrity-verified where verification is required, MUST constrain the claim ceiling of that result.

A substitution MUST be explicit and separately identified.

\[
Declared\ Dependency \neq Resolved\ Dependency
\]

\[
Substituted\ Dependency \neq Declared\ Dependency
\]

A substituted dependency does not inherit the identity or standing of the declared dependency merely because it occupies the same operational role.

Dependency absence, resolution failure, or integrity uncertainty MAY support a dependency, provenance, or evidence-sufficiency finding. It MUST NOT alone be promoted into a contradiction or external-state failure claim.

---

## 47. v0.1.3 Candidate Standing

`LENS-SHIFT-METHOD-SPEC-v0.1.3-CANDIDATE` is a traceability successor to v0.1.2.

It is not an empirical qualification release.

Its present standing is:

```text
METHOD_IDENTITY = ESTABLISHED_AS_CANDIDATE_ARTIFACT
PREDECESSOR_IDENTITY = BOUND
RECURSIVE_TRACEABILITY = SPECIFIED
FIXED_POINT_SEMANTICS = SPECIFIED
METHOD_HASH_CANONICALIZATION_BINDING = SPECIFIED
DEPENDENCY_RESOLUTION_TRACEABILITY = SPECIFIED
EMPIRICAL_EFFECTIVENESS = UNESTABLISHED
UTILITY = UNESTABLISHED
SUPERIORITY = UNESTABLISHED
GENERALIZATION = UNESTABLISHED
CAUSAL_ATTRIBUTION = UNESTABLISHED
INDEPENDENT_REPLICATION = UNESTABLISHED
FREEZE = NOT_FROZEN
```

The proper next state is execution pressure against this candidate, including negative, null, divergent, and dependency-blocked outcomes.

The candidate MAY later be amended, superseded, narrowed, retired, or reactivated through preserved successor relations.

\[
Present\ Standing \neq Permanent\ Standing
\]


---

## 48. v0.1.4 Subject-First Operational Revision Ledger

**Amendment:** `LS-OPS-SUBJECT-FOREGROUND-001`  
**Affected sections:** §§ 27, 41; supplements but does not displace §§ 1–26, 28–40, and 42–47.  
**Issue corrected:** recurring presentation and evaluation of the analytical method can displace the actual requested subject, especially where reflective recursion is treated as a principal output rather than a means.  
**Replacement rule:** use deconstruction, classification, examination, and reconstruction to develop subject-specific findings; do not require the visible output to narrate the method, evaluate its own effect, or seek approval of a non-consequential analytical observation.  
**Authorization reservation:** autonomous analytical transformation does not authorize external action, accessing restricted sources, making formal determinations, or overriding the human's requested task.  
**Non-inheritance:** the amendment neither validates past unexamined methodological claims nor changes standing of earlier studies or specifications.  
**Operational test:** when asked to apply Lens Shift to FORK-AAR, the answer foregrounds physical observability, source and inference separation, investigation choices, architecture, risks, experiments and findings; method-effect discussion is omitted unless itself requested.  
**Status:** `SPECIFIED_NOT_EMPIRICALLY_QUALIFIED`.

A user-visible answer MAY be concise even when the underlying subject requires substantial analytical work. The gain sought is in the quality of the reconstructed subject understanding and decisions, not in the prominence of the method's name.
