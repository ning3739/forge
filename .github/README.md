# GitHub Actions Workflows

## Workflows

### CI (`ci.yml`)
- Runs on push/PR to `main` or `develop`
- Tests build on Python 3.9-3.12
- Validates package distribution

### Publish (`publish.yml`)
- Runs on GitHub Release (automatic)
- Manual trigger for Test PyPI
- Uses PyPI Trusted Publishing (no tokens needed)

## Setup

See [PUBLISHING.md](../PUBLISHING.md) for complete instructions.
