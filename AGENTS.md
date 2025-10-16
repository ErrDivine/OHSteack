# Repository Guidelines

## Project Structure & Module Organization
The Flask factory in `app/__init__.py` wires blueprints from `app/views/` (main, auth, team, resource, result). Feature-specific templates live under `templates/<blueprint>/`, while shared helpers stay in `app/utils/`. Keep forms and models in `app/forms/` and `app/models/`; static assets, uploads, and bundles belong in `static/`. Migrations reside in `migrations/`, environment overrides in `instance/`, and deployment scripts under `scripts/` and `deployment/`.

## Build, Test, and Development Commands
Run `bash scripts/setup.sh` once to install dependencies and prepare directories. Activate the virtualenv with `source venv/bin/activate`. Start the API using `FLASK_APP=run.py flask run`. Apply schema updates via `flask db upgrade`, initialize a fresh database with `flask init-db`, and seed an administrator using `flask create-admin`. Install new requirements through `pip install -r requirements.txt` inside the environment.

## Coding Style & Naming Conventions
Follow PEP 8 with 4-space indentation, descriptive docstrings, and `snake_case` naming. Blueprint modules must expose `<name>_bp`, and templates should mirror their blueprint path (for example, `templates/team/detail.html`). Keep reusable Jinja filters in `app/utils/filters.py` and register them through the factory. Default to ASCII unless extending an existing localized template.

## Testing Guidelines
Use pytest with the Flask test client; run the full suite via `pytest` or target a module like `pytest tests/test_team_routes.py`. Structure cases as arrange-act-assert, rely on fixtures for setup, and let database interactions roll back to keep tests isolated.

## Commit & Pull Request Guidelines
Write imperative commit messages (e.g., “Add team dashboard template”) and bundle related migrations, docs, and code together. Pull requests should summarize changes, link relevant issues, include screenshots for UI updates, and note any `flask db upgrade` impacts or `.env` updates. Mention manual verification or test results before requesting review.

## Security & Configuration Tips
Store secrets in `.env` and keep it out of version control. Prefer environment variables over hard-coded settings, review `config.py` for feature flags, and ensure `static/uploads/` stays sanitized. Confirm logging and file permissions align with deployment expectations.
