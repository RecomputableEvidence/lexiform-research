"""Cross-process LC009 verifier; no network or live audit handle required."""
import argparse
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from bootstrap import resolve


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind', choices=['packet', 'reassessment'])
    parser.add_argument('file', type=Path)
    parser.add_argument('--trusted-ledger-tip')
    parser.add_argument('--trusted-packet-hash')
    parser.add_argument('--trusted-before-packet-hash')
    parser.add_argument('--trusted-after-packet-hash')
    parser.add_argument('--trusted-receipt-hash')
    args = parser.parse_args()
    try:
        with tempfile.TemporaryDirectory(prefix='lc009-verify-') as work:
            resolve(work)
            from relational_audit import load_json, verify_scoped_packet, verify_reassessment
            obj = load_json(args.file)
            if args.kind == 'packet':
                if any((args.trusted_before_packet_hash, args.trusted_after_packet_hash,
                        args.trusted_receipt_hash)):
                    raise ValueError('reassessment anchors cannot be used for a packet')
                result = verify_scoped_packet(obj, args.trusted_ledger_tip, args.trusted_packet_hash)
            else:
                if args.trusted_ledger_tip or args.trusted_packet_hash:
                    raise ValueError('use explicitly scoped endpoint/receipt anchors for reassessment')
                result = verify_reassessment(obj, args.trusted_before_packet_hash,
                                             args.trusted_after_packet_hash, args.trusted_receipt_hash)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (ValueError, TypeError, KeyError, AttributeError, IndexError, RecursionError,
            OSError, UnicodeError, OverflowError) as error:
        print(json.dumps({'verified': False, 'error': str(error)}, indent=2), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())