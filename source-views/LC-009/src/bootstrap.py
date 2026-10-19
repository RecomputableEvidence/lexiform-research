"""Resolve immutable LC008 before importing its frozen replay instruments."""
import hashlib
from pathlib import Path, PurePosixPath
import stat
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PARENT_SHA256 = '7af3bd382abf3289d4282a9be3d36dd10092ad9bbe0e19b5b7d15b68a85c1ddd'
PARENT_NAME = 'LC-EXP-008-PORTABLE-AUDIT-001'


def verify_manifest(root):
    root = Path(root).resolve()
    listed = set()
    for line in (root / 'MANIFEST.sha256').read_text(encoding='utf-8').splitlines():
        digest, rel = line.split('  ', 1)
        p = PurePosixPath(rel)
        target = (root / rel).resolve()
        if p.is_absolute() or '..' in p.parts or '\\' in rel or root not in target.parents:
            raise ValueError('unsafe manifest path')
        if rel in listed:
            raise ValueError('duplicate manifest path')
        listed.add(rel)
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise ValueError('manifest mismatch: ' + rel)
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*')
              if p.is_file() and p.name != 'MANIFEST.sha256' and '__pycache__' not in p.parts}
    if actual != listed:
        raise ValueError('manifest file set mismatch')
    return len(listed)


def resolve(destination):
    archive = ROOT / 'history' / (PARENT_NAME + '.zip')
    if hashlib.sha256(archive.read_bytes()).hexdigest() != PARENT_SHA256:
        raise ValueError('LC008 archive hash mismatch')
    destination = Path(destination)
    with zipfile.ZipFile(archive) as z:
        for entry in z.infolist():
            p = PurePosixPath(entry.filename)
            if p.is_absolute() or '..' in p.parts or '\\' in entry.filename:
                raise ValueError('unsafe archive path')
            if stat.S_ISLNK(entry.external_attr >> 16):
                raise ValueError('archive symlink')
        z.extractall(destination)
    parent = destination / PARENT_NAME
    n = verify_manifest(parent)
    sys.path.insert(0, str(parent / 'src'))
    from dependencies import load_dependency_paths
    manifests = load_dependency_paths(destination / 'inherited')
    return parent, {'08': n, **manifests}