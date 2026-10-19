"""LC008: export portable historical audit packets; replay offline with the typed oracle.

Evidence is only user-declared information. Packet hashes provide integrity checks, not
signatures, independent trust anchors, physical validity, or authenticated provenance.
The replay deliberately recomputes the full ledger and typed graph; it is NOT O(1).
Dependencies must first be resolved from the embedded, hash-verified predecessor chain.
"""
from dataclasses import asdict
import copy
import re

from evidence import EvidenceRecord, EvidenceLedger, sha
from registry import FrozenDefinitions
from typed_audit import TypedAudit
from lazy_graph import select_witness
from persistent_ledger import LedgerSnapshot, DOMAIN, GENESIS
from selective_audit import SelectiveAudit, AuditHandle
from dependencies import PARENT_SHA256

SCHEMA='LC-EXP-008-PORTABLE-AUDIT-1'
MAX_RECORDS=10000
MAX_EXPRESSION_CHARS=100000
MAX_WITNESSES=32


def _ensure(condition, message):
    if not condition:raise ValueError(message)


def _packed_index(i):
    _ensure(type(i) is int and i>=0,'witness index must be nonnegative integer')
    return str(i)


def export_packet(engine,handle,snapshot,registry,witness_indices=(0,)):
    """Export a historical revision. Does not require full_graph(handle) materialization."""
    _ensure(type(engine) is SelectiveAudit,'selective engine required')
    _ensure(type(handle) is AuditHandle,'issued audit handle required')
    _ensure(type(snapshot) is LedgerSnapshot,'revision snapshot required')
    _ensure(type(registry) is FrozenDefinitions,'bounded registry required')
    engine._validate_handle(handle)
    snapshot._check();registry._check_seal()
    _ensure(engine.registry is registry and handle.registry_digest==registry.digest,'registry mismatch')
    _ensure(snapshot.digest==handle.ledger_digest,'historical ledger tip mismatch')
    _ensure(type(witness_indices) in (list,tuple),'witness indices must be list or tuple')
    _ensure(0 < len(witness_indices) <= MAX_WITNESSES,'invalid witness export count')
    _ensure(all(type(i) is int for i in witness_indices),'invalid witness index type')
    _ensure(len(set(witness_indices))==len(witness_indices),'repeated witness index')
    rows=snapshot.records_for_replay()
    _ensure(len(rows)<=MAX_RECORDS,'too many ledger rows')
    _ensure(len(handle.expression)<=MAX_EXPRESSION_CHARS,'expression too long')
    root=engine._node_at(engine.plan['root'],handle.revision)
    declared_indices=sorted(witness_indices)
    witnesses=[{'index_decimal':_packed_index(i),'witness':engine.witness(handle,i)}
               for i in declared_indices]
    packet={
        'schema':SCHEMA,
        'predecessor':{'id':'LC-EXP-007-APPEND-BOUND-AUDIT-001','archive_sha256':PARENT_SHA256},
        'context':{'expression':handle.expression,'query_stage':handle.query_stage,
                   'knowledge_stage':handle.knowledge_stage,'definitions':registry.get_definitions()},
        'ledger':{'domain':DOMAIN,'length':snapshot.length,'tip':snapshot.digest,'records':rows},
        'expected':{'root_id':root['id'],'value':root['value'],'start':root['start'],
                    'end':root['end'],'stage':root['stage'],'histogram':copy.deepcopy(root['histogram']),
                    'witness_count_decimal':str(root['witness_count']),
                    'registry_digest':registry.digest},
        'witnesses':witnesses,
    }
    packet['packet_sha256']=sha(packet)
    return copy.deepcopy(packet)


