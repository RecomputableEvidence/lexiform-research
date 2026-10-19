"""Wire-format, frozen-registry, and observation utilities only; no common parser/evaluator."""
import hashlib, json
from pathlib import Path

REGISTRY_PATH = Path(__file__).resolve().parents[1] / 'spec' / 'registry.json'

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)

def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()

def registry():
    obj = json.loads(REGISTRY_PATH.read_text(encoding='utf-8'))
    if obj['grammar_version'] != 'LC-EXP-001-GRAMMAR-1.0.0':
        raise ValueError('unrecognized grammar version')
    return obj

EVIDENCE = [
    {'id':'E001','stage':0,'predicate':'S','entity':'A','value':'T','source':'seal check'},
    {'id':'E002','stage':1,'predicate':'P','entity':'A','value':'T','source':'inspection record'},
    {'id':'E003','stage':2,'predicate':'S','entity':'A','value':'F','source':'later seal break observation'},
]

def details(evidence, stage, predicate, entity):
    active = [e for e in evidence if e['predicate']==predicate and e['entity']==entity and e['stage']<=stage]
    if not active:
        return {'value':'U','evidence_ids':[],'reason':'missing'}
    latest=max(e['stage'] for e in active)
    selected=sorted((e for e in active if e['stage']==latest), key=lambda x:x['id'])
    vals={e['value'] for e in selected}
    if len(vals)!=1:
        return {'value':'U','evidence_ids':[e['id'] for e in selected], 'reason':'conflict'}
    val=vals.pop()
    if val not in ('T','F','U'):
        raise ValueError('bad observed truth value')
    return {'value':val,'evidence_ids':[e['id'] for e in selected], 'reason':'observed'}

def snapshot(evidence, stage):
    pairs = sorted({(e['predicate'], e['entity']) for e in evidence})
    return {f'{p}({ent})':details(evidence,stage,p,ent) for p,ent in pairs}
