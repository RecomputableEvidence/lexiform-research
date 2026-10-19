"""Verify all frozen distribution members against the SHA-256 manifest."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from bootstrap import verify_manifest
if __name__=='__main__':
    print(f'{verify_manifest(Path(__file__).resolve().parent)} manifest members match')
