# Contributing to CreatorApp24

Thanks for your interest in contributing! This repository contains the production architecture for CreatorApp24.

How to contribute

- For bugs or feature requests: open an issue using the provided templates (.github/ISSUE_TEMPLATE).
- For code changes: fork the repo, create a feature branch, make your change, run tests and linters, and open a pull request against `main`.

Branch naming

- Use descriptive branch names, e.g. `feat/add-login`, `fix/auth-timeout`.

Commit messages

- Use conventional commits where practical, e.g. `feat:`, `fix:`, `chore:`.

Code style

- Python: Black, isort, flake8, and mypy are used. Please run formatting and lint checks before opening a PR.

CI and checks

- This repository includes a GitHub Actions workflow that runs linters, type checks, and tests. Your PR should pass all checks before merging.

Security

- Do not commit secrets or private keys. Use environment variables and `.env` files (which are ignored by .gitignore). If you discover a security issue, please contact the maintainers privately.

Contact

- If you need help, open an issue and tag @ashleygeeeeg.
