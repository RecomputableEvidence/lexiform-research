"""Matched conventional typed AST arm. Independent fixed-point algorithm; common schema only."""
from dataclasses import dataclass
from contract import validate,scope,PROJ_FIELDS

@dataclass(frozen=True)
class Node:
    op:str
    args:tuple=()

def build(abstract):
    op=abstract['op']
    if op=='ATOM':return Node('predicate',(abstract['kind'],abstract['predicate'],abstract['subject'],abstract['object']))
    if op=='LINK':return Node('link',(abstract['id'],))
    if op=='NOT':return Node('negation',(build(abstract['arg']),))
    if op in {'ALL','ANY'}:return Node('conjunction' if op=='ALL' else 'disjunction',tuple(build(t) for t in abstract['args']))
    if op=='SCOPE':return Node('scope',(abstract['query'],abstract['knowledge'],abstract['context'],build(abstract['body'])))
    raise ValueError('typed abstract operator')

class TypedControl:
    def __init__(self,L):
        self.L=L;self.ix=validate(L);self._memo={}

    def eval_condition(self,guard,q,k,c):
        t=guard[0]
        if t=='CONST':return guard[1],set()
        if t=='FACT':
            facts=[v for v in self.L['conditions'] if v['key']==guard[1] and scope(v,q,k,c)]
            values={v['value'] for v in facts}
            return (list(values)[0] if len(values)==1 else 'U'),{v['source_id'] for v in facts}
        if t=='NOT':
            v,e=self.eval_condition(guard[1],q,k,c);return {'T':'F','F':'T','U':'U'}[v],e
        parts=[self.eval_condition(x,q,k,c) for x in guard[1:]]
        vals=[v for v,_ in parts];proof=set().union(*(p for _,p in parts))
        if t=='AND':v= 'F' if 'F' in vals else ('U' if 'U' in vals else 'T')
        else:v='T' if 'T' in vals else ('U' if 'U' in vals else 'F')
        return v,proof

    def _state(self,q,k,c):
        key=(q,k,c)
        if key in self._memo:return self._memo[key]
        claimpool={x['id']:x for x in self.L['claims'] if scope(x,q,k,c)}
        active_edges=[];staged={};pending=set();permitted=set();challenged=set();qualifiers=set();support=set()
        for r in self.L['links']:
            if r['source'] not in claimpool or r['target'] not in claimpool or not scope(r,q,k,c):continue
            review=next((a for a in self.L['admissions'] if a['relation_id']==r['id'] and a['observed']<=k),None)
            gv,ev=self.eval_condition(r['guard'],q,k,c);support|=ev
            if review is not None and (review['outcome']=='WITHHELD' or
                c not in self.ix['reviewers'][review['reviewer_id']]['contexts']):st='F'
            elif gv=='F':st='F'
            elif review is None or gv=='U':st='U'
            else:st='T'
            staged[r['id']]=st
            if st=='U':pending.add(r['id']);continue
            if st!='T':continue
            permitted.add(r['id']);support.update(r['evidence_ids']);support.update(review['evidence_ids'])
            if r['kind'] in {'CORRECTS','SUPERSEDES'}:active_edges.append((r['source'],r['target']))
            elif r['kind']=='DISPUTES':challenged.add(r['target'])
            else:qualifiers.add(r['source'])
        # Conventional Dung characteristic function, independently implemented.
        attacks={id:set() for id in claimpool}
        for source,target in active_edges:attacks[target].add(source)
        accepted=set()
        for _ in range(len(claimpool)+2):
            defended={source for src,target in active_edges if src in accepted for source in [target]}
            step={id for id in claimpool if all(attacker in defended for attacker in attacks[id])}
            if step==accepted:break
            accepted=step
        else:raise RuntimeError('nonconvergent characteristic function')
        defeated={target for src,target in active_edges if src in accepted}
        undec=set(claimpool)-accepted-defeated
        state=(claimpool,active_edges,staged,pending,permitted,challenged,qualifiers,support,
               accepted,defeated,undec)
        self._memo[key]=state
        return state

    def evaluate(self,node,q,k,c='default'):
        if node.op=='scope':return self.evaluate(node.args[3],*node.args[:3])
        if node.op in {'conjunction','disjunction','negation'}:
            parts=[self.evaluate(a,q,k,c) for a in node.args]
            vals=[v['value'] for v in parts]
            if node.op=='negation':result={'T':'F','F':'T','U':'U'}[vals[0]]
            elif node.op=='conjunction':result='F' if 'F' in vals else 'U' if 'U' in vals else 'T'
            else:result='T' if 'T' in vals else 'U' if 'U' in vals else 'F'
            return {'value':result,**{field:sorted(set().union(*(set(x[field]) for x in parts))) for field in PROJ_FIELDS}}
        (claimpool,active_edges,staged,pending,permitted,challenged,qualifiers,support,
         accepted,defeated,undec)=self._state(q,k,c)
        if node.op=='link':
            rid=node.args[0];v=staged.get(rid,'U')
            return {'value':v,**{f:([rid] if (f=='admitted' and v=='T') or (f=='pending' and v=='U') else [])
                                   for f in PROJ_FIELDS}}
        if node.op!='predicate':raise ValueError('invalid typed node')
        targeted={name for name,v in claimpool.items() if
                  (v['kind'],v['predicate'],v['subject'],v['object'])==node.args}
        targetlinks={r['id'] for r in self.L['links'] if r['target'] in targeted and
                     r['source'] in claimpool and scope(r,q,k,c)}
        chosen=accepted&targeted;values={claimpool[id]['value'] for id in chosen}
        value=next(iter(values)) if len(values)==1 and not (undec&targeted) and not (pending&targetlinks) else 'U'
        return {'value':value,'accepted':sorted(chosen),'defeated':sorted(defeated&targeted),
                'undecided':sorted(undec&targeted),
                'attacks':sorted({f'{a}>{b}' for a,b in active_edges if b in targeted}),
                'admitted':sorted(permitted&targetlinks),'pending':sorted(pending&targetlinks),
                'disputed':sorted(challenged&targeted),'qualifiers':sorted(qualifiers),
                'support':sorted(support|{claimpool[i]['source_id'] for i in targeted})}
