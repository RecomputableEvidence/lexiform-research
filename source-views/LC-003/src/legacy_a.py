"""REL-A: recursive AST parser/evaluator and independently implemented evidence selection."""
import copy
import hashlib
import json
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class Term:
    op: str
    args: tuple

class RelationalA:
    def __init__(self, macros):
        self.macros = copy.deepcopy(macros)
        self.seal = self._digest(self.macros)

    @staticmethod
    def _digest(obj):
        return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()

    def parse(self, expression, macro_stack=()):
        if self._digest(self.macros) != self.seal:
            raise ValueError('macro registry mutated')
        tokens=[]
        cursor=0
        pat=re.compile(r'\s*([A-Za-z][A-Za-z0-9]*|[0-9]+|[(),])')
        while cursor<len(expression):
            matched=pat.match(expression,cursor)
            if matched is None:
                if expression[cursor:].strip():raise ValueError('invalid character')
                break
            tokens.append(matched.group(1))
            cursor=matched.end()
        if not tokens:raise ValueError('empty expression')
        pos = 0
        def build(depth=0):
            nonlocal pos
            if depth > 48 or pos + 1 >= len(tokens):
                raise ValueError('nesting/incomplete expression')
            op = tokens[pos]; pos += 1
            if tokens[pos] != '(':
                raise ValueError('missing open')
            pos += 1
            children = []
            while True:
                if pos >= len(tokens): raise ValueError('unclosed expression')
                if tokens[pos] == ')':
                    pos += 1; break
                if children:
                    if tokens[pos] != ',': raise ValueError('missing comma')
                    pos += 1
                if pos >= len(tokens): raise ValueError('incomplete argument')
                if pos+1 < len(tokens) and tokens[pos+1] == '(':
                    children.append(build(depth+1))
                else:
                    children.append(tokens[pos]); pos += 1
            return Term(op,tuple(children))
        root=build()
        if pos != len(tokens): raise ValueError('trailing characters')
        return self._typecheck(root, 0, macro_stack)

    def _typecheck(self, t, depth, macro_stack):
        if depth > 48: raise ValueError('expansion limit')
        op,args=t.op,t.args
        entity=lambda x: isinstance(x,str) and bool(re.fullmatch('[A-Z][A-Z0-9]*',x))
        if op in ('R','S','P'):
            required=2 if op=='R' else 1
            if len(args)!=required or not all(map(entity,args)):raise ValueError('invalid atom signature')
            return t
        if op=='C':
            if len(args)!=2 or not all(isinstance(x,Term) for x in args):raise ValueError('chain arity')
            a,b=(self._typecheck(x,depth+1,macro_stack) for x in args)
            if a.op in ('S','P') or b.op in ('S','P'):raise ValueError('expected path')
            return Term(op,(a,b))
        if op=='J':
            if len(args)!=2 or not all(isinstance(x,Term) for x in args):raise ValueError('guard arity')
            a,b=(self._typecheck(x,depth+1,macro_stack) for x in args)
            if a.op not in ('S','P') or b.op in ('S','P'):raise ValueError('guard type')
            return Term(op,(a,b))
        if op=='AT':
            if len(args)!=2 or not isinstance(args[0],str) or not re.fullmatch(r'(0|[1-9][0-9]*)',args[0]) or not isinstance(args[1],Term):raise ValueError('stage type')
            child=self._typecheck(args[1],depth+1,macro_stack)
            if child.op in ('S','P'):raise ValueError('time-scoped path required')
            return Term(op,(int(args[0]),child))
        if op in ('H1','H2'):
            if len(args)!=3 or not all(map(entity,args)) or op not in self.macros:raise ValueError('macro signature')
            if op in macro_stack:raise ValueError('recursive macro expansion')
            entry=self.macros[op]['expression']
            # Bounded, declared substitution into separately parsed grammar.
            for k,v in zip(('a','b','c'),args):entry=entry.replace('{'+k+'}',v)
            return self._typecheck(self.parse(entry,macro_stack+(op,)),depth+1,macro_stack+(op,))
        raise ValueError('unrecognized operator')

    @staticmethod
    def _fetch(evidence,stage,atom):
        # Independent evidence selection: evaluate highest eligible stage, never default U to F.
        found=[]
        for row in evidence:
            if row.get('atom') == atom and type(row.get('stage')) is int and row['stage']<=stage:
                found.append(row)
        if not found:return {'value':'U','reason':'missing','evidence_ids':[]}
        stage_max=max(item['stage'] for item in found)
        selected=sorted([item for item in found if item['stage']==stage_max],key=lambda r:r['id'])
        values=set(item['value'] for item in selected)
        if not values.issubset({'T','F','U'}):raise ValueError('invalid evidence value')
        if len(values)>1:return {'value':'U','reason':'conflict','evidence_ids':[x['id'] for x in selected]}
        return {'value':next(iter(values)),'reason':'observed','evidence_ids':[x['id'] for x in selected]}

    @staticmethod
    def _and(x,y):
        return 'F' if 'F' in (x,y) else ('T' if x==y=='T' else 'U')

    def evaluate(self,expression,evidence,stage):
        if self._digest(self.macros)!=self.seal:raise ValueError('macro registry mutated')
        tree=self.parse(expression)
        def visit(t,current):
            if t.op=='AT':return visit(t.args[1],t.args[0])
            if t.op=='R':
                a,b=t.args; atom=f'R({a},{b})'; rec=self._fetch(evidence,current,atom)
                return {'start':a,'end':b,'stage':current,'value':rec['value'],'support':{atom:rec},'links':[atom],'guards':[],'nodes':[a,b]}
            if t.op=='C':
                left,right=(visit(t.args[0],current),visit(t.args[1],current))
                if left['end']!=right['start']:raise ValueError('noncontiguous chain')
                if left['stage']!=right['stage']:raise ValueError('mixed-stage chain')
                support={**left['support'],**right['support']}
                return {'start':left['start'],'end':right['end'],'stage':left['stage'],
                    'value':self._and(left['value'],right['value']), 'support':support,
                    'links':left['links']+right['links'],'guards':left['guards']+right['guards'],
                    'nodes':left['nodes']+right['nodes'][1:]}
            if t.op=='J':
                test,path=t.args; result=visit(path,current)
                name=test.args[0]
                if name not in result['nodes']:raise ValueError('unbound guard subject')
                atom=f'{test.op}({name})'; rec=self._fetch(evidence,result['stage'],atom)
                result['value']=self._and(rec['value'],result['value'])
                result['support'][atom]=rec
                result['guards']=[atom]+result['guards']
                return result
            raise ValueError('invalid path node')
        return visit(tree,stage)

    def reconstruct(self,expr,evidence,stage):
        row=self.evaluate(expr,evidence,stage)
        labels=[f"{key}={v['value']}({v['reason']}:{','.join(v['evidence_ids'])})" for key,v in sorted(row['support'].items())]
        row['text']=(f"Specified witness {' -> '.join(row['nodes'])} at stage {row['stage']} is {row['value']}; "
                      f"links={row['links']}; guards={row['guards']}; observations={'; '.join(labels)}. "
                      "This does not establish any unobserved link or general authority.")
        return row
