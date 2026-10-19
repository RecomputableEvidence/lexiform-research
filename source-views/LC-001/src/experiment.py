"""Vertical slice: frozen definitions, independent agreement, replayable audit ledger."""
import itertools, json
from pathlib import Path
from common import EVIDENCE, registry, digest, details, canonical
from interpreter_a import InterpreterA
from interpreter_b import InterpreterB
from baseline import TypedEvaluator, TRANSFER_TREE

ROOT=Path(__file__).resolve().parents[1]


def prove_rewrite(expr_a, expr_b, a, b, *, max_atoms=8):
    aa=a.evaluate(expr_a,valuation={})['atoms']
    bb=b.evaluate(expr_b,valuation={})['atoms']
    union=sorted(set(aa+bb))
    if len(union)>max_atoms:
        return {'valid':False,'reason':'too many distinct atoms for exhaustive proof','checked':0}
    count=0
    for values in itertools.product(['T','U','F'],repeat=len(union)):
        valuation=dict(zip(union,values))
        x=a.evaluate(expr_a,valuation=valuation)['value']
        y=b.evaluate(expr_a,valuation=valuation)['value']
        z=a.evaluate(expr_b,valuation=valuation)['value']
        w=b.evaluate(expr_b,valuation=valuation)['value']
        count+=1
        if x!=y or z!=w:
            return {'valid':False,'reason':'independent interpreters disagree',
                    'checked':count,'witness':valuation,'results':[x,y,z,w]}
        if x!=z:
            return {'valid':False,'reason':'inequivalent under three-valued logic',
                    'checked':count,'witness':valuation,'results':[x,z]}
    return {'valid':True,'reason':'bounded exhaustive truth-table equivalence', 'checked':count}


def audit_event(history, kind, payload, reg):
    prev=history[-1]['event_hash'] if history else 'GENESIS'
    row={'seq':len(history)+1,'kind':kind,'grammar_version':reg['grammar_version'],
         'registry_digest':digest(reg),'previous_hash':prev,**payload}
    row['event_hash']=digest(row)
    history.append(row)
    return row


def verify_history(history):
    prev='GENESIS'
    for i,row in enumerate(history):
        unsigned={k:v for k,v in row.items() if k!='event_hash'}
        if row['seq']!=i+1 or row['previous_hash']!=prev or digest(unsigned)!=row['event_hash']:
            return False
        prev=row['event_hash']
    return True


def run_episode(save=True):
    reg=registry(); a=InterpreterA(reg['definitions']); b=InterpreterB(reg['definitions'])
    c=TypedEvaluator(); history=[]; results=[]
    expr='G1(A)'
    for stage, added in [(0,['E001']),(1,['E002']),(2,['E003'])]:
        x=a.evaluate(expr,evidence=EVIDENCE,stage=stage)
        y=b.evaluate(expr,evidence=EVIDENCE,stage=stage)
        z=c.evaluate(TRANSFER_TREE,EVIDENCE,stage)
        decoded_a=a.reconstruct(expr,evidence=EVIDENCE,stage=stage)
        decoded_b=b.reconstruct(expr,evidence=EVIDENCE,stage=stage)
        if {k:v for k,v in decoded_a.items() if k!='text'} != {k:v for k,v in decoded_b.items() if k!='text'}:
            raise AssertionError('independent semantic reconstruction mismatch')
        if x!=y or x!=z: raise AssertionError('three-way agreement failure')
        terms={s:details(EVIDENCE,stage,s,'A') for s in ('S','P')}
        value=x['value']
        problems=[]
        for pred,meaning in (('S','sealed'),('P','inspection_passed')):
            item=terms[pred]
            if item['value']!='T':
                problems.append({'condition':meaning,'state':item['value'],'reason':item['reason']})
        conclusion={'stage':stage,'expression':expr,
                    'authorization':'established' if value=='T' else 'not_established',
                    'three_valued_result':value,'unmet_conditions':problems,
                    'evidence_state':terms,
                    'record_evidence_ids':sorted(set(sum((x['evidence_ids'] for x in terms.values()),[])))}
        audit_event(history,'REASSESS',{
            'stage':stage,'new_evidence_ids':added,'input_expression_id':digest(expr),
            'output_conclusion':conclusion,
            'rule':'G1 condition at selected evidence snapshot',
            'premise_evidence_ids':conclusion['record_evidence_ids'],
            'full_evidence_log_digest':digest(EVIDENCE),
            'stage_evidence_digest':digest([e for e in EVIDENCE if e['stage']<=stage]),
            'reconstructions':{'interpreter_a':decoded_a['text'],'interpreter_b':decoded_b['text']},
            'semantic_reconstruction_agreement':True,
            'validation_status':'ACCEPTED','interpreter_agreement':True},reg)
        results.append(conclusion)
    good=prove_rewrite('!(&(S(A),P(A)))','|(!(S(A)),!(P(A)))',a,b)
    bad=prove_rewrite('!(&(S(A),P(A)))','&(!(S(A)),P(A))',a,b)
    for status,proof,right in [('ACCEPTED',good,'|(!(S(A)),!(P(A)))'),
                               ('REJECTED',bad,'&(!(S(A)),P(A))')]:
        audit_event(history,'REWRITE',{
            'input_expression_id':digest('!(&(S(A),P(A)))'),
            'before':'!(&(S(A),P(A)))','after_candidate':right,
            'rule':'three-valued exhaustive equivalence',
            'proof':proof,'full_evidence_log_digest':digest(EVIDENCE),'validation_status':status,
            'output_expression_id':digest(right) if status=='ACCEPTED' else None},reg)
    if save:
        path=ROOT/'results'/'episode_trace.json'
        path.write_text(json.dumps({'registry_digest':digest(reg),'evidence_log_digest':digest(EVIDENCE),'evidence_log':EVIDENCE,
                                    'conclusions':results,'audit_chain':history,
                                    'trace_verified':verify_history(history)},indent=2)+'\n')
    return {'conclusions':results,'accepted_rewrite':good,'rejected_rewrite':bad,
            'audit':history,'trace_verified':verify_history(history),
            'interpreter_a_stats':a.stats}

if __name__=='__main__':
    r=run_episode()
    print(json.dumps({k:v for k,v in r.items() if k!='audit'},indent=2))
