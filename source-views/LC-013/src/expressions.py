"""Bounded declared abstract expression grammar."""
from contract import assert_ok,txt,stage

def check(e,depth=0):
    assert_ok(depth<=48,'expression depth exceeded')
    assert_ok(type(e) is dict and txt(e.get('op')),'expression must be mapping with operation')
    op=e['op']
    if op=='ATOM':
        assert_ok(set(e)=={'op','kind','predicate','subject','object'},'ATOM fields')
        assert_ok(e['kind'] in ('observation','policy','context'),'ATOM kind')
        assert_ok(all(txt(e[x]) for x in ('predicate','subject','object')),'ATOM labels')
    elif op=='LINK':
        assert_ok(set(e)=={'op','id'} and txt(e['id']),'LINK fields')
    elif op=='NOT':
        assert_ok(set(e)=={'op','arg'},'NOT fields');check(e['arg'],depth+1)
    elif op=='SCOPE':
        assert_ok(set(e)=={'op','query','knowledge','context','body'},'SCOPE fields')
        assert_ok(stage(e['query']) and stage(e['knowledge']) and txt(e['context']),'SCOPE values')
        check(e['body'],depth+1)
    elif op in ('ALL','ANY'):
        assert_ok(set(e)=={'op','args'} and type(e['args']) is list and len(e['args'])>=2,'ALL/ANY arity')
        for ch in e['args']:check(ch,depth+1)
    else:raise ValueError('unknown expression operation')
    return True
