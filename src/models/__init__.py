from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, timezone
import json

db = SQLAlchemy()

class Chapter(db.Model):
    __tablename__ = 'chapters'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    source_language = db.Column(db.String(50), nullable=False)
    target_language = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationship to vocabulary cards
    cards = db.relationship('VocabularyCard', backref='chapter', lazy=True, cascade='all, delete-orphan')
    
    def get_success_rate(self):
        """Calculate success rate for this chapter"""
        if not self.cards:
            return 0
        
        total_reviews = sum(len(card.reviews) for card in self.cards)
        if total_reviews == 0:
            return 0
            
        successful_reviews = sum(
            len([r for r in card.reviews if r.correct]) 
            for card in self.cards
        )
        
        return round((successful_reviews / total_reviews) * 100, 1)
    
    def get_due_count(self):
        """Get count of cards due for review"""
        now = datetime.now(timezone.utc)
        return len([card for card in self.cards if card.is_due()])
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'source_language': self.source_language,
            'target_language': self.target_language,
            'card_count': len(self.cards),
            'success_rate': self.get_success_rate(),
            'due_count': self.get_due_count(),
            'created_at': self.created_at.isoformat()
        }

class VocabularyCard(db.Model):
    __tablename__ = 'vocabulary_cards'
    
    id = db.Column(db.Integer, primary_key=True)
    source_word = db.Column(db.String(200), nullable=False)
    target_word = db.Column(db.String(200), nullable=False)
    example_sentence = db.Column(db.Text)
    context_hint = db.Column(db.String(500), default='')  # Context or hint for the word pair
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # SRS fields
    box_level = db.Column(db.Integer, default=1)  # Leitner box (1-5)
    next_review = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)  # Index for due card queries
    
    # Foreign key
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    
    # Relationships
    reviews = db.relationship('ReviewHistory', backref='card', lazy=True, cascade='all, delete-orphan')
    
    def is_due(self):
        """Check if card is due for review"""
        now = datetime.now(timezone.utc)
        next_review = self.next_review
        
        # Handle timezone-naive datetimes from database
        if next_review.tzinfo is None:
            next_review = next_review.replace(tzinfo=timezone.utc)
            
        return now >= next_review
    
    def update_srs(self, correct):
        """Update SRS data based on review result"""
        from src.services.srs import SRSService
        self.box_level, self.next_review = SRSService.calculate_next_review(self.box_level, correct)
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_word': self.source_word,
            'target_word': self.target_word,
            'example_sentence': self.example_sentence,
            'context_hint': self.context_hint,
            'box_level': self.box_level,
            'next_review': self.next_review.isoformat(),
            'is_due': self.is_due(),
            'chapter_id': self.chapter_id
        }

class ReviewHistory(db.Model):
    __tablename__ = 'review_history'
    
    id = db.Column(db.Integer, primary_key=True)
    correct = db.Column(db.Boolean, nullable=False)
    direction = db.Column(db.String(20), nullable=False)  # 'source_to_target' or 'target_to_source'
    reviewed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)  # Index for statistics queries
    
    # Foreign key
    card_id = db.Column(db.Integer, db.ForeignKey('vocabulary_cards.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'correct': self.correct,
            'direction': self.direction,
            'reviewed_at': self.reviewed_at.isoformat(),
            'card_id': self.card_id
        }