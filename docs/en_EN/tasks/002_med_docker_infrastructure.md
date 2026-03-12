# Task 002: Docker Infrastructure Scaffolding

**Priority:** 🟡 Medium
**Status:** 📅 Planned
**Target Version:** v0.3.0

## 📝 Description
Provide a production-ready Docker configuration automatically when generating a new project. To maintain a clean project structure, all deployment-related files will be placed in a dedicated `deploy/` directory.

## 🎯 Objectives
1. **Infrastructure Isolation**: Create a `deploy/` folder in the project root.
2. **Templates**: Create `Dockerfile.j2` and `docker-compose.yml.j2` inside the `deploy/` folder.
3. **Environment**: Ensure Docker Compose correctly maps `.env` variables from the root.
4. **Context Management**: Configure Docker to use the project root as the build context while keeping configs in `deploy/`.

## 🛠 Technical Notes
- Base image: `python:3.12-slim`.
- Command to run: `docker-compose -f deploy/docker-compose.yml up`.
- Use a non-root user inside the container for security.

## ✅ Definition of Done
- [ ] Project contains a `deploy/` directory with `Dockerfile` and `docker-compose.yml`.
- [ ] Bot starts correctly using the configuration from the `deploy/` folder.
- [ ] Redis and DB connections work "out-of-the-box" via compose networks.
