# Release checklist

Use this checklist before publishing an AttackAtlas release.

- [ ] Confirm `VERSION` and application version match the release tag
- [ ] Build the frontend
- [ ] Validate backend imports/compilation
- [ ] Build the Docker image
- [ ] Test startup with a fresh empty `data/` directory
- [ ] Test startup with a copy of an existing database when migrations changed
- [ ] Back up and restore `data/` together with `secrets/credential-vault.json`
- [ ] Verify Add host, Nmap import, users, credentials, connections and exports
- [ ] Search the repository for secrets, private keys, real engagement data and local databases
- [ ] Confirm screenshots contain synthetic data and no embedded metadata
- [ ] Review `CHANGELOG.md`
- [ ] Create an annotated Git tag
- [ ] Publish the GitHub release as a pre-release while the project is alpha
