"""Test the Flask application factory and basic functionality."""

def test_app_creation(app):
    """Test that the app is created correctly."""
    assert app is not None
    assert app.config['TESTING'] is True

def test_app_context(app):
    """Test that app context works."""
    with app.app_context():
        from src.models import db
        assert db is not None

def test_database_tables(app):
    """Test that database tables are created."""
    with app.app_context():
        from src.models import db
        # Check that tables exist
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        assert 'chapters' in tables
        assert 'vocabulary_cards' in tables
        assert 'review_history' in tables