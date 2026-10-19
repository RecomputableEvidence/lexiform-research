"""LexiFORM candidate: independently parse/evaluate list-form descriptors."""
from contracts import ledger_validate,scope_ok

def tri_not(x):return {'T':'F','F':'T','U':'U'}[x]
def tri_all(v):return 'F' if 'F' in v else ('U' if 'U' in v else 'T')
def tri_any(v):return 'T' if 'T' in v else ('U' if 'U' in v else 'F')

def projection(v):
    return {k:sorted(set(v[k])) for k in ['active','displaced','disputed','qualifiers','admitted','pending','support']} | {'value':v['value']}

def outcome(value='U',**kw):
    r=dict(value=value,active=[],displaced=[],disputed=[],qualifiers=[],admitted=[],pending=[],support=[])
    r.update(kw);return projection(r)

class Lexicon:
    def __init__(self, ledger):
        self.ledger=ledger
        self.by=ledger_validate(ledger)

    def relationship(self, rid,q,k,context):
        l=self.by['links'].get(rid)
        if l is None or not scope_ok(l,q,k,context):return 'U',None
        valid=[a for a in self.ledger['admissions'] if a['relation_id']==rid and a['observed']<=k]
        if not valid:return 'U',l
        return ('T' if valid[0]['outcome']=='ADMITTED' else 'F'),l

    def atom(self,kind,pred,sub,obj,q,k,context):
        candidates=[c for c in self.ledger['claims'] if
                    (c['kind'],c['predicate'],c['subject'],c['object'])==(kind,pred,sub,obj)
                    and scope_ok(c,q,k,context)]
        byid={c['id']:c for c in candidates}
        displaced=set(); disputed=set(); qualifiers=set(); admitted=set(); pending=set()
        for l in self.ledger['links']:
            if l['target'] not in byid or l['source'] not in self.by['claims']:
                continue
            s=self.by['claims'][l['source']]
            if not scope_ok(s,q,k,context) or not scope_ok(l,q,k,context):continue
            status,_=self.relationship(l['id'],q,k,context)
            if status=='U':pending.add(l['id']);continue
            if status!='T':continue
            admitted.add(l['id'])
            if l['kind'] in ('CORRECTS','SUPERSEDES'):
                displaced.add(l['target'])
            elif l['kind']=='DISPUTES':disputed.add(l['target'])
            elif l['kind']=='ADDS_CONTEXT':qualifiers.add(s['id'])
        active=[c for c in candidates if c['id'] not in displaced]
        vals={c['value'] for c in active}
        value=next(iter(vals)) if len(vals)==1 else 'U'
        return outcome(value,active=[c['id'] for c in active],displaced=list(displaced),
                       disputed=list(disputed),qualifiers=list(qualifiers),admitted=list(admitted),
                       pending=list(pending),support=[c['source_id'] for c in candidates]+
                       [e for l in self.ledger['links'] if l['id'] in admitted
                        for e in l['evidence_ids']])

    def eval(self,expr,q,k,context='default'):
        if type(expr) is not list or not expr or type(expr[0]) is not str:
            raise ValueError('invalid lexicon expression')
        op=expr[0]
        if op=='A':
            if len(expr)!=5 or not all(type(t) is str for t in expr[1:]):raise ValueError('A arity')
            return self.atom(*expr[1:],q,k,context)
        if op=='L':
            if len(expr)!=2 or type(expr[1]) is not str:raise ValueError('L arity')
            status,link=self.relationship(expr[1],q,k,context)
            return outcome(status,admitted=[expr[1]] if status=='T' else [],
                           pending=[expr[1]] if status=='U' and link else [],
                           support=link['evidence_ids'] if link is not None and status=='T' else [])
        if op=='S':
            if len(expr)!=5 or not (type(expr[1]) is int and type(expr[2]) is int and
                expr[1]>=0 and expr[2]>=0 and type(expr[3]) is str):raise ValueError('S arity')
            return self.eval(expr[4],expr[1],expr[2],expr[3])
        if op=='N':
            if len(expr)!=2:raise ValueError('N arity')
            z=self.eval(expr[1],q,k,context);return z|{'value':tri_not(z['value'])}
        if op in ('&','|'):
            if len(expr)<3:raise ValueError('variadic op requires >=2 children')
            children=[self.eval(child,q,k,context) for child in expr[1:]]
            combine=tri_all if op=='&' else tri_any
            return outcome(combine([c['value'] for c in children]),**{
                field:[e for child in children for e in child[field]]
                for field in ('active','displaced','disputed','qualifiers','admitted','pending','support')})
        raise ValueError('unknown descriptor '+op)
