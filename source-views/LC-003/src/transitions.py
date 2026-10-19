"""Explicit non-interchangeable REWRITE and REASSESS receipts."""
from dataclasses import dataclass
from legacy_a import Term
from evidence import sha, EvidenceLedger, stage_num
from engine import EngineA, EngineB, projection


def format_term(t):
    return str(t) if isinstance(t,(str,int)) else f"{t.op}({','.join(format_term(a) for a in t.args)})"

# Rule valid for well-typed contiguous, stage-aligned path composition.
# C(C(a,b),c) -> C(a,C(b,c)). No evidence state, epistemic status, or guard removed.
def rewrite_assoc_right(source,registry):
    ast=EngineA(registry).parser.parse(source)
    if ast.op!='C' or ast.args[0].op!='C':
        raise ValueError('rewrite premise absent')
    left=ast.args[0]
    result=Term('C',(left.args[0], Term('C',(left.args[1],ast.args[1]))))
    return format_term(result)

def rewrite_receipt(source,registry,ledger,q,k=None):
    q=stage_num(q);k=stage_num(q if k is None else k)
    target=rewrite_assoc_right(source,registry)
    ea=EngineA(registry);eb=EngineB(registry)
    beforeA=ea.evaluate(source,ledger,q,k);afterA=ea.evaluate(target,ledger,q,k)
    beforeB=eb.evaluate(source,ledger,q,k);afterB=eb.evaluate(target,ledger,q,k)
    if not(projection(beforeA)==projection(afterA)==projection(beforeB)==projection(afterB)):
        raise ValueError('rewrite equivalence failed under tested evidence')
    receipt={'type':'REWRITE','rule':'ASSOC_C_LEFT_TO_RIGHT_1',
             'contract':'typed contiguous path; strong Kleene conjunction; equal active stage',
             'original_expression':source,'successor_expression':target,
             'original_trace_sha256':sha(beforeA),'successor_trace_sha256':sha(afterA),
             'projection_sha256':beforeA['semantic_projection_sha256'],
             'ledger_sha256':ledger.digest,'registry_sha256':registry.digest,
             'query_stage':q,'knowledge_stage':k,
             'rule_status':'bounded declared rule, checked for this input; not general theorem-prover certification'}
    receipt['receipt_sha256']=sha(receipt)
    return receipt

def reassess_receipt(expr,registry,old_ledger,new_ledger,query_stage,old_knowledge,new_knowledge):
    q=stage_num(query_stage);ko=stage_num(old_knowledge);kn=stage_num(new_knowledge)
    if not isinstance(old_ledger,EvidenceLedger) or not isinstance(new_ledger,EvidenceLedger):
        raise ValueError('immutable ledgers required')
    beforeA,beforeB=EngineA(registry).evaluate(expr,old_ledger,q,ko),EngineB(registry).evaluate(expr,old_ledger,q,ko)
    afterA,afterB=EngineA(registry).evaluate(expr,new_ledger,q,kn),EngineB(registry).evaluate(expr,new_ledger,q,kn)
    if projection(beforeA)!=projection(beforeB) or projection(afterA)!=projection(afterB):
        raise ValueError('cross-engine comparison disagreement')
    old={r.id:r for r in old_ledger.records};new={r.id:r for r in new_ledger.records}
    ids_in_both=set(old)&set(new)
    if any(old[i]!=new[i] for i in ids_in_both):
        raise ValueError('reused evidence ID with changed content; append independent record instead')
    if not set(old).issubset(new):
        raise ValueError('evidence removal violates append-only reassessment; use a new superseding observation')
    receipt={'type':'REASSESS','original_expression':expr,'successor_expression':expr,
             'query_stage':q,'previous_knowledge_stage':ko,'new_knowledge_stage':kn,
             'previous_evidence_sha256':old_ledger.digest,'new_evidence_sha256':new_ledger.digest,
             'registry_sha256':registry.digest,
             'previous_trace_sha256':sha(beforeA),'new_trace_sha256':sha(afterA),
             'previous_projection_sha256':beforeA['semantic_projection_sha256'],
             'new_projection_sha256':afterA['semantic_projection_sha256'],
             'previous_value':beforeA['value'],'new_value':afterA['value'],
             'added_ids':sorted(set(new)-set(old)),'removed_ids':[],
             'interpretation_changed':projection(beforeA)!=projection(afterA),
             'predecessor_preserved':'referenced by digest; previous trace supplied separately'}
    receipt['receipt_sha256']=sha(receipt)
    return receipt, beforeA, afterA
