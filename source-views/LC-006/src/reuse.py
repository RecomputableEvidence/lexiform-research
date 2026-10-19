"""LC-EXP-006: dependency-sensitive, context-bound incremental witness graph.

Declared semantics are inherited unchanged from LC-EXP-005/003. This is an
incremental execution experiment, NOT independent grounding or semantic discovery.
The A/B controls use different parsers but share this incremental algorithm;
full TypedAudit recomputation is the separate reference implementation.
"""
import copy
from collections import defaultdict
from grammar_a import ParserA
from grammar_b import ParserB
from lazy_graph import NAMES, meet, mul_hist, plus_hist, with_guard, hist_value
from evidence import EvidenceLedger, sha, stage_num

class BoundReuse:
    def __init__(self, registry, parser='A'):
        if parser not in ('A', 'B'): raise ValueError('parser choice A/B required')
        self.registry=registry
        self.parser=ParserA() if parser=='A' else ParserB()
        self.parser_identity=parser
        self.plan=None
        self.state={}
        self.observations={}
        self.ledger=None
        self.context=None
        self.last_receipt=None
        self.receipts=[]

    def _compile(self, expression, query_stage):
        definitions=self.registry.get_definitions()
        root_tree=self.parser.parse(expression)
        plans={}; order=[]; by_atom=defaultdict(set); parents=defaultdict(set)
        def add(tree, at, depth=0):
            if depth>192 or len(plans)>8192:raise ValueError('resource bound')
            op=tree[0]
            pid=sha({'tree':tree,'stage':at})
            if pid in plans:return pid
            children=[];atom=None;meta=None
            if op=='R':
                start,end=tree[1:];stage=at;guaranteed={start,end};atom=f'R({start},{end})'
            elif op in ('C','CHOICE'):
                children=[add(tree[1],at,depth+1),add(tree[2],at,depth+1)]
                a,b=[plans[c] for c in children]
                if a['stage']!=b['stage']:raise ValueError('mixed stages')
                if op=='C':
                    if a['end']!=b['start']:raise ValueError('serial endpoint mismatch')
                    start,end=a['start'],b['end']
                    guaranteed=a['guaranteed']|b['guaranteed']
                else:
                    if (a['start'],a['end'])!=(b['start'],b['end']):raise ValueError('choice endpoint mismatch')
                    start,end=a['start'],a['end']
                    guaranteed=a['guaranteed']&b['guaranteed']
                stage=a['stage']
            elif op=='J':
                children=[add(tree[2],at,depth+1)];a=plans[children[0]]
                pred,entity=tree[1]
                if entity not in a['guaranteed']:raise ValueError('guard not universal')
                stage,start,end=a['stage'],a['start'],a['end'];guaranteed=a['guaranteed']
                atom=f'{pred}({entity})'
            elif op=='AT':
                target=stage_num(tree[1]);children=[add(tree[2],target,depth+1)]
                a=plans[children[0]];stage,start,end=a['stage'],a['start'],a['end']
                guaranteed=a['guaranteed'];meta={'target_stage':target}
            elif op=='MACRO':
                name,args=tree[1:];d=definitions[name];expanded=d['expression']
                for p,v in zip(('a','b','c'),args):expanded=expanded.replace('{'+p+'}',v)
                children=[add(self.parser.parse(expanded),at,depth+1)]
                a=plans[children[0]];stage,start,end=a['stage'],a['start'],a['end']
                guaranteed=a['guaranteed']
                meta={'name':name,'version':d['version'],'definition_sha256':sha(d),
                      'arguments':list(args),'expansion':expanded}
            else:raise ValueError('unknown operator')
            plans[pid]={'op':op,'children':tuple(children),'atom':atom,'meta':meta,
                        'stage':stage,'start':start,'end':end,'guaranteed':guaranteed}
            for child in children:parents[child].add(pid)
            if atom is not None:by_atom[atom].add(pid)
            order.append(pid)
            return pid
        root=add(root_tree,query_stage)
        return {'nodes':plans,'order':order,'parents':parents,'by_atom':by_atom,'root':root,
                'expression':expression,'query_stage':query_stage,'registry_digest':self.registry.digest}

    def _compute(self, pid):
        plan=self.plan['nodes'][pid];op=plan['op']
        children=[self.state[x] for x in plan['children']]
        evidence=copy.deepcopy(self.observations.get(pid))
        if op=='R':
            h=tuple(int(evidence['value']==x) for x in NAMES)
        elif op=='C':
            a,b=children
            h=mul_hist(tuple(a['histogram'][x] for x in NAMES),
                       tuple(b['histogram'][x] for x in NAMES))
        elif op=='CHOICE':
            a,b=children
            h=plus_hist(tuple(a['histogram'][x] for x in NAMES),
                        tuple(b['histogram'][x] for x in NAMES))
        elif op=='J':
            a=children[0];h=with_guard(tuple(a['histogram'][x] for x in NAMES),evidence['value'])
        elif op in ('AT','MACRO'):
            a=children[0];h=tuple(a['histogram'][x] for x in NAMES)
        else:raise ValueError('unsupported node type')
        links=[n['id'] for n in children]
        metadata={'atom':plan['atom']} if op in ('R','J') else plan['meta']
        fingerprint={'op':op,'children':tuple(links),'stage':plan['stage'],
                     'start':plan['start'],'end':plan['end'],'hist':tuple(h),
                     'guaranteed':sorted(plan['guaranteed']),
                     'evidence':evidence,'meta':metadata}
        digest=sha(fingerprint)
        return {'id':digest,'op':op,'children':links,'stage':plan['stage'],
                'start':plan['start'],'end':plan['end'],
                'histogram':dict(zip(NAMES,h)),'witness_count':sum(h),
                'value':hist_value(h),'guaranteed_nodes':sorted(plan['guaranteed']),
                'evidence':evidence,'metadata':copy.deepcopy(metadata)}

    def evaluate(self, expression, ledger, query_stage, knowledge_stage=None):
        self.registry._check_seal()
        if type(ledger) is not EvidenceLedger:raise ValueError('immutable EvidenceLedger required')
        q=stage_num(query_stage);k=stage_num(q if knowledge_stage is None else knowledge_stage)
        previous_root=self.state[self.plan['root']]['id'] if self.plan is not None else None
        previous_value=self.state[self.plan['root']]['value'] if self.plan is not None else None
        if self.plan is None:
            self.plan=self._compile(expression,q)
            self.context=(expression,q,k,self.registry.digest)
            self.ledger=ledger
            dirty=set(self.plan['order']);observed=set();stats={}
            for pid in self.plan['order']:
                node=self.plan['nodes'][pid]
                if node['atom'] is not None:
                    self.observations[pid]=ledger.lookup(node['atom'],node['stage'],k,stats)
                    observed.add(pid)
                self.state[pid]=self._compute(pid)
            mode='COLD'
            new_records=len(ledger.records)
            changed_atoms={r.atom for r in ledger.records}
            changed=set(dirty)
        else:
            if self.context!=(expression,q,k,self.registry.digest):
                raise ValueError('context/version changed: new evaluator required')
            if len(ledger.records)<len(self.ledger.records) or ledger.records[:len(self.ledger.records)]!=self.ledger.records:
                raise ValueError('non-append historical ledger: reuse rejected')
            new_rows=ledger.records[len(self.ledger.records):]
            new_records=len(new_rows)
            stats={};observed=set();changed=set()
            changed_atoms={r.atom for r in new_rows}
            for atom in changed_atoms:
                for pid in self.plan['by_atom'].get(atom,()):
                    observed.add(pid)
                    plan=self.plan['nodes'][pid]
                    selected=ledger.lookup(atom,plan['stage'],k,stats)
                    if selected!=self.observations[pid]:
                        self.observations[pid]=selected
                        changed.add(pid)
            dirty=set(changed)
            frontier=list(changed)
            while frontier:
                pid=frontier.pop()
                for parent in self.plan['parents'].get(pid,()):
                    if parent not in dirty:
                        dirty.add(parent);frontier.append(parent)
            for pid in self.plan['order']:
                if pid in dirty:self.state[pid]=self._compute(pid)
            self.ledger=ledger
            mode='APPEND' if new_rows else 'REPLAY'
        root=self.state[self.plan['root']]
        # Complete output serialization is O(number of graph nodes), even if no semantic
        # nodes were recomputed. It must not be counted as O(1) incremental processing.
        graph={}
        for pid in self.plan['order']:
            node=self.state[pid]
            graph[node['id']]=copy.deepcopy(node)
        result={'value':root['value'],'start':root['start'],'end':root['end'],
                'stage':root['stage'],'witness_count':root['witness_count'],
                'histogram':copy.deepcopy(root['histogram']), 'root_id':root['id'],
                'nodes':graph,'source_expression':expression,
                'ledger_sha256':ledger.digest,'registry_sha256':self.registry.digest,
                'knowledge_stage':k,'contract':'LC-EXP-005-LAZY-WITNESS-0.1',
                'claim_scope':'syntactic paths; evidence claims are not independent observations'}
        receipt={'mode':mode,'before_ledger_sha256':self.receipts[-1]['after_ledger_sha256'] if self.receipts else None,
                 'after_ledger_sha256':ledger.digest,'registry_sha256':self.registry.digest,
                 'expression_sha256':sha(expression),'query_stage':q,'knowledge_stage':k,
                 'new_records':new_records,'changed_atoms':sorted(changed_atoms),
                 'affected_structural_ids':sorted(dirty),
                 'refreshed_lookup_structural_ids':sorted(observed),
                 'changed_lookup_structural_ids':sorted(changed),
                 'previous_root_id':previous_root,'previous_root_value':previous_value,
                 'lookup_calls':stats.get('lookup_calls',0),
                 'candidate_rows_examined':stats.get('candidate_rows_examined',0),
                 'lookup_nodes_refreshed':len(observed),'nodes_recomputed':len(dirty),
                 'nodes_reused':len(self.plan['order'])-len(dirty),
                 'root_id':root['id'],'root_value':root['value'],
                 'semantic_equivalence_claim':'bounded full-result match only'}
        self.last_receipt=copy.deepcopy(receipt)
        self.receipts.append(copy.deepcopy(receipt))
        return result
