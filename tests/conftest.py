import os
import shutil
import tempfile

import pytest

from app import create_app, db


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)
    upload_dir = tempfile.mkdtemp()

    app = create_app('testing')
    app.config.update({
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'UPLOAD_FOLDER': upload_dir,
        'WTF_CSRF_ENABLED': False,
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

    os.unlink(db_path)
    shutil.rmtree(upload_dir, ignore_errors=True)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A CLI runner for the app."""
    return app.test_cli_runner()
