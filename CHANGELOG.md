# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-04-23

### Changed

- **Aiogram Stack**: Raised the core `aiogram` dependency contract to `>=3.27.0,<4.0` and the optional i18n extra to `aiogram-i18n[runtime]>=1.5,<2.0`.
- **Project Templates**: Updated generated project dependencies to use the same modern aiogram and aiogram-i18n ranges.

### Fixed

- **I18n Manager Initialization**: Updated `FSMContextI18nManager` to initialize `aiogram-i18n`'s `BaseManager`, restoring `locale_getter` and `locale_setter` for `I18nMiddleware`.

## [0.2.1] - 2026-04-18

### Fixed

- **API Restoration**: Restored `FeatureDiscoveryService.discover_models()` to fix broken Alembic model registration in generated projects.
- **Bridge Methods**: Restored `UnifiedViewDTO.send()` as a compatibility bridge for existing feature handlers.
- **Template Bugfixes**: Fixed boolean literal generation in `config.py.j2` by removing the invalid `| lower` filter (resolving `True`/`False` token errors).
- **Mypy Hardening**: Added `codex_platform.*` overrides to project templates to ensure new projects pass type-checking out of the box.
- **Security Patches**: Updated `aiohttp` (3.13.4), `pygments` (2.20.0), and `pytest` (9.0.3) to resolve 12 identified vulnerabilities.
- **Import Resilience**: Implemented robust `TYPE_CHECKING` patterns for optional dependencies (`codex-platform`) to prevent linting paradoxes.

## [0.1.1] - 2025-03-09

### Added
- **CI/CD Automation**: Integrated GitHub Actions for automated publishing to PyPI using Trusted Publishers (OIDC).
- **Project Metadata**: Added comprehensive project URLs (Documentation, Repository, Issues, Changelog) to `pyproject.toml` for better PyPI presentation.

### Fixed
- **Documentation Links**: Corrected broken documentation links in `README.md` to point to the actual GitHub Pages site.

## [0.1.0] - 2025-03-09

### Added
- **Initial Library Release**: Migration and adaptation of core infrastructure from production projects into a reusable feature-based framework.
- **Feature-based Architecture**: Implementation of `BaseBotOrchestrator` and `Director` for stateless UI management.
- **Redis Integration**: Stream processing, consumer groups support, and Redis-based dispatching.
- **FSM Enhancements**: `GarbageStateRegistry` for automatic UI cleanup and advanced state management.
- **Unified View System**: `ViewSender` and `UnifiedViewDTO` for consistent message rendering across different platforms.
- **I18n Engine**: Custom Fluent-based locales compiler with isolation support.
- **CLI Tools**: Scaffolding templates for rapid feature development.
- **Multi-language Documentation**: Comprehensive guides and API references in English and Russian.
- **DevOps Infrastructure**: Pre-commit hooks, Ruff/Mypy configurations, and GitHub Actions for docs.
- **Final Polish**: Refined `Director` logic, `BotBuilder` factory, and `RouterBuilder` for better stability.
- **Enhanced State Management**: Improved `StateManager` and `FSM` handlers for more robust session control.
- **Redis Dispatcher Optimization**: Fine-tuned stream processing and error handling in `RedisDispatcher`.
- **Test Coverage**: Added comprehensive unit tests for all core modules.
