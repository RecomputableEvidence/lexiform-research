"""Experimental CHOICE descriptor, parser A: balanced scanner, DAG-A leaf evaluator.
Deliberately restricts CHOICE to top-level/nested alternatives of LC-EXP-003 paths.
This is a declared new operator, not an emergent semantics claim.
"""
from engine import EngineA, projection
from evidence import sha

ORDER={'F':0,'U':1,'T':2}

class ChoiceA:
    def __init__(self,registry):
        self.registry=registry
        self.leaf=EngineA(registry)

    def parse(self,text):
        text=''.join(text.split())
        if not text.startswith('CHOICE('):
            self.leaf.compile(text) # predecessor validates leaf
            return ('leaf',text)
        if not text.endswith(')'):raise ValueError('incomplete CHOICE')
        interior=text[len('CHOICE('):-1]
        level=0;separators=[]
        for i,ch in enumerate(interior):
            if ch=='(':level+=1
            elif ch==')':
                level-=1
                if level<0:raise ValueError('unbalanced')
            elif ch==',' and level==0:separators.append(i)
        if level!=0 or len(separators)!=1:raise ValueError('CHOICE requires exactly two branches')
        cut=separators[0]
        if not interior[:cut] or not interior[cut+1:]:raise ValueError('empty branch')
        return ('choice',self.parse(interior[:cut]),self.parse(interior[cut+1:]))

    def evaluate(self,expression,ledger,q,k=None):
        syntax=self.parse(expression)
        branches=[]
        def walk(node):
            if node[0]=='leaf':
                res=self.leaf.evaluate(node[1],ledger,q,k)
                p=projection(res)
                branches.append({'expression':node[1],'projection':p,'projection_sha256':sha(p),
                                 'definition_lineage':res['definition_lineage']})
            else:
                walk(node[1]);walk(node[2])
        walk(syntax)
        first=branches[0]['projection']; key=(first['start'],first['end'],first['stage'])
        for x in branches[1:]:
            p=x['projection']
            if (p['start'],p['end'],p['stage']) != key:raise ValueError('CHOICE branch endpoint/stage mismatch')
        value=max((x['projection']['value'] for x in branches),key=lambda v:ORDER[v])
        best=[i for i,b in enumerate(branches) if b['projection']['value']==value]
        return {'value':value,'start':key[0],'end':key[1],'stage':key[2],
                'branches':branches,'winning_branch_indices':best,
                'source_expression':expression,'registry_sha256':self.registry.digest,
                'ledger_sha256':ledger.digest,'knowledge_stage':q if k is None else k,
                'operator':'CHOICE_v0.1', 'interpreter':'BALANCED_RECURSIVE_A'}
