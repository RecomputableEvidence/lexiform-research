"""Verify the shipped file inventory before executing commands that regenerate results."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from bootstrap import verify_manifest

if __name__ == '__main__':
    print(str(verify_manifest(ROOT)) + ' files match the distribution manifest')