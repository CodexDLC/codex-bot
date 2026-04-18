# Task 002: Docker Infrastructure

**Priority:** Medium
**Status:** Planned
**Category:** Infrastructure

---

## 🎯 Goal
Provide ready-to-use Docker templates (`Dockerfile.j2`, `docker-compose.yml.j2`) during new project generation. All infrastructure files will be managed within a dedicated `deploy/` directory.

## 🛠 Features
1. **Infrastructure Isolation**: Create `deploy/` folder in the project root.
2. **Templates**: Include `Dockerfile.j2` and `docker-compose.yml.j2` for user onboarding.
3. **Environment Sync**: Ensure Compose correctly loads variables from the root `.env`.

---
[⬅️ Back to Roadmap](../roadmap.md)
