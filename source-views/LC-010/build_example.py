"""Create a synthetic three-step chain; not an authenticated external history."""
import json
from pathlib import Path
import sys
import tempfile
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from bootstrap import load_frozen


def main():
    with tempfile.TemporaryDirectory(prefix='lc010-example-') as temp:
        load_frozen(temp)
        sys.path.insert(0,str(ROOT/'tests'))
        from test_chain import setup_chain
        from chain_audit import verify_chain
        _, chain = setup_chain()
        verified = verify_chain(chain)
    (ROOT/'examples').mkdir(exist_ok=True)
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'examples'/'three_stage_chain.json').write_text(json.dumps(chain,sort_keys=True,indent=2)+'\n')
    (ROOT/'results'/'verified_chain.json').write_text(json.dumps(verified,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'verified':verified['verified'],'steps':verified['step_count'],
                      'chain_tip':verified['chain_tip']},indent=2))
if __name__=='__main__':main()
