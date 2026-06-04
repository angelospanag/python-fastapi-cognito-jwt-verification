# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All tasks run via `mise run <task>`. The toolchain (Python 3.14, uv) is pinned in `mise.toml`.

| Task | Command |
|---|---|
| Install dependencies | `mise run install` |
| Dev server | `mise run dev` |
| Production server | `mise run serve` |
| Format | `mise run fmt` |
| Lint | `mise run lint` |
| Type check | `mise run typecheck` |
| Vulnerability audit | `mise run vuln` |
| Run tests | `mise run test` |
| Upgrade dependencies | `mise run deps` |

## Architecture

`app/main.py` owns the FastAPI application. It exposes two protected routes:

- `GET /protected-with-access-token` — requires a valid Cognito access token
- `GET /protected-with-id-token` — requires a valid Cognito ID token

`app/dependencies.py` implements `CognitoJWTAuthorizer`, a callable FastAPI dependency that validates the `Authorization: Bearer <token>` header against Cognito's JWKS endpoint using PyJWT. Two pre-wired instances (`cognito_jwt_authorizer_access_token`, `cognito_jwt_authorizer_id_token`) are created at module level.

`app/config.py` loads `AWS_DEFAULT_REGION`, `COGNITO_USER_POOL_ID`, and `COGNITO_APP_CLIENT_ID` from the environment (or a `.env` file) via pydantic-settings.

Tests live in `tests/`. `tests/conftest.py` sets the required environment variables before any app import so the module-level settings and authorizer construction succeed without a real Cognito pool.
