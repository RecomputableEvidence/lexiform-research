"""Conventional typed-AST comparator. Independent selector and recursive evaluation."""
from dataclasses import dataclass
from contracts import ledger_validate

@dataclass(frozen=True)
class Node:
    name:str
    data:tuple=()
    children:tuple=()

def build(x):
    if type(x) is not dict or 'op' not in x:raise ValueError('typed expression expected')
    op=x['op']
    if op=='ATOM':
        if set(x)!=set(('op','kind','predicate','subject','object')):raise ValueError('atom fields')
        return Node(op,(x['kind'],x['predicate'],x['subject'],x['object']))
    if op=='LINK':
        if set(x)!=set(('op','id')):raise ValueError('link fields')
        return Node(op,(x['id'],))
    if op=='SCOPE':
        if set(x)!=set(('op','query','knowledge','context','body')):raise ValueError('scope fields')
        return Node(op,(x['query'],x['knowledge'],x['context']),(build(x['body']),))
    if op=='NOT':
        if set(x)!=set(('op','arg')):raise ValueError('not fields')
        return Node(op,(),(build(x['arg']),))
    if op in ('ALL','ANY'):
        if set(x)!=set(('op','args')) or type(x['args']) is not list or len(x['args'])<2:
            raise ValueError('combinator fields')
        return Node(op,(),tuple(build(c) for c in x['args']))
    raise ValueError('unknown typed op')

class Typed:
    def __init__(self,ledger):
        self.ledger=ledger;self.idx=ledger_validate(ledger)
    @staticmethod
    def eligible(x,now,known,context):
        return x['from']<=now and now<x['until'] and x['observed']<=known and context in x['contexts']
    def relation_state(self,rid,now,known,context):
        link=self.idx['links'].get(rid)
        if link is None or not self.eligible(link,now,known,context):return 'U',None
        a=next((a for a in self.ledger['admissions'] if a['relation_id']==rid and a['observed']<=known),None)
        if a is None:return 'U',link
        return ('T' if a['outcome']=='ADMITTED' else 'F'),link
    def leaf(self,data,now,known,context):
        matches=[c for c in self.ledger['claims'] if
                 (c['kind'],c['predicate'],c['subject'],c['object'])==data
                 and self.eligible(c,now,known,context)]
        index={c['id']:c for c in matches}
        kicked=set(); contested=set(); extra=set(); approved=set(); waiting=set(); provenance=set()
        for c in matches:provenance.add(c['source_id'])
        for r in self.ledger['links']:
            if r['target'] not in index or not self.eligible(r,now,known,context):continue
            src=self.idx['claims'][r['source']]
            if not self.eligible(src,now,known,context):continue
            decision,_=self.relation_state(r['id'],now,known,context)
            if decision=='U':waiting.add(r['id']);continue
            if decision=='F':continue
            approved.add(r['id']);provenance.update(r['evidence_ids'])
            match r['kind']:
                case 'CORRECTS'|'SUPERSEDES':kicked.add(r['target'])
                case 'DISPUTES':contested.add(r['target'])
                case 'ADDS_CONTEXT':extra.add(src['id'])
        visible=[c for c in matches if c['id'] not in kicked]
        readings={c['value'] for c in visible}
        return dict(value=next(iter(readings)) if len(readings)==1 else 'U',
                    active=sorted(c['id'] for c in visible),displaced=sorted(kicked),
                    disputed=sorted(contested),qualifiers=sorted(extra),
                    admitted=sorted(approved),pending=sorted(waiting),support=sorted(provenance))
    def eval(self,node,now,known,context='default'):
        op=node.name
        if op=='ATOM':return self.leaf(node.data,now,known,context)
        if op=='LINK':
            d,link=self.relation_state(node.data[0],now,known,context)
            return dict(value=d,active=[],displaced=[],disputed=[],qualifiers=[],
                        admitted=[node.data[0]] if d=='T' else [],
                        pending=[node.data[0]] if d=='U' and link else [],
                        support=sorted(link['evidence_ids']) if link is not None and d=='T' else [])
        if op=='SCOPE':return self.eval(node.children[0],*node.data)
        if op=='NOT':
            out=self.eval(node.children[0],now,known,context)
            out['value']={'T':'F','F':'T','U':'U'}[out['value']];return out
        c=[self.eval(ch,now,known,context) for ch in node.children]
        x=[r['value'] for r in c]
        v=('F' if 'F' in x else 'U' if 'U' in x else 'T') if op=='ALL' else (
          'T' if 'T' in x else 'U' if 'U' in x else 'F')
        return dict(value=v,**{field:sorted(set(e for v2 in c for e in v2[field]))
                for field in ('active','displaced','disputed','qualifiers','admitted','pending','support')})
