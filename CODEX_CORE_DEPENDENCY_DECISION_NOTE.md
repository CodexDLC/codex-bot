# codex-core Dependency Decision Note

Updated: 2026-03-27

## Current Factual Usage

`codex-core` is currently used in `codex-bot` only for development tooling.

Direct import hits:

- `tools/dev/check.py` imports `codex_core.dev.check_runner`
- `tools/dev/generate_project_tree.py` imports `codex_core.dev.project_tree`

Zero-hit zones (direct import and string reference scan):

- `src/codex_bot/**` (runtime library code)
- `tests/**` (test code)
- `src/codex_bot/templates/**` (generated output templates)
- `pyproject.toml` dependency declarations
- `README.md` and `docs/**` public dependency messaging

## Dependency Status Recommendation

Recommended status: `codex-core` is **dev-only** for `codex-bot` at the current repository state.

Rationale:

- no runtime imports or runtime coupling signals were found
- no template-level requirement for generated projects was found
- usage is isolated to repository-local development scripts

## Files Justifying The Conclusion

- `tools/dev/check.py`
- `tools/dev/generate_project_tree.py`
- `src/codex_bot/**` (no `codex_core` references found)
- `tests/**` (no `codex_core` references found)
- `src/codex_bot/templates/**` (no `codex_core` references found)
- `pyproject.toml` (no `codex-core` dependency declared)

## Follow-up Actions

1. Tooling:
   - keep local fallback tooling in `tools/dev/*` to ensure self-validation in clean checkouts
   - if shared `codex-core` tooling is used, keep it optional and explicitly documented
2. Packaging:
   - keep `codex-core` out of runtime dependencies unless runtime code starts importing it
   - if needed for maintainers, add explicit optional dev dependency policy in docs
3. Templates:
   - assert in template tests that generated projects do not import `codex_core` unless explicitly intended
4. Docs:
   - document that `codex-core` is ecosystem-adjacent and currently optional for `codex-bot` consumers
   - separate ecosystem vision text from hard runtime dependency claims
