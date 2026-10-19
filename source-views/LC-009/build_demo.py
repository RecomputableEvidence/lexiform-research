"""Create bounded declared-evidence examples, preserving the frozen predecessor ZIP."""
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from bootstrap import resolve


def main():
    with tempfile.TemporaryDirectory(prefix='lc009-demo-') as work:
        resolve(work)
        from registry import FrozenDefinitions
        from persistent_ledger import AppendLedger
        from selective_audit import SelectiveAudit
        from portable_audit import export_packet
        from relational_audit import make_reassessment, verify_reassessment
        definitions = FrozenDefinitions({
            'H1': {'version': 1, 'parameters': ['a', 'b', 'c'], 'expression': 'C(R({a},{b}),R({b},{c}))'},
            'H2': {'version': 2, 'parameters': ['a', 'b', 'c'], 'expression': 'J(P({b}),C(R({a},{b}),R({b},{c})))'}})
        def row(i, value, atom='R(A,B)'):
            return dict(id=i, atom=atom, value=value, observed_stage=0, valid_from=0,
                        valid_until=10, source='synthetic demonstration', persistence_policy='bounded')
        def packet(rows):
            store = AppendLedger(rows); snap = store.snapshot(); engine = SelectiveAudit(definitions)
            handle = engine.evaluate('R(A,B)', snap, 0, 0)['audit_handle']
            return export_packet(engine, handle, snap, definitions, [0])
        before = packet([row('e1', 'T')])
        examples = {
            'before_packet': before,
            'changed_truth': make_reassessment(before, packet([row('e1', 'T'), row('e2', 'F')])),
            'corroboration': make_reassessment(before, packet([row('e1', 'T'), row('e2', 'T')])),
            'unrelated_append': make_reassessment(before, packet([row('e1', 'T'), row('z', 'T', 'R(Z,Q)')]))}
        (ROOT / 'examples').mkdir(exist_ok=True)
        for name, obj in examples.items():
            (ROOT / 'examples' / (name + '.json')).write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')
        results = {name: verify_reassessment(obj) for name, obj in examples.items() if name != 'before_packet'}
        (ROOT / 'results' / 'demo_verification.json').write_text(json.dumps(results, indent=2, sort_keys=True) + '\n')
        print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()