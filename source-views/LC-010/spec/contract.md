# LC-EXP-010 — Declared ordered relationship-chain contract v0.1

## Inherited behavior

LC-EXP-009 verifies one fixed-query append reassessment at a time by full replay of two portable packets. The recovered executable LC009 ZIP is separately identified by its **new archive hash**, and its original text/binary entries by the original **39/39 manifest**. This contract adds an external wrapper; it does not change those semantics or predecessor files.

## New objects

`LC-EXP-010-RELATION-CHAIN-1` contains exactly `schema`, `start_packet_sha256`, `steps`, and `chain_tip`. The nonempty ordered `steps` list (at most 32) contains exactly `ordinal`, `prior_tip`, `receipt`, and `step_sha256` per entry. Each `receipt` must be a valid frozen LC009 `REASSESS_FIXED_QUERY_APPEND` receipt. The complete receipt objects are embedded: **no succinct proof**.

Genesis = inherited `evidence.sha` of `{domain:'LC-EXP-010-CHAIN-GENESIS-1', schema, start_packet_sha256}`. Step commitment = inherited `evidence.sha` of `{domain:'LC-EXP-010-CHAIN-STEP-1', ordinal, prior_tip, receipt_sha256}`. The chain tip is the last step commitment. Commitments bind *canonicalized declared bytes* according to the Python JSON canonicalization inherited from LC009, not the raw JSON file encoding.

Verifier additionally checks:

1. Ordinal is a Python integer equal to its zero-based position, rather than a Boolean.
2. The step predecessor commitment equals the previously computed tip.
3. The first receipt's before-packet identity equals the declared start identity.
4. Every next receipt's before-packet object is canonically **identical** to the preceding receipt's after-packet object, with matching packet hash. This is stricter than matching truth values, evidence tips, or expression alone.
5. Every receipt passes full LC009 verification. Steps whose query/definition/knowledge restrictions fail remain rejected by LC009.
6. The terminal chain tip matches the recomputed commitment.

A caller can optionally supply a start-packet hash or chain-tip commitment. These are checked by equality. The verifier **does not establish independent origin** of supplied commitments.

## Sample semantics

For common sampled witness indices, distinguish:

- Full witness payload, including packet-level ledger/root commitment references.
- Selected witness content, excluding only the `ledger_commitment` and `root_id` audit-envelope fields.
- Selected supporting evidence IDs.
- Ledger binding changes even with identical selected evidence.
- Sample order and sample index-set changes, independently.

These fields concern the **provided samples only**. They do not attest all possible witnesses. LC008 export canonicalizes requested sample order, so changing only the caller's requested order typically does not change the stored output.

## Evidence claims / exclusion boundaries

- `verified=True` means an internally consistent **declared** ordered sequence of valid LC009 fixed-query reassessment receipts.
- It does NOT establish that any event physically occurred, that all historic events were disclosed, that the starting point is historically authentic, or that a supplied hash was obtained independently. A valid subsequence may be constructed when no external anchoring exists.
- `previous after == next before` does not prove the external world remained continuously in that state between recorded events.
- Same verified endpoints can support different **separately declared** chains. A chain-tip hash disambiguates an externally retained exact sequence, but does not create an external trust source.
- No new primitive semantic grammar, proof compression, model learning, computational advantage, signature, private-key authentication, temporal authority, or external consensus is demonstrated.
- Full replay cost and repeated embedding of endpoints remain; max 32 transitions and 8 MB CLI file cap are only partial resource bounds. Python API is not hardened for arbitrary hostile memory objects.
