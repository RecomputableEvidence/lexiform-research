#!/usr/bin/env python3
"""Publish reviewed LexiFORM baseline to existing empty/minimally initialized GitHub repository.

This script never creates a repository, force-pushes, or edits original source archives.
Requires explicit --publish --confirmed-rights; default is no network/no mutation.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REMOTE = "https://github.com/RecomputableEvidence/lexiform-research.git"
TAG = "lexiform-research-baseline-v0.1.2"
EXPECTED_EXISTING_ROOT = {"README.md", "LICENSE"}


def run(*args, cwd=None, capture=True):
    p = subprocess.run(args, cwd=cwd, text=True, capture_output=capture, check=False)
    if p.returncode:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(args)}\n{p.stdout[-1400:] if p.stdout else ''}\n{p.stderr[-1800:] if p.stderr else ''}")
    return p.stdout.strip() if capture else ""


def verify_local():
    p = run(sys.executable, str(ROOT / 'tools' / 'verify_sources.py'), cwd=ROOT)
    if '"archive_count_verified": 13' not in p or '"manifest_entries_verified": 288' not in p:
        raise RuntimeError('Unexpected experiment verifier summary')
    sums = ROOT / 'RELEASE_SHA256SUMS.txt'
    listed = {}
    for line in sums.read_text(encoding='utf-8').splitlines():
        digest, filename = line.split('  ', 1)
        filename = filename.strip()
        target = ROOT / filename
        if filename in listed or not target.is_file() or target.resolve().is_relative_to(ROOT.resolve()) is False:
            raise RuntimeError(f'Invalid manifest path: {filename}')
        got = hashlib.sha256(target.read_bytes()).hexdigest()
        if got != digest:
            raise RuntimeError(f'Release SHA mismatch: {filename}: {digest} != {got}')
        listed[filename] = got
    actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and p != sums}
    if set(listed) != actual:
        raise RuntimeError(f'Release file-set mismatch; missing={sorted(actual - set(listed))}; extras={sorted(set(listed) - actual)}')
    print(f"LOCAL_VERIFIED archive_count=13 internal_entries=288 release_files={len(listed)}")
    return listed


def prepare_existing_repository(remote: str, workdir: Path):
    if workdir.exists():
        raise RuntimeError(f'Publication worktree already exists (refusing overwrite): {workdir}')
    if shutil.which('git') is None:
        raise RuntimeError('Git is not installed. Use Git for Windows and authenticate with GitHub.')
    user = run('git', 'config', '--global', '--get', 'user.name')
    email = run('git', 'config', '--global', '--get', 'user.email')
    if not user or not email:
        raise RuntimeError('Configure git user.name and user.email before publishing')
    run('git', 'clone', '--branch', 'main', '--single-branch', remote, str(workdir))
    existing = {p.name for p in workdir.iterdir() if p.name != '.git'}
    if not existing.issubset(EXPECTED_EXISTING_ROOT) or 'README.md' not in existing:
        raise RuntimeError(f'Unexpected public files already on main; refusing overwrite: {sorted(existing)}')
    readme = (workdir / 'README.md').read_text(encoding='utf-8')
    if not readme.startswith('# LexiFORM'):
        raise RuntimeError('Existing public README identity mismatch; refusing overwrite')
    return run('git', 'rev-parse', 'HEAD', cwd=workdir)


def publish(remote: str, workdir: Path, tag: str=TAG):
    listed = verify_local()
    prior = prepare_existing_repository(remote, workdir)
    # Preserve remote .git. Copy content, including dotfiles and binary archives, exactly.
    for item in ROOT.iterdir():
        if item.name == '.git':
            raise RuntimeError('Release source unexpectedly contains .git; do not publish')
        dest = workdir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        elif item.is_file():
            shutil.copy2(item, dest)
    run('git', 'add', '-A', cwd=workdir)
    # Historical archived source views deliberately preserve original formatting, including
    # pre-existing trailing whitespace. Lint only release-authored front matter.
    run('git', 'diff', '--cached', '--check', '--', 'README.md', 'LICENSE', 'docs/RELEASE_GATES.md', 'docs/PUBLICATION_AUTHORIZATION_20261018.md', 'scripts/README.md', 'scripts/publish_github.ps1', 'tools/publish_existing_repo.py', cwd=workdir)
    changed = run('git', 'diff', '--cached', '--name-only', cwd=workdir)
    if not changed or 'archives/LC-EXP-013-SCOPED-RELATIONSHIP-001.zip' not in changed:
        raise RuntimeError('Release population not staged, or expected source archive absent')
    run('git', 'commit', '-m', 'release: publish rights-reviewed LexiFORM LC001–LC013 research baseline v0.1.2', cwd=workdir)
    commit = run('git', 'rev-parse', 'HEAD', cwd=workdir)
    run('git', 'fetch', 'origin', 'main', cwd=workdir)
    if run('git', 'rev-parse', 'origin/main', cwd=workdir) != prior:
        raise RuntimeError('Remote main changed during publication. Stop and reconcile; do not force push.')
    remote_tag = run('git', 'ls-remote', '--tags', 'origin', f'refs/tags/{tag}', cwd=workdir)
    if remote_tag:
        raise RuntimeError('Release tag already exists: '+tag)
    # First network mutation; fast-forward only; no force ever.
    run('git', 'push', 'origin', 'HEAD:refs/heads/main', cwd=workdir)
    remote_head = run('git', 'ls-remote', 'origin', 'refs/heads/main', cwd=workdir).split()[0]
    if remote_head != commit:
        raise RuntimeError('Push succeeded but remote head verification does not match; no tag was created')
    run('git', 'tag', '-a', tag, '-m', 'Verified LexiFORM LC001–LC013 historical research baseline', cwd=workdir)
    run('git', 'push', 'origin', f'refs/tags/{tag}:refs/tags/{tag}', cwd=workdir)
    remote_tag_after = run('git', 'ls-remote', '--tags', 'origin', f'refs/tags/{tag}', cwd=workdir)
    if not remote_tag_after:
        raise RuntimeError('GitHub release tag push cannot be confirmed')
    receipt = {
        'schema':'lexiform-research-published-baseline-receipt-001',
        'observed_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'repository':'RecomputableEvidence/lexiform-research',
        'main_commit':commit,
        'original_main_commit':prior,
        'tag':tag,
        'experiment_archives':13,
        'native_manifest_entries':288,
        'release_files_hashed':len(listed),
        'release_sha256s_sha256':hashlib.sha256((ROOT/'RELEASE_SHA256SUMS.txt').read_bytes()).hexdigest(),
        'doi':None,'orcid_work_registration':None,
        'scope':'Historic synthetic experiment artifacts; publication is not independent validation',
    }
    out = workdir.parent / 'LEXIFORM_PUBLICATION_RECEIPT_v0.1.2.json'
    out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(('PUBLISHED_VERIFIED https://github.com/RecomputableEvidence/lexiform-research' if remote == REMOTE else 'LOCAL_SIMULATION_VERIFIED '+remote))
    print('COMMIT='+commit)
    print('TAG='+tag)
    print('RECEIPT='+str(out))
    return receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish',action='store_true',help='Create a commit and push public source archives')
    parser.add_argument('--confirmed-rights',action='store_true',help='Operator approval of code/archive distribution and MIT license')
    a=parser.parse_args()
    try:
        verify_local()
        if not a.publish:
            print('PREFLIGHT_ONLY; no network or repo changes. To publish, add --publish --confirmed-rights.')
            return 0
        if not a.confirmed_rights:
            raise RuntimeError('Rights authorization flag missing; no publication')
        publish(REMOTE, ROOT.parent/'lexiform-release-git-worktree')
        return 0
    except Exception as exc:
        print('PUBLICATION_STOP: '+str(exc),file=sys.stderr)
        return 1

if __name__=='__main__':
    raise SystemExit(main())
