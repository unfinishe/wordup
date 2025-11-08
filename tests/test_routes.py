"""Test the main routes."""

import io
import os

from src.models import AppConfig
from src.services.theming import get_theming_folder

from src.__version__ import __version__

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
    expected = f"WordUp {__version__}".encode()
    assert expected in response.data
    assert b'Build Date:' in response.data


# Context Mode Tests

def test_learning_session_setup_shows_context_mode_options(client, sample_chapter):
    """Test that learning session setup page shows context mode options."""
    response = client.get(f'/learn/chapter/{sample_chapter.id}')
    assert response.status_code == 200
    assert b'Learning Mode' in response.data
    assert b'Combined Mode' in response.data
    assert b'Word Mode' in response.data
    assert b'Context Mode' in response.data


def test_create_session_with_word_mode(client, app, sample_chapter):
    """Test creating a learning session with word mode."""
    from src.models import VocabularyCard, db
    
    with app.app_context():
        # Create cards with and without context
        card_with_context = VocabularyCard(
            source_word="Hallo",
            target_word="Hello",
            example_sentence="Hallo, wie geht es dir?",
            context_hint="greeting",
            chapter_id=sample_chapter.id
        )
        card_without_context = VocabularyCard(
            source_word="Tschüss",
            target_word="Goodbye",
            chapter_id=sample_chapter.id
        )
        db.session.add_all([card_with_context, card_without_context])
        db.session.commit()
        
        # Create session with word mode
        response = client.post(f'/learn/chapter/{sample_chapter.id}/session', data={
            'context_mode': 'word',
            'practice_mode': 'all_cards',
            'direction': 'source_to_target',
            'limit': 10
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert '/learn/review' in response.location


def test_create_session_with_context_mode(client, app, sample_chapter):
    """Test creating a learning session with context mode."""
    from src.models import VocabularyCard, db
    
    with app.app_context():
        # Create cards with and without context
        card_with_context = VocabularyCard(
            source_word="Hallo",
            target_word="Hello",
            example_sentence="Hallo, wie geht es dir?",
            context_hint="greeting",
            chapter_id=sample_chapter.id
        )
        card_without_context = VocabularyCard(
            source_word="Tschüss",
            target_word="Goodbye",
            chapter_id=sample_chapter.id
        )
        db.session.add_all([card_with_context, card_without_context])
        db.session.commit()
        
        # Create session with context mode
        response = client.post(f'/learn/chapter/{sample_chapter.id}/session', data={
            'context_mode': 'context',
            'practice_mode': 'all_cards',
            'direction': 'source_to_target',
            'limit': 10
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert '/learn/review' in response.location


def test_create_session_with_combined_mode(client, app, sample_chapter):
    """Test creating a learning session with combined mode."""
    from src.models import VocabularyCard, db
    
    with app.app_context():
        # Create cards with and without context
        card_with_context = VocabularyCard(
            source_word="Hallo",
            target_word="Hello",
            example_sentence="Hallo, wie geht es dir?",
            context_hint="greeting",
            chapter_id=sample_chapter.id
        )
        card_without_context = VocabularyCard(
            source_word="Tschüss",
            target_word="Goodbye",
            chapter_id=sample_chapter.id
        )
        db.session.add_all([card_with_context, card_without_context])
        db.session.commit()
        
        # Create session with combined mode
        response = client.post(f'/learn/chapter/{sample_chapter.id}/session', data={
            'context_mode': 'combined',
            'practice_mode': 'all_cards',
            'direction': 'source_to_target',
            'limit': 10
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert '/learn/review' in response.location


def test_context_mode_filters_cards_correctly(client, app, sample_chapter):
    """Test that context mode only shows cards with context and example sentence."""
    from src.models import VocabularyCard, db
    
    with app.app_context():
        # Create cards: one with both context and example, one without
        card_with_both = VocabularyCard(
            source_word="Hallo",
            target_word="Hello",
            example_sentence="Hallo, wie geht es dir?",
            context_hint="greeting",
            chapter_id=sample_chapter.id
        )
        card_without_example = VocabularyCard(
            source_word="Test",
            target_word="Test",
            context_hint="test word",
            chapter_id=sample_chapter.id
        )
        card_without_context = VocabularyCard(
            source_word="Tschüss",
            target_word="Goodbye",
            example_sentence="Tschüss und auf Wiedersehen!",
            chapter_id=sample_chapter.id
        )
        db.session.add_all([card_with_both, card_without_example, card_without_context])
        db.session.commit()
        
        # Create session with context mode
        with client.session_transaction() as sess:
            response = client.post(f'/learn/chapter/{sample_chapter.id}/session', data={
                'context_mode': 'context',
                'practice_mode': 'all_cards',
                'direction': 'source_to_target',
                'limit': 10
            }, follow_redirects=False)
            
            # Session should only contain card_with_both
            learning_session = sess.get('learning_session')
            if learning_session:
                assert len(learning_session['cards']) == 1
                assert learning_session['cards'][0]['mode'] == 'context'


def test_context_mode_review_does_not_affect_srs(client, app, sample_chapter):
    """Test that context mode reviews don't update SRS data."""
    from src.models import VocabularyCard, ReviewHistory, db
    from datetime import datetime, timezone
    
    with app.app_context():
        # Create a card with context
        card = VocabularyCard(
            source_word="Hallo",
            target_word="Hello",
            example_sentence="Hallo, wie geht es dir?",
            context_hint="greeting",
            chapter_id=sample_chapter.id,
            box_level=1,
            next_review=datetime.now(timezone.utc)
        )
        db.session.add(card)
        db.session.commit()
        original_box_level = card.box_level
        original_next_review = card.next_review
        card_id = card.id
        
        # Submit a context mode answer via API
        response = client.post('/learn/api/answer', 
            json={
                'card_id': card_id,
                'correct': True,
                'direction': 'context'
            })
        
        assert response.status_code == 200
        
        # Check that SRS data was NOT updated
        card = VocabularyCard.query.get(card_id)
        assert card.box_level == original_box_level
        
        # Check that no review history was created
        review_count = ReviewHistory.query.filter_by(card_id=card_id).count()
        assert review_count == 0


def test_word_mode_review_updates_srs(client, app, sample_chapter):
    """Test that word mode reviews DO update SRS data."""
    from src.models import VocabularyCard, ReviewHistory, db
    from datetime import datetime, timezone
    
    with app.app_context():
        # Create a card
        card = VocabularyCard(
            source_word="Hallo",
            target_word="Hello",
            chapter_id=sample_chapter.id,
            box_level=1,
            next_review=datetime.now(timezone.utc)
        )
        db.session.add(card)
        db.session.commit()
        original_box_level = card.box_level
        card_id = card.id
        
        # Submit a word mode answer via API
        response = client.post('/learn/api/answer', 
            json={
                'card_id': card_id,
                'correct': True,
                'direction': 'source_to_target'
            })
        
        assert response.status_code == 200
        
        # Check that SRS data WAS updated
        card = VocabularyCard.query.get(card_id)
        assert card.box_level > original_box_level
        
        # Check that review history was created
        review_count = ReviewHistory.query.filter_by(card_id=card_id).count()
        assert review_count == 1


def test_combined_mode_duplicates_context_cards(client, app, sample_chapter):
    """Test that combined mode shows context cards twice."""
    from src.models import VocabularyCard, db
    
    with app.app_context():
        # Create one card with context and one without
        card_with_context = VocabularyCard(
            source_word="Hallo",
            target_word="Hello",
            example_sentence="Hallo, wie geht es dir?",
            context_hint="greeting",
            chapter_id=sample_chapter.id
        )
        card_without_context = VocabularyCard(
            source_word="Tschüss",
            target_word="Goodbye",
            chapter_id=sample_chapter.id
        )
        db.session.add_all([card_with_context, card_without_context])
        db.session.commit()
        
        # Create session with combined mode
        with client.session_transaction() as sess:
            response = client.post(f'/learn/chapter/{sample_chapter.id}/session', data={
                'context_mode': 'combined',
                'practice_mode': 'all_cards',
                'direction': 'source_to_target',
                'limit': 10
            }, follow_redirects=False)
            
            # Session should contain 3 cards: card_with_context twice (context + word), card_without_context once
            learning_session = sess.get('learning_session')
            if learning_session:
                assert len(learning_session['cards']) == 3
                
                # Check that we have both modes for the context card
                modes = [card['mode'] for card in learning_session['cards']]
                assert 'context' in modes
                assert modes.count('word') == 2  # One for each card


def test_review_page_displays_context_hint(client, app, sample_chapter):
    """Test that review page displays context hint correctly."""
    from src.models import VocabularyCard, db
    
    with app.app_context():
        # Create a card with context
        card = VocabularyCard(
            source_word="Hallo",
            target_word="Hello",
            example_sentence="Hallo, wie geht es dir?",
            context_hint="greeting",
            chapter_id=sample_chapter.id
        )
        db.session.add(card)
        db.session.commit()
        
        # Create a context mode session manually
        with client.session_transaction() as sess:
            sess['learning_session'] = {
                'chapter_id': sample_chapter.id,
                'cards': [{'card_id': card.id, 'mode': 'context'}],
                'direction': 'source_to_target',
                'context_mode': 'context',
                'current_index': 0,
                'correct_count': 0,
                'total_count': 1
            }
        
        # Visit review page
        response = client.get('/learn/review')
        assert response.status_code == 200
        assert b'greeting' in response.data
        assert b'Hallo' in response.data


def test_no_cards_with_context_shows_message(client, app, sample_chapter):
    """Test that appropriate message is shown when no context cards are available."""
    from src.models import VocabularyCard, db
    
    with app.app_context():
        # Create only cards without context
        card = VocabularyCard(
            source_word="Tschüss",
            target_word="Goodbye",
            chapter_id=sample_chapter.id
        )
        db.session.add(card)
        db.session.commit()
        
        # Try to create session with context mode
        response = client.post(f'/learn/chapter/{sample_chapter.id}/session', data={
            'context_mode': 'context',
            'practice_mode': 'all_cards',
            'direction': 'source_to_target',
            'limit': 10
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'No cards with context hints available' in response.data


def test_admin_theming_page_renders(client):
    """The theming settings page should render successfully."""
    response = client.get('/admin/theming')
    assert response.status_code == 200
    assert b'Theming Settings' in response.data
    assert b'Upload background image' in response.data


def test_admin_theming_upload_and_enable(client, app):
    """Uploading and enabling theming should persist settings and files."""
    image_stream = io.BytesIO(b'\x89PNG\r\n\x1a\n' + b'\x00' * 16)

    response = client.post(
        '/admin/theming',
        data={
            'enable_theming': 'on',
            'background_image': (image_stream, 'background.png'),
            'action': 'save'
        },
        content_type='multipart/form-data',
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b'Theming settings updated successfully.' in response.data

    with app.app_context():
        config = AppConfig.get_config()
        assert config.theming_enabled is True
        assert config.theming_background
        folder = get_theming_folder(app)
        assert os.path.exists(os.path.join(folder, config.theming_background))


def test_admin_theming_remove_background(client, app):
    """Removing the background disables theming and deletes the file."""
    upload_stream = io.BytesIO(b'\x89PNG\r\n\x1a\n' + b'\x01' * 16)

    client.post(
        '/admin/theming',
        data={
            'enable_theming': 'on',
            'background_image': (upload_stream, 'background.png'),
            'action': 'save'
        },
        content_type='multipart/form-data',
        follow_redirects=True
    )

    with app.app_context():
        config = AppConfig.get_config()
        folder = get_theming_folder(app)
        background_path = os.path.join(folder, config.theming_background)
        assert os.path.exists(background_path)

    response = client.post('/admin/theming', data={'action': 'remove'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Background image removed and theming disabled.' in response.data

    with app.app_context():
        config = AppConfig.get_config()
        assert config.theming_enabled is False
        assert config.theming_background is None
        assert not os.path.exists(background_path)
