"""Full-replay endpoint and fixed-query append-reassessment verification.

Commitment matches describe supplied values, never certify their independent origin.
This module does not authenticate evidence, authorize decisions, or restore caches.
"""
import copy
import json
import re

from evidence import sha
from portable_audit import verify_packet

SCHEMA = 'LC-EXP-009-REASSESSMENT-1'
MAX_JSON_BYTES = 8_000_000


def ensure(condition, message):
    if not condition:
        raise ValueError(message)


def exact(a, b):
    """Compare canonical JSON bytes, not Python's True == 1 coercion."""
    def encode(x):
        return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                          allow_nan=False).encode('utf-8')
    return encode(a) == encode(b)


def validate_hash(value):
    ensure(type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None,
           'commitment must be lowercase 64-hex SHA-256')


def verify_scoped_packet(packet, trusted_ledger_tip=None, trusted_packet_hash=None):
    """Supplied anchors may be independently trusted by a caller; we cannot prove that."""
    for value in (trusted_ledger_tip, trusted_packet_hash):
        if value is not None:
            validate_hash(value)
    result = verify_packet(packet, trusted_ledger_tip, trusted_packet_hash)
    # Avoid Python numeric/Boolean equivalence in root summary fields used below.
    # This is not a complete adversarial schema/security qualification.
    ensure(type(packet['expected']['stage']) is int, 'expected stage must be integer')
    ensure(type(packet['expected']['histogram']) is dict and
           set(packet['expected']['histogram']) == {'T', 'F', 'U'} and
           all(type(x) is int and x >= 0 for x in packet['expected']['histogram'].values()),
           'histogram must contain nonnegative integers, not Booleans')
    result.pop('anchor_status', None)
    result['commitment_matches'] = {
        'ledger_records_order_and_length': trusted_ledger_tip is not None,
        'entire_packet_including_context_claim_and_samples': trusted_packet_hash is not None,
    }
    result['anchor_origin'] = 'CALLER_SUPPLIED_NOT_INDEPENDENTLY_CHECKED' if (
        trusted_ledger_tip is not None or trusted_packet_hash is not None) else 'NOT_SUPPLIED'
    result['source_authentication'] = 'NOT_ESTABLISHED'
    result['claim_ceiling'] = 'replay consistency and explicitly scoped commitment match only'
    return result


def verify_reassessment(receipt, trusted_before_packet_hash=None,
                        trusted_after_packet_hash=None, trusted_receipt_hash=None):
    ensure(type(receipt) is dict and set(receipt) == {
        'schema', 'operation', 'before', 'after', 'receipt_sha256'}, 'receipt keys invalid')
    ensure(receipt['schema'] == SCHEMA and receipt['operation'] == 'REASSESS_FIXED_QUERY_APPEND',
           'receipt operation/schema invalid')
    validate_hash(receipt['receipt_sha256'])
    payload = {k: v for k, v in receipt.items() if k != 'receipt_sha256'}
    ensure(sha(payload) == receipt['receipt_sha256'], 'receipt hash mismatch')
    if trusted_receipt_hash is not None:
        validate_hash(trusted_receipt_hash)
        ensure(trusted_receipt_hash == receipt['receipt_sha256'], 'receipt commitment mismatch')
    before, after = receipt['before'], receipt['after']
    vb = verify_scoped_packet(before, trusted_packet_hash=trusted_before_packet_hash)
    va = verify_scoped_packet(after, trusted_packet_hash=trusted_after_packet_hash)
    bc, ac = before['context'], after['context']
    for field in ('expression', 'query_stage', 'definitions'):
        ensure(exact(bc[field], ac[field]), 'fixed context changed: ' + field)
    ensure(ac['knowledge_stage'] >= bc['knowledge_stage'], 'knowledge cutoff moved backward')
    old, new = before['ledger']['records'], after['ledger']['records']
    ensure(len(new) >= len(old) and exact(old, new[:len(old)]),
           'after ledger does not preserve exact ordered prefix')
    b, a = before['expected'], after['expected']
    return {
        'verified': True,
        'relation': 'FIXED_QUERY_APPEND_REASSESSMENT',
        'before_packet_sha256': before['packet_sha256'],
        'after_packet_sha256': after['packet_sha256'],
        'receipt_sha256': receipt['receipt_sha256'],
        'appended_records': len(new) - len(old),
        'knowledge_stage_changed': bc['knowledge_stage'] != ac['knowledge_stage'],
        'scalar_truth_changed': b['value'] != a['value'],
        'before_value': b['value'], 'after_value': a['value'],
        'root_content_changed': b['root_id'] != a['root_id'],
        'histogram_changed': not exact(b['histogram'], a['histogram']),
        'ledger_commitment_changed': before['ledger']['tip'] != after['ledger']['tip'],
        'sample_selection_changed': not exact([x['index_decimal'] for x in before['witnesses']],
                                              [x['index_decimal'] for x in after['witnesses']]),
        'endpoint_commitments': {'before': vb['commitment_matches'], 'after': va['commitment_matches']},
        'whole_receipt_commitment_match': trusted_receipt_hash is not None,
        'anchor_origin': 'CALLER_SUPPLIED_NOT_INDEPENDENTLY_CHECKED' if any(x is not None for x in
            (trusted_before_packet_hash, trusted_after_packet_hash, trusted_receipt_hash)) else 'NOT_SUPPLIED',
        'source_authentication': 'NOT_ESTABLISHED',
        'claim_ceiling': 'full-replay-consistent fixed-query append relation over declared evidence; not physical continuity, authorization, or cache recovery',
    }


def make_reassessment(before, after):
    receipt = {'schema': SCHEMA, 'operation': 'REASSESS_FIXED_QUERY_APPEND',
               'before': copy.deepcopy(before), 'after': copy.deepcopy(after)}
    receipt['receipt_sha256'] = sha(receipt)
    verify_reassessment(receipt)
    return receipt


def load_json(path):
    raw = path.read_bytes()
    ensure(len(raw) <= MAX_JSON_BYTES, 'JSON file exceeds byte limit')
    def pairs(items):
        result = {}
        for k, v in items:
            ensure(k not in result, 'duplicate JSON key: ' + k)
            result[k] = v
        return result
    def constant(value):
        raise ValueError('invalid JSON constant: ' + value)
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=constant)