"""LC-EXP-003: typed DAG evaluator (A) and independent stack interpreter (B).
Both share a validated immutable evidence index; that is a declared common dependency.
"""
import copy
from legacy_a import RelationalA, Term
from legacy_b import RelationalB
from evidence import SEMANTICS_VERSION, EvidenceLedger, sha, stage_num
from registry import FrozenDefinitions

TRUTH={'F':-1,'U':0,'T':1}
INVERSE={v:k for k,v in TRUTH.items()}

def meet(a,b):return INVERSE[min(TRUTH[a],TRUTH[b])]

def projection(row):
    return {key:copy.deepcopy(row[key]) for key in ('start','end','stage','value','support','links','guards','nodes')}

def bind_result(row, expr, registry, ledger, knowledge_stage, mechanism):
    ret=copy.deepcopy(row)
    ret['source_expression']=expr
    ret['definition_lineage']=registry.invocation_lineage(expr)
    ret['definition_registry_sha256']=registry.digest
    ret['evidence_ledger_sha256']=ledger.digest
    ret['semantic_contract']=SEMANTICS_VERSION
    ret['knowledge_stage']=knowledge_stage
    ret['mechanism']=mechanism
    ret['semantic_projection_sha256']=sha(projection(row))
    return ret

class EngineA:
    """Hash-consed typed DAG with dependency/context-bound result memoization."""
    def __init__(self, registry: FrozenDefinitions, use_result_cache=True):
        self.registry=registry
        self.parser=RelationalA(registry.get_definitions())
        self.use_result_cache=use_result_cache
        self.nodes={}
        self.expr_cache={}
        self.result_cache={}
        self.stats={}
        self.reset_stats()

    def reset_stats(self):
        self.stats={'lookup_calls':0,'candidate_rows_examined':0,'result_cache_hits':0,
                    'result_cache_misses':0,'compiled_expressions':0,'graph_nodes_created':0}

    def intern(self, term):
        parts=tuple(self.intern(c) if isinstance(c,Term) else c for c in term.args)
        key=(term.op,parts)
        if key not in self.nodes:
            self.nodes[key]=key
            self.stats['graph_nodes_created']+=1
        return self.nodes[key]

    def compile(self, expr):
        if expr not in self.expr_cache:
            self.expr_cache[expr]=self.intern(self.parser.parse(expr))
            self.stats['compiled_expressions']+=1
        return self.expr_cache[expr]

    def _eval(self,node,ledger,q,k):
        key=(node,ledger.digest,q,k,self.registry.digest,SEMANTICS_VERSION)
        if self.use_result_cache and key in self.result_cache:
            self.stats['result_cache_hits']+=1
            return copy.deepcopy(self.result_cache[key])
        self.stats['result_cache_misses']+=1
        op,children=node
        if op=='AT':
            result=self._eval(children[1],ledger,children[0],k)
        elif op=='R':
            left,right=children;atom=f'R({left},{right})'
            observation=ledger.lookup(atom,q,k,self.stats)
            result={'start':left,'end':right,'stage':q,'value':observation['value'],
                    'support':{atom:observation},'links':[atom],'guards':[],'nodes':[left,right]}
        elif op=='C':
            left=self._eval(children[0],ledger,q,k)
            right=self._eval(children[1],ledger,q,k)
            if left['end'] != right['start']:raise ValueError('noncontiguous directed links')
            if left['stage'] != right['stage']:raise ValueError('mixed query stages')
            result={'start':left['start'],'end':right['end'],'stage':left['stage'],
                    'value':meet(left['value'],right['value']),
                    'support':{**left['support'],**right['support']},
                    'links':left['links']+right['links'],
                    'guards':left['guards']+right['guards'],
                    'nodes':left['nodes']+right['nodes'][1:]}
        elif op=='J':
            guard,path=children
            result=self._eval(path,ledger,q,k)
            if guard[1][0] not in result['nodes']:raise ValueError('unbound guard entity')
            atom=f'{guard[0]}({guard[1][0]})'
            observation=ledger.lookup(atom,result['stage'],k,self.stats)
            result['value']=meet(result['value'],observation['value'])
            result['support'][atom]=observation
            result['guards']=[atom]+result['guards']
        else:
            raise ValueError('unexpected compiled node')
        if self.use_result_cache:self.result_cache[key]=copy.deepcopy(result)
        return copy.deepcopy(result)

    def evaluate(self,expr,ledger,q,k=None):
        if type(ledger) is not EvidenceLedger:raise ValueError('ledger object required')
        q=stage_num(q);k=stage_num(q if k is None else k)
        node=self.compile(expr)
        value=self._eval(node,ledger,q,k)
        return bind_result(value,expr,self.registry,ledger,k,'TYPED_DAG_A')

class EngineB:
    """Stack bytecode interpreter; no A evaluator, AST interning, or result memoization."""
    def __init__(self, registry:FrozenDefinitions):
        self.registry=registry
        self.compiler=RelationalB(registry.get_definitions())
        self.stats={}
        self.reset_stats()
    def reset_stats(self):
        self.stats={'lookup_calls':0,'candidate_rows_examined':0,'instructions':0,'compiled_expressions':0}
    def evaluate(self,expr,ledger,q,k=None):
        if type(ledger) is not EvidenceLedger:raise ValueError('ledger object required')
        q=stage_num(q);k=stage_num(q if k is None else k)
        program=self.compiler.compile(expr)
        self.stats['compiled_expressions']+=1
        stack=[];stages=[q]
        for inst in program:
            self.stats['instructions']+=1
            op=inst[0]
            if op=='enter':stages.append(inst[1]);continue
            if op=='exit':
                if len(stages)<2:raise ValueError('unmatched stage exit')
                stages.pop();continue
            if op=='loadlink':
                _,a,b=inst;atom=f'R({a},{b})'
                rec=ledger.lookup(atom,stages[-1],k,self.stats)
                stack.append({'start':a,'end':b,'stage':stages[-1],
                              'value':rec['value'],'support':{atom:rec},
                              'links':[atom],'guards':[],'nodes':[a,b]})
            elif op=='chain':
                right=stack.pop();left=stack.pop()
                if left['end']!=right['start']:raise ValueError('noncontiguous directed links')
                if left['stage']!=right['stage']:raise ValueError('mixed query stages')
                stack.append({'start':left['start'],'end':right['end'],'stage':left['stage'],
                              'value':meet(left['value'],right['value']),
                              'support':{**left['support'],**right['support']},
                              'links':left['links']+right['links'],
                              'guards':left['guards']+right['guards'],
                              'nodes':left['nodes']+right['nodes'][1:]})
            elif op=='guard':
                _,pred,entity=inst;path=stack.pop()
                if entity not in path['nodes']:raise ValueError('unbound guard entity')
                atom=f'{pred}({entity})';rec=ledger.lookup(atom,path['stage'],k,self.stats)
                path['value']=meet(path['value'],rec['value'])
                path['support'][atom]=rec
                path['guards'].insert(0,atom)
                stack.append(path)
            else:raise ValueError('unknown VM instruction')
        if len(stack)!=1 or len(stages)!=1:raise ValueError('unfinished VM')
        return bind_result(stack[0],expr,self.registry,ledger,k,'STACK_VM_B')

def verified_pair(expr,ledger,query_stage,knowledge_stage,registry):
    a=EngineA(registry).evaluate(expr,ledger,query_stage,knowledge_stage)
    b=EngineB(registry).evaluate(expr,ledger,query_stage,knowledge_stage)
    if projection(a)!=projection(b):raise ValueError('interpreters disagree')
    return a,b
