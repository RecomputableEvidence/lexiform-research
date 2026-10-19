"""LC007 revision-addressable audit output over LC006 compiled relational DAG.
The computation is inherited, not claimed novel. Audit handles reference immutable
revision records; full graph construction is explicit, not done per append.
"""
import bisect,copy,secrets
from dataclasses import dataclass
from collections import defaultdict
from reuse import BoundReuse
from evidence import sha,stage_num
from lazy_graph import meet
from persistent_ledger import LedgerSnapshot

@dataclass(frozen=True)
class AuditHandle:
    engine_id:str
    revision:int
    root_id:str
    ledger_digest:str
    expression:str
    query_stage:int
    knowledge_stage:int
    registry_digest:str

class SelectiveAudit(BoundReuse):
    def __init__(self,registry,parser='A'):
        super().__init__(registry,parser)
        self._engine_id=secrets.token_hex(16)
        self._versions=defaultdict(list)
        self._issued={}
        self._revision=-1
        self.last_receipt=None
    def _node_at(self,pid,rev):
        entries=self._versions[pid]
        idx=bisect.bisect_right([x[0] for x in entries],rev)-1
        if idx<0:raise ValueError('node not available in revision')
        return entries[idx][1]  # internally immutable by convention, never exposed raw
    def _validate_handle(self,handle):
        if type(handle) is not AuditHandle or handle.engine_id!=self._engine_id or self._issued.get(handle.revision)!=handle:
            raise ValueError('invalid or unknown audit handle')
    def evaluate(self,expression,ledger,query_stage,knowledge_stage=None):
        self.registry._check_seal()
        if type(ledger) is not LedgerSnapshot:raise ValueError('LC007 ledger snapshot required')
        ledger._check()
        q=stage_num(query_stage);k=stage_num(q if knowledge_stage is None else knowledge_stage)
        old_root=self.state[self.plan['root']]['id'] if self.plan is not None else None
        if self.plan is None:
            plan=self._compile(expression,q)
            self.plan=plan;self.context=(expression,q,k,self.registry.digest)
            self.ledger=ledger
            dirty=set(plan['order']);selected=set();changed=set(dirty);stats={}
            for pid in plan['order']:
                node=plan['nodes'][pid]
                if node['atom'] is not None:
                    self.observations[pid]=ledger.lookup(node['atom'],node['stage'],k,stats)
                    selected.add(pid)
                self.state[pid]=self._compute(pid)
            changed_atoms={r.atom for r in ledger._store._records[:ledger.length]}
            delta_count=ledger.length;mode='COLD'
        else:
            if self.context!=(expression,q,k,self.registry.digest):raise ValueError('changed expression / context / definitions')
            delta=ledger.appended_since(self.ledger)
            delta_count=len(delta);stats={};selected=set();changed=set()
            changed_atoms={r.atom for r in delta}
            for atom in changed_atoms:
                for pid in self.plan['by_atom'].get(atom,()):
                    selected.add(pid)
                    n=self.plan['nodes'][pid]
                    ev=ledger.lookup(atom,n['stage'],k,stats)
                    if ev!=self.observations[pid]:
                        self.observations[pid]=ev;changed.add(pid)
            dirty=set(changed);stack=list(changed)
            while stack:
                child=stack.pop()
                for p in self.plan['parents'].get(child,()):
                    if p not in dirty:dirty.add(p);stack.append(p)
            for pid in self.plan['order']:
                if pid in dirty:self.state[pid]=self._compute(pid)
            self.ledger=ledger
            mode='APPEND' if delta else 'REPLAY'
        rev=self._revision+1
        for pid in self.plan['order']:
            if pid in dirty:self._versions[pid].append((rev,copy.deepcopy(self.state[pid])))
        self._revision=rev
        root=self.state[self.plan['root']]
        handle=AuditHandle(self._engine_id,rev,root['id'],ledger.digest,expression,q,k,self.registry.digest)
        self._issued[rev]=handle
        receipt={'revision':rev,'mode':mode,'ledger_commitment':ledger.digest,
                 'ledger_length':ledger.length,'appended_records':delta_count,
                 'changed_atoms':sorted(changed_atoms),'lookups':stats.get('lookup_calls',0),
                 'nodes_recomputed':len(dirty),'nodes_reused':len(self.plan['order'])-len(dirty),
                 'root_id':root['id'],'root_value':root['value'],
                 'audit_mode':'ROOT_ONLY','full_graph_serialized':False,
                 'claim_scope':'trusted in-process append chain; witness-derived paths'}
        self.last_receipt=copy.deepcopy(receipt)
        self.receipts.append(copy.deepcopy(receipt))
        return {'value':root['value'],'root_id':root['id'],'start':root['start'],'end':root['end'],
                'stage':root['stage'],'histogram':copy.deepcopy(root['histogram']),
                'witness_count':root['witness_count'],'ledger_sha256':ledger.digest,
                'registry_sha256':self.registry.digest,'source_expression':expression,
                'knowledge_stage':k,'audit_handle':handle}
    def full_graph(self,handle):
        self._validate_handle(handle)
        nodes={}
        for pid in self.plan['order']:
            node=self._node_at(pid,handle.revision)
            nodes[node['id']]=copy.deepcopy(node)
        root=nodes[handle.root_id]
        return {'value':root['value'],'start':root['start'],'end':root['end'],
                'stage':root['stage'],'witness_count':root['witness_count'],
                'histogram':copy.deepcopy(root['histogram']),'root_id':handle.root_id,
                'nodes':nodes,'source_expression':handle.expression,
                'ledger_sha256':handle.ledger_digest,'registry_sha256':handle.registry_digest,
                'knowledge_stage':handle.knowledge_stage,
                'contract':'LC-EXP-005-LAZY-WITNESS-0.1',
                'claim_scope':'syntactic paths; evidence claims are not independent observations'}
    def witness(self,handle,index):
        self._validate_handle(handle)
        root=self._node_at(self.plan['root'],handle.revision)
        if type(index) is not int or not 0<=index<root['witness_count']:
            raise ValueError('invalid witness index')
        def at(pid):return self._node_at(pid,handle.revision)
        def walk(pid,n):
            node=at(pid);op=node['op'];children=self.plan['nodes'][pid]['children']
            if op=='R':
                return {'nodes':[node['start'],node['end']],'atoms':[node['metadata']['atom']],
                        'evidence':[{'atom':node['metadata']['atom'],'lookup':copy.deepcopy(node['evidence'])}],
                        'decisions':[],'lineage':[],'value':node['value']}
            if op=='CHOICE':
                left_count=at(children[0])['witness_count'];side=0 if n<left_count else 1
                result=walk(children[side],n if side==0 else n-left_count)
                result['decisions'].insert(0,{'choice_node':node['id'],'arm':side})
                return result
            if op=='C':
                right_count=at(children[1])['witness_count']
                left=walk(children[0],n//right_count);right=walk(children[1],n%right_count)
                return {'nodes':left['nodes']+right['nodes'][1:],
                        'atoms':left['atoms']+right['atoms'],
                        'evidence':left['evidence']+right['evidence'],
                        'decisions':left['decisions']+right['decisions'],
                        'lineage':left['lineage']+right['lineage'],
                        'value':meet(left['value'],right['value'])}
            if op in ('J','AT','MACRO'):
                result=walk(children[0],n)
                if op=='MACRO':result['lineage'].insert(0,copy.deepcopy(node['metadata']))
                if op=='J':
                    atom=node['metadata']['atom']
                    result['evidence'].append({'atom':atom,'lookup':copy.deepcopy(node['evidence'])})
                    result['atoms'].append(atom);result['value']=meet(result['value'],node['evidence']['value'])
                return result
            raise ValueError('unexpected node')
        result=walk(self.plan['root'],index)
        result['index']=index
        result['evidence_ids']=[eid for row in result['evidence'] for eid in row['lookup']['evidence_ids']]
        result['ledger_commitment']=handle.ledger_digest
        result['root_id']=handle.root_id
        return result
