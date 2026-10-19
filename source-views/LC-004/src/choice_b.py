"""Independent CHOICE descriptor tokenizer/stack compiler B; LC-EXP-003 VM B leaves.
Shares source grammar and indexed ledger semantics with A, NOT independent epistemology.
"""
import re
from engine import EngineB,projection
from evidence import sha
ORDER={'F':0,'U':1,'T':2}

class ChoiceB:
    def __init__(self, registry):
        self.registry=registry
        self.leaf=EngineB(registry)

    def parse(self,expr):
        # Tokenized via a distinct lexical path from A; iterative subtree capture.
        toks=re.findall(r'[A-Za-z][A-Za-z0-9]*|[0-9]+|[(),]',expr)
        if ''.join(toks)!=''.join(expr.split()):raise ValueError('invalid tokens')
        pos=0
        def consume(depth):
            nonlocal pos
            if depth>32:raise ValueError('CHOICE nesting bound')
            if pos >= len(toks):raise ValueError('expected expression')
            if toks[pos]=='CHOICE':
                pos+=1
                if pos>=len(toks) or toks[pos]!='(':raise ValueError('CHOICE open missing')
                pos+=1
                a=consume(depth+1)
                if pos>=len(toks) or toks[pos]!=',':raise ValueError('CHOICE comma missing')
                pos+=1
                b=consume(depth+1)
                if pos>=len(toks) or toks[pos]!=')':raise ValueError('CHOICE close missing')
                pos+=1
                return ('choice',a,b)
            start=pos
            # A leaf starts with a complete function call; seek matching close and
            # validate with the independent predecessor VM compiler.
            if pos+1>=len(toks) or toks[pos+1]!='(':raise ValueError('expected call')
            pos+=2;level=1
            while pos<len(toks) and level:
                if toks[pos]=='(':level+=1
                elif toks[pos]==')':level-=1
                pos+=1
            if level:raise ValueError('unclosed leaf')
            s=''.join(toks[start:pos]);self.leaf.compiler.compile(s)
            return ('leaf',s)
        syntax=consume(0)
        if pos!=len(toks):raise ValueError('trailing token')
        return syntax

    def evaluate(self,expr,ledger,q,k=None):
        stack=[]
        def compile_tree(t):
            if t[0]=='leaf':stack.append(t[1])
            else:compile_tree(t[1]);compile_tree(t[2])
        compile_tree(self.parse(expr))
        branches=[]
        for leaf in stack:
            res=self.leaf.evaluate(leaf,ledger,q,k)
            p=projection(res)
            branches.append({'expression':leaf,'projection':p,'projection_sha256':sha(p),
                            'definition_lineage':res['definition_lineage']})
        first=branches[0]['projection'];key=(first['start'],first['end'],first['stage'])
        for b in branches[1:]:
            p=b['projection']
            if (p['start'],p['end'],p['stage'])!=key:raise ValueError('CHOICE branch endpoint/stage mismatch')
        vals=[b['projection']['value'] for b in branches]
        best_val=['F','U','T'][max(ORDER[v] for v in vals)]
        return {'value':best_val,'start':key[0],'end':key[1],'stage':key[2],
                'branches':branches, 'winning_branch_indices':[i for i,v in enumerate(vals) if v==best_val],
                'source_expression':expr,'registry_sha256':self.registry.digest,
                'ledger_sha256':ledger.digest,'knowledge_stage':q if k is None else k,
                'operator':'CHOICE_v0.1','interpreter':'TOKEN_STACK_B'}
