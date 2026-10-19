"""Reproduce bounded negative probes, including an alternative valid but unanchored history."""
import copy
import json
from pathlib import Path
import sys
import tempfile
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from bootstrap import load_frozen


def main():
    out=[]
    with tempfile.TemporaryDirectory(prefix='lc010-pressure-') as work:
        load_frozen(work)
        sys.path.insert(0,str(ROOT/'tests'))
        from test_chain import setup_chain
        from chain_audit import build_chain,verify_chain,step_commitment
        from relational_audit import make_reassessment
        (a,b,c,d),chain=setup_chain()
        def check(label,value,expected):
            try:
                result=verify_chain(value)
                status='PASS' if expected=='PASS' else 'UNEXPECTED_ACCEPT'
                reason=result['claim_ceiling']
            except Exception as error:
                status='REJECT' if expected=='REJECT' else 'UNEXPECTED_REJECT'
                reason=str(error)
            out.append({'case':label,'expected':expected,'observed':status,'reason':reason})
        check('intact_chain',chain,'PASS')
        altered=copy.deepcopy(chain)
        altered['steps'][0]['receipt']['after']['expected']['value']='F'
        check('changed_result_without_rehash',altered,'REJECT')
        altered=copy.deepcopy(chain)
        altered['steps'][0],altered['steps'][1]=altered['steps'][1],altered['steps'][0]
        check('swapped_events',altered,'REJECT')
        altered=copy.deepcopy(chain)
        altered['steps'].pop(1)
        altered['steps'][1]['ordinal']=1
        altered['steps'][1]['prior_tip']=altered['steps'][0]['step_sha256']
        altered['steps'][1]['step_sha256']=step_commitment(1,altered['steps'][1]['prior_tip'],altered['steps'][1]['receipt']['receipt_sha256'])
        altered['chain_tip']=altered['steps'][1]['step_sha256']
        check('gap_between_valid_pair_receipts',altered,'REJECT')
        shorter=build_chain([make_reassessment(b,c),make_reassessment(c,d)])
        check('shorter_self_consistent_unanchored_subsequence',shorter,'PASS')
        try:
            verify_chain(shorter,trusted_chain_tip=chain['chain_tip'])
            out.append({'case':'shorter_subsequence_wrong_external_tip','expected':'REJECT','observed':'UNEXPECTED_ACCEPT'})
        except ValueError as e:
            out.append({'case':'shorter_subsequence_wrong_external_tip','expected':'REJECT','observed':'REJECT','reason':str(e)})
    return out
if __name__=='__main__':
    report=main()
    print(json.dumps(report,indent=2,sort_keys=True))
    raise SystemExit(0 if all(x['expected']==x['observed'] for x in report) else 1)
