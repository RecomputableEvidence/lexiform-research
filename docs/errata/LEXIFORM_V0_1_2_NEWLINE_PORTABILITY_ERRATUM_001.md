# LexiFORM v0.1.2 — Additive newline-portability erratum 001

**Date recorded:** 2026-10-19  
**Standing:** Additive postpublication integrity erratum; no replacement of source evidence, Zenodo files, historical release manifest, Git tag, or DOI.  
**Scope:** Exact owner-supplied ZIP represented as a download of the published LexiFORM v0.1.2 software archive.  
**Original publication:** [Zenodo version DOI 10.5281/zenodo.23466511](https://doi.org/10.5281/zenodo.23466511).  
**Frozen Git tag:** [`lexiform-research-baseline-v0.1.2`](https://github.com/RecomputableEvidence/lexiform-research/releases/tag/lexiform-research-baseline-v0.1.2).  
**Issue record:** [LexiFORM issue #2](https://github.com/RecomputableEvidence/lexiform-research/issues/2).

## Finding

An independent read-only examination of the owner-supplied ZIP found **225/230** byte-exact matches against the original `RELEASE_SHA256SUMS.txt`. **Five files do not match the manifest at the byte level.** The five differences are exhausted by newline encoding; applying the specific transformation in the table below reproduces each original declared hash. This explanation **does not convert the original strict check into a 230/230 PASS** and does not establish that the altered bytes are identical.

The ZIP itself passes CRC integrity. Separately, **13/13** indexed original experiment ZIPs match their archived registry SHA-256 and size values and pass ZIP CRC checks; **288/288** entries in their native internal manifests recompute. The two additional indexed historical examination ZIPs also match their archived SHA-256 values and pass CRC. These latter findings were obtained from the original read-only postpublication examination, not from the limited outer-release helper supplied with this erratum.

**Downloaded snapshot identity** (submitted by the owner; direct server-side retrieval not attested):

- Filename: `lexiform-research-lexiform-research-baseline-v0.1.2.zip`
- Bytes: `4273191`
- SHA-256: `d6346b5dc8784aefc253076bc95876f0273ef36883c48442ff1064af2f4781ed`
- Embedded `RELEASE_SHA256SUMS.txt` SHA-256: `140595142eb5298038fcd01e97d52b6fdbd49a2c41c4f45c9155c39f2b3c6ef7`

## Exact manifest discrepancies

| Original release path | Original manifest SHA-256 | Observed downloaded SHA-256 | Exact transformation reproducing original SHA-256 |
|---|---|---|---|
| `scripts/publish_github.ps1` | `089eb59d9c303b84affc914830c2ee5869c88724f8954924044b72cf6931689b` | `63d91ed06513587fbd072f8b8763cab8db680db23552638a5576cd80d5559b6e` | Downloaded CRLF → LF |
| `source-views/LC-008/methods/lens_removal.txt` | `f9a6c997a30148a9f84998c2817b2efca21e16445dc2db4b2dbd261d9499f184` | `85ddb02fc84c38f26ef8fa6c5e8b49ccbf14244608d1094b25824fe8b3a0a4ce` | Downloaded LF → CRLF |
| `source-views/LC-009/methods/lens_removal.txt` | `f9a6c997a30148a9f84998c2817b2efca21e16445dc2db4b2dbd261d9499f184` | `85ddb02fc84c38f26ef8fa6c5e8b49ccbf14244608d1094b25824fe8b3a0a4ce` | Downloaded LF → CRLF |
| `source-views/LC-012/methods/lens_removal.txt` | `f9a6c997a30148a9f84998c2817b2efca21e16445dc2db4b2dbd261d9499f184` | `85ddb02fc84c38f26ef8fa6c5e8b49ccbf14244608d1094b25824fe8b3a0a4ce` | Downloaded LF → CRLF |
| `source-views/LC-013/methods/lens_removal.txt` | `f9a6c997a30148a9f84998c2817b2efca21e16445dc2db4b2dbd261d9499f184` | `85ddb02fc84c38f26ef8fa6c5e8b49ccbf14244608d1094b25824fe8b3a0a4ce` | Downloaded LF → CRLF |

The tagged `.gitattributes` specifies `*.ps1 text eol=crlf` but does not specify a `*.txt` newline rule. This is relevant packaging context, **not evidence of which application or step generated the five differences**. The direction of normalization differs across the paths; there is no justified global “normalize all newlines and treat hashes as equal” rule.

## Portable, bounded verification

A new *separate*, read-only helper is provided at [`scripts/verify_v012_zenodo_newline_erratum.py`](../../scripts/verify_v012_zenodo_newline_erratum.py). The helper does not amend or replace the historical verifier or original release checksum file.

```powershell
# Preserve the historical strict byte check: expected nonzero exit status (225/230 exact).
py -3 scripts/verify_v012_zenodo_newline_erratum.py "C:\path\to\lexiform-research-lexiform-research-baseline-v0.1.2.zip" --mode strict

# Separately request a bounded recognition of the five documented newline variants.
py -3 scripts/verify_v012_zenodo_newline_erratum.py "C:\path\to\lexiform-research-lexiform-research-baseline-v0.1.2.zip" --mode erratum
```

- The helper pins the complete downloaded ZIP hash and original embedded manifest hash, requires exactly 230 manifest entries, verifies ZIP CRC, checks that all listed files are present, and tests every byte-exact SHA-256.
- `strict` mode is **the default** and exits nonzero for the known release, preserving `STRICT_RELEASE_MANIFEST_FAIL`.
- `erratum` mode exits zero only if exactly **225 strict matches and all five pinned newline-only differences** are confirmed with **zero unexplained mismatches**; it continues to report strict failure.
- Neither mode extracts, rewrites, normalizes, replaces, or republishes any file. The transformed bytes are ephemeral inputs to a comparison only.
- The helper is not a reenactment of experiments or an independent authenticity attestation of the uploaded ZIP's Zenodo origin.

**Local offline regression tests (2026-10-19):** Original snapshot: `strict` exit 1, `erratum` exit 0, five explained; modified README snapshot rejected; alternative snapshot with one newline discrepancy removed also rejected due to differing pinned archive identity and count. This validates version-specific recognition rather than generalized acceptance of arbitrary hashes.

## Claim boundary and historical preservation

**Do not rewrite these outcomes:**

- **PASS:** downloaded ZIP CRC; 13 archived experiment ZIP identities/CRC; 288 internal experiment-manifest entries; two additional historical examination ZIP identities/CRC; **225** outer release manifest entries byte-exact.
- **FAIL:** outer release manifest **230/230 strict byte equality**, because five files differ in newline bytes.
- **EXPLAINED:** exactly five pinned newline-equivalent versions reproduce their earlier recorded manifest digests; this is not an authorized replacement of SHA-256 byte identity.
- **NOT TESTED:** fresh LexiFORM experiment execution, semantic validity, independent authorship/authenticity attestation, or publisher-origin authentication beyond the owner-supplied copy.

The published Zenodo v0.1.2 archive, version DOI, frozen Git tag, `RELEASE_SHA256SUMS.txt`, archived experiment files and negative results **remain unchanged**. This erratum is additive, scoped to the described postpublication comparison, and does not imply a new LexiFORM release, a new Zenodo version, or an alteration of the NGAST diagnostic publication.
