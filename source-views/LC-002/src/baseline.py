"""Conventional typed-tree control. Identical toy logic, no compressed macro syntax.
Caching is offered as a separate control: caching is not unique to lexiconic representations.
"""
from common import details, digest

TRANSFER_TREE={
    'op':'and',
    'args':[{'op':'atom','predicate':'S','entity':'A'},
            {'op':'atom','predicate':'P','entity':'A'}]
}

class TypedEvaluator:
    def __init__(self, *, cached=False):
        self.cached=cached; self.memo={}; self.cache_hits=0

    def evaluate(self, tree, evidence, stage):
        key=None
        if self.cached:
            # The benchmark treats the typed tree as immutable throughout the run.
            # Identity is used as a fixed compiled-tree handle, just as the lexicon
            # uses an immutable expression string as its compiled-expression handle.
            key=(id(tree),digest(evidence),stage)
            if key in self.memo:
                self.cache_hits+=1
                return self.memo[key]
        def walk(n):
            op=n['op']
            if op=='atom':
                p,e=n['predicate'],n['entity']
                return details(evidence,stage,p,e)['value'],{f'{p}({e})'}
            if op=='not':
                a,refs=walk(n['args'][0]); return {'T':'F','F':'T','U':'U'}[a],refs
            left,l=walk(n['args'][0]); right,r=walk(n['args'][1])
            if op=='and': val='F' if 'F' in (left,right) else ('T' if left==right=='T' else 'U')
            elif op=='or': val='T' if 'T' in (left,right) else ('F' if left==right=='F' else 'U')
            elif op=='implies':
                a={'T':'F','F':'T','U':'U'}[left]
                val='T' if 'T' in (a,right) else ('F' if a==right=='F' else 'U')
            else: raise ValueError('unknown structured op')
            return val,l|r
        value,refs=walk(tree)
        result={'value':value,'atoms':sorted(refs)}
        if self.cached:self.memo[key]=result
        return result
