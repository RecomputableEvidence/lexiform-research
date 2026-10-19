"""LC007 append-only in-process ledger, hash-linked to an explicitly trusted anchor.

Not a signature, not an authenticated external storage system. Untrusted callers must
verify an anchor through a separate channel and independently replay disclosed data.
Snapshots are immutable views of a trusted builder with version-limited lookup.
"""
from bisect import bisect_left
from dataclasses import asdict
from evidence import EvidenceRecord, ATOM, stage_num, sha

DOMAIN='LC-EXP-007-APPEND-LEDGER-v1'
GENESIS=sha({'domain':DOMAIN,'genesis':True})

def step(tip, index, row):
    if type(index) is not int or index<0 or type(tip) is not str or len(tip)!=64:
        raise ValueError('invalid chain state')
    r=EvidenceRecord.build(row if type(row) is dict else asdict(row))
    return sha({'domain':DOMAIN,'position':index,'previous':tip,'record':asdict(r)})

class LedgerSnapshot:
    __slots__=('_store','length','digest','_locked')
    def __init__(self, store, length, digest, token):
        if token is not store._token:raise ValueError('snapshot cannot be constructed externally')
        object.__setattr__(self,'_store',store)
        object.__setattr__(self,'length',length)
        object.__setattr__(self,'digest',digest)
        object.__setattr__(self,'_locked',True)
    def __setattr__(self,*_):raise AttributeError('immutable snapshot')
    def _check(self):
        s=self._store
        if self.length<0 or self.length>=len(s._tips) or s._tips[self.length]!=self.digest:
            raise ValueError('snapshot integrity error')
    def appended_since(self, prior):
        self._check()
        if type(prior) is not LedgerSnapshot or prior._store is not self._store:
            raise ValueError('unrelated ledger lineage')
        prior._check()
        if self.length < prior.length:raise ValueError('non-append history')
        return tuple(self._store._records[prior.length:self.length])
    def lookup(self, atom, query_stage, knowledge_stage, stats=None):
        self._check();q=stage_num(query_stage);k=stage_num(knowledge_stage)
        if type(atom) is not str or not ATOM.fullmatch(atom):raise ValueError('invalid atom lookup')
        positions=self._store._index.get(atom,())
        valid_positions=positions[:bisect_left(positions,self.length)]
        rows=[self._store._records[i] for i in valid_positions]
        if stats is not None:
            stats['lookup_calls']=stats.get('lookup_calls',0)+1
            stats['candidate_rows_examined']=stats.get('candidate_rows_examined',0)+len(rows)
        available=[r for r in rows if r.observed_stage<=k]
        applicable=[r for r in available if r.valid_from<=q and (r.valid_until is None or q<r.valid_until)]
        omitted=sorted(r.id for r in available if r not in applicable)
        if not applicable:
            reason='not_valid_at_query' if available else ('not_yet_observed' if rows else 'missing')
            return {'value':'U','reason':reason,'evidence_ids':[],'nonapplicable_ids':omitted,
                    'selected_records':[],'query_stage':q,'knowledge_stage':k}
        latest=max(r.observed_stage for r in applicable)
        selected=sorted((r for r in applicable if r.observed_stage==latest),key=lambda r:r.id)
        values={r.value for r in selected}
        return {'value':next(iter(values)) if len(values)==1 else 'U',
                'reason':'observed_claim' if len(values)==1 else 'conflict',
                'evidence_ids':[r.id for r in selected], 'nonapplicable_ids':omitted,
                'selected_records':[asdict(r) for r in selected],
                'query_stage':q,'knowledge_stage':k}
    def records_for_replay(self):
        self._check()
        return [asdict(x) for x in self._store._records[:self.length]]
    def transition(self, prior):
        delta=self.appended_since(prior)
        return {'domain':DOMAIN,'previous_tip':prior.digest,'previous_length':prior.length,
                'new_tip':self.digest,'new_length':self.length,
                'new_records':[asdict(r) for r in delta]}

class AppendLedger:
    __slots__=('_records','_tips','_ids','_index','_token')
    def __init__(self,rows=()):
        self._records=[];self._tips=[GENESIS];self._ids=set();self._index={};self._token=object()
        for row in rows:self.append(row)
    def snapshot(self):
        return LedgerSnapshot(self,len(self._records),self._tips[-1],self._token)
    def append(self, row):
        data=asdict(row) if type(row) is EvidenceRecord else row
        r=EvidenceRecord.build(data)
        if r.id in self._ids:raise ValueError('duplicate evidence id')
        tip=step(self._tips[-1],len(self._records),asdict(r))
        index=len(self._records)
        self._records.append(r);self._tips.append(tip);self._ids.add(r.id)
        self._index.setdefault(r.atom,[]).append(index)
        return self.snapshot()

def verify_transition(receipt, trusted_tip, trusted_length, trusted_ids):
    """Verify a delta against a trusted prior tip AND maintained historical ID set.

    Caller maintains trusted_ids across verified updates, seeded from an independently
    validated genesis/replay. Without that prior identity state, duplicate IDs across
    the boundary cannot be detected from the hash commitment alone.
    """
    if type(trusted_ids) not in (set,frozenset) or not all(type(v) is str for v in trusted_ids):
        return False
    if type(receipt) is not dict or receipt.get('domain')!=DOMAIN or type(trusted_length) is not int or trusted_length<0:
        return False
    if receipt.get('previous_tip')!=trusted_tip or receipt.get('previous_length')!=trusted_length:
        return False
    tip=trusted_tip
    rows=receipt.get('new_records')
    if type(rows) is not list or not rows:return False
    try:
        ids=set()
        for i,row in enumerate(rows, trusted_length):
            if row['id'] in ids or row['id'] in trusted_ids:return False
            ids.add(row['id']);tip=step(tip,i,row)
    except (ValueError,TypeError,KeyError,AttributeError):return False
    return receipt.get('new_length')==trusted_length+len(rows) and receipt.get('new_tip')==tip

def verify_full_replay(rows, expected_tip):
    tip=GENESIS;ids=set()
    for i,row in enumerate(rows):
        r=EvidenceRecord.build(row)
        if r.id in ids:return False
        ids.add(r.id);tip=step(tip,i,row)
    return tip==expected_tip
