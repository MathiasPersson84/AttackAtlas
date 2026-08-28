# Contributing to AttackAtlas

Bug reports, focused feature proposals and code contributions are welcome.

AttackAtlas is intended to remain local-first, lightweight, usable without external services and easy to run in isolated lab or assessment environments.

## Issues first for larger changes

For substantial features, architectural changes or new runtime dependencies, open an Issue before investing in an implementation. Small fixes do not need prior discussion.

## Code contributions

1. Fork the repository.
2. Create a focused branch in your fork.
3. Keep unrelated refactors out of the change.
4. Run the available checks locally.
5. Submit a pull request from your fork.

Pull requests are reviewed before merge. There is no expectation that every proposed feature will be accepted; changes should fit the project's scope and lightweight/local-first goals.

## Local checks

Docker Compose v2:

```bash
docker compose up --build
```

Docker Compose v1:

```bash
docker-compose up --build
```

The application is served on `http://127.0.0.1:7843` by default.

GitHub Actions validates the Python backend, builds the frontend and performs a Docker image build.

## Sensitive data

Never commit real engagement data, credentials, hashes, local databases, `.env` files, scan artifacts or exported project archives. Screenshots and examples must use synthetic data and should have metadata removed before being committed.
