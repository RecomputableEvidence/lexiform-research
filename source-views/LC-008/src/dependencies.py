"""Resolve the frozen predecessor chain; never execute unverified dependency archives."""
import hashlib
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/'history'/'LC-EXP-007-APPEND-BOUND-AUDIT-001.zip'
# This digest identifies the exact LC-007 file supplied inside the original LexiFORM.zip.
PARENT_SHA256='b47645864323e90e95ce0408d1602cc36ef801dcbc78c244bfdf0d5954d4ac00'


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def safe_extract(archive, destination):
    destination=Path(destination)
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            path=PurePosixPath(info.filename)
            if path.is_absolute() or '..' in path.parts or '\\' in info.filename:
                raise ValueError('unsafe archive path')
            if (info.external_attr >> 16) & 0o170000 == stat.S_IFLNK:
                raise ValueError('symlink not allowed')
        z.extractall(destination)


def verify_manifest(package):
    p=Path(package)
    lines=(p/'MANIFEST.sha256').read_text(encoding='utf-8').splitlines()
    for line in lines:
        h,rel=line.split('  ',1)
        path=PurePosixPath(rel)
        if path.is_absolute() or '..' in path.parts:raise ValueError('unsafe manifest path')
        if sha_bytes((p/rel).read_bytes())!=h:raise ValueError('frozen manifest mismatch: '+rel)
    return len(lines)


def load_dependency_paths(destination):
    if sha_bytes(ARCHIVE.read_bytes())!=PARENT_SHA256:
        raise ValueError('frozen LC-007 archive hash mismatch')
    destination=Path(destination)
    safe_extract(ARCHIVE,destination)
    p7=destination/'LC-EXP-007-APPEND-BOUND-AUDIT-001'
    n7=verify_manifest(p7)
    p6z=p7/'history'/'LC-EXP-006-DEPENDENCY-BOUND-REUSE-001.zip'
    safe_extract(p6z,destination)
    p6=destination/'LC-EXP-006-DEPENDENCY-BOUND-REUSE-001'
    n6=verify_manifest(p6)
    p5z=p6/'history'/'LC-EXP-005-LAZY-COMPOSITION-001.zip'
    safe_extract(p5z,destination)
    p5=destination/'LC-EXP-005-LAZY-COMPOSITION-001'
    n5=verify_manifest(p5)
    p4z=p5/'history'/'LC-EXP-004-DESCRIPTOR-PRESSURE-001.zip'
    safe_extract(p4z,destination)
    p4=destination/'LC-EXP-004-DESCRIPTOR-PRESSURE-001'
    n4=verify_manifest(p4)
    p3z=p4/'history'/'LC-EXP-003-EVIDENCE-BOUND-EXECUTED.zip'
    safe_extract(p3z,destination)
    p3=destination/'LC-EXP-003'
    n3=verify_manifest(p3)
    dirs=[p7/'src',p6/'src',p5/'src',p4/'src',p3/'src']
    for d in reversed(dirs):sys.path.insert(0,str(d))
    return {'07':n7,'06':n6,'05':n5,'04':n4,'03':n3}
