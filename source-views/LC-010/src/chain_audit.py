"""Bounded portable sequence of LC009 verified append-reassessment events.

This is a declared sequence, not a proof that no events were omitted externally.
All anchor origin and evidence source authentication remain outside this verifier.
"""
import copy
import re
from evidence import sha
from relational_audit import exact, ensure, verify_reassessment

SCHEMA='LC-EXP-010-RELATION-CHAIN-1'
DOMAIN='LC-EXP-010-CHAIN-GENESIS-1'
STEP_DOMAIN='LC-EXP-010-CHAIN-STEP-1'
MAX_STEPS=32


def hash_ok(s):
    ensure(type(s) is str and re.fullmatch('[a-f0-9]{64}',s) is not None, 'invalid SHA-256 commitment')


def genesis(start):
    hash_ok(start)
    return sha({'domain':DOMAIN,'schema':SCHEMA,'start_packet_sha256':start})


def step_commitment(i,prior,receipt_hash):
    ensure(type(i) is int and 0<=i<MAX_STEPS,'invalid step ordinal')
    hash_ok(prior)
    hash_ok(receipt_hash)
    return sha({'domain':STEP_DOMAIN,'ordinal':i,'prior_tip':prior,'receipt_sha256':receipt_hash})


def witness_comparison(before,after):
    """Distinguish sample order, selected indices, content and provenance at shared indices."""
    bw=before['witnesses'];aw=after['witnesses']
    bi=[w['index_decimal'] for w in bw];ai=[w['index_decimal'] for w in aw]
    bm={w['index_decimal']:w['witness'] for w in bw}
    am={w['index_decimal']:w['witness'] for w in aw}
    common=sorted(set(bm)&set(am),key=int)
    def semantic_witness_content(w):
        # Ledger and root commitments bind the audit envelope. Their change alone
        # does not mean the selected route, decision or evidence actually changed.
        return {k:v for k,v in w.items() if k not in ('ledger_commitment','root_id')}
    return {
        'sample_order_changed':not exact(bi,ai),
        'sample_index_set_changed':set(bi)!=set(ai),
        'shared_sample_payload_changed':any(not exact(bm[i],am[i]) for i in common),
        'shared_sample_content_changed':any(not exact(semantic_witness_content(bm[i]),semantic_witness_content(am[i])) for i in common),
        'shared_sample_ledger_binding_changed':any(not exact(bm[i].get('ledger_commitment'),am[i].get('ledger_commitment')) for i in common),
        'shared_sample_evidence_ids_changed':any(not exact(bm[i]['evidence_ids'],am[i]['evidence_ids']) for i in common),
        'shared_sample_indices':common,
        'sampled_scope_only':True,
    }


def build_chain(receipts):
    ensure(type(receipts) is list and 1<=len(receipts)<=MAX_STEPS,'step count outside declared bounds')
    start=receipts[0]['before']['packet_sha256']
    tip=genesis(start)
    steps=[]
    for i,receipt in enumerate(receipts):
        commit=step_commitment(i,tip,receipt['receipt_sha256'])
        steps.append({'ordinal':i,'prior_tip':tip,'receipt':copy.deepcopy(receipt),'step_sha256':commit})
        tip=commit
    chain={'schema':SCHEMA,'start_packet_sha256':start,'steps':steps,'chain_tip':tip}
    verify_chain(chain)
    return chain


def verify_chain(chain,trusted_start_packet_hash=None,trusted_chain_tip=None):
    ensure(type(chain) is dict and set(chain)=={'schema','start_packet_sha256','steps','chain_tip'},'chain keys invalid')
    ensure(chain['schema']==SCHEMA,'chain schema invalid')
    hash_ok(chain['start_packet_sha256']);hash_ok(chain['chain_tip'])
    if trusted_start_packet_hash is not None:
        hash_ok(trusted_start_packet_hash)
        ensure(trusted_start_packet_hash==chain['start_packet_sha256'],'trusted start mismatch')
    if trusted_chain_tip is not None:
        hash_ok(trusted_chain_tip)
        ensure(trusted_chain_tip==chain['chain_tip'],'trusted chain tip mismatch')
    steps=chain['steps']
    ensure(type(steps) is list and 1<=len(steps)<=MAX_STEPS,'step count outside declared bounds')
    tip=genesis(chain['start_packet_sha256'])
    previous_after=None
    summaries=[]
    for i,step in enumerate(steps):
        ensure(type(step) is dict and set(step)=={'ordinal','prior_tip','receipt','step_sha256'},'step keys invalid')
        ensure(type(step['ordinal']) is int and step['ordinal']==i,'incorrect step order')
        ensure(step['prior_tip']==tip,'chain predecessor commitment mismatch')
        receipt=step['receipt']
        evidence=verify_reassessment(receipt)
        before=receipt['before'];after=receipt['after']
        if i==0:
            ensure(before['packet_sha256']==chain['start_packet_sha256'],'first packet does not match start')
        else:
            ensure(previous_after is not None and before['packet_sha256']==previous_after['packet_sha256']
                   and exact(before,previous_after),'adjacent historical packet mismatch')
        target=step_commitment(i,tip,receipt['receipt_sha256'])
        ensure(step['step_sha256']==target,'step commitment mismatch')
        tip=target
        summaries.append({
            'ordinal':i,'before_packet_sha256':before['packet_sha256'],
            'after_packet_sha256':after['packet_sha256'],
            'before_value':evidence['before_value'],'after_value':evidence['after_value'],
            'scalar_truth_changed':evidence['scalar_truth_changed'],
            'root_content_changed':evidence['root_content_changed'],
            'ledger_commitment_changed':evidence['ledger_commitment_changed'],
            'appended_records':evidence['appended_records'],
            'witness_sample':witness_comparison(before,after),
            'step_sha256':tip,
        })
        previous_after=after
    ensure(chain['chain_tip']==tip,'chain tip mismatch')
    return {
        'verified':True,'relation':'DECLARED_ORDERED_FIXED_QUERY_REASSESSMENT_CHAIN',
        'step_count':len(steps),'start_packet_sha256':chain['start_packet_sha256'],
        'final_packet_sha256':previous_after['packet_sha256'],
        'chain_tip':tip,
        'commitment_matches':{
            'supplied_start_packet':trusted_start_packet_hash is not None,
            'supplied_whole_chain_tip':trusted_chain_tip is not None,
        },
        'anchor_origin':'CALLER_SUPPLIED_NOT_INDEPENDENTLY_CHECKED' if (
            trusted_start_packet_hash is not None or trusted_chain_tip is not None) else 'NOT_SUPPLIED',
        'source_authentication':'NOT_ESTABLISHED',
        'external_event_completeness':'NOT_ESTABLISHED',
        'summary':summaries,
        'claim_ceiling':'verified declared ordered pairwise relation chain, full replay; not authenticated real-world history, complete event inventory, semantic discovery or compact proof',
    }
