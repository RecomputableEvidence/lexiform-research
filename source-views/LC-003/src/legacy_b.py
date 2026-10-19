"""REL-B: frame-stack parser, stack VM, independent observation selection and projection."""
import copy
import hashlib
import json
import re

class RelationalB:
    def __init__(self,macros):
        self.macros=copy.deepcopy(macros)
        self._seal=self._hash(self.macros)

    @staticmethod
    def _hash(obj):
        return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()

    def compile(self,text,macro_stack=()):
        if self._hash(self.macros)!=self._seal:raise ValueError('macro definition changed')
        if len(macro_stack)>16:raise ValueError('macro depth exceeded')
        toks=[]
        cursor=0
        matcher=re.compile(r'\s*([A-Za-z][A-Za-z0-9]*|[0-9]+|[(),])')
        while cursor<len(text):
            m=matcher.match(text,cursor)
            if m is None:
                if text[cursor:].strip():raise ValueError('malformed expression')
                break
            toks.append(m.group(1))
            cursor=m.end()
        if not toks:raise ValueError('malformed expression')
        frames=[]; top=[]; index=0
        def append(value):
            if frames:
                frame=frames[-1]
                if not frame['expect']:raise ValueError('missing separator')
                frame['args'].append(value)
                frame['expect']=False
            else:
                top.append(value)
        while index<len(toks):
            current=toks[index]
            if index+1<len(toks) and toks[index+1]=='(':
                if len(frames)>48:raise ValueError('nesting too deep')
                if frames and not frames[-1]['expect']:raise ValueError('missing comma')
                frames.append({'name':current,'args':[],'expect':True});index+=2;continue
            if current==',':
                if not frames or frames[-1]['expect']:raise ValueError('unexpected comma')
                frames[-1]['expect']=True;index+=1;continue
            if current==')':
                if not frames:raise ValueError('unmatched close')
                frame=frames.pop()
                if frame['expect']:raise ValueError('empty argument')
                name=frame['name']; args=frame['args']
                entity=lambda value: value[0]=='lit' and bool(re.fullmatch('[A-Z][A-Z0-9]*',value[1]))
                if name in ('R','S','P'):
                    count=2 if name=='R' else 1
                    if len(args)!=count or not all(entity(x) for x in args):raise ValueError('bad atom args')
                    if name=='R':value=('path',[('loadlink',args[0][1],args[1][1])])
                    else:value=('test',name,args[0][1])
                elif name=='C':
                    if len(args)!=2 or any(x[0]!='path' for x in args):raise ValueError('bad chain args')
                    value=('path',args[0][1]+args[1][1]+[('chain',)])
                elif name=='J':
                    if len(args)!=2 or args[0][0]!='test' or args[1][0]!='path':raise ValueError('bad guard args')
                    value=('path',args[1][1]+[('guard',args[0][1],args[0][2])])
                elif name=='AT':
                    if len(args)!=2 or args[0][0]!='lit' or not re.fullmatch(r'(0|[1-9][0-9]*)',args[0][1]) or args[1][0]!='path':raise ValueError('bad stage args')
                    value=('path',[('enter',int(args[0][1]))]+args[1][1]+[('exit',)])
                elif name in ('H1','H2'):
                    if len(args)!=3 or not all(entity(x) for x in args) or name not in self.macros:raise ValueError('bad macro args')
                    if name in macro_stack:raise ValueError('macro loop')
                    expanded=self.macros[name]['expression']
                    for key,item in zip(('a','b','c'),args):expanded=expanded.replace('{'+key+'}',item[1])
                    value=('path',self.compile(expanded,macro_stack+(name,)))
                else:raise ValueError('unknown function')
                append(value); index+=1;continue
            if not re.fullmatch(r'(?:[A-Za-z][A-Za-z0-9]*|[0-9]+)',current):raise ValueError('invalid literal')
            append(('lit',current));index+=1
        if frames or len(top)!=1 or top[0][0]!='path':raise ValueError('invalid top-level expression')
        return top[0][1]

    @staticmethod
    def _lookup(records,at,atom):
        # Select by matching key and greatest eligible stage, independently from A.
        bucket={}
        for item in records:
            if item.get('atom')==atom and type(item.get('stage')) is int and item['stage']<=at:
                bucket.setdefault(item['stage'],[]).append(item)
        if not bucket:return {'value':'U','reason':'missing','evidence_ids':[]}
        selected=sorted(bucket[max(bucket)],key=lambda item:item['id'])
        symbols=[item['value'] for item in selected]
        if any(symbol not in ('T','F','U') for symbol in symbols):raise ValueError('bad evidence')
        if len(set(symbols))>1:return {'value':'U','reason':'conflict','evidence_ids':[r['id'] for r in selected]}
        return {'value':symbols[0],'reason':'observed','evidence_ids':[r['id'] for r in selected]}

    def evaluate(self,expression,evidence,stage):
        bytecode=self.compile(expression)
        stack=[]; clocks=[stage]
        for instruction in bytecode:
            op=instruction[0]
            if op=='enter':clocks.append(instruction[1]);continue
            if op=='exit':
                if len(clocks)<2:raise ValueError('unmatched clock')
                clocks.pop();continue
            if op=='loadlink':
                _,a,b=instruction; atom=f'R({a},{b})'
                obs=self._lookup(evidence,clocks[-1],atom)
                stack.append({'start':a,'end':b,'stage':clocks[-1], 'value':obs['value'],
                              'support':{atom:obs},'links':[atom],'guards':[],'nodes':[a,b]})
                continue
            if op=='guard':
                _,predicate,entity=instruction
                path=stack.pop()
                if entity not in path['nodes']:raise ValueError('guard subject outside path')
                atom=f'{predicate}({entity})'
                obs=self._lookup(evidence,path['stage'],atom)
                truth=min({'F':-1,'U':0,'T':1}[path['value']], {'F':-1,'U':0,'T':1}[obs['value']])
                path['value']={-1:'F',0:'U',1:'T'}[truth]
                path['support'][atom]=obs
                path['guards'].insert(0,atom)
                stack.append(path);continue
            if op=='chain':
                right=stack.pop();left=stack.pop()
                if left['end']!=right['start']:raise ValueError('broken path')
                if left['stage']!=right['stage']:raise ValueError('asynchronous path cannot compose')
                val=min({'F':-1,'U':0,'T':1}[left['value']],{'F':-1,'U':0,'T':1}[right['value']])
                stack.append({'start':left['start'],'end':right['end'],'stage':left['stage'],
                    'value':{-1:'F',0:'U',1:'T'}[val],
                    'support':{**left['support'],**right['support']},
                    'links':left['links']+right['links'],'guards':left['guards']+right['guards'],
                    'nodes':left['nodes']+right['nodes'][1:]})
                continue
            raise ValueError('unsupported VM operation')
        if len(stack)!=1 or len(clocks)!=1:raise ValueError('invalid VM state')
        return stack[0]

    def reconstruct(self,expr,evidence,stage):
        result=self.evaluate(expr,evidence,stage)
        rows=[f'{atom}: {record["value"]}, {record["reason"]}, ids={record["evidence_ids"]}'
              for atom,record in sorted(result['support'].items())]
        result['text']=(f'Observed witness route {" -> ".join(result["nodes"])} at time {result["stage"]}: '
                        f'{result["value"]}. Conditions {result["guards"]}. '
                        f'Edges {result["links"]}. Evidence {"; ".join(rows)}. '
                        'No unrecorded transfer or authority is inferred.')
        return result
