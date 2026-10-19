"""Verify frozen reconstructed LC009 and load its portable replay dependencies."""
import hashlib
import importlib.util
import stat
from pathlib import Path, PurePosixPath
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
PARENT='LC-EXP-009-RECONSTRUCTED-RUNNABLE.zip'
PARENT_SHA256='d2068668386340be540c2b943bebef4078a124e50a54e0692e5d310970af813b'


def verify_manifest(root):
    root=Path(root).resolve()
    entries={}
    for line in (root/'MANIFEST.sha256').read_text(encoding='utf-8').splitlines():
        digest,rel=line.split('  ',1)
        p=PurePosixPath(rel)
        target=(root/rel).resolve()
        if p.is_absolute() or '..' in p.parts or '\\' in rel or root not in target.parents or rel in entries:
            raise ValueError('unsafe or duplicate manifest entry')
        entries[rel]=digest
        if hashlib.sha256(target.read_bytes()).hexdigest()!=digest:
            raise ValueError('manifest digest mismatch: '+rel)
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name!='MANIFEST.sha256' and '__pycache__' not in p.parts}
    if actual!=set(entries):
        raise ValueError('manifest file set mismatch')
    return len(entries)


def load_frozen(tmp):
    archive=ROOT/'history'/PARENT
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=PARENT_SHA256:
        raise ValueError('frozen LC009 zip identity mismatch')
    tmp=Path(tmp)
    with zipfile.ZipFile(archive) as z:
        names=set()
        for x in z.infolist():
            p=PurePosixPath(x.filename)
            if p.is_absolute() or '..' in p.parts or '\\' in x.filename or x.filename in names:
                raise ValueError('unsafe zip content')
            names.add(x.filename)
            if stat.S_ISLNK(x.external_attr>>16):
                raise ValueError('symlink in archive')
        z.extractall(tmp)
    path=tmp/'LC-EXP-009-RELATIONAL-AUDIT-001'
    if verify_manifest(path)!=39:
        raise ValueError('incorrect LC009 manifest entry count')
    sys.path.insert(0,str(path/'src'))
    sys.path.insert(0,str(path))
    spec=importlib.util.spec_from_file_location('lc009_frozen_bootstrap',path/'src'/'bootstrap.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    parent, manifests = module.resolve(tmp/'frozen_dependencies')
    return path,{'LC009':39,'LC008':manifests['08']}
