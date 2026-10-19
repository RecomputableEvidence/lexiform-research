"""LC011 deliberately bounded critical and withheld-like generated tests."""
import copy,random,json,hashlib
from contracts import ledger_validate,is_prefix,digest
from fixtures import main_episode,full_fixture,ATOM,POLICY,to_lex
from engine import concordance,reassess,rewrite_demorgan,rewrite_receipt
from lexicon import Lexicon,tri_not,tri_all,tri_any
from typed_control import Typed,build
from oracle import truth
from latest_stage import latest_stage_atom

N=0
def verify(condition,label):
    global N
    assert condition,label
    N+=1

def fails(fn,label):
    try:fn()
    except (ValueError,AssertionError):return verify(True,label)
    raise AssertionError('expected rejection: '+label)

def assess():
    case=main_episode();L=full_fixture()
    for x in case+[L]:ledger_validate(x)
    verify(all(is_prefix(case[i],case[i+1]) for i in range(3)),'append exact prefix')
    seq=[concordance(ATOM,case[i],3,i if i<3 else 2) for i in range(4)]
    verify([x['value'] for x in seq]==['T','U','U','F'],'newer claim alone does not defeat')
    verify(seq[3]['displaced']==['original'] and seq[3]['admitted']==['r-correct'],
           'admitted correction conditions')
    verify(seq[2]['pending']==['r-correct'],'unadmitted correction visible')
    receipt=reassess(case[1],case[3],ATOM,3,1,2)
    verify(receipt['before']['value']=='U' and receipt['after']['value']=='F' and
           receipt['before']['active']==['later','original'],'reassessment retains both views')
    verify(concordance(ATOM,case[0],3,0)['value']=='T','historical understanding not changed')
    verify(concordance(POLICY,L,6,5)['value']=='U','new policy is not automatically authoritative')
    verify(concordance(POLICY,L,6,6)['value']=='F' and
           concordance(POLICY,L,6,6)['displaced']==['policy-old'],'admitted scoped policy supersession')
    verify(concordance(POLICY,L,3,6)['value']=='T', 'supersession does not govern earlier query stage')
    dis=concordance(ATOM,L,3,4)
    verify(dis['value']=='F' and dis['disputed']==['later'],'challenge not itself refutation')
    before=concordance(ATOM,L,3,7,'lab')
    after=concordance(ATOM,L,3,8,'lab')
    verify(before['value']==after['value']=='F' and before['qualifiers']==[] and
           after['qualifiers']==['extra'],'context qualifies without altering truth')
    verify(concordance(ATOM,L,3,8,'default')['qualifiers']==[],
           'contextual standing is scoped')
    verify(concordance({'op':'LINK','id':'r-correct'},L,3,1)['value']=='U',
           'relationship proposed but not admitted yet')
    verify(concordance({'op':'LINK','id':'r-correct'},L,3,2)['value']=='T',
           'relationship admitted at later knowledge stage')
    verify(concordance({'op':'SCOPE','query':3,'knowledge':0,'context':'default','body':ATOM},L,8,8)['value']=='T',
           'inner knowledge scope does not inherit enriched hindsight')
    verify(concordance({'op':'SCOPE','query':3,'knowledge':2,'context':'default','body':ATOM},L,8,8)['value']=='F',
           'explicit enriched knowledge scope changes status')

    expression={'op':'NOT','arg':{'op':'ANY','args':[ATOM,{'op':'NOT','arg':POLICY}]}}
    eq=rewrite_demorgan(expression)
    r=rewrite_receipt(expression,eq,L,6,6)
    verify(r['operation']=='REWRITE' and r['preserved_projection']==concordance(eq,L,6,6),
           'licensed rewrite and full provenance equivalence')
    non_eq={'op':'ANY','args':[{'op':'NOT','arg':ATOM},{'op':'NOT','arg':{'op':'NOT','arg':POLICY}}]}
    fails(lambda:rewrite_receipt(expression,non_eq,L,6,6),'unlicensed logical rewrite rejected')
    mismatched={'op':'ANY','args':[{'op':'NOT','arg':ATOM},{'op':'NOT','arg':POLICY}]}
    verify(concordance(expression,L,6,6)['value']!=concordance(mismatched,L,6,6)['value'],
           'negative scope/quantifier fixture is actually distinct')
    bad=copy.deepcopy(L);bad['claims'][0]['observed']=-1
    fails(lambda:ledger_validate(bad),'negative stage invalid')
    bad=copy.deepcopy(L);bad['claims'][0]['observed']=True
    fails(lambda:ledger_validate(bad),'Boolean disguised as stage invalid')
    bad=copy.deepcopy(L);bad['evidence'].append(copy.deepcopy(bad['evidence'][0]))
    fails(lambda:ledger_validate(bad),'duplicate evidence identity rejected')
    bad=copy.deepcopy(L);bad['admissions'][0]['rule']='ALLOW_SUPERSESSION'
    fails(lambda:ledger_validate(bad),'admission relation type mismatch')
    bad=copy.deepcopy(L);bad['links'][0]['target']='nonexistent'
    fails(lambda:ledger_validate(bad),'dangling relationship rejected')
    bad=copy.deepcopy(L);bad['links'][0]['evidence_ids']=['e5']
    fails(lambda:ledger_validate(bad),'relationship future evidence rejected')
    bad=copy.deepcopy(L);bad['links'][0]['evidence_ids']=['absent']
    fails(lambda:ledger_validate(bad),'missing relationship provenance rejected')
    bad=copy.deepcopy(L);bad['admissions'].append(copy.deepcopy(bad['admissions'][0])|{'id':'duplicate-review'})
    fails(lambda:ledger_validate(bad),'multiple reviews of same relationship rejected')
    bad=copy.deepcopy(L);bad['claims'][-1]['subject']='not-A'
    fails(lambda:ledger_validate(bad),'unrelated contextual claim cannot qualify target')
    bad=copy.deepcopy(L);bad['links'][0]['kind']='SUPERSEDES'
    fails(lambda:ledger_validate(bad),'cross-domain policy/observation operator rejected')
    bad=copy.deepcopy(case[3]);bad['claims'][0]['value']='F'
    verify(not is_prefix(case[0],bad),'past claims cannot be silently rewritten')
    bad=copy.deepcopy(case[3]);bad['evidence'].reverse()
    verify(not is_prefix(case[1],bad),'reordered historical evidence cannot be accepted')
    fails(lambda:reassess(case[1],bad,ATOM,3,1,2),'reassessment rejects altered predecessor')

    # Distinct source claim and qualified challenge, but no admitted relation.
    unreviewed=copy.deepcopy(case[1])
    unreviewed['evidence'].append({'id':'unreviewed','source_id':'fictitious','description':'proposal','observed':2})
    unreviewed['links'].append({'id':'claimed-correction','kind':'CORRECTS','source':'later','target':'original',
                      'observed':2,'from':0,'until':12,'contexts':['default'],'evidence_ids':['unreviewed']})
    verify(concordance(ATOM,unreviewed,3,2)['value']=='U',
           'claimed relation alone cannot change standing')

    # Relation direction and declared context scope are semantic, not decorative.
    reverse=copy.deepcopy(case[-1])
    reverse['links'][0]['source'],reverse['links'][0]['target']=('original','later')
    verify(concordance(ATOM,reverse,3,2)['value']=='T',
           'reversing admitted correction direction changes result')
    scoped=copy.deepcopy(case[-1]);scoped['links'][0]['contexts']=['lab']
    verify(concordance(ATOM,scoped,3,2,'default')['value']=='U' and
           concordance(ATOM,scoped,3,2,'lab')['value']=='F',
           'correction only applies in its declared scope')
    withheld=copy.deepcopy(case[-1]);withheld['admissions'][0]['outcome']='WITHHELD'
    verify(concordance(ATOM,withheld,3,2)['value']=='U',
           'withheld admission does not displace target')
    for lhs in ['T','U','F']:
        for rhs in ['T','U','F']:
            verify(tri_not(tri_any([lhs,rhs]))==tri_all([tri_not(lhs),tri_not(rhs)]),
                   'strong Kleene De Morgan 9 valuations')
    # Operational latest-stage policy comparison: at k=1 it would yield F, whereas LC011 is U.
    latest=latest_stage_atom(case[1],'observation','sealed','A','B',3,1)
    verify(latest=='F' and seq[1]['value']=='U',
           'latest-stage heuristic differs in overlapping-claim conflict')

    # An unrelated append must not change existing semantic projections.
    unrelated=copy.deepcopy(case[-1]);unrelated['evidence'].append({'id':'unrelated-e','source_id':'synthetic-u',
        'description':'unrelated item','observed':3})
    unrelated['claims'].append({'id':'unrelated-claim','kind':'observation','predicate':'other',
        'subject':'X','object':'Y','value':'F','observed':3,'from':0,'until':12,
        'contexts':['default'],'source_id':'unrelated-e'})
    verify(concordance(ATOM,case[-1],3,3)==concordance(ATOM,unrelated,3,3),
           'unrelated evidence does not change selected meaning or audit witness')
    verify(digest(case[-1])!=digest(unrelated) and is_prefix(case[-1],unrelated),
           'unrelated append changes ledger commitment without semantic change')
    # Corroboration adds support without changing the scalar truth.
    corroborated=copy.deepcopy(case[-1]);corroborated['evidence'].append({'id':'corrob-e','source_id':'synthetic-c',
        'description':'matching later report','observed':3})
    corroborated['claims'].append({'id':'corrob','kind':'observation','predicate':'sealed',
        'subject':'A','object':'B','value':'F','observed':3,'from':0,'until':12,
        'contexts':['default','lab'],'source_id':'corrob-e'})
    before_corrob=concordance(ATOM,case[-1],3,3)
    after_corrob=concordance(ATOM,corroborated,3,3)
    verify(before_corrob['value']==after_corrob['value']=='F' and
           before_corrob['support']!=after_corrob['support'],
           'corroboration changes evidence support not conclusion')
    # Seeded withheld-like compositions. No expression-specific definitions or expected values.
    r=random.Random(20261017)
    leaves=[ATOM,POLICY,{'op':'LINK','id':'r-correct'},{'op':'LINK','id':'r-dispute'},
            {'op':'LINK','id':'r-sup'},{'op':'LINK','id':'r-context'},
            {'op':'ATOM','kind':'observation','predicate':'absent','subject':'X','object':'Y'}]
    def grow(depth):
        if depth==0 or r.random()<0.23:return copy.deepcopy(r.choice(leaves))
        op=r.choice(['ALL','ANY','NOT','SCOPE'])
        if op=='NOT':return {'op':'NOT','arg':grow(depth-1)}
        if op=='SCOPE':return {'op':'SCOPE','query':r.randrange(2,10),
                              'knowledge':r.randrange(0,10),'context':r.choice(['default','lab']),
                              'body':grow(depth-1)}
        return {'op':op,'args':[grow(depth-1) for _ in range(r.randrange(2,5))]}
    expressions=[];seen=set();attempts=0
    while len(expressions)<512 and attempts<5000:
        attempts+=1
        x=grow(r.randrange(2,6));h=digest(x)
        if h in seen:continue
        seen.add(h);q=r.randrange(2,10);k=r.randrange(0,10)
        c=r.choice(['default','lab'])
        concordance(x,L,q,k,c)
        expressions.append(x)
    distinct=len(seen)
    verify(distinct==512,'512 syntactically distinct withheld-like composites')
    # Explicit control sensitivity: future evidence and scope mutations must be observable.
    verify(concordance(ATOM,case[0],3,0)['value']!=concordance(ATOM,case[1],3,1)['value'],
           'knowledge enrichment changes outcome')
    verify(concordance({'op':'SCOPE','query':3,'knowledge':7,'context':'lab','body':ATOM},L,3,0)['value']==
           concordance(ATOM,L,3,7,'lab')['value'],'nested scope semantics independent of outer values')
    return {'assertion_groups':N,'generated_checks':len(expressions),'distinct_generated_expressions':distinct,'generation_attempts':attempts,
            'episode_values':[v['value'] for v in seq], 'rewrite_rule':'DE_MORGAN_ANY_TO_ALL_KLEENE',
            'comparison_paths':['lexicon recursive','typed AST recursive','independent oracle']}

if __name__=='__main__':print(json.dumps(assess(),indent=2))
