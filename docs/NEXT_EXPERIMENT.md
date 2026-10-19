# Proposed next gate — clean-room conditional relation oracle

**Status: PROPOSED, NOT PREREGISTERED, NOT EXECUTED.**

**Question.** Does LC013 preserve separate effects of (a) conflicting defeating claims, (b) relevant vs irrelevant pending relationships, (c) authority grant/revocation events and their effective times, and (d) evidence availability/knowledge cutoffs, when the expected outputs are established independently before implementation examination?

## Required freeze before execution

1. Author a minimal, independent normative semantics document for typed relations, admission, authorization, scope, effective-time, and information-time. Clearly mark any rule that is stipulated rather than empirically discovered.
2. Predeclare twelve to twenty discriminating fixtures and expected outcomes without running LC013 or adapting expected outputs to it. Preserve a hash and time-coordinated freeze.
3. Provide at least two cases that differ in *one factor only* for each of: relevant target, relation kind, effective-time boundary, authority status, and received evidence.
4. Instruct an independent reviewer to challenge the semantics and fixture definitions *before* the implementation is run, then preserve the review with attribution and scope.
5. Run against the unmodified, hash-bound LC013 archive. Preserve raw outcomes, deviations and negative results, without merging a repair into the frozen object.
6. If the outcome is underdetermined by the frozen semantics, mark it `UNRESOLVED`; do not promote a pass by selecting a favorable interpretation.

**Admission ceiling:** Supports or refutes specified properties of the stipulated synthetic system under named frozen cases. This experiment alone cannot authenticate external authority or real-world truth.
