"""Triangulation, scoped rewrite, immutable historical reassessment."""
from contract import validate,is_prefix,sha
from lexicon import Lexicon
from typed_baseline import TypedControl,build
from oracle import truth
from fixtures import to_lex
from expressions import check
import copy

def agreement(expression,ledger,q,k,c='default', oracle_enabled=True):
    validate(ledger);check(expression)
    a=Lexicon(ledger).eval(to_lex(expression),q,k,c)
    b=TypedControl(ledger).evaluate(build(expression),q,k,c)
    if a!=b:raise AssertionError('lexicon/typed disagree: '+str((a,b)))
    if oracle_enabled:
        d=truth(expression,ledger,q,k,c)
        if a!=d:raise AssertionError('oracle divergence: '+str((a,d)))
    return a

def rewrite_demorgan(e):
    if e.get('op')!='NOT' or e['arg'].get('op')!='ANY':raise ValueError('unlicensed REWRITE')
    return {'op':'ALL','args':[{'op':'NOT','arg':copy.deepcopy(ch)} for ch in e['arg']['args']]}

def rewrite_receipt(expr,L,q,k,c='default'):
    successor=rewrite_demorgan(expr)
    before=agreement(expr,L,q,k,c);after=agreement(successor,L,q,k,c)
    if before!=after:raise ValueError('rewrite lost full projection')
    return {'operation':'REWRITE','rule':'KLEENE_DEMORGAN','original':sha(expr),'successor':sha(successor),
            'projection_sha256':sha(before),'projection':before}

def reassess(old,new,e,q,k0,k1,c='default'):
    validate(old);validate(new)
    if not is_prefix(old,new):raise ValueError('history must append exact previous categories')
    a=agreement(e,old,q,k0,c);b=agreement(e,new,q,k1,c)
    return {'operation':'REASSESS','before_ledger_sha256':sha(old),'after_ledger_sha256':sha(new),
            'expression_sha256':sha(e),'query':q,'context':c,'before_cutoff':k0,'after_cutoff':k1,
            'before':a,'after':b,'changed_fields':sorted(k for k in a if a[k]!=b[k]),
            'predecessor_retained':True}
