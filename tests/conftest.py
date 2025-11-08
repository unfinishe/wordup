"""Test configuration and fixtures for WordUp tests."""

import os
import shutil
import sys
import tempfile

import pytest

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.app import create_app
from src.models import db, Chapter, VocabularyCard

@pytest.fixture
def app():
    """Create and configure a test Flask app."""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Set test configuration
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False
    }
    
    # Create app with test config
    app = create_app(test_config)
    
    with app.app_context():
        db.create_all()
        yield app
        
    # Cleanup
    os.close(db_fd)
    if os.path.exists(db_path):
        os.unlink(db_path)

    theming_dir = os.path.join(os.path.dirname(db_path), 'theming')
    if os.path.exists(theming_dir):
        shutil.rmtree(theming_dir)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def sample_chapter(app):
    """Create a sample chapter for testing."""
    with app.app_context():
        chapter = Chapter(
            name="Test German",
            source_language="German", 
            target_language="English"
        )
        db.session.add(chapter)
        db.session.commit()
        # Refresh to ensure we have the ID and stay attached to session
        db.session.refresh(chapter)
        yield chapter
        # Cleanup
        db.session.delete(chapter)
        db.session.commit()

@pytest.fixture
def sample_card(app, sample_chapter):
    """Create a sample vocabulary card for testing."""
    with app.app_context():
        card = VocabularyCard(
            source_word="Hallo",
            target_word="Hello",
            example_sentence="Hallo, wie geht es dir?",
            context_hint="greeting",
            chapter_id=sample_chapter.id,
            box_level=1
        )
        db.session.add(card)
        db.session.commit()
        # Refresh to ensure we have the ID and stay attached to session
        db.session.refresh(card)
        yield card
        # Cleanup
        db.session.delete(card)
        db.session.commit()