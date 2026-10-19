"""LC-EXP-003: bounded, immutable evidence store with interval-aware queries.
Observed statements are declarations, never attestation of real-world truth.
"""
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from types import MappingProxyType

SEMANTICS_VERSION = 'LC-EXP-003-EVIDENCE-1.0.0'
ATOM = re.compile(r'(?:R\([A-Z][A-Z0-9]*,[A-Z][A-Z0-9]*\)|[SP]\([A-Z][A-Z0-9]*\))\Z')
IDENT = re.compile(r'[A-Za-z][A-Za-z0-9_-]{0,95}\Z')

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def sha(obj):
    return hashlib.sha256(canonical(obj).encode('utf-8')).hexdigest()

def stage_num(value):
    if type(value) is not int or value < 0:
        raise ValueError('stage must be nonnegative int (bool is not int)')
    return value

@dataclass(frozen=True)
class EvidenceRecord:
    id: str
    atom: str
    value: str
    observed_stage: int
    valid_from: int
    valid_until: int | None
    source: str
    persistence_policy: str

    @classmethod
    def build(cls, data):
        if type(data) is not dict or set(data) != set(cls.__dataclass_fields__):
            raise ValueError('record keys mismatch (explicit temporal fields required)')
        if type(data['id']) is not str or not IDENT.fullmatch(data['id']):
            raise ValueError('invalid evidence identifier')
        if type(data['atom']) is not str or not ATOM.fullmatch(data['atom']):
            raise ValueError('invalid evidence atom')
        if data['value'] not in ('T','F','U') or type(data['value']) is not str:
            raise ValueError('invalid evidence truth')
        obs=stage_num(data['observed_stage'])
        begin=stage_num(data['valid_from'])
        end=data['valid_until']
        if end is not None:
            stage_num(end)
            if end <= begin: raise ValueError('empty/reversed validity interval')
        if type(data['source']) is not str or not data['source'].strip():
            raise ValueError('evidence source required')
        if data['persistence_policy'] not in ('bounded','open_asserted') or type(data['persistence_policy']) is not str:
            raise ValueError('persistence policy required')
        if (end is None) != (data['persistence_policy']=='open_asserted'):
            raise ValueError('validity interval and persistence policy mismatch')
        return cls(data['id'],data['atom'],data['value'],obs,begin,end,data['source'],data['persistence_policy'])

class EvidenceLedger:
    __slots__ = ('records','digest','_buckets','index_build_rows')
    def __setattr__(self,key,value):
        raise AttributeError('evidence ledger is immutable after construction')
    def __init__(self, rows):
        if type(rows) not in (list,tuple):raise ValueError('evidence must be list/tuple')
        records=[]
        for data in rows:
            if type(data) is EvidenceRecord: data=asdict(data)
            if type(data) is not dict:raise ValueError('invalid record type')
            records.append(EvidenceRecord.build(data))
        records=tuple(records)
        ids=[r.id for r in records]
        if len(ids)!=len(set(ids)):raise ValueError('duplicate evidence ID')
        object.__setattr__(self,'records',records)
        object.__setattr__(self,'digest',sha({'schema':SEMANTICS_VERSION,'records':[asdict(r) for r in records]}))
        buckets={}
        for r in records:buckets.setdefault(r.atom,[]).append(r)
        object.__setattr__(self,'_buckets',MappingProxyType({k:tuple(v) for k,v in buckets.items()}))
        object.__setattr__(self,'index_build_rows',len(records))

    def lookup(self, atom, query_stage, knowledge_stage, stats=None):
        q=stage_num(query_stage);k=stage_num(knowledge_stage)
        if type(atom) is not str or not ATOM.fullmatch(atom):raise ValueError('invalid atom lookup')
        rows=self._buckets.get(atom,())
        if stats is not None:
            stats['lookup_calls']=stats.get('lookup_calls',0)+1
            stats['candidate_rows_examined']=stats.get('candidate_rows_examined',0)+len(rows)
        available=[r for r in rows if r.observed_stage<=k]
        applicable=[r for r in available if r.valid_from<=q and (r.valid_until is None or q<r.valid_until)]
        omitted=sorted(r.id for r in available if r not in applicable)
        if not applicable:
            reason='not_valid_at_query' if available else ('not_yet_observed' if rows else 'missing')
            return {'value':'U','reason':reason,'evidence_ids':[], 'nonapplicable_ids':omitted,
                    'selected_records':[],'query_stage':q,'knowledge_stage':k}
        latest=max(r.observed_stage for r in applicable)
        selected=sorted((r for r in applicable if r.observed_stage==latest),key=lambda r:r.id)
        values={r.value for r in selected}
        return {'value':next(iter(values)) if len(values)==1 else 'U',
                'reason':'observed_claim' if len(values)==1 else 'conflict',
                'evidence_ids':[r.id for r in selected], 'nonapplicable_ids':omitted,
                'selected_records':[asdict(r) for r in selected],
                'query_stage':q,'knowledge_stage':k}

    def records_as_dicts(self):
        return [asdict(r) for r in self.records]
