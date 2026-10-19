# Separately named LC012 recomputation-bound audit — incomplete delivered ZIP

The newly submitted 69,203-byte `LC-EXP-012.zip` SHA-256 `538aeda99adc0a86bb7aa96cee503edade7d17e23bfc69bd925d9595e62fd5ff` identifies **LC-EXP-012-RECOMPUTATION-BOUND-AUDIT-001**. This is not the already-preserved `LC-EXP-012-CONTESTED-STANDING-001` and it must not overwrite that experiment's archive or standing.

The attached report asserts 11 successful fresh historical supplied-code runs and 10 changed expanded-root manifests, with frozen executable surfaces unchanged. This is evidence of reported work, not a newly reproducible 11-pair audit from this particular submitted ZIP.

Direct checks of this uploaded object: ZIP CRC passed, but the referenced `history/` original/recomputed corpus, `evidence/lc011-replay/` receipts, and `MANIFEST.sha256` are absent. `verify_manifest.py` exits with `MISSING`, and 15/17 tests pass; two error because referenced evidence is absent, not because a semantic comparator was shown incorrect.

**Gate:** recover the exact complete successor archive with its internal manifest, frozen corpus, and replay evidence before adding this branch as a reproducible public release candidate. Preserve this identity collision explicitly; future namespace mapping must not rewrite either predecessor. The submitted ZIP is not re-published in this baseline addendum pending the gate and release rights review.
