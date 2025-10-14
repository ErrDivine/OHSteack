# Repository Guidelines

## Project Structure & Module Organization
The Flask application factory lives in `app/__init__.py`, wiring blueprints from `app/views/` (main, auth, team, resource, result). Feature templates stay under `templates/<blueprint>/`, while forms, models, and shared helpers live respectively in `app/forms/`, `app/models/`, and `app/utils/`. Static assets, uploads, and bundles sit in `static/`, and deployment or provisioning scripts reside in `scripts/` and `deployment/`. Database migrations are tracked in `migrations/`, with environment-specific overrides in `instance/`.

## Build, Test, and Development Commands
Run `bash scripts/setup.sh` once to install dependencies and create expected directories, then activate the environment with `source venv/bin/activate`. Start the API locally with `FLASK_APP=run.py flask run`. Apply schema changes via `flask db upgrade`, initialize a fresh database using `flask init-db`, and seed an administrator through `flask create-admin`. Use `pip install -r requirements.txt` inside the virtualenv whenever dependencies change.

## Coding Style & Naming Conventions
Follow PEP 8 with 4-space indentation, expressive docstrings, and `snake_case` identifiers. Blueprint modules must expose a `<name>_bp` object, and template filenames should mirror their blueprint paths (e.g., `templates/team/detail.html`). Keep reusable Jinja filters in `app/utils/filters.py` and register them through the factory. Default to ASCII unless a template already contains localized UTF-8 strings.

## Testing Guidelines
Pytest runs against Flask’s test client; execute `pytest` or target feature suites such as `pytest tests/test_team_routes.py`. Organize test modules by blueprint, arrange-act-assert within each case, and use factory fixtures for setup. Ensure tests leave the database clean by relying on rollbacks or temporary transactions.

## Commit & Pull Request Guidelines
Write imperative commit messages (`Add team dashboard template`) and bundle related code, migrations, and docs together. Reference issue IDs when applicable. Pull requests should include a concise summary, screenshots for UI work, migration notes (`flask db upgrade`), and proof of local testing or manual verification. Call out configuration changes and provide `.env` updates for reviewers.

## Security & Configuration Tips
Store secrets in `.env` and never commit them. Review `config.py` before adding feature flags, prefer environment variables over hard-coded defaults, and keep `static/uploads/` sanitized. Confirm file permissions and logging behavior before deploying.
