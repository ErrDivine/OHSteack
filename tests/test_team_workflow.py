from app.models import Resource, Result, Team

from .test_auth_flow import register


def test_team_resource_result_flow(client, app):
    register(client)

    create_response = client.post(
        '/team/create',
        data={
            'name': 'Alpha Squad',
            'description': 'Core competition team',
            'competition_name': 'Global Hackathon',
            'competition_url': 'https://example.com/hackathon',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
        },
        follow_redirects=True,
    )
    assert create_response.status_code == 200

    with app.app_context():
        team = Team.query.filter_by(name='Alpha Squad').first()
        assert team is not None
        team_id = team.id

    resource_response = client.post(
        f'/resource/create/{team_id}',
        data={
            'title': 'Research Paper',
            'description': 'Key reference document',
            'content': '# Outline\n- Introduction',
            'resource_type': 'document',
            'url': '',
            'category': '',
            'tags': 'research,planning',
        },
        follow_redirects=True,
    )
    assert resource_response.status_code == 200

    with app.app_context():
        resource = Resource.query.filter_by(team_id=team_id).first()
        assert resource is not None
        assert resource.title == 'Research Paper'

    result_response = client.post(
        f'/result/create/{team_id}',
        data={
            'title': 'Prototype v1',
            'description': 'Initial working prototype',
            'content': '## Progress\nFunctional core completed.',
            'result_type': 'document',
            'status': 'draft',
            'repository_url': '',
            'demo_url': '',
            'category': '',
            'tags': 'prototype,iteration1',
        },
        follow_redirects=True,
    )
    assert result_response.status_code == 200

    with app.app_context():
        result = Result.query.filter_by(team_id=team_id).first()
        assert result is not None
        assert result.current_iteration_id is not None
        assert result.iterations.count() == 1
