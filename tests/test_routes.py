"""Test the main routes."""

def test_dashboard_route(client):
    """Test the main dashboard route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'WordUp' in response.data

def test_help_route(client):
    """Test the help route."""
    response = client.get('/help')
    assert response.status_code == 200
    assert b'Help Guide' in response.data

def test_help_version_info(client):
    """Test that version info appears on help page."""
    response = client.get('/help')
    assert response.status_code == 200
    assert b'WordUp 1.0.0' in response.data
    assert b'Build Date:' in response.data