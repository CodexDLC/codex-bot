# codex-bot Audit And Migration Plan

Updated: 2026-03-27

## Purpose

This document is a working audit and execution plan for bringing `codex-bot` up to the same operational standard as the stronger `codex-*` libraries, especially `codex-django`.

It is written for humans and agents working inside this repository.

## Product Context

`codex-bot` should not be interpreted as an isolated standalone library with no ecosystem ties.

It is part of the broader team framework stack built around:

- `codex-core`
- `codex-services`
- `codex-platform`
- `codex-ai`

The intended direction is:

- a shared `codex` team framework with open-source distribution
- `codex-bot` as the Telegram and Aiogram-oriented framework layer
- shared foundations and universal configuration patterns in `codex-core`
- future expansion with an additional framework layer around FastAPI

That means cross-repo alignment is expected at the product level.

However, expected ecosystem coupling still needs to be expressed clearly in packaging, tooling, documentation, and validation flows. The real problem is not that `codex-bot` knows about the rest of the stack. The real problem is that some of those dependencies and expectations are still implicit instead of being formalized.

## Executive Summary

`codex-bot` is no longer just a small reusable library. It is a mixed repository with three responsibilities:

1. a published Python library
2. a CLI scaffolding tool
3. a large documentation and template system

Those responsibilities are all valid, but they are not sharply separated yet. The result is that the repository looks more mature from the outside than it behaves in a clean environment.

The most important finding is simple:

- `uv` and `Python 3.12+` are now aligned
- packaging is acceptable
- release workflow is acceptable
- but repository-level quality, documentation discipline, tooling boundaries, and generated-project guarantees are still below the standard of the better `codex-*` libraries

This means `codex-bot` should be treated as a dedicated normalization project, not as a quick polish task.

## Current State Snapshot

### What is already in good shape

- `pyproject.toml` uses `hatchling` and `hatch-vcs`
- `requires-python` is already `>=3.12`
- `uv.lock` exists
- CI, docs, and publish workflows already use `uv`
- publish still uses standard PyPI flow, which is the right compatibility choice
- the repository contains a meaningful test suite and a substantial docs set

Relevant files:

- `pyproject.toml`
- `.github/workflows/ci.yml`
- `.github/workflows/docs.yml`
- `.github/workflows/publish.yml`
- `uv.lock`

### What is not yet at target level

- the quality gate is not self-contained
- documentation is large, but not obviously curated as a maintained product
- templates are powerful, but they increase maintenance burden significantly
- repository boundaries are blurry between library code, internal tooling, and project scaffolding
- integration confidence is lower than the repository surface suggests

## Hard Findings

### 1. The checker is broken in a clean environment

`tools/dev/check.py` imports `BaseCheckRunner` from `codex_core.dev.check_runner`.

In a clean `uv sync --locked --extra dev` environment for this repository, the checker fails with:

`ModuleNotFoundError: No module named 'codex_core'`

This is a structural problem, not a one-line bug.

Implication:

- `codex-bot` is not self-validating in a clean checkout of its own repository
- the dependency on shared `codex-core` tooling may be conceptually valid, but it is implicit rather than intentionally packaged and documented

Files involved:

- `tools/dev/check.py`
- `tools/dev/generate_project_tree.py`
- `pyproject.toml`

### 2. The repository has too many roles without hard boundaries

The repository currently contains:

- reusable runtime modules in `src/codex_bot`
- CLI commands in `src/codex_bot/cli`
- project templates in `src/codex_bot/templates`
- architecture docs in `docs`
- generated API docs references in `docs/api`

This is workable, but it means every change can break:

- library runtime behavior
- CLI behavior
- generated project output
- docs correctness

Without stronger contracts, the repository accumulates drift faster than the smaller libraries.

### 3. The documentation footprint is large, but maintenance guarantees are unclear

The repository currently has 80+ Markdown files under `docs`.

That is not automatically a problem. The problem is that the docs system appears broader than the validation around it:

- bilingual docs increase synchronization cost
- architecture docs are extensive
- roadmap and task docs are mixed into the docs tree
- the docs site presents a polished surface, but there is no obvious strict doc freshness contract

Risk:

- docs can become aspirational rather than reliably operational

### 4. Template surface area is already platform-sized

The project generator and feature generator do more than bootstrap a toy example. They generate a real stack with branching behavior:

- data mode selection
- Redis FSM options
- Redis Streams options
- i18n options
- logging options
- smart merge behavior for existing repositories

That is strong product value, but it also means template quality has to be treated almost like source code quality for another product.

Current risk:

- template correctness can drift from runtime APIs
- generated projects may not remain equal to "current best practice"

### 5. Integration coverage is still not proportional to repository ambition

There is real integration testing, but there is also still a placeholder integration test.

That is a sign that the integration suite exists, but the repository is not yet fully validated at the level implied by its platform ambitions.

File:

- `tests/integration/test_placeholder.py`

## Architectural Assessment

`codex-bot` should be treated as a layered product inside the broader `codex` framework ecosystem:

1. runtime library layer
2. CLI/scaffolding layer
3. documentation/productization layer
4. cross-framework integration layer with the rest of the `codex-*` stack

The current repository mixes these layers in one repo, which is acceptable for now, but only if we introduce stronger contracts between them.

The target state should be:

- the library is testable and releasable as a defined part of the `codex` ecosystem
- the checker works without hidden repo-to-repo assumptions
- the CLI and templates are validated as first-class outputs
- docs are curated, versioned, and intentionally scoped
- generated projects reflect the current supported standard, not legacy historical options
- framework-level dependencies on `codex-core`, `codex-services`, `codex-platform`, and `codex-ai` are explicit where they are truly part of the supported stack

## Recommended Target Standard

### Packaging And Tooling

- keep `hatchling + hatch-vcs`
- keep PyPI installation standard for users
- keep `uv` as the dev, CI, and build frontend
- keep `Python 3.12+` as the floor
- document which parts of the wider `codex-*` stack are optional integrations and which are first-class supported framework dependencies

### Quality Gates

- `tools/dev/check.py` must run in a clean environment without undeclared cross-repo imports
- quality gate should cover:
  - formatting/lint
  - typing
  - unit tests
  - integration tests
  - secrets scan
  - security audit

### Repository Boundaries

- library code must not depend on undocumented internal repository conventions
- dev tooling may depend on shared `codex-*` tooling only if that dependency is explicit and reproducible
- templates must be treated as a supported output surface
- ecosystem coupling is acceptable, but hidden coupling is not

### Documentation

- docs should be split into:
  - user-facing guides
  - architecture references
  - generated API reference
  - internal roadmap and backlog material
- roadmap/task management content should not dominate the public docs experience

## What Should Not Be Changed Immediately

- do not split the repository into multiple repos as a first move
- do not replace `hatchling`
- do not redesign the CLI product surface before contracts and tests are in place
- do not rewrite all docs before deciding which docs are public product docs and which are internal working notes
- do not expand feature scope while validation is still weaker than the current surface area

## Migration Strategy

`codex-bot` should be upgraded in phases.

### Phase 1. Make The Repo Self-Consistent

Goal:

- make the repository self-validating and predictable

Tasks:

1. fix `tools/dev/check.py` so it works in a clean repository environment
2. decide whether shared dev tooling from `codex-core` is:
   - vendored into `codex-bot`
   - declared as an explicit dev dependency
   - or extracted into a dedicated shared internal tooling package later
3. do the same review for `tools/dev/generate_project_tree.py`
4. make checker execution part of the expected local development flow

Definition of done:

- a fresh `uv sync --locked --extra dev`
- then `uv run python tools/dev/check.py --ci`
- works without hidden setup, while still allowing intentional shared `codex-*` tooling where officially supported

### Phase 2. Normalize The Product Boundary

Goal:

- make it obvious what `codex-bot` is promising to users

Tasks:

1. define the supported public surface:
   - runtime APIs
   - CLI commands
   - generated project layout
   - supported integration points with other `codex-*` libraries
2. define what is internal:
   - backlog docs
   - working notes
   - historical architecture notes that are not part of user guidance
3. tighten README and docs landing pages around the actual supported path

Definition of done:

- a new user can understand installation, quick start, supported extras, and docs navigation without reading internal material

### Phase 3. Treat Templates As First-Class Output

Goal:

- make generated projects a reliable contract

Tasks:

1. review every template family under `src/codex_bot/templates`
2. classify templates into:
   - must support now
   - keep but simplify
   - deprecate
3. add stronger tests for generated projects:
   - project generation succeeds
   - generated project installs with `uv`
   - generated project passes its own baseline checks
   - generated project entrypoints run
4. review smart merge mode and decide whether to keep, narrow, or harden it

Definition of done:

- template output is validated against the same standard we claim in docs

### Phase 4. Rebuild The Documentation System

Goal:

- reduce drift and make docs trustworthy

Tasks:

1. separate public docs from internal planning docs
2. define documentation ownership by area:
   - getting started
   - architecture
   - API reference
   - template/generator usage
3. review bilingual strategy:
   - either keep both languages with explicit sync discipline
   - or define one primary source language and translation policy
4. ensure docs navigation reflects supported reality, not aspirational structure
5. verify all code samples and CLI examples against current `uv` and `3.12+` flows

Definition of done:

- docs are smaller, clearer, and easier to trust

### Phase 5. Raise Confidence To Platform Level

Goal:

- make the repo operationally comparable to the strongest libraries

Tasks:

1. remove placeholder integration coverage where real coverage should exist
2. add scenario tests for:
   - Redis-enabled flows
   - i18n-enabled generated projects
   - DB mode vs API mode generation
   - CLI project creation and feature creation
3. define release criteria for `codex-bot` versions

Definition of done:

- version releases reflect validated behavior, not best effort

## Concrete File Areas To Rework

### Immediate

- `tools/dev/check.py`
- `tools/dev/generate_project_tree.py`
- `pyproject.toml`
- `README.md`
- `docs/README.md`
- `tests/integration/test_placeholder.py`

### High Priority

