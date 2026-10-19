"""Matched conventional typed dynamic-programming control + small-case eager oracle.
Uses its own token parser and algebra. Shares LC-003 evidence lookup, as declared.
"""
import copy
from grammar_b import ParserB
from evidence import EvidenceLedger,sha,stage_num
ORDER={'F':0,'U':1,'T':2};TRUTH=('F','U','T')
def small(a,b):return min((a,b),key=ORDER.get)
class TypedDP:
    def __init__(self,registry):self.registry=registry;self.parser=ParserB();self.cache={};self.stats={}
    def reset_stats(self):self.stats={'lookup_calls':0,'candidate_rows_examined':0,'cache_hits':0,'cache_misses':0,'nodes_visited':0}
    def evaluate(self,expr,ledger,q,k=None):
        self.registry._check_seal()
        if type(ledger) is not EvidenceLedger:raise ValueError('ledger required')
        q=stage_num(q);k=stage_num(q if k is None else k)
        key=(''.join(expr.split()),ledger.digest,q,k,self.registry.digest)
        if not self.stats:self.reset_stats()
        if key in self.cache:
            self.stats['cache_hits']+=1
            return copy.deepcopy(self.cache[key])
        self.stats['cache_misses']+=1
        tree=self.parser.parse(expr);defs=self.registry.get_definitions();seen={}
        def calc(t,stage,depth=0):
            self.stats['nodes_visited']+=1
            if depth>192:raise ValueError('depth cap')
            key=(t,stage)
            if key in seen:return seen[key]
            op=t[0]
            if op=='R':
                a,b=t[1:];ev=ledger.lookup(f'R({a},{b})',stage,k,self.stats)
                counts={v:int(v==ev['value']) for v in TRUTH};result=(a,b,stage,counts,frozenset((a,b)))
            elif op in ('C','CHOICE'):
                x=calc(t[1],stage,depth+1);y=calc(t[2],stage,depth+1)
                if x[2]!=y[2]:raise ValueError('temporal incompatibility')
                if op=='C':
                    if x[1]!=y[0]:raise ValueError('endpoint mismatch')
                    counts={v:0 for v in TRUTH}
                    for xv,xn in x[3].items():
                        for yv,yn in y[3].items():counts[small(xv,yv)]+=xn*yn
                    result=(x[0],y[1],x[2],counts,x[4]|y[4])
                else:
                    if (x[0],x[1])!=(y[0],y[1]):raise ValueError('choice mismatch')
                    counts={v:x[3][v]+y[3][v] for v in TRUTH}
                    result=(x[0],x[1],x[2],counts,x[4]&y[4])
            elif op=='J':
                pred,entity=t[1];path=calc(t[2],stage,depth+1)
                if entity not in path[4]:raise ValueError('nonuniversal guard')
                ev=ledger.lookup(f'{pred}({entity})',path[2],k,self.stats)
                counts={v:0 for v in TRUTH}
                for v,n in path[3].items():counts[small(v,ev['value'])]+=n
                result=(*path[:3],counts,path[4])
            elif op=='AT':
                result=calc(t[2],stage_num(t[1]),depth+1)
            elif op=='MACRO':
                name,args=t[1:];d=defs[name];expr2=d['expression']
                for param,arg in zip(('a','b','c'),args):expr2=expr2.replace('{'+param+'}',arg)
                result=calc(self.parser.parse(expr2),stage,depth+1)
            else:raise ValueError('invalid operator')
            seen[key]=result
            return result
        a,b,stage,h,_=calc(tree,q)
        result={'start':a,'end':b,'stage':stage,'histogram':h,
                'value':next(v for v in ('T','U','F') if h[v]),'witness_count':sum(h.values()),
                'ledger_sha256':ledger.digest,'registry_sha256':self.registry.digest,
                'source_expression':expr,'engine':'CONVENTIONAL_TYPED_DP'}
        self.cache[key]=copy.deepcopy(result)
        return copy.deepcopy(result)

class EagerOracle:
    """Enumerate each branch path, deliberately unoptimized; max 4096 witnesses."""
    def __init__(self,registry):self.registry=registry;self.parser=ParserB()
    def evaluate(self,expr,ledger,q,k=None,cap=4096):
        self.registry._check_seal()
        if type(ledger) is not EvidenceLedger:raise ValueError('ledger required')
        q=stage_num(q);k=stage_num(q if k is None else k)
        defs=self.registry.get_definitions();tree=self.parser.parse(expr)
        def solve(t,stage,depth):
            if depth>96:raise ValueError('depth')
            op=t[0]
            if op=='R':
                a,b=t[1:];v=ledger.lookup(f'R({a},{b})',stage,k)['value']
                return [(a,b,stage,v,(a,b),())]
            if op in ('C','CHOICE'):
                lhs=solve(t[1],stage,depth+1);rhs=solve(t[2],stage,depth+1)
                if not lhs or not rhs:raise ValueError('empty')
                if op=='CHOICE':
                    if {(x[0],x[1],x[2]) for x in lhs+rhs}.__len__()!=1:raise ValueError('choice endpoints')
                    if len(lhs)+len(rhs)>cap:raise OverflowError('eager cap')
                    return lhs+rhs
                if any(x[1]!=y[0] or x[2]!=y[2] for x in lhs for y in rhs):raise ValueError('serial endpoints')
                if len(lhs)*len(rhs)>cap:raise OverflowError('eager cap')
                return [(a[0],b[1],a[2],small(a[3],b[3]),a[4]+b[4][1:],a[5]+b[5]) for a in lhs for b in rhs]
            if op=='J':
                pred,entity=t[1];paths=solve(t[2],stage,depth+1)
                if any(entity not in p[4] for p in paths):raise ValueError('guard not universal')
                ev=ledger.lookup(f'{pred}({entity})',paths[0][2],k)['value']
                return [(p[0],p[1],p[2],small(p[3],ev),p[4],p[5]+(f'{pred}({entity})',)) for p in paths]
            if op=='AT':return solve(t[2],stage_num(t[1]),depth+1)
            if op=='MACRO':
                name,args=t[1:];d=defs[name];s=d['expression']
                for a,b in zip(('a','b','c'),args):s=s.replace('{'+a+'}',b)
                return solve(self.parser.parse(s),stage,depth+1)
            raise ValueError('unknown')
        paths=solve(tree,q,0)
        h={v:sum(p[3]==v for p in paths) for v in TRUTH}
        return {'start':paths[0][0],'end':paths[0][1],'stage':paths[0][2],
                'value':next(v for v in ('T','U','F') if h[v]),'histogram':h,'witness_count':len(paths),
                'paths':[{'nodes':list(p[4]),'value':p[3],'guards':list(p[5])} for p in paths]}
