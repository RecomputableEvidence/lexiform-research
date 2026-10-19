"""LC011 frozen v0.1 input contract. Schema checks are not evidence authentication."""
from __future__ import annotations
import hashlib, json

KINDS={'CORRECTS','DISPUTES','SUPERSEDES','ADDS_CONTEXT'}
RULE={'CORRECTS':'ALLOW_CORRECTION','DISPUTES':'REGISTER_DISPUTE','SUPERSEDES':'ALLOW_SUPERSESSION','ADDS_CONTEXT':'REGISTER_CONTEXT'}


def canonical(v):
    return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()

def digest(v):return hashlib.sha256(canonical(v)).hexdigest()

def req(ok,msg):
    if not ok:raise ValueError(msg)

def fields(v, expected, key):
    req(type(v) is dict and set(v)==set(expected),f'{key}: incorrect fields')

def stage(v):return type(v) is int and v>=0

def text(v):return type(v) is str and bool(v.strip())

def interval(v):
    return stage(v['from']) and type(v['until']) is int and v['until']>v['from']

def ledger_validate(L):
    fields(L,['schema','claims','evidence','links','admissions'],'ledger')
    req(L['schema']=='LC011-LEDGER-v0.1','ledger schema')
    idx={}
    for key, names in [
      ('claims',['id','kind','predicate','subject','object','value','observed','from','until','contexts','source_id']),
      ('evidence',['id','source_id','description','observed']),
      ('links',['id','kind','source','target','observed','from','until','contexts','evidence_ids']),
      ('admissions',['id','relation_id','reviewer','rule','observed','evidence_ids','outcome'])]:
        req(type(L[key]) is list,f'{key}: not a list')
        ids=set(); idx[key]={}
        for x in L[key]:
            fields(x,names,key)
            req(text(x['id']) and x['id'] not in ids,f'{key}: repeated/invalid identity')
            ids.add(x['id']);idx[key][x['id']]=x
            if key in {'claims','links'}:
                req(interval(x),f'{key}: invalid validity interval')
                req(type(x['contexts']) is list and len(x['contexts'])>0 and
                    len(x['contexts'])==len(set(x['contexts'])) and all(text(t) for t in x['contexts']),
                    f'{key}: invalid contexts')
            req(stage(x['observed']),f'{key}: invalid observed stage')
            if key in {'links','admissions'}:
                req(type(x['evidence_ids']) is list and len(x['evidence_ids'])>0 and
                    len(set(x['evidence_ids']))==len(x['evidence_ids']) and
                    all(text(t) for t in x['evidence_ids']),f'{key}: invalid evidence IDs')
            if key=='claims':
                req(x['kind'] in {'observation','policy','context'},'unknown claim kind')
                req(all(text(x[n]) for n in ('predicate','subject','object','source_id')),'claim fields')
                req(x['value'] in {'T','F'} and type(x['value']) is str,'claim value')
            if key=='evidence':
                req(text(x['source_id']) and text(x['description']),'invalid evidence record')
            if key=='links':req(x['kind'] in KINDS,'unknown claim-link kind')
            if key=='admissions':
                req(text(x['reviewer']) and x['outcome'] in {'ADMITTED','WITHHELD'},'admission')
    claims=idx['claims']; ev=idx['evidence']; links=idx['links']
    for x in L['links']:
        req(x['source'] in claims and x['target'] in claims,'link references unknown claim')
        source,target=claims[x['source']],claims[x['target']]
        if x['kind']=='ADDS_CONTEXT':
            req(source['kind']=='context','context enrichment requires context claim')
            req((source['subject'],source['object'])==(target['subject'],target['object']),
                'context enrichment must identify same subject/object')
        else:
            req((source['kind'],source['predicate'],source['subject'],source['object'])==
                (target['kind'],target['predicate'],target['subject'],target['object']),
                'relationship must address same typed proposition')
            if x['kind']=='SUPERSEDES':req(source['kind']=='policy','supersession requires policy claims')
            else:req(source['kind']=='observation','correction/dispute requires observations')
        req(all(e in ev for e in x['evidence_ids']),'link has unknown evidence')
        req(all(ev[e]['observed']<=x['observed'] for e in x['evidence_ids']),
            'relationship uses evidence unavailable at declaration time')
    for x in L['claims']:
        req(x['source_id'] in ev,'claim missing source evidence')
        req(ev[x['source_id']]['observed']<=x['observed'],'source evidence known after claim')
    for x in L['admissions']:
        req(x['relation_id'] in links,'unknown admitted relation')
        req(x['rule']==RULE[links[x['relation_id']]['kind']],'admission rule mismatch')
        req(x['observed']>=links[x['relation_id']]['observed'],'admission before relation')
        req(all(e in ev for e in x['evidence_ids']),'admission references unknown evidence')
        req(all(ev[e]['observed']<=x['observed'] for e in x['evidence_ids']),
            'admission evidence not yet available')
    req(len(L['admissions'])==len({a['relation_id'] for a in L['admissions']}),
        'one review per relationship under v0.1')
    return idx

def is_prefix(old,new):
    for k in ['claims','evidence','links','admissions']:
        if len(new[k])<len(old[k]) or canonical(old[k])!=canonical(new[k][:len(old[k])]):return False
    return old['schema']==new['schema']

def scope_ok(record, q,k,context):
    return record['observed']<=k and record['from']<=q<record['until'] and context in record['contexts']

def make_ledger():return {'schema':'LC011-LEDGER-v0.1','claims':[],'evidence':[],'links':[],'admissions':[]}