- `.github/workflows/ci.yml`
- `.github/workflows/docs.yml`
- `mkdocs.yml`
- `src/codex_bot/cli/commands/startproject.py`
- `src/codex_bot/cli/commands/create_feature.py`
- `tests/integration/test_templates_e2e.py`
- `tests/test_template_consistency.py`

### Broad Review Surface

- `src/codex_bot/templates/project/**`
- `src/codex_bot/templates/feature/**`
- `docs/en_EN/**`
- `docs/ru_RU/**`
- `docs/api/**`

## Risks And Tradeoffs

### If we move too slowly

- docs drift will continue
- templates will keep diverging from runtime behavior
- agents and contributors will lose confidence in what is authoritative

### If we try to rewrite everything at once

- we will create a huge review surface
- regressions in templates and CLI behavior will be easy to miss
- the repository may look cleaner while becoming less stable

### Recommended tradeoff

- keep the repo structure for now
- strengthen contracts first
- narrow public promises second
- refactor deeper only after tests and docs boundaries improve

## Recommended Order Of Execution

1. make checker and dev tooling self-contained
2. make generated projects verifiable
3. clean docs information architecture
4. expand integration confidence
5. only then consider larger architectural reshaping

## Practical Next Actions

The next best concrete tasks are:

1. fix the broken checker dependency on `codex-core`
2. decide explicit policy for shared dev tooling across `codex-*`
3. replace placeholder integration coverage with real generator/runtime scenarios
4. split public docs from internal roadmap/task material
5. run a template-by-template support review and mark deprecated paths
6. write down the intended long-term relationship between `codex-bot` and the future FastAPI-oriented framework layer

## Instruction: Audit Whether `codex-core` Is Dev-Only Or More

Do not assume yet that `codex-core` is only a dev dependency for `codex-bot`.

That may be true, but it must be proven by code audit.

The audit should answer one concrete question:

- is `codex-core` used only for repository-local development and maintenance tooling
- or is it part of the actual supported framework contract of `codex-bot`

### Audit Scope

The audit must inspect these areas separately.

#### 1. Runtime code

Inspect:

- `src/codex_bot/**`

Goal:

- find direct imports from `codex_core`
- find concepts that are effectively shared foundation logic and may belong in `codex-core`

Questions:

- does runtime code import `codex_core`
- does runtime behavior rely on conventions defined only in `codex-core`
- are there modules in `codex-bot` that are not Telegram/Aiogram-specific and should be treated as shared foundation

#### 2. Dev tooling and maintenance scripts

Inspect:

- `tools/**`
- test helper code
- any repo-local scripts used in CI or docs generation

Goal:

- identify every place where `codex-core` is used for development-only purposes

Questions:

- is `codex_core.dev.*` used only by repo maintenance scripts
- can those dependencies be declared explicitly as internal dev dependencies
- should any of that tooling be vendored, shared, or extracted later

#### 3. Tests

Inspect:

- `tests/**`

Goal:

- determine whether tests rely on `codex-core` only as a maintainer convenience or as part of the intended framework contract

Questions:

- do tests import `codex_core`
- do tests only need `codex-core` because the repo tooling is coupled to it

#### 4. Templates and generated projects

Inspect:

- `src/codex_bot/templates/project/**`
- `src/codex_bot/templates/feature/**`
- CLI generation logic in `src/codex_bot/cli/**`

Goal:

- verify whether generated consumer projects require `codex-core`

Questions:

- does generated code import `codex_core`
- does generated `pyproject.toml` declare `codex-core`
- does generated project structure assume a `tools` folder or `codex-core` tooling

This is especially important because generated consumer projects do not currently get the repository `tools` layout automatically.

#### 5. Documentation and support contract

Inspect:

- `README.md`
- `docs/**`
- CLI help text and setup instructions

Goal:

- verify what the repository claims publicly about `codex-core`

Questions:

- is `codex-core` presented as required, optional, or internal
- do docs match actual code behavior

### Recommended Method

Use this order:

1. search all imports and string references to `codex_core` and `codex-core`
2. classify every hit as:
   - runtime
   - dev tooling
   - tests
   - templates
   - docs
3. inspect zero-hit zones too, not only matched files
4. write down whether each dependency is:
   - direct import
   - conceptual shared logic
   - packaging dependency
   - documentation-only mention
5. conclude with one of these outcomes:
   - `codex-core` is dev-only for `codex-bot`
   - `codex-core` is an optional ecosystem dependency
   - `codex-core` is a real runtime/foundation dependency

### Required Deliverable

At the end of the audit, produce a short decision note with:

- current factual usage of `codex-core`
- recommended dependency status
- files that justify that conclusion
- follow-up actions required in packaging, tooling, templates, and docs

Do not change dependency declarations before this audit is completed.

## Final Recommendation

Do not treat `codex-bot` as "docs cleanup" or "workflow cleanup".

Treat it as a platform-repo normalization effort with these priorities:

- self-contained tooling
- explicit product boundary
- tested scaffolding output
- curated documentation
- release discipline

Within the broader team vision, `codex-bot` is a framework layer in a larger `codex` ecosystem, not a disconnected package. That vision is good. The work now is to formalize that ecosystem contract so the repository behaves as intentionally as the architecture already sounds.
