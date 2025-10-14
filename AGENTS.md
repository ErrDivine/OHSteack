# Repository Guidelines

## Project Structure & Module Organization
The Flask application factory lives in `app/__init__.py`, and blueprints are grouped under `app/views/` (main, auth, team, resource, result). Data models sit in `app/models/`, forms in `app/forms/`, and shared helpers in `app/utils/`. HTML templates are organized by feature under `templates/`, while static assets (CSS, JS, images, uploads) live in `static/`. Deployment scripts reside in `scripts/` and `deployment/`, and database migrations are tracked via `migrations/`. Use the `instance/` folder for machine-specific configs and secrets.

## Build, Test, and Development Commands
Run `bash scripts/setup.sh` once to bootstrap the virtualenv, install dependencies, and create expected folders. Activate the environment with `source venv/bin/activate`, then launch the app via `FLASK_APP=run.py flask run`. Apply schema changes with `flask db upgrade` and initialize a fresh database using `flask init-db`. When seeding an admin, run `flask create-admin` and follow the prompts.

## Coding Style & Naming Conventions
Follow PEP 8 with 4-space indentation, descriptive docstrings, and snake_case for functions, variables, and SQLAlchemy columns. Blueprint modules should expose a `*_bp` object; keep template filenames aligned with their blueprint (e.g., `templates/team/detail.html`). Place reusable filters in `app/utils/filters.py` and import them through the factory. Localized strings stay in UTF-8; otherwise keep files ASCII.

## Testing Guidelines
Testing uses Flask’s built-in test client alongside the `TestingConfig`. Create `tests/` modules that mirror blueprint boundaries (e.g., `tests/test_team_routes.py`) and load fixtures through factory fixtures. Activate testing with `FLASK_ENV=testing FLASK_APP=run.py flask shell` or inside `pytest` after adding it to your dev requirements. Each test module should arrange-act-assert and clean up with database rollbacks.

## Commit & Pull Request Guidelines
Commits should be short and imperative (e.g., `Add team dashboard template`), grouping related changes with migrations and docs updated together. Reference issue IDs when available. Pull requests need: a concise summary, screenshots for UI updates, migration notes (`flask db upgrade`), and evidence of local testing or manual verification. Flag configuration changes and attach `.env` instructions for reviewers.

## Configuration & Security Tips
Store secrets in `.env` and never commit them. Review `config.py` when adding flags, and prefer environment variables over hard-coded settings. Keep uploads sanitized and maintain the `static/uploads/` directory structure created by `setup.sh`.
