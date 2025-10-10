"""Test the data models."""

from datetime import datetime, timezone
from src.models import db, Chapter, VocabularyCard, ReviewHistory

def test_chapter_creation(app):
    """Test creating a chapter."""
    with app.app_context():
        chapter = Chapter(
            name="Test Chapter",
            source_language="German",
            target_language="English"
        )
        db.session.add(chapter)
        db.session.commit()
        
        assert chapter.id is not None
        assert chapter.name == "Test Chapter"
        assert chapter.source_language == "German"
        assert chapter.target_language == "English"
        assert chapter.created_at is not None

def test_chapter_to_dict(app, sample_chapter):
    """Test chapter serialization."""
    with app.app_context():
        chapter_dict = sample_chapter.to_dict()
        
        assert 'id' in chapter_dict
        assert 'name' in chapter_dict
        assert 'source_language' in chapter_dict
        assert 'target_language' in chapter_dict
        assert 'created_at' in chapter_dict

def test_vocabulary_card_creation(app, sample_chapter):
    """Test creating a vocabulary card."""
    with app.app_context():
        card = VocabularyCard(
            source_word="Danke",
            target_word="Thank you",
            example_sentence="Danke für die Hilfe",
            context_hint="gratitude",
            chapter_id=sample_chapter.id,
            box_level=1
        )
        db.session.add(card)
        db.session.commit()
        
        assert card.id is not None
        assert card.source_word == "Danke"
        assert card.target_word == "Thank you"
        assert card.box_level == 1
        assert card.chapter_id == sample_chapter.id

def test_vocabulary_card_is_due(app, sample_chapter):
    """Test vocabulary card due checking."""
    with app.app_context():
        # Card with past due date
        card = VocabularyCard(
            source_word="Test",
            target_word="Test",
            chapter_id=sample_chapter.id,
            box_level=1,
            next_review=datetime(2020, 1, 1, tzinfo=timezone.utc)  # Past date with timezone
        )
        db.session.add(card)
        db.session.commit()
        
        assert card.is_due() is True

def test_vocabulary_card_update_srs(app, sample_chapter):
    """Test SRS update functionality."""
    with app.app_context():
        card = VocabularyCard(
            source_word="Test",
            target_word="Test", 
            chapter_id=sample_chapter.id,
            box_level=1
        )
        db.session.add(card)
        db.session.commit()
        
        original_box = card.box_level
        card.update_srs(correct=True)
        
        assert card.box_level == original_box + 1
        assert card.next_review is not None

def test_review_history_creation(app, sample_card):
    """Test creating review history."""
    with app.app_context():
        review = ReviewHistory(
            card_id=sample_card.id,
            correct=True,
            direction="source_to_target"
        )
        db.session.add(review)
        db.session.commit()
        
        assert review.id is not None
        assert review.correct is True
        assert review.direction == "source_to_target"
        assert review.reviewed_at is not None