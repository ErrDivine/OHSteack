from app import db


def test_app_uses_testing_config(app):
    assert app.config['TESTING'] is True
    assert app.config['WTF_CSRF_ENABLED'] is False
    assert app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:///')


def test_database_is_initialized(app):
    with app.app_context():
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
    # core tables should be present after create_all
    expected = {'users', 'teams', 'team_members', 'resources', 'results', 'result_iterations'}
    assert expected.issubset(set(tables))
