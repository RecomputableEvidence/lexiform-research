#!/usr/bin/env python3
"""Read-only, version-specific verifier for the LexiFORM v0.1.2 Zenodo ZIP.

No file extraction, modification, remote access, dependency installation or model execution.
Default --mode strict preserves the five original release-manifest hash failures.
--mode erratum accepts ONLY the five pinned newline-equivalent cases, reports
strict failure explicitly, and rejects unrecognized byte differences.
"""
import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

ZIP_SHA256 = 'd6346b5dc8784aefc253076bc95876f0273ef36883c48442ff1064af2f4781ed'
MANIFEST_SHA256 = '140595142eb5298038fcd01e97d52b6fdbd49a2c41c4f45c9155c39f2b3c6ef7'
EXPECTED_FILES = 230
EXPECTED_STRICT_MATCHES = 225
EXCEPTIONS = {
    'scripts/publish_github.ps1': {
        'sha256': '63d91ed06513587fbd072f8b8763cab8db680db23552638a5576cd80d5559b6e',
        'transformation': 'CRLF_to_LF',
    },
    **{
        f'source-views/{ref}/methods/lens_removal.txt': {
            'sha256': '85ddb02fc84c38f26ef8fa6c5e8b49ccbf14244608d1094b25824fe8b3a0a4ce',
            'transformation': 'LF_to_CRLF',
        }
        for ref in ('LC-008', 'LC-009', 'LC-012', 'LC-013')
    },
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check(zip_path):
    result = {
        'zip_path': str(zip_path),
        'strict_manifest': 'FAIL',
        'bounded_newline_exception': 'FAIL',
        'manifest_entries': 0, 'strict_matches': 0, 'explained_mismatches': 0,
        'unexplained_mismatches': [], 'errors': [],
    }
    if not zip_path.is_file():
        result['errors'].append('ZIP path does not exist')
        return result
    result['zip_sha256'] = digest(zip_path.read_bytes())
    if result['zip_sha256'] != ZIP_SHA256:
        result['errors'].append('Archive SHA-256 differs from pinned owner-supplied downloaded snapshot')
    try:
        with zipfile.ZipFile(zip_path) as z:
            bad_member = z.testzip()
            if bad_member:
                result['errors'].append(f'ZIP CRC failure at {bad_member}')
            all_files = [n for n in z.namelist() if not n.endswith('/')]
            manifest_paths = [n for n in all_files if n.endswith('/RELEASE_SHA256SUMS.txt')]
            if len(manifest_paths) != 1:
                result['errors'].append('Expected exactly one root RELEASE_SHA256SUMS.txt')
                return result
            path = manifest_paths[0]
            prefix = path[:-len('RELEASE_SHA256SUMS.txt')]
            if not prefix or any(not n.startswith(prefix) for n in all_files):
                result['errors'].append('Unexpected archive-root layout')
                return result
            raw_manifest = z.read(path)
            if digest(raw_manifest) != MANIFEST_SHA256:
                result['errors'].append('Manifest bytes differ from known original')
            declared = {}
            for line in raw_manifest.decode('utf-8').splitlines():
                match = re.fullmatch(r'([0-9a-f]{64})  (.+)', line)
                if not match:
                    result['errors'].append('Malformed manifest entry')
                    continue
                sha, rel = match.groups()
                if rel in declared or rel.startswith('/') or '..' in rel.split('/') or '\\' in rel:
                    result['errors'].append(f'Invalid or duplicate relative path: {rel}')
                declared[rel] = sha
            result['manifest_entries'] = len(declared)
            if len(declared) != EXPECTED_FILES:
                result['errors'].append(f'Manifest count is {len(declared)} not {EXPECTED_FILES}')
            files = {n[len(prefix):] for n in all_files if n.startswith(prefix)} - {'RELEASE_SHA256SUMS.txt'}
            if files != set(declared):
                result['errors'].append('Archive/manifest file-name set mismatch')
            for rel, expected in declared.items():
                absolute = prefix + rel
                if absolute not in z.namelist():
                    result['unexplained_mismatches'].append(rel + ': missing')
                    continue
                data = z.read(absolute)
                observed = digest(data)
                if observed == expected:
                    result['strict_matches'] += 1
                    continue
                exception = EXCEPTIONS.get(rel)
                if not exception or observed != exception['sha256']:
                    result['unexplained_mismatches'].append(rel + ': unpinned hash mismatch')
                    continue
                transform = exception['transformation']
                if transform == 'CRLF_to_LF':
                    # Ensure all newlines are CRLF, then replace only CRLF bytes.
                    if b'\n' not in data or b'\r\n' not in data or data.replace(b'\r\n', b'').find(b'\n') != -1:
                        result['unexplained_mismatches'].append(rel + ': not purely CRLF')
                        continue
                    normalized = data.replace(b'\r\n', b'\n')
                else:
                    # Ensure all newlines are LF, with no CR bytes.
                    if b'\n' not in data or b'\r' in data:
                        result['unexplained_mismatches'].append(rel + ': not purely LF')
                        continue
                    normalized = data.replace(b'\n', b'\r\n')
                if digest(normalized) == expected:
                    result['explained_mismatches'] += 1
                else:
                    result['unexplained_mismatches'].append(rel + ': newline-normalized hash mismatch')
            if result['strict_matches'] == EXPECTED_FILES and not result['errors']:
                result['strict_manifest'] = 'PASS'
            if (
                not result['errors'] and not result['unexplained_mismatches']
                and result['strict_matches'] == EXPECTED_STRICT_MATCHES
                and result['explained_mismatches'] == len(EXCEPTIONS)
                and result['manifest_entries'] == EXPECTED_FILES
            ):
                result['bounded_newline_exception'] = 'PASS'
    except (OSError, ValueError, UnicodeDecodeError, zipfile.BadZipFile, RuntimeError) as exc:
        result['errors'].append(f'Cannot verify archive: {exc}')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('zip_path', type=Path)
    parser.add_argument('--mode', choices=['strict','erratum'], default='strict',
                        help='strict hash match required by default; explicit erratum mode allows only five pinned newline cases')
    args = parser.parse_args(argv)
    report = check(args.zip_path)
    report['mode'] = args.mode
    report['accepted'] = report['strict_manifest'] == 'PASS' if args.mode == 'strict' else (
        report['strict_manifest'] == 'PASS' or report['bounded_newline_exception'] == 'PASS')
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report['accepted'] else 1


if __name__ == '__main__':
    sys.exit(main())
