from datetime import datetime, timedelta
import random

class SRSService:
    """Service for Spaced Repetition System logic"""
    
    # Leitner system intervals (in days)
    BOX_INTERVALS = {
        1: 1,    # Review daily
        2: 3,    # Review every 3 days  
        3: 7,    # Review weekly
        4: 14,   # Review bi-weekly
        5: 30    # Review monthly
    }
    
    @staticmethod
    def calculate_next_review(box_level, correct):
        """Calculate next review date based on current box and result"""
        if correct:
            # Move to next box (max 5)
            new_box = min(box_level + 1, 5)
        else:
            # Reset to box 1 on incorrect answer
            new_box = 1
        
        days_to_add = SRSService.BOX_INTERVALS[new_box]
        next_review = datetime.utcnow() + timedelta(days=days_to_add)
        
        return new_box, next_review
    
    @staticmethod
    def get_due_cards(cards):
        """Filter cards that are due for review"""
        now = datetime.utcnow()
        return [card for card in cards if card.next_review <= now]
    
    @staticmethod
    def get_random_direction():
        """Get random learning direction"""
        directions = ['source_to_target', 'target_to_source']
        return random.choice(directions)
    
    @staticmethod
    def get_review_queue(chapter, direction='random', limit=10):
        """Get cards for review session"""
        due_cards = SRSService.get_due_cards(chapter.cards)
        
        # Shuffle and limit
        random.shuffle(due_cards)
        queue = due_cards[:limit]
        
        # Add direction info
        for card in queue:
            if direction == 'random':
                card.review_direction = SRSService.get_random_direction()
            else:
                card.review_direction = direction
        
        return queue
    
    @staticmethod
    def calculate_chapter_stats(chapter):
        """Calculate comprehensive stats for a chapter"""
        if not chapter.cards:
            return {
                'total_cards': 0,
                'due_cards': 0,
                'success_rate': 0,
                'box_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                'total_reviews': 0
            }
        
        total_cards = len(chapter.cards)
        due_cards = len(SRSService.get_due_cards(chapter.cards))
        
        # Box distribution
        box_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for card in chapter.cards:
            box_distribution[card.box_level] += 1
        
        # Success rate calculation
        total_reviews = sum(len(card.reviews) for card in chapter.cards)
        if total_reviews > 0:
            successful_reviews = sum(
                len([r for r in card.reviews if r.correct]) 
                for card in chapter.cards
            )
            success_rate = round((successful_reviews / total_reviews) * 100, 1)
        else:
            success_rate = 0
        
        return {
            'total_cards': total_cards,
            'due_cards': due_cards,
            'success_rate': success_rate,
            'box_distribution': box_distribution,
            'total_reviews': total_reviews
        }