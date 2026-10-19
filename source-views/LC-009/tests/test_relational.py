import copy
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

from evidence import sha
from registry import FrozenDefinitions
from persistent_ledger import AppendLedger
from selective_audit import SelectiveAudit
from portable_audit import export_packet, verify_packet
from relational_audit import make_reassessment, verify_reassessment, verify_scoped_packet, load_json

ROOT = Path(__file__).resolve().parents[1]
DEFINITIONS = FrozenDefinitions({
    'H1': {'version': 1, 'parameters': ['a', 'b', 'c'], 'expression': 'C(R({a},{b}),R({b},{c}))'},
    'H2': {'version': 2, 'parameters': ['a', 'b', 'c'], 'expression': 'J(P({b}),C(R({a},{b}),R({b},{c})))'}})


def row(i, atom='R(A,B)', value='T', obs=0, until=10):
    return dict(id=i, atom=atom, value=value, observed_stage=obs, valid_from=0,
                valid_until=until, source='synthetic', persistence_policy='bounded')


def packet(rows=None, expr='R(A,B)', q=0, k=0, indices=(0,)):
    store = AppendLedger([row('a')] if rows is None else rows)
    snap = store.snapshot()
    engine = SelectiveAudit(DEFINITIONS)
    handle = engine.evaluate(expr, snap, q, k)['audit_handle']
    return export_packet(engine, handle, snap, DEFINITIONS, indices)


def rehash(obj, key='receipt_sha256'):
    obj[key] = sha({k: v for k, v in obj.items() if k != key})
    return obj


def unchecked(before, after):
    from relational_audit import SCHEMA
    return rehash(dict(schema=SCHEMA, operation='REASSESS_FIXED_QUERY_APPEND',
                       before=before, after=after))


