"""LC012 independent finite-set oracle: enumerate complete extensions (small fixtures).
Not authenticated truth, not an independent axiomatization, and intentionally bounded to <= 10 claims.
"""
from itertools import combinations
from contract import scope,PROJ_FIELDS

def kleene_not(v):return 'U' if v=='U' else ('F' if v=='T' else 'T')
def combine(vals,and_mode):
    if and_mode:return 'F' if 'F' in vals else ('U' if 'U' in vals else 'T')
    return 'T' if 'T' in vals else ('U' if 'U' in vals else 'F')

def fact_truth(g,L,q,k,ctx):
    t=g[0]
    if t=='CONST':return g[1],set()
    if t=='FACT':
        rows=[a for a in L['conditions'] if a['key']==g[1] and scope(a,q,k,ctx)]
        values={a['value'] for a in rows}
        return (next(iter(values)) if len(values)==1 else 'U'),{a['source_id'] for a in rows}
    if t=='NOT':
        v,p=fact_truth(g[1],L,q,k,ctx);return kleene_not(v),p
    terms=[fact_truth(x,L,q,k,ctx) for x in g[1:]]
    return combine([v for v,_ in terms],t=='AND'),set().union(*(p for _,p in terms))

def world(L,q,k,ctx):
    claims={a['id']:a for a in L['claims'] if scope(a,q,k,ctx)}
    reviewers={r['id']:r for r in L['reviewers']}
    reviews={a['relation_id']:a for a in L['admissions'] if a['observed']<=k}
    eligible=[];states={};support=set();admitted=set();pending=set();disputed=set();qualifiers=set()
    relation_support={};qualifier_map={}
    for rel in L['links']:
        if not(scope(rel,q,k,ctx) and rel['source'] in claims and rel['target'] in claims):continue
        review=reviews.get(rel['id']);cond,sources=fact_truth(rel['guard'],L,q,k,ctx);support|=sources
        relation_support[rel['id']]=set(sources)
        if cond=='F' or (review and (review['outcome']=='WITHHELD' or
            ctx not in reviewers[review['reviewer_id']]['contexts'])):st='F'
        elif not review or cond=='U':st='U'
        else:st='T'
        states[rel['id']]=st
        if st=='U':pending.add(rel['id']);continue
        if st!='T':continue
        admitted.add(rel['id']);support|=set(rel['evidence_ids'])|set(review['evidence_ids'])
        relation_support[rel['id']].update(rel['evidence_ids']);relation_support[rel['id']].update(review['evidence_ids'])
        if rel['kind'] in {'CORRECTS','SUPERSEDES'}:eligible.append((rel['source'],rel['target']))
        elif rel['kind']=='DISPUTES':disputed.add(rel['target'])
        else:
            qualifiers.add(rel['source'])
            qualifier_map[rel['id']]=rel['source']
    names=sorted(claims)
    if len(names)>10:raise ValueError('oracle max ten claims')
    # A complete extension S satisfies S = F(S), the characteristic function.
    complete=[]
    edges=set(eligible)
    for size in range(len(names)+1):
        for combo in combinations(names,size):
            S=set(combo);attacked={v for u,v in edges if u in S}
            defended={node for node in names if all(att in attacked for att,tgt in edges if tgt==node)}
            if S==defended:complete.append(S)
        if complete:break
    if len(complete)!=1:raise RuntimeError('nonunique minimal complete extension')
    chosen=complete[0]
    beaten={v for u,v in edges if u in chosen}
    return dict(claims=claims,accepted=chosen,defeated=beaten,
                undecided=set(names)-chosen-beaten,edges=edges,states=states,
                admitted=admitted,pending=pending,disputed=disputed,qualifiers=qualifiers,support=support,
                relation_support=relation_support,qualifier_map=qualifier_map)

def truth(e,L,q,k,c='default'):
    op=e['op']
    if op=='SCOPE':return truth(e['body'],L,e['query'],e['knowledge'],e['context'])
    if op in ('ALL','ANY','NOT'):
        xs=[truth(e['arg'],L,q,k,c)] if op=='NOT' else [truth(x,L,q,k,c) for x in e['args']]
        v=kleene_not(xs[0]['value']) if op=='NOT' else combine([x['value'] for x in xs],op=='ALL')
        return {'value':v,**{p:sorted(set().union(*(set(x[p]) for x in xs))) for p in PROJ_FIELDS}}
    w=world(L,q,k,c)
    if op=='LINK':
        v=w['states'].get(e['id'],'U')
        return {'value':v,**{p:([e['id']] if p=='admitted' and v=='T' or p=='pending' and v=='U' else [])
                              for p in PROJ_FIELDS}}
    if op!='ATOM':raise ValueError('unknown abstract op')
    key=(e['kind'],e['predicate'],e['subject'],e['object'])
    rel={i for i,x in w['claims'].items() if
         (x['kind'],x['predicate'],x['subject'],x['object'])==key}
    l_ids={a['id'] for a in L['links'] if a['target'] in rel and a['source'] in w['claims']
           and scope(a,q,k,c)}
    alive=rel&w['accepted'];truthset={w['claims'][i]['value'] for i in alive}
    pending_attacks={r['id'] for r in L['links'] if r['id'] in w['pending']&l_ids
                     and r['kind'] in {'CORRECTS','SUPERSEDES'}}
    v=next(iter(truthset)) if len(truthset)==1 and not (rel&w['undecided']) and not pending_attacks else 'U'
    local_support={w['claims'][i]['source_id'] for i in rel}
    for rid in l_ids:local_support.update(w['relation_support'].get(rid,()))
    return {'value':v,'accepted':sorted(alive),'defeated':sorted(rel&w['defeated']),
            'undecided':sorted(rel&w['undecided']),
            'attacks':sorted(f'{a}>{b}' for a,b in w['edges'] if b in rel),
            'admitted':sorted(w['admitted']&l_ids),'pending':sorted(w['pending']&l_ids),
            'disputed':sorted(w['disputed']&rel),
            'qualifiers':sorted({w['qualifier_map'][rid] for rid in l_ids if rid in w['qualifier_map']}),
            'support':sorted(local_support)}
