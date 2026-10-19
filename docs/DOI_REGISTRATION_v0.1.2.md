# DOI registration and source-bound status — LexiFORM baseline v0.1.2

**Document date (UTC):** 2026-10-19  
**Document class:** POST-PUBLICATION CITATION / CHECKPOINT; NON-AUTHORITATIVE ABOUT EXPERIMENT STANDING  
**Effect on tagged release:** NONE

## Identifiers

| Object / system | Identifier | Evidentiary basis |
| --- | --- | --- |
| GitHub repository | `RecomputableEvidence/lexiform-research` | Public repository, checked through GitHub repository/commit API |
| Immutable tagged source | [`lexiform-research-baseline-v0.1.2`](https://github.com/RecomputableEvidence/lexiform-research/releases/tag/lexiform-research-baseline-v0.1.2) | GitHub annotated tag dereferences to the exact frozen commit |
| Source commit | `9c1ccdd32ed0d3e130f173eaed2a10e26457abdb` | GitHub API; 231 tracked files and 13 frozen experiment ZIPs |
| Zenodo **release-specific DOI displayed by integration** | [`10.5281/zenodo.23466511`](https://doi.org/10.5281/zenodo.23466511) | Account-holder screenshot of Zenodo GitHub integration, showing this tag, the title and `Published` status |
| Researcher ORCID iD | [`0009-0000-7863-5792`](https://orcid.org/0009-0000-7863-5792) | Repository `CITATION.cff`, not a verified imported ORCID Works entry |

## Publication sequence

1. The rights-holder authorized public distribution of materials they control and MIT licensing before the GitHub baseline publication.
2. GitHub `main` commit `9c1ccdd32ed0d3e130f173eaed2a10e26457abdb` and its annotated tag were independently confirmed. A GitHub Release for that tag is published and no longer flagged as pre-release.
3. Zenodo GitHub integration was enabled; the release was published before repository integration enablement, so a subsequent edit from release → pre-release → release recovered ingestion, preserving the existing tag and commit.
4. The account-holder then supplied a screenshot showing **Published** for the correct release tag and DOI `10.5281/zenodo.23466511`. This establishes the DOI displayed in the owner's Zenodo account, not an independent downloaded-archive hash check.
5. This post-publication citation pointer is added on `main`. It is **not** a rebuild or retag of v0.1.2.

## Still to establish

- Open and inspect the **full Zenodo record** (metadata: creators, work type software, title, version, license, referenced GitHub URL, exact archive contents/checksum); direct Zenodo record/API access was unavailable during this inspection, so these individual fields are **not independently re-verified**.
- Check the ORCID **Works** section for this **same version DOI**, avoiding duplication. GitHub/Zenodo/ORCID account linking does not establish that this particular work has been imported.
- If absent, add/import a single software work with the version DOI, confirm title/creator/version and public visibility. Record the work's ORCID entry only after confirming it exists.
- Preserve the difference between DOI for the baseline software **collection**, individual experiment claims, and independently judged scientific validity.

## Citation boundaries

Use the Zenodo record's generated citation after checking its actual creator/title/version metadata. The intended output is a versioned **software research baseline**, not a peer-reviewed paper. Do not substitute a concept DOI for a version-specific citation or issue 13 DOIs simply because 13 experiment ZIPs are preserved.

No claim is made here that publication, a DOI or CI integrity checks independently validate LexiFORM's semantics, establish external authority or warrant Fork standing inheritance.
