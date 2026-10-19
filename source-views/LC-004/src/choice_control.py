"""Matched conventional typed AST arm for candidate CHOICE; shared CHOICE syntax.
Not a truly independent parser; tests whether result is uniquely lexiconic.
"""
from choice_a import ChoiceA
from baseline import TypedBaseline
from engine import projection
from evidence import sha
ORDER={'F':0,'U':1,'T':2}
class ChoiceTypedBaseline:
    def __init__(self,registry):
        self.registry=registry
        self.parser=ChoiceA(registry) # parsing is intentionally shared, execution differs
        self.interpreter=TypedBaseline(registry,False)
    def evaluate(self,expr,ledger,q,k=None):
        tree=self.parser.parse(expr)
        def leaves(t):
            if t[0]=='leaf':return [t[1]]
            return leaves(t[1])+leaves(t[2])
        branch_results=[self.interpreter.evaluate(b,ledger,q,k) for b in leaves(tree)]
        projected=[projection(x) for x in branch_results]
        loc={(p['start'],p['end'],p['stage']) for p in projected}
        if len(loc)!=1:raise ValueError('CHOICE incompatible branches')
        start,end,stage=next(iter(loc))
        value=max((p['value'] for p in projected),key=lambda s:ORDER[s])
        return {'value':value,'start':start,'end':end,'stage':stage,
                'branches':[{'expression':r['source_expression'],'projection':p,'projection_sha256':sha(p),
                             'definition_lineage':r['definition_lineage']} for r,p in zip(branch_results,projected)],
                'winning_branch_indices':[i for i,p in enumerate(projected) if p['value']==value]}
