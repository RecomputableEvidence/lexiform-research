"""LC-EXP-012 frozen candidate contract. Valid syntax is NOT authenticated evidence."""
from __future__ import annotations
import json, hashlib

KINDS = {'CORRECTS','DISPUTES','SUPERSEDES','ADDS_CONTEXT'}
POLICY = {'CORRECTS':'REVIEW_CORRECTION', 'DISPUTES':'REGISTER_CHALLENGE',
          'SUPERSEDES':'REVIEW_SUPERSESSION','ADDS_CONTEXT':'REGISTER_ENRICHMENT'}
PROJ_FIELDS = ('accepted','defeated','undecided','attacks','admitted','pending',
               'disputed','qualifiers','support')

def canonical(v):
    return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')

def sha(v): return hashlib.sha256(canonical(v)).hexdigest()
def assert_ok(ok,msg):
    if not ok: raise ValueError(msg)
def fields(obj,names,ctx):
    assert_ok(type(obj) is dict and set(obj)==set(names),f'{ctx}: unexpected fields')
def txt(x):return type(x) is str and bool(x.strip())
def stage(x):return type(x) is int and x>=0

def time_bounds(x):
    return stage(x['from']) and type(x['until']) is int and x['until']>x['from']
def contexts(x):
    c=x['contexts']
    return type(c) is list and len(c)>0 and len(c)==len(set(c)) and all(txt(t) for t in c)
def refs(x):
    return type(x) is list and len(x)>0 and len(set(x))==len(x) and all(txt(t) for t in x)

def guard_check(g,depth=0):
    assert_ok(depth<=24,'guard nesting limit')
    assert_ok(type(g) is list and len(g)>=2,'guard syntax')
    op=g[0]
    if op=='FACT':assert_ok(len(g)==2 and txt(g[1]),'FACT requires a fact key')
    elif op=='NOT':assert_ok(len(g)==2,'NOT arity');guard_check(g[1],depth+1)
    elif op in {'AND','OR'}:
        assert_ok(len(g)>=3,'AND/OR arity')
        for ch in g[1:]:guard_check(ch,depth+1)
    elif op=='CONST':assert_ok(len(g)==2 and g[1] in ('T','F','U'),'CONST value')
    else:raise ValueError('unknown guard operation')

