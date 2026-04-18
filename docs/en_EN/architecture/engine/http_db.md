# HTTP and Databases

For interacting with the external world (backend APIs) and persisting data (DBs), **codex-bot** provides a set of base abstractions that minimize the boilerplate code required for connection setup.

---

## 🌐 HTTP Client (BaseApiClient)

`BaseApiClient` is a wrapper around the `httpx` library, optimized for asynchronous operation.

### Key Features:
1. **Connection Pooling**: The client is created once in the container and reuses TCP connections. This significantly speeds up performance for frequent API requests.
2. **Response Typing**: Automatically parses JSON responses and provides mechanisms for error handling (ApiClientError).
3. **Metadata Ready**: Designed with the future implementation of the Smart Resolver pattern (handling navigation headers) in mind.

### Usage Example:
```python
class MyBackendClient(BaseApiClient):
    async def get_user(self, user_id: int):
        return await self._request("GET", f"/users/{user_id}")
```

---

## 🗄 Database (SQLAlchemy)

The framework supports any SQL database through **SQLAlchemy 2.0**. The CLI templates pre-configure integration with **aiosqlite** (for development) and **asyncpg** (for production).

### Components:
- **Engine Factory**: Rapid creation of an asynchronous DB engine with connection pooling.
- **Middleware**: Automatic DB session creation for each request (DatabaseTransactionMiddleware).
- **Alembic**: A pre-configured migration environment in the project root.

### How it works:
You receive a database session directly in the orchestrator via `director.container.session` (if the middleware is enabled) or use repositories initialized in the container.

---

## 🧭 Related Sections
- **[API: HTTP Client](../../../api/http.md)** — Description of _request methods.
- **[Container](./container.md)** — Where clients are typically initialized.