class RelationalTests(unittest.TestCase):
    def test_changed_truth_exact_append(self):
        p, a = packet(), packet([row('a'), row('b', value='F')])
        result = verify_reassessment(make_reassessment(p, a))
        self.assertEqual((result['before_value'], result['after_value']), ('T', 'U'))
        self.assertEqual(result['appended_records'], 1)
        self.assertTrue(result['scalar_truth_changed'])

    def test_unrelated_append_valid_null(self):
        p, a = packet(), packet([row('a'), row('z', 'R(Z,Q)')])
        got = verify_reassessment(make_reassessment(p, a))
        self.assertFalse(got['root_content_changed'])
        self.assertFalse(got['scalar_truth_changed'])
        self.assertTrue(got['ledger_commitment_changed'])

    def test_corroboration_changes_provenance_not_truth(self):
        got = verify_reassessment(make_reassessment(packet(), packet([row('a'), row('b')])))
        self.assertTrue(got['root_content_changed'])
        self.assertFalse(got['scalar_truth_changed'])

    def test_same_packet_and_empty_ledger(self):
        for p in (packet(), packet([])):
            got = verify_reassessment(make_reassessment(p, p))
            self.assertEqual(got['appended_records'], 0)
            self.assertFalse(got['root_content_changed'])

    def test_knowledge_only_change(self):
        rows = [row('a', obs=3)]
        got = verify_reassessment(make_reassessment(packet(rows, k=0), packet(rows, k=3)))
        self.assertEqual((got['before_value'], got['after_value']), ('U', 'T'))
        self.assertFalse(got['ledger_commitment_changed'])
        self.assertTrue(got['knowledge_stage_changed'])

    def test_backward_knowledge_rejected(self):
        with self.assertRaisesRegex(ValueError, 'backward'):
            verify_reassessment(unchecked(packet(k=3), packet(k=0)))

    def test_different_expression_and_query_rejected(self):
        rows = [row('a'), row('z', 'R(Z,Q)', 'F')]
        p = packet(rows)
        for a in (packet(rows, expr='R(Z,Q)'), packet(rows, q=1)):
            self.assertTrue(verify_packet(a)['verified'])
            with self.assertRaisesRegex(ValueError, 'fixed context'):
                verify_reassessment(unchecked(p, a))

    def test_reordered_valid_endpoints_rejected_as_relation(self):
        rows = [row('a'), row('z', 'R(Z,Q)')]
        p, a = packet(rows), packet(rows[::-1])
        self.assertTrue(verify_packet(a)['verified'])
        with self.assertRaisesRegex(ValueError, 'ordered prefix'):
            verify_reassessment(unchecked(p, a))

    def test_fork_and_truncation_rejected(self):
        p = packet([row('a'), row('z', 'R(Z,Q)')])
        for a in (packet([row('a', value='F'), row('z', 'R(Z,Q)')]), packet()):
            self.assertTrue(verify_packet(a)['verified'])
            with self.assertRaisesRegex(ValueError, 'ordered prefix'):
                verify_reassessment(unchecked(p, a))

    def test_ledger_anchor_does_not_bind_context(self):
        rows = [row('a', until=1), row('z', 'R(Z,Q)', 'F', until=1)]
        p = packet(rows)
        for a in (packet(rows, expr='R(Z,Q)'), packet(rows, q=1)):
            got = verify_scoped_packet(a, trusted_ledger_tip=p['ledger']['tip'])
            self.assertTrue(got['commitment_matches']['ledger_records_order_and_length'])
            self.assertFalse(got['commitment_matches']['entire_packet_including_context_claim_and_samples'])
            self.assertNotIn('anchor_status', got)
            with self.assertRaisesRegex(ValueError, 'external packet hash mismatch'):
                verify_scoped_packet(a, trusted_packet_hash=p['packet_sha256'])

    def test_endpoint_and_whole_receipt_anchor_scope(self):
        r = make_reassessment(packet(), packet([row('a'), row('b')]))
        got = verify_reassessment(r, trusted_before_packet_hash=r['before']['packet_sha256'],
                                 trusted_receipt_hash=r['receipt_sha256'])
        self.assertTrue(got['whole_receipt_commitment_match'])
        self.assertTrue(got['endpoint_commitments']['before']['entire_packet_including_context_claim_and_samples'])
        self.assertFalse(got['endpoint_commitments']['after']['entire_packet_including_context_claim_and_samples'])
        self.assertEqual(got['source_authentication'], 'NOT_ESTABLISHED')
        for kwargs in ({'trusted_before_packet_hash': '0' * 64},
                       {'trusted_after_packet_hash': '0' * 64}, {'trusted_receipt_hash': '0' * 64}):
            with self.assertRaises(ValueError):
                verify_reassessment(r, **kwargs)

    def test_receipt_hash_and_endpoint_forgery(self):
        r = make_reassessment(packet(), packet([row('a'), row('b')]))
        bad = copy.deepcopy(r); bad['operation'] = 'other'
        with self.assertRaises(ValueError): verify_reassessment(bad)
        bad = copy.deepcopy(r); bad['after']['expected']['value'] = 'F'
        with self.assertRaisesRegex(ValueError, 'receipt hash'): verify_reassessment(bad)
        rehash(bad['after'], 'packet_sha256'); rehash(bad)
        with self.assertRaisesRegex(ValueError, 'reconstructed audit'): verify_reassessment(bad)

    def test_no_boolean_histogram_coercion(self):
        p = packet(); p['expected']['histogram']['T'] = True; rehash(p, 'packet_sha256')
        with self.assertRaisesRegex(ValueError, 'histogram'): verify_scoped_packet(p)

    def test_invalid_hash_and_schema(self):
        p = packet()
        for h in ('X' * 64, 'a', True):
            with self.assertRaises(ValueError): verify_scoped_packet(p, trusted_ledger_tip=h)
        r = make_reassessment(p, p); r['extra'] = 1; rehash(r)
        with self.assertRaisesRegex(ValueError, 'keys'): verify_reassessment(r)

    def test_seeded_append_relations(self):
        rng = random.Random(9009)
        rows = [row('a')]
        p = packet(rows)
        for i in range(128):
            rows.append(row(f'new-{i}', rng.choice(['R(A,B)', 'R(Z,Q)']), rng.choice(['T', 'F', 'U'])))
            a = packet(rows)
            got = verify_reassessment(make_reassessment(p, a))
            self.assertEqual(got['appended_records'], 1)
            self.assertEqual(got['scalar_truth_changed'], p['expected']['value'] != a['expected']['value'])
            p = a

    def test_alternative_witness_samples_not_truth_change(self):
        expr = 'CHOICE(R(A,B),R(A,B))'
        p = packet(expr=expr, indices=(0,)); a = packet(expr=expr, indices=(1,))
        got = verify_reassessment(make_reassessment(p, a))
        self.assertTrue(got['sample_selection_changed'])
        self.assertFalse(got['scalar_truth_changed'])
        self.assertFalse(got['root_content_changed'])

    def test_cross_process_and_json_boundaries(self):
        r = make_reassessment(packet(), packet([row('a'), row('b', value='F')]))
        with tempfile.TemporaryDirectory(prefix='lc009-cli-test-') as work:
            p = Path(work) / 'receipt.json'; p.write_text(json.dumps(r))
            cmd = [sys.executable, str(ROOT / 'verify_audit.py'), 'reassessment', str(p)]
            run = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertTrue(json.loads(run.stdout)['scalar_truth_changed'])
            p.write_text(json.dumps(r)[:-1] + ',"schema":"other"}')
            run = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            self.assertEqual(run.returncode, 1)
            self.assertIn('duplicate JSON key', run.stderr)
            p.write_text('{"x":NaN}')
            with self.assertRaisesRegex(ValueError, 'constant'): load_json(p)
            p.write_bytes(b' ' * 8_000_001)
            with self.assertRaisesRegex(ValueError, 'byte limit'): load_json(p)

    def test_guarded_macro_and_expired_evidence(self):
        rows = [row('ab'), row('bc', 'R(B,C)'), row('pb', 'P(B)')]
        invalid = 'J(P(B),CHOICE(C(R(A,B),R(B,C)),R(A,C)))'
        with self.assertRaisesRegex(ValueError, 'guard not universal'):
            packet(rows, expr=invalid)
        for expr in ('H2(A,B,C)', 'J(P(B),CHOICE(C(R(A,B),R(B,C)),C(R(A,B),R(B,C))))'):
            before = packet(rows, expr=expr)
            after = packet(rows + [row('new', 'R(B,C)', 'F')], expr=expr)
            self.assertTrue(verify_reassessment(make_reassessment(before, after))['verified'])
        expired = [row('a', until=1)]
        got = verify_reassessment(make_reassessment(packet(expired, q=2, k=2),
            packet(expired + [row('new', obs=2)], q=2, k=2)))
        self.assertEqual((got['before_value'], got['after_value']), ('U', 'T'))

    def test_large_witness_indices_preserved(self):
        expr = ''; rows = []
        for i in range(64):
            term = f'CHOICE(R(N{i},N{i+1}),R(N{i},N{i+1}))'
            expr = term if not expr else f'C({expr},{term})'
            rows.append(row(f'e{i}', f'R(N{i},N{i+1})'))
        before = packet(rows, expr=expr, indices=(0, 2**64-1))
        after = packet(rows + [row('unrelated', 'R(Z,Q)')], expr=expr, indices=(0, 2**64-1))
        got = verify_reassessment(make_reassessment(before, after))
        self.assertEqual(before['expected']['witness_count_decimal'], str(2**64))
        self.assertFalse(got['root_content_changed'])
        self.assertFalse(got['scalar_truth_changed'])


if __name__ == '__main__':
    unittest.main()