"""LC-EXP-005: context-bound lazy witness DAG. Not a novel reasoning theorem.

Histograms count syntactic derivation paths, NOT independent physical evidence.
Witness identity is a sequence of ordered branch selections through this frozen DAG.
"""
import copy
from grammar_a import ParserA
from evidence import EvidenceLedger,sha,stage_num

ORDER={'F':0,'U':1,'T':2}
NAMES=('F','U','T')
def meet(a,b):return NAMES[min(ORDER[a],ORDER[b])]
def plus_hist(a,b):return tuple(x+y for x,y in zip(a,b))
def mul_hist(a,b):
    h=[0,0,0]
    for i in range(3):
        for j in range(3):h[min(i,j)]+=a[i]*b[j]
    return tuple(h)
def with_guard(h,v):
    out=[0,0,0]
    for i,n in enumerate(h):out[min(i,ORDER[v])]+=n
    return tuple(out)
def hist_value(h):return next(NAMES[i] for i in (2,1,0) if h[i])

class LazyGraph:
    def __init__(self,registry):
        self.registry=registry;self.parser=ParserA();self.result_cache={};self.stats={}
    def reset_stats(self):self.stats={'lookup_calls':0,'candidate_rows_examined':0,'cache_hits':0,'cache_misses':0,'nodes_created':0}
    def evaluate(self,expr,ledger,query_stage,knowledge_stage=None):
        self.registry._check_seal()
        if type(ledger) is not EvidenceLedger:raise ValueError('invalid ledger')
        q=stage_num(query_stage);k=stage_num(q if knowledge_stage is None else knowledge_stage)
        normalized=''.join(expr.split());cache_key=(normalized,ledger.digest,q,k,self.registry.digest)
        if not self.stats:self.reset_stats()
        if cache_key in self.result_cache:
            self.stats['cache_hits']+=1
            return copy.deepcopy(self.result_cache[cache_key])
        self.stats['cache_misses']+=1
        syntax=self.parser.parse(normalized)
        definitions=self.registry.get_definitions()
        nodes={};intern={};memo={};active=set()
        def mk(op,children,stage,start,end,h,guaranteed,evidence=None,meta=None):
            h=tuple(h);children=tuple(children)
            fingerprint={'op':op,'children':children,'stage':stage,'start':start,'end':end,
                         'hist':h,'guaranteed':sorted(guaranteed),'evidence':evidence,'meta':meta}
            sig=sha(fingerprint)
            if sig not in nodes:
                nodes[sig]={'id':sig,'op':op,'children':list(children),'stage':stage,
                            'start':start,'end':end,'histogram':dict(zip(NAMES,h)),
                            'witness_count':sum(h),'value':hist_value(h),
                            'guaranteed_nodes':sorted(guaranteed),'evidence':copy.deepcopy(evidence),
                            'metadata':copy.deepcopy(meta)}
                self.stats['nodes_created']+=1
            return sig
        def walk(t,at,depth=0):
            if depth>192:raise ValueError('evaluation resource bound')
            key=(t,at)
            if key in memo:return memo[key]
            if key in active:raise ValueError('recursive macro')
            active.add(key)
            op=t[0]
            if op=='R':
                a,b=t[1:];atom=f'R({a},{b})'
                ev=ledger.lookup(atom,at,k,self.stats)
                h=tuple(int(x==ev['value']) for x in NAMES)
                node=mk('R',(),at,a,b,h,{a,b},ev,{'atom':atom})
            elif op=='C':
                l=nodes[walk(t[1],at,depth+1)];r=nodes[walk(t[2],at,depth+1)]
                if l['end']!=r['start'] or l['stage']!=r['stage']:raise ValueError('incompatible serial endpoints/stages')
                h=mul_hist(tuple(l['histogram'][x] for x in NAMES),tuple(r['histogram'][x] for x in NAMES))
                node=mk('C',(l['id'],r['id']),l['stage'],l['start'],r['end'],h,
                        set(l['guaranteed_nodes'])|set(r['guaranteed_nodes']))
            elif op=='CHOICE':
                l=nodes[walk(t[1],at,depth+1)];r=nodes[walk(t[2],at,depth+1)]
                if (l['start'],l['end'],l['stage'])!=(r['start'],r['end'],r['stage']):
                    raise ValueError('incompatible choice endpoints/stages')
                h=plus_hist(tuple(l['histogram'][x] for x in NAMES),tuple(r['histogram'][x] for x in NAMES))
                node=mk('CHOICE',(l['id'],r['id']),l['stage'],l['start'],l['end'],h,
                        set(l['guaranteed_nodes'])&set(r['guaranteed_nodes']))
            elif op=='J':
                pred,entity=t[1]
                p=nodes[walk(t[2],at,depth+1)]
                if entity not in p['guaranteed_nodes']:raise ValueError('guard entity absent in at least one possible witness')
                atom=f'{pred}({entity})';ev=ledger.lookup(atom,p['stage'],k,self.stats)
                h=with_guard(tuple(p['histogram'][x] for x in NAMES),ev['value'])
                node=mk('J',(p['id'],),p['stage'],p['start'],p['end'],h,
                        p['guaranteed_nodes'],ev,{'atom':atom})
            elif op=='AT':
                stage=stage_num(t[1]);p=nodes[walk(t[2],stage,depth+1)]
                node=mk('AT',(p['id'],),p['stage'],p['start'],p['end'],
                        tuple(p['histogram'][x] for x in NAMES),p['guaranteed_nodes'],meta={'target_stage':stage})
            elif op=='MACRO':
                name,args=t[1:];d=definitions[name]
                expansion=d['expression']
                for param,arg in zip(('a','b','c'),args):expansion=expansion.replace('{'+param+'}',arg)
                p=nodes[walk(self.parser.parse(expansion),at,depth+1)]
                node=mk('MACRO',(p['id'],),p['stage'],p['start'],p['end'],
                        tuple(p['histogram'][x] for x in NAMES),p['guaranteed_nodes'],
                        meta={'name':name,'version':d['version'],'definition_sha256':sha(d),
                              'arguments':list(args),'expansion':expansion})
            else:raise ValueError('invalid operator')
            active.remove(key);memo[key]=node
            return node
        root=walk(syntax,q)
        n=nodes[root]
        result={'value':n['value'],'start':n['start'],'end':n['end'],'stage':n['stage'],
                'witness_count':n['witness_count'],'histogram':copy.deepcopy(n['histogram']),
                'root_id':root,'nodes':nodes,'source_expression':expr,
                'ledger_sha256':ledger.digest,'registry_sha256':self.registry.digest,
                'knowledge_stage':k,'contract':'LC-EXP-005-LAZY-WITNESS-0.1',
                'claim_scope':'syntactic paths; evidence claims are not independent observations'}
        self.result_cache[cache_key]=copy.deepcopy(result)
        return copy.deepcopy(result)