def verify_packet(packet, trusted_ledger_tip=None, trusted_packet_hash=None):
    """Independently recompute a packet, not merely validate its self-hash.

    'trusted_*' parameters MUST come from outside the packet. Without such an anchor,
    valid is evidence of internal reproducibility only (UNANCHORED).
    """
    _ensure(type(packet) is dict and set(packet)=={'schema','predecessor','context','ledger','expected','witnesses','packet_sha256'},
            'packet keys invalid')
    _ensure(packet['schema']==SCHEMA,'packet schema mismatch')
    pred=packet['predecessor']
    _ensure(type(pred) is dict and pred=={'id':'LC-EXP-007-APPEND-BOUND-AUDIT-001',
                                       'archive_sha256':PARENT_SHA256},'predecessor identity mismatch')
    declared_hash=packet['packet_sha256']
    _ensure(type(declared_hash) is str and re.fullmatch('[0-9a-f]{64}',declared_hash) is not None,
            'invalid packet hash')
    payload={key:value for key,value in packet.items() if key!='packet_sha256'}
    _ensure(sha(payload)==declared_hash,'packet content hash mismatch')
    if trusted_packet_hash is not None:
        _ensure(type(trusted_packet_hash) is str and trusted_packet_hash==declared_hash,
                'external packet hash mismatch')
    context=packet['context'];ledger=packet['ledger'];expected=packet['expected']
    _ensure(type(context) is dict and set(context)=={'expression','query_stage','knowledge_stage','definitions'},
            'context keys invalid')
    _ensure(type(ledger) is dict and set(ledger)=={'domain','length','tip','records'},'ledger keys invalid')
    _ensure(type(expected) is dict and set(expected)=={'root_id','value','start','end','stage','histogram',
                                                      'witness_count_decimal','registry_digest'},'expected keys invalid')
    _ensure(type(context['expression']) is str and 0<len(context['expression'])<=MAX_EXPRESSION_CHARS,
            'invalid expression size')
    _ensure(type(context['query_stage']) is int and context['query_stage']>=0 and
            type(context['knowledge_stage']) is int and context['knowledge_stage']>=0,
            'invalid stage')
    rows=ledger['records']
    _ensure(ledger['domain']==DOMAIN and type(rows) is list and len(rows)<=MAX_RECORDS,
            'invalid ledger')
    _ensure(type(ledger['length']) is int and ledger['length']==len(rows),'ledger length mismatch')
    _ensure(type(ledger['tip']) is str and re.fullmatch('[0-9a-f]{64}',ledger['tip']) is not None,
            'invalid chain tip')
    if trusted_ledger_tip is not None:
        _ensure(type(trusted_ledger_tip) is str and trusted_ledger_tip==ledger['tip'],
                'external ledger tip mismatch')
    ids=set();tip=GENESIS
    # Fresh, explicitly coded chain replay; does not trust LC007's snapshot/index/step.
    for index,row in enumerate(rows):
        r=EvidenceRecord.build(row)
        normalized=asdict(r)
        _ensure(row==normalized,'noncanonical evidence record')
        _ensure(r.id not in ids,'reused evidence identifier')
        ids.add(r.id)
        tip=sha({'domain':DOMAIN,'position':index,'previous':tip,'record':normalized})
    _ensure(tip==ledger['tip'],'independent chain replay mismatch')
    registry=FrozenDefinitions(context['definitions'])
    _ensure(registry.digest==expected['registry_digest'],'registry binding mismatch')
    # Independent conventional typed stack computation, not LC007's selective cache.
    reference=TypedAudit(registry).evaluate(context['expression'],EvidenceLedger(rows),
                                             context['query_stage'],context['knowledge_stage'])
    matches={
        'root_id':reference['root_id'],'value':reference['value'],'start':reference['start'],
        'end':reference['end'],'stage':reference['stage'],'histogram':reference['histogram'],
        'witness_count_decimal':str(reference['witness_count']),
        'registry_digest':reference['registry_sha256'],
    }
    _ensure(matches==expected,'independently reconstructed audit differs')
    provided=packet['witnesses']
    _ensure(type(provided) is list and 0<len(provided)<=MAX_WITNESSES,'witness count invalid')
    seen=set()
    for entry in provided:
        _ensure(type(entry) is dict and set(entry)=={'index_decimal','witness'},'witness record schema')
        idx=entry['index_decimal']
        _ensure(type(idx) is str and re.fullmatch(r'(0|[1-9][0-9]*)',idx) is not None,
                'noncanonical witness index')
        _ensure(idx not in seen,'duplicate witness index')
        seen.add(idx)
        integer=int(idx)
        answer=select_witness(reference,integer)
        answer['ledger_commitment']=ledger['tip']
        answer['root_id']=reference['root_id']
        _ensure(entry['witness']==answer,'independent witness mismatch for index '+idx)
    return {'verified':True,'anchor_status':'EXTERNALLY_ANCHORED' if
            (trusted_ledger_tip is not None or trusted_packet_hash is not None) else 'UNANCHORED',
            'claim_ceiling':'replay-consistent declared evidence, not authenticated source or reality',
            'replayed_records':len(rows),'verified_witnesses':len(provided),
            'graph_nodes':len(reference['nodes']),'root_id':reference['root_id'],
            'packet_sha256':declared_hash,'ledger_tip':tip}
