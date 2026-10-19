# LC009 contract 1.0.0 — fixed-query append reassessment

## Objects and boundaries

An endpoint is an unchanged LC008 portable audit packet. A receipt contains exactly `schema`, `operation`, `before`, `after`, `receipt_sha256`. Schema is `LC-EXP-009-REASSESSMENT-1`; operation is `REASSESS_FIXED_QUERY_APPEND`.

Verification requires both endpoints to pass frozen LC008 replay and LC009 root-stage/histogram type checks. It additionally requires:

1. Exact canonical-JSON equality of expression, query stage and definitions.
2. Integer after knowledge stage greater than or equal to before knowledge stage (endpoint replay checks types).
3. After record count at least before count; exact canonical-JSON equality of before records with the ordered after prefix.
4. Receipt content hash match.

Empty deltas and no semantic change are admissible. No requirement that records' declared observation stages increase in ledger order is added; ledger append order and observation stage remain distinct.

Textual rewrites, query changes, backwards knowledge and definition changes are outside this operation. Rejection does not mean those operations are impossible or that an independently valid endpoint is false. They need a different contract.

## Output distinctions

`scalar_truth_changed` compares root T/F/U only. `root_content_changed` compares content IDs. `histogram_changed` compares syntactic-derivation counts. `ledger_commitment_changed` compares ordered evidence commitments. `sample_selection_changed` compares provided witness indices, not all possible witnesses or physical routes.

The root may change solely because evidence provenance changes. The ledger can change without changing the root. A witness-sample change can occur without any ledger or semantic change. These distinctions are not confidence scores.

## Commitment scope and canonicalization

Inherited `evidence.sha(x)` is SHA-256 over UTF-8 encoding of Python `json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=False)`.

- Packet: hash whole packet dictionary **excluding** `packet_sha256`.
- Receipt: hash whole receipt dictionary **excluding** `receipt_sha256`; endpoint self-hashes remain included.
- Ledger: frozen LC007 domain-separated ordered chain; LC008 independently reconstructs it from complete records.
- ZIP and method identity: SHA-256 over exact raw file bytes; no text normalization, metadata stripping, newline transformation or redaction.

`exact` uses the same canonical JSON settings plus `allow_nan=False` to prevent non-JSON constants. Exact comparison distinguishes integers from Booleans; it is not Unicode normalization or a universally standardized JSON canonicalizer. The supported format is this Python-bound experimental contract, not all JSON implementations.

A supplied ledger tip matches records/order/length, not expression/query/definitions/claim/sample choice. A supplied packet hash matches that entire packet. A before packet hash does not commit to the after endpoint. A receipt hash matches the whole declared relation and both packets. Matching cannot establish independent origin of the supplied value. Source authentication is always `NOT_ESTABLISHED`.

## Resource and trust limits

CLI input cap: 8,000,000 bytes. Endpoint limits remain LC008's 10,000 records, 100,000 expression characters, 32 witness samples. These are partial experimental bounds, not production security. Full endpoint evaluation and witness checking may be costly. Both endpoints are embedded in full; no computation, storage, authentication or proof-size advantage follows.

## Successor relation and standing

Relation: `PORTABLE_RELATION_ADDITION_AND_COMMITMENT_SCOPE_REFINEMENT`. Predecessor identity: exact supplied LC008 ZIP. Protected invariants: historical bytes/findings, stipulated grammar, evidence-selection policy, no authority inheritance, source assertion/authentication distinction.

No predecessor API is overwritten. New wrapper outputs are separately identified. Local tests establish declared fixture behavior only; all stronger semantic grounding, practical utility, performance, cryptographic security and method qualification claims remain withheld.