"""Exploratory strengthened append-only ordering contract for REASSESS.
Not a modification to the frozen LC-EXP-003 transition implementation.
"""
from transitions import reassess_receipt
from evidence import EvidenceLedger

def strict_reassess(expr, registry, old, new, q, old_k, new_k):
    if not isinstance(old,EvidenceLedger) or not isinstance(new,EvidenceLedger):
        raise ValueError('ledger required')
    n=len(old.records)
    if new.records[:n] != old.records:
        raise ValueError('append-only identity/order broken: original ledger must be an exact prefix')
    if new_k<old_k:
        raise ValueError('forward-enrichment requires nondescending knowledge stage')
    return reassess_receipt(expr,registry,old,new,q,old_k,new_k)