def validate(L):
    fields(L,('schema','claims','conditions','evidence','links','reviewers','admissions'),'ledger')
    assert_ok(L['schema']=='LC012-LEDGER-v0.1','ledger schema mismatch')
    keydefs={
      'claims':('id','kind','predicate','subject','object','value','observed','from','until','contexts','source_id'),
      'conditions':('id','key','value','observed','from','until','contexts','source_id'),
      'evidence':('id','source_id','description','observed'),
      'links':('id','kind','source','target','observed','from','until','contexts','evidence_ids','guard'),
      'reviewers':('id','allowed_kinds','contexts','from','until'),
      'admissions':('id','relation_id','reviewer_id','rule','observed','evidence_ids','outcome')}
    ix={}
    for key,names in keydefs.items():
        assert_ok(type(L[key]) is list,f'{key}: not list')
        ix[key]={}
        for x in L[key]:
            fields(x,names,key)
            assert_ok(txt(x['id']) and x['id'] not in ix[key],f'{key}: invalid or duplicate id')
            ix[key][x['id']]=x
            if key!='reviewers':assert_ok(stage(x['observed']),f'{key}: observed stage invalid')
            if key in {'claims','conditions','links','reviewers'}:
                assert_ok(time_bounds(x) and contexts(x),f'{key}: scope invalid')
            if key=='claims':
                assert_ok(x['kind'] in {'observation','policy','context'},'unknown claim kind')
                assert_ok(all(txt(x[n]) for n in ('predicate','subject','object','source_id')),'claim fields')
                assert_ok(x['value'] in {'T','F'},'claim truth must be T/F')
            elif key=='conditions':
                assert_ok(txt(x['key']) and x['value'] in {'T','F'},'condition fields')
                assert_ok(txt(x['source_id']),'condition source')
            elif key=='evidence':
                assert_ok(txt(x['source_id']) and txt(x['description']),'evidence fields')
            elif key=='links':
                assert_ok(x['kind'] in KINDS and refs(x['evidence_ids']),'link type/evidence')
                guard_check(x['guard'])
            elif key=='reviewers':
                assert_ok(refs(x['allowed_kinds']) and set(x['allowed_kinds'])<=KINDS,'reviewer permissions')
            elif key=='admissions':
                assert_ok(x['outcome'] in {'ADMITTED','WITHHELD'} and refs(x['evidence_ids']), 'admission fields')
                assert_ok(txt(x['rule']) and txt(x['reviewer_id']),'admission reviewer')
    evidence,claims,links=ix['evidence'],ix['claims'],ix['links']
    for section in ('claims','conditions'):
        for x in L[section]:
            assert_ok(x['source_id'] in evidence,'missing observation source evidence')
            assert_ok(evidence[x['source_id']]['observed']<=x['observed'],'future observation evidence')
    for rel in L['links']:
        assert_ok(rel['source'] in claims and rel['target'] in claims,'unknown link claim')
        a,b=claims[rel['source']],claims[rel['target']]
        if rel['kind']=='ADDS_CONTEXT':
            assert_ok(a['kind']=='context' and (a['subject'],a['object'])==(b['subject'],b['object']),
                      'context source must match target identity')
        else:
            assert_ok((a['kind'],a['predicate'],a['subject'],a['object'])==
                     (b['kind'],b['predicate'],b['subject'],b['object']), 'link proposition mismatch')
            if rel['kind']=='SUPERSEDES':assert_ok(a['kind']=='policy','supersession must be policy')
            else:assert_ok(a['kind']=='observation','correction/dispute must be observation')
        assert_ok(rel['source']!=rel['target'],'self relationship prohibited')
        for eid in rel['evidence_ids']:
            assert_ok(eid in evidence and evidence[eid]['observed']<=rel['observed'], 'invalid link evidence stage')
    unique_reviews=set()
    for a in L['admissions']:
        assert_ok(a['relation_id'] in links and a['reviewer_id'] in ix['reviewers'], 'unknown reviewer or relation')
        assert_ok(a['relation_id'] not in unique_reviews,'at most one admission per relation')
        unique_reviews.add(a['relation_id'])
        rel=links[a['relation_id']];reviewer=ix['reviewers'][a['reviewer_id']]
        assert_ok(a['rule']==POLICY[rel['kind']],'admission rule mismatch')
        assert_ok(a['observed']>=rel['observed'],'admission predates declaration')
        assert_ok(rel['kind'] in reviewer['allowed_kinds'] and
                  reviewer['from']<=a['observed']<reviewer['until'] and
                  bool(set(rel['contexts']) & set(reviewer['contexts'])),
                  'admission not within DECLARED reviewer permission')
        for eid in a['evidence_ids']:
            assert_ok(eid in evidence and evidence[eid]['observed']<=a['observed'], 'future admission evidence')
    return ix

def is_prefix(old,new):
    if old['schema']!=new['schema']:return False
    for k in ('claims','conditions','evidence','links','reviewers','admissions'):
        if len(old[k])>len(new[k]) or canonical(old[k])!=canonical(new[k][:len(old[k])]):return False
    return True

def scope(x,q,k,ctx):return x['observed']<=k and x['from']<=q<x['until'] and ctx in x['contexts']
def blank():return {'schema':'LC012-LEDGER-v0.1',**{k:[] for k in ('claims','conditions','evidence','links','reviewers','admissions')}}

def out(value,**sets):
    return {'value':value,**{k:sorted(set(sets.get(k,()))) for k in PROJ_FIELDS}}
