import os,sys,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent
sys.path[:0]=[str(root/'src'),str(root/'tests')]
from test_lc011 import assess
if __name__=='__main__':
    result=assess()
    (root/'results').mkdir(exist_ok=True)
    (root/'results'/'test_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
