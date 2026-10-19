"""Declared predecessor-style latest-stage heuristic comparison arm (scalar only)."""
def latest_stage_atom(ledger,kind,pred,sub,obj,query,knowledge,context='default'):
    candidates=[x for x in ledger['claims'] if
                (x['kind'],x['predicate'],x['subject'],x['object'])==(kind,pred,sub,obj) and
                x['observed']<=knowledge and x['from']<=query<x['until'] and
                context in x['contexts']]
    if not candidates:return 'U'
    maxstage=max(x['observed'] for x in candidates)
    outcomes={x['value'] for x in candidates if x['observed']==maxstage}
    return next(iter(outcomes)) if len(outcomes)==1 else 'U'
