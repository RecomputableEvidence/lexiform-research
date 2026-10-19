"""Audit-equivalent conventional typed stack evaluator using ParserB, not ParserA.
Produces the same complete witness graph contract and provenance as LazyGraph.
This tests whether the technique is specific to a 'lexiconic' notation (it isn't).
"""
import copy
from grammar_b import ParserB
from evidence import EvidenceLedger,sha,stage_num
from typed_controls import ORDER,TRUTH,small

class TypedAudit:
    def __init__(self,registry):self.registry=registry;self.parser=ParserB();self.cache={};self.stats={}
    def reset_stats(self):self.stats={'lookup_calls':0,'candidate_rows_examined':0,'cache_hits':0,'cache_misses':0,'instructions':0,'nodes_created':0}
    def evaluate(self,expr,ledger,query_stage,knowledge_stage=None):
        self.registry._check_seal()
        if type(ledger) is not EvidenceLedger:raise ValueError('ledger required')
        q=stage_num(query_stage);k=stage_num(q if knowledge_stage is None else knowledge_stage)
        key=(''.join(expr.split()),ledger.digest,q,k,self.registry.digest)
        if not self.stats:self.reset_stats()
        if key in self.cache:
            self.stats['cache_hits']+=1
            return copy.deepcopy(self.cache[key])
        self.stats['cache_misses']+=1
        defs=self.registry.get_definitions();root=self.parser.parse(expr)
        program=[]
        def emit(t,stage,depth=0):
            if depth>192:raise ValueError('instruction depth bound')
            op=t[0]
            if op=='R':program.append(('load',t[1],t[2],stage))
            elif op in ('C','CHOICE'):
                emit(t[1],stage,depth+1);emit(t[2],stage,depth+1);program.append((op,))
            elif op=='J':
                emit(t[2],stage,depth+1);program.append(('guard',*t[1]))
            elif op=='AT':
                emit(t[2],stage_num(t[1]),depth+1);program.append(('at',t[1]))
            elif op=='MACRO':
                name,args=t[1:];d=defs[name];source=d['expression']
                for p,v in zip(('a','b','c'),args):source=source.replace('{'+p+'}',v)
                emit(self.parser.parse(source),stage,depth+1)
                program.append(('macro',{'name':name,'version':d['version'],
                    'definition_sha256':sha(d),'arguments':list(args),'expansion':source}))
            else:raise ValueError('unknown descriptor')
        emit(root,q)
        nodes={};stack=[]
        def put(op,links,stage,start,end,h,guaranteed,observation=None,meta=None):
            vec=tuple(h[x] for x in TRUTH)
            fingerprint={'op':op,'children':list(links),'stage':stage,'start':start,'end':end,
                         'hist':vec,'guaranteed':sorted(guaranteed),'evidence':observation,'meta':meta}
            digest=sha(fingerprint)
            if digest not in nodes:
                nodes[digest]={'id':digest,'op':op,'children':list(links),'stage':stage,
                               'start':start,'end':end,'histogram':copy.deepcopy(h),'witness_count':sum(vec),
                               'value':next(x for x in ('T','U','F') if h[x]),'guaranteed_nodes':sorted(guaranteed),
                               'evidence':copy.deepcopy(observation),'metadata':copy.deepcopy(meta)}
                self.stats['nodes_created']+=1
            stack.append(digest)
        for instruction in program:
            self.stats['instructions']+=1
            op=instruction[0]
            if op=='load':
                _,a,b,s=instruction;atom=f'R({a},{b})';ev=ledger.lookup(atom,s,k,self.stats)
                hist={x:int(ev['value']==x) for x in TRUTH}
                put('R',[],s,a,b,hist,{a,b},ev,{'atom':atom})
            elif op in ('C','CHOICE'):
                if len(stack)<2:raise ValueError('bytecode underflow')
                right_id=stack.pop();left_id=stack.pop();l=nodes[left_id];r=nodes[right_id]
                if l['stage']!=r['stage']:raise ValueError('stage mismatch')
                if op=='CHOICE':
                    if (l['start'],l['end'])!=(r['start'],r['end']):raise ValueError('endpoint mismatch')
                    h={x:l['histogram'][x]+r['histogram'][x] for x in TRUTH}
                    guaranteed=set(l['guaranteed_nodes'])&set(r['guaranteed_nodes'])
                    s,e=l['start'],l['end']
                else:
                    if l['end']!=r['start']:raise ValueError('serial discontinuity')
                    h=dict.fromkeys(TRUTH,0)
                    for lv,count_l in l['histogram'].items():
                        for rv,count_r in r['histogram'].items():h[small(lv,rv)]+=count_l*count_r
                    guaranteed=set(l['guaranteed_nodes'])|set(r['guaranteed_nodes'])
                    s,e=l['start'],r['end']
                put(op,(left_id,right_id),l['stage'],s,e,h,guaranteed)
            elif op=='guard':
                if not stack:raise ValueError('bytecode underflow')
                _,pred,entity=instruction;child_id=stack.pop();n=nodes[child_id]
                if entity not in n['guaranteed_nodes']:raise ValueError('guard not universal')
                atom=f'{pred}({entity})';ev=ledger.lookup(atom,n['stage'],k,self.stats)
                h=dict.fromkeys(TRUTH,0)
                for x,count in n['histogram'].items():h[small(x,ev['value'])]+=count
                put('J',(child_id,),n['stage'],n['start'],n['end'],h,n['guaranteed_nodes'],ev,{'atom':atom})
            elif op in ('at','macro'):
                if not stack:raise ValueError('bytecode underflow')
                child_id=stack.pop();n=nodes[child_id]
                meta={'target_stage':instruction[1]} if op=='at' else instruction[1]
                put('AT' if op=='at' else 'MACRO',(child_id,),n['stage'],n['start'],n['end'],
                    n['histogram'],n['guaranteed_nodes'],None,meta)
            else:raise ValueError('unknown VM opcode')
        if len(stack)!=1:raise ValueError('invalid bytecode final stack')
        root_id=stack[0];n=nodes[root_id]
        result={'value':n['value'],'start':n['start'],'end':n['end'],'stage':n['stage'],
                'witness_count':n['witness_count'],'histogram':copy.deepcopy(n['histogram']),
                'root_id':root_id,'nodes':nodes,'source_expression':expr,
                'ledger_sha256':ledger.digest,'registry_sha256':self.registry.digest,
                'knowledge_stage':k,'contract':'LC-EXP-005-LAZY-WITNESS-0.1',
                'claim_scope':'syntactic paths; evidence claims are not independent observations'}
        self.cache[key]=copy.deepcopy(result)
        return copy.deepcopy(result)
