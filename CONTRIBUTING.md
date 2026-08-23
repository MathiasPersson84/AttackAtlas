# Contributing to AttackAtlas

Thanks for considering a contribution.

## Development

1. Fork or clone the repository.
2. Create a feature branch.
3. Keep changes focused and avoid unnecessary runtime dependencies.
4. Run the backend and frontend checks locally when possible.
5. Open a pull request describing what changed and why.

AttackAtlas is intentionally designed to remain lightweight and local-first. New dependencies and background services should have a clear benefit.

## Local Docker build

```bash
docker-compose up --build
```

The UI/API are served on `http://127.0.0.1:7843` by default.
