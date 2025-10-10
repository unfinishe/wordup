"""Test the SRS service functionality."""

from src.services.srs import SRSService
from src.models import VocabularyCard, db

def test_srs_calculate_next_review(app):
    """Test SRS next review calculation."""
    with app.app_context():
        # Test correct answer progression
        box_level, next_review = SRSService.calculate_next_review(1, correct=True)
        assert box_level == 2
        assert next_review is not None
        
        # Test incorrect answer (should reset to box 1)
        box_level, next_review = SRSService.calculate_next_review(3, correct=False)
        assert box_level == 1
        assert next_review is not None

def test_srs_box_intervals(app):
    """Test that SRS box intervals are defined correctly."""
    with app.app_context():
        intervals = SRSService.BOX_INTERVALS
        assert len(intervals) == 5
        assert intervals[1] == 1  # Daily
        assert intervals[2] == 3  # Every 3 days
        assert intervals[5] == 30  # Monthly

def test_srs_get_due_cards(app, sample_chapter):
    """Test getting due cards."""
    with app.app_context():
        # Create some test cards
        from datetime import datetime, timedelta, timezone
        
        # Due card
        due_card = VocabularyCard(
            source_word="Due",
            target_word="Due",
            chapter_id=sample_chapter.id,
            next_review=datetime.now(timezone.utc) - timedelta(days=1)
        )
        
        # Not due card
        future_card = VocabularyCard(
            source_word="Future",
            target_word="Future", 
            chapter_id=sample_chapter.id,
            next_review=datetime.now(timezone.utc) + timedelta(days=1)
        )
        
        db.session.add_all([due_card, future_card])
        db.session.commit()
        
        all_cards = [due_card, future_card]
        due_cards = SRSService.get_due_cards(all_cards)
        
        assert len(due_cards) == 1
        assert due_cards[0].source_word == "Due"

def test_srs_calculate_chapter_stats(app, sample_chapter):
    """Test chapter statistics calculation."""
    with app.app_context():
        from src.models import ReviewHistory
        
        # Create a card with some review history
        card = VocabularyCard(
            source_word="Stats",
            target_word="Statistics",
            chapter_id=sample_chapter.id,
            box_level=2
        )
        db.session.add(card)
        db.session.commit()
        
        # Add some review history
        review1 = ReviewHistory(card_id=card.id, correct=True, direction="source_to_target")
        review2 = ReviewHistory(card_id=card.id, correct=False, direction="target_to_source")
        db.session.add_all([review1, review2])
        db.session.commit()
        
        # Calculate stats
        stats = SRSService.calculate_chapter_stats(sample_chapter)
        
        assert 'total_cards' in stats
        assert 'success_rate' in stats
        assert 'box_distribution' in stats
        assert stats['total_cards'] > 0