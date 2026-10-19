"""LC012 list-form lexicon; iterative IN/OUT/UNDEC labeling of admitted attacks."""
from contract import validate,scope,out,PROJ_FIELDS

def neg(x):return {'T':'F','F':'T','U':'U'}[x]
def both(xs):return 'F' if 'F' in xs else ('U' if 'U' in xs else 'T')
def either(xs):return 'T' if 'T' in xs else ('U' if 'U' in xs else 'F')

class Lexicon:
    def __init__(self,ledger):
        self.L=ledger;self.idx=validate(ledger)
        self.memo={}

    def guard(self,g,q,k,ctx):
        op=g[0]
        if op=='CONST':return g[1],set()
        if op=='FACT':
            matches=[f for f in self.L['conditions'] if f['key']==g[1] and scope(f,q,k,ctx)]
            v={f['value'] for f in matches}
            return (v.pop() if len(v)==1 else 'U'),{f['source_id'] for f in matches}
        if op=='NOT':
            x,ev=self.guard(g[1],q,k,ctx);return neg(x),ev
        vals=[];ev=set()
        for part in g[1:]:
            v,p=self.guard(part,q,k,ctx);vals.append(v);ev.update(p)
        return (both(vals) if op=='AND' else either(vals)),ev

    def prepare(self,q,k,ctx):
        key=(q,k,ctx)
        if key in self.memo:return self.memo[key]
        claims={c['id']:c for c in self.L['claims'] if scope(c,q,k,ctx)}
        attacks=set();admitted=set();pending=set();disputed=set();qualifiers=set();support=set()
        relation_states={}
        for link in self.L['links']:
            if not scope(link,q,k,ctx) or link['target'] not in claims or link['source'] not in claims:
                continue
            review=next((a for a in self.L['admissions'] if a['relation_id']==link['id'] and a['observed']<=k),None)
            gate,gate_proof=self.guard(link['guard'],q,k,ctx)
            support.update(gate_proof)
            if review is None:state='U' if gate!='F' else 'F'
            elif review['outcome']=='WITHHELD' or gate=='F':state='F'
            elif ctx not in self.idx['reviewers'][review['reviewer_id']]['contexts']:state='F'
            elif gate=='U':state='U'
            else:state='T'
            relation_states[link['id']]=state
            if state=='U':pending.add(link['id'])
            if state!='T':continue
            admitted.add(link['id'])
            support.update(link['evidence_ids']);support.update(review['evidence_ids'])
            if link['kind'] in {'CORRECTS','SUPERSEDES'}:attacks.add((link['source'],link['target']))
            elif link['kind']=='DISPUTES':disputed.add(link['target'])
            else:qualifiers.add(link['source'])
        # Dung-style grounded in/out/undec labeling. This does NOT establish factual truth.
        attackers={name:set() for name in claims}
        for src,tgt in attacks:attackers[tgt].add(src)
        IN=set();OUT=set();rounds=0
        while True:
            take={node for node in claims if node not in IN|OUT and attackers[node]<=OUT}
            if not take:break
            IN|=take
            OUT|={tgt for src,tgt in attacks if src in take and tgt not in IN}
            rounds+=1
            if rounds>len(claims)+1:raise RuntimeError('grounding did not terminate')
        undec=set(claims)-IN-OUT
        state=dict(claims=claims,IN=IN,OUT=OUT,UNDEC=undec,attacks=attacks,admitted=admitted,
                   pending=pending,disputed=disputed,qualifiers=qualifiers,support=support,
                   relation_states=relation_states,rounds=rounds)
        self.memo[key]=state
        return state

    def atom(self,kind,predicate,subject,obj,q,k,ctx):
        s=self.prepare(q,k,ctx)
        relevant={name for name,c in s['claims'].items() if
                  (c['kind'],c['predicate'],c['subject'],c['object'])==(kind,predicate,subject,obj)}
        accepted=s['IN']&relevant;defeated=s['OUT']&relevant;undec=s['UNDEC']&relevant
        linked={l['id'] for l in self.L['links'] if l['target'] in relevant and l['source'] in s['claims']
                and scope(l,q,k,ctx)}
        pending=s['pending']&linked
        values={s['claims'][id]['value'] for id in accepted}
        v=next(iter(values)) if len(values)==1 and not undec and not pending else 'U'
        return out(v,accepted=accepted,defeated=defeated,undecided=undec,
                   attacks=[f'{a}>{b}' for a,b in s['attacks'] if b in relevant],
                   admitted=s['admitted']&linked,pending=pending,
                   disputed=s['disputed']&relevant,qualifiers=s['qualifiers'],
                   support=[s['claims'][id]['source_id'] for id in relevant]+list(s['support']))

    def eval(self,term,q,k,ctx='default'):
        if type(term) is not list or len(term)<2:raise ValueError('invalid expression')
        tag=term[0]
        if tag=='ATOM':
            if len(term)!=5:raise ValueError('ATOM arity')
            return self.atom(*term[1:],q,k,ctx)
        if tag=='LINK':
            if len(term)!=2:raise ValueError('LINK arity')
            s=self.prepare(q,k,ctx);v=s['relation_states'].get(term[1],'U')
            return out(v,admitted=[term[1]] if v=='T' else [],pending=[term[1]] if v=='U' else [])
        if tag=='SCOPE':
            if len(term)!=5:raise ValueError('SCOPE arity')
            return self.eval(term[4],term[1],term[2],term[3])
        if tag=='NOT':
            if len(term)!=2:raise ValueError('NOT arity')
            p=self.eval(term[1],q,k,ctx);return {**p,'value':neg(p['value'])}
        if tag not in ('AND','OR') or len(term)<3:raise ValueError('unknown or invalid operator')
        items=[self.eval(t,q,k,ctx) for t in term[1:]]
        v=both([p['value'] for p in items]) if tag=='AND' else either([p['value'] for p in items])
        return out(v,**{f:[x for item in items for x in item[f]] for f in PROJ_FIELDS})
