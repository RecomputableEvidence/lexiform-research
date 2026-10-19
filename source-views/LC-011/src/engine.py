"""Concordance, equivalence-preserving rewriting, and historical reassessment."""
import copy
from contracts import ledger_validate,is_prefix,digest
from lexicon import Lexicon
from typed_control import Typed,build
from oracle import truth
from fixtures import to_lex

def concordance(expr,ledger,q,k,c='default'):
    ledger_validate(ledger)
    a=Lexicon(ledger).eval(to_lex(expr),q,k,c)
    b=Typed(ledger).eval(build(expr),q,k,c)
    o=truth(expr,ledger,q,k,c)
    if not(a==b==o):raise AssertionError('independent-path disagreement '+str((a,b,o)))
    return a

def rewrite_demorgan(expr):
    if expr.get('op')!='NOT' or expr['arg'].get('op')!='ANY':
        raise ValueError('rule only applies to NOT(ANY(...))')
    return {'op':'ALL','args':[{'op':'NOT','arg':copy.deepcopy(e)} for e in expr['arg']['args']]}

def rewrite_receipt(before,after,ledger,q,k,c='default'):
    expected=rewrite_demorgan(before)
    if after!=expected:raise ValueError('unlicensed rewrite')
    a=concordance(before,ledger,q,k,c);b=concordance(after,ledger,q,k,c)
    if a!=b:raise ValueError('rewrite did not preserve semantic projection')
    return dict(operation='REWRITE',rule='DE_MORGAN_ANY_TO_ALL_KLEENE',
                before_expression_sha256=digest(before),after_expression_sha256=digest(after),
                preserved_projection=a)

def reassess(before,after,expr,q,k0,k1,c='default'):
    ledger_validate(before);ledger_validate(after)
    if not is_prefix(before,after):raise ValueError('history is not append-only')
    a=concordance(expr,before,q,k0,c);b=concordance(expr,after,q,k1,c)
    return dict(operation='REASSESS',old_ledger=digest(before),new_ledger=digest(after),
                expression=digest(expr),query_stage=q,before_cutoff=k0,after_cutoff=k1,
                before=a,after=b,delta={name:(a[name],b[name]) for name in a if a[name]!=b[name]},
                historical_statement='Predecessor is retained and not reinterpreted as a past claim.')
