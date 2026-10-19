"""Finite witness of expressivity gap: meet-only formulas cannot express join.
Not a proof of all possible future lexicon grammars. Assumes no other operators
than conjunction/atom repetition on two independent atomic path propositions.
"""
from itertools import product
ORDER={'F':0,'U':1,'T':2}

def evaluate_formula(kind,a,b):
    if kind=='left':return a
    if kind=='right':return b
    if kind=='both':return min((a,b),key=lambda x:ORDER[x])
    if kind=='target':return max((a,b),key=lambda x:ORDER[x])
    raise ValueError(kind)

def run():
    valuations=list(product('FUT',repeat=2))
    table=[{'left':a,'right':b,'target':evaluate_formula('target',a,b),
            'left_only':evaluate_formula('left',a,b),
            'right_only':evaluate_formula('right',a,b),
            'meet':evaluate_formula('both',a,b)} for a,b in valuations]
    differences={col:[{'left':row['left'],'right':row['right'],'expected':row['target'],'actual':row[col]}
                      for row in table if row[col]!=row['target']]
                 for col in ('left_only','right_only','meet')}
    assert all(differences.values())
    return {'truth_table':table,'candidate_expression_classes':['left_only','right_only','meet'],
            'counterexamples':differences,'claim_scope':'meet-only two-atom formulas without constants or join cannot express join'}
