# Contributing to AttackAtlas

Contributions, bug reports and focused feature proposals are welcome.

## Development principles

AttackAtlas is intended to remain:

- local-first
- lightweight in CPU and memory use
- usable without external services
- easy to run through Docker
- suitable for isolated lab and assessment environments

New runtime dependencies or background services should therefore have a clear benefit.

## Workflow

1. Fork or clone the repository.
2. Create a focused feature branch.
3. Make the change and keep unrelated refactors separate.
4. Run the available checks locally when possible.
5. Open a pull request describing the problem, approach and user-visible impact.

## Local Docker build

Docker Compose v2:

```bash
docker compose up --build
```

Docker Compose v1:

```bash
docker-compose up --build
```

The application is served on `http://127.0.0.1:7843` by default.

## CI

GitHub Actions validates the Python backend, builds the frontend and performs a Docker image build on pushes to `main` and pull requests.

Before opening a pull request, avoid committing local databases, exported engagement data, `.env` files, credentials, scan artifacts or `node_modules`.
