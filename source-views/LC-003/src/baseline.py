"""Matched, indexed conventional typed-AST comparator; independently written evaluator.
Uses the identical immutable evidence index and optional equal-footing result memo.
"""
import copy
from legacy_a import RelationalA
from evidence import EvidenceLedger,stage_num
from engine import bind_result

ORD={'F':0,'U':1,'T':2}
BACK=['F','U','T']

class TypedBaseline:
    def __init__(self,registry, cache=False):
        self.registry=registry
        self.parser=RelationalA(registry.get_definitions())
        self.cache=cache
        self.memo={}
        self.ast_cache={}
        self.stats={}
        self.reset_stats()
    def reset_stats(self):
        self.stats={'lookup_calls':0,'candidate_rows_examined':0,'result_cache_hits':0,
                    'result_cache_misses':0,'compiled_expressions':0}
    def evaluate(self,expr,ledger,q,k=None):
        if type(ledger) is not EvidenceLedger:raise ValueError('ledger required')
        q=stage_num(q);k=stage_num(q if k is None else k)
        if expr not in self.ast_cache:
            self.ast_cache[expr]=self.parser.parse(expr)
            self.stats['compiled_expressions']+=1
        def solve(t,at):
            # Direct AST recursion, no DAG interning. Structural hash memo on same evidence context.
            key=(t,at,k,ledger.digest,self.registry.digest)
            if self.cache and key in self.memo:
                self.stats['result_cache_hits']+=1
                return copy.deepcopy(self.memo[key])
            self.stats['result_cache_misses']+=1
            if t.op=='AT':
                result=solve(t.args[1],t.args[0])
            elif t.op=='R':
                a,b=t.args; atom=f'R({a},{b})';obs=ledger.lookup(atom,at,k,self.stats)
                result={'start':a,'end':b,'stage':at,'value':obs['value'],
                        'support':{atom:obs},'links':[atom],'guards':[],'nodes':[a,b]}
            elif t.op=='C':
                l=solve(t.args[0],at);r=solve(t.args[1],at)
                if l['end']!=r['start'] or l['stage']!=r['stage']:
                    raise ValueError('incompatible directed path')
                result={'start':l['start'],'end':r['end'],'stage':l['stage'],
                        'value':BACK[min(ORD[l['value']],ORD[r['value']])],
                        'support':{**l['support'],**r['support']},
                        'links':l['links']+r['links'],'guards':l['guards']+r['guards'],
                        'nodes':l['nodes']+r['nodes'][1:]}
            elif t.op=='J':
                cond,path=t.args; result=solve(path,at)
                entity=cond.args[0]
                if entity not in result['nodes']:raise ValueError('unbound guard')
                atom=f'{cond.op}({entity})';obs=ledger.lookup(atom,result['stage'],k,self.stats)
                result['value']=BACK[min(ORD[result['value']],ORD[obs['value']])]
                result['support'][atom]=obs;result['guards']=[atom]+result['guards']
            else:raise ValueError('invalid typed expression')
            if self.cache:self.memo[key]=copy.deepcopy(result)
            return copy.deepcopy(result)
        return bind_result(solve(self.ast_cache[expr],q),expr,self.registry,ledger,k,'TYPED_AST_BASELINE')
