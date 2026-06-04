# python-fastapi-cognito-jwt-verification

A FastAPI application demonstrating Cognito JWT verification. Incoming requests to protected routes must carry a valid `Authorization: Bearer <token>` header. The middleware verifies the JWT against Cognito's public JWKS endpoint using PyJWT.

## Getting Started

[mise](https://mise.jdx.dev/) manages the pinned toolchain (Python 3.14, uv).

```bash
# macOS / Linux
curl https://mise.run | sh

# Windows
winget install jdx.mise
```

Activate mise in your shell (`~/.zshrc`):

```zsh
eval "$(mise activate zsh)"
```

Then, in the repo:

```bash
mise trust         # one-time
mise install       # downloads Python and uv
mise run install   # installs dependencies into .venv
```

Create a `.env` file at the root of the project:

```dotenv
AWS_DEFAULT_REGION=us-east-1
COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
COGNITO_APP_CLIENT_ID=XXXXXXXXXXXXXXXXXXXXXXXXXX
```

Start the server:

```bash
mise run dev
```

## Routes

| Method | Path                            | Auth required |
|--------|---------------------------------|---------------|
| GET    | `/protected-with-access-token`  | Cognito access token |
| GET    | `/protected-with-id-token`      | Cognito ID token |

## Development

| Command              | Description                              |
|----------------------|------------------------------------------|
| `mise run install`   | Install dependencies into `.venv`        |
| `mise run dev`       | FastAPI dev server on `127.0.0.1:8000`   |
| `mise run serve`     | Production server on `0.0.0.0:8000`      |
| `mise run test`      | Run tests                                |
| `mise run fmt`       | Format code via `ruff format`            |
| `mise run lint`      | Lint code via `ruff check`               |
| `mise run typecheck` | Type check via `ty check`                |
| `mise run vuln`      | Audit deps for known vulnerabilities     |
| `mise run deps`      | Update and sync dependencies             |
