"""Typed transformation evidence: no retrospective replacement of original records.
REWRITE certifies a declared algebraic rule + tests the particular evidence context.
REASSESS records differences, not an authority to claim physical truth.
"""
from grammar_a import ParserA
from lazy_graph import LazyGraph
from typed_controls import TypedDP
from evidence import EvidenceLedger,sha,stage_num

def show(t):
    op=t[0]
    if op=='R':return f'R({t[1]},{t[2]})'
    if op in ('C','CHOICE'):return f'{op}({show(t[1])},{show(t[2])})'
    if op=='J':return f'J({t[1][0]}({t[1][1]}),{show(t[2])})'
    if op=='AT':return f'AT({t[1]},{show(t[2])})'
    if op=='MACRO':return f'{t[1]}({",".join(t[2])})'
    raise ValueError('unknown tree')

def proposed_rewrite(expression,rule):
    t=ParserA().parse(expression)
    if rule=='CHAIN_CHOICE_LEFT' and t[0]=='C' and t[1][0]=='CHOICE':
        a,b=t[1][1:];z=t[2]
        return show(('CHOICE',('C',a,z),('C',b,z)))
    if rule=='CHAIN_CHOICE_RIGHT' and t[0]=='C' and t[2][0]=='CHOICE':
        z=t[1];a,b=t[2][1:]
        return show(('CHOICE',('C',z,a),('C',z,b)))
    if rule=='GUARD_CHOICE' and t[0]=='J' and t[2][0]=='CHOICE':
        guard=t[1];a,b=t[2][1:]
        return show(('CHOICE',('J',guard,a),('J',guard,b)))
    if rule=='TIME_CHOICE' and t[0]=='AT' and t[2][0]=='CHOICE':
        at=t[1];a,b=t[2][1:]
        return show(('CHOICE',('AT',at,a),('AT',at,b)))
    raise ValueError('rewrite precondition not met')

def rewrite_receipt(expression,rule,registry,ledger,q,k=None):
    target=proposed_rewrite(expression,rule)
    lazy=LazyGraph(registry);typed=TypedDP(registry)
    a=lazy.evaluate(expression,ledger,q,k);b=lazy.evaluate(target,ledger,q,k)
    c=typed.evaluate(expression,ledger,q,k);d=typed.evaluate(target,ledger,q,k)
    fields=('value','start','end','stage','histogram','witness_count')
    if any(a[f]!=b[f] or a[f]!=c[f] or b[f]!=d[f] for f in fields):
        raise ValueError('contextual equivalence proof obligation FAILED')
    receipt={'kind':'REWRITE','rule':rule,'source':expression,'target':target,
             'source_root':a['root_id'],'target_root':b['root_id'],
             'source_summary_sha256':sha({f:a[f] for f in fields}),
             'target_summary_sha256':sha({f:b[f] for f in fields}),
             'source_graph_sha256':sha(a['nodes']),'target_graph_sha256':sha(b['nodes']),
             'evidence_records':ledger.records_as_dicts(),
             'registry_sha256':registry.digest,'ledger_sha256':ledger.digest,
             'requested_query_stage':stage_num(q),'effective_stage':a['stage'],'knowledge_stage':a['knowledge_stage'],
             'obligation':'declared 3-valued lattice distributivity + typed comparator equality; not universal independent proof'}
    receipt['receipt_sha256']=sha(receipt)
    return receipt

def reassess_receipt(expression,registry,previous,new,q,old_k,new_k):
    if type(previous) is not EvidenceLedger or type(new) is not EvidenceLedger:raise ValueError('ledger required')
    if new.records[:len(previous.records)]!=previous.records:
        raise ValueError('strict append-only ledger prefix violated')
    old_k=stage_num(old_k);new_k=stage_num(new_k)
    if new_k<old_k:raise ValueError('knowledge regression')
    a=LazyGraph(registry).evaluate(expression,previous,q,old_k)
    b=LazyGraph(registry).evaluate(expression,new,q,new_k)
    c=TypedDP(registry).evaluate(expression,previous,q,old_k)
    d=TypedDP(registry).evaluate(expression,new,q,new_k)
    for x,y in ((a,c),(b,d)):
        for key in ('value','histogram','witness_count','start','end','stage'):
            if x[key]!=y[key]:raise ValueError('independent control mismatch')
    def snap(v):
        return {key:v[key] for key in ('value','histogram','witness_count','root_id','ledger_sha256',
                                      'registry_sha256','stage','knowledge_stage')}
    receipt={'kind':'REASSESS','source_expression':expression,'previous':snap(a),'successor':snap(b),
             'append_only_prefix_length':len(previous.records),
             'previous_graph_sha256':sha(a['nodes']),'successor_graph_sha256':sha(b['nodes']),
             'previous_evidence_records':previous.records_as_dicts(),
             'successor_evidence_records':new.records_as_dicts(),
             'requested_query_stage':stage_num(q),
             'added_evidence_ids':[r.id for r in new.records[len(previous.records):]],
             'interpretive_change':a['value']!=b['value'],
             'claim_scope':'reassessment from declared evidence; no independent physical verification'}
    receipt['receipt_sha256']=sha(receipt)
    return receipt