def select_witness(result,index):
    """Direct index selection; no full cartesian enumeration even for 2^128 paths."""
    if type(index) is not int or not 0<=index<result['witness_count']:raise ValueError('invalid witness index')
    nodes=result['nodes']
    def solve(node_id,n):
        node=nodes[node_id];op=node['op'];children=node['children']
        if op=='R':
            assert n==0
            return {'nodes':[node['start'],node['end']],'atoms':[node['metadata']['atom']],
                    'evidence':[{'atom':node['metadata']['atom'],'lookup':copy.deepcopy(node['evidence'])}],
                    'decisions':[],'lineage':[],'value':node['value']}
        if op=='CHOICE':
            a=nodes[children[0]]['witness_count'];side=0 if n<a else 1
            w=solve(children[side],n if side==0 else n-a)
            w['decisions'].insert(0,{'choice_node':node_id,'arm':side})
            return w
        if op=='C':
            right_count=nodes[children[1]]['witness_count']
            a=solve(children[0],n//right_count);b=solve(children[1],n%right_count)
            return {'nodes':a['nodes']+b['nodes'][1:],'atoms':a['atoms']+b['atoms'],
                    'evidence':a['evidence']+b['evidence'],
                    'decisions':a['decisions']+b['decisions'],'lineage':a['lineage']+b['lineage'],
                    'value':meet(a['value'],b['value'])}
        if op in ('AT','MACRO','J'):
            w=solve(children[0],n)
            if op=='MACRO':w['lineage'].insert(0,copy.deepcopy(node['metadata']))
            if op=='J':
                atom=node['metadata']['atom'];w['evidence'].append({'atom':atom,'lookup':copy.deepcopy(node['evidence'])})
                w['atoms'].append(atom);w['value']=meet(w['value'],node['evidence']['value'])
            return w
        raise ValueError('invalid DAG node')
    w=solve(result['root_id'],index)
    w['index']=index
    w['evidence_ids']=[eid for row in w['evidence'] for eid in row['lookup']['evidence_ids']]
    return w
