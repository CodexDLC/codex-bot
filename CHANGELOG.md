# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
