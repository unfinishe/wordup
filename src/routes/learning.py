from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from datetime import datetime
from src.models import Chapter, VocabularyCard, ReviewHistory, db
from src.services.srs import SRSService
import random

learning_bp = Blueprint('learning', __name__)

@learning_bp.route('/chapter/<int:chapter_id>')
def start_session(chapter_id):
    """Start learning session setup"""
    chapter = Chapter.query.get_or_404(chapter_id)
    due_count = chapter.get_due_count()
    
    # Calculate box distribution for display
    box_distribution = {}
    for i in range(1, 6):
        box_distribution[i] = len([card for card in chapter.cards if card.box_level == i])
    
    return render_template('learning/setup.html', 
                         chapter=chapter, 
                         due_count=due_count,
                         box_distribution=box_distribution)

@learning_bp.route('/chapter/<int:chapter_id>/session', methods=['POST'])
def create_session(chapter_id):
    """Create learning session with specified parameters"""
    chapter = Chapter.query.get_or_404(chapter_id)
    
    direction = request.form.get('direction', 'random')
    limit = min(int(request.form.get('limit', 10)), 50)  # Max 50 cards per session
    context_mode = request.form.get('context_mode', 'combined')  # context, word, or combined
    
    # Check if user wants to practice all cards, specific box, or just due cards
    practice_mode = request.form.get('practice_mode', 'due_only')
    
    if practice_mode == 'all_cards':
        # Get all cards from the chapter
        all_cards = list(chapter.cards)
        random.shuffle(all_cards)
        queue = all_cards[:limit]
        # Set direction for each card
        for card in queue:
            if direction == 'random':
                card.review_direction = SRSService.get_random_direction()
            else:
                card.review_direction = direction
    elif practice_mode == 'box_specific':
        # Get cards from specific box level
        box_level = int(request.form.get('box_level', 1))
        box_cards = [card for card in chapter.cards if card.box_level == box_level]
        random.shuffle(box_cards)
        queue = box_cards[:limit]
        # Set direction for each card
        for card in queue:
            if direction == 'random':
                card.review_direction = SRSService.get_random_direction()
            else:
                card.review_direction = direction
    else:
        # Get review queue (due cards only)
        queue = SRSService.get_review_queue(chapter, direction, limit)
    
    # Apply context mode filtering
    if context_mode == 'context':
        # Only cards with both context_hint and example_sentence
        queue = [card for card in queue if card.context_hint and card.example_sentence]
    elif context_mode == 'word':
        # All cards (no filtering), but we'll handle display differently
        pass
    elif context_mode == 'combined':
        # Duplicate cards that have context for two reviews
        # We'll handle this in the review phase by tracking card presentation mode
        pass
    
    if not queue:
        if practice_mode == 'box_specific':
            box_level = int(request.form.get('box_level', 1))
            flash(f'No cards available in Box {box_level} for this chapter', 'info')
        elif context_mode == 'context':
            flash('No cards with context hints available for review in this chapter', 'info')
        else:
            flash('No cards available for review in this chapter', 'info')
        return redirect(url_for('chapters.view_chapter', chapter_id=chapter_id))
    
    # Build session cards list with presentation mode for combined mode
    # We also pre-compute and persist the direction per card so recap mode can reuse it
    session_cards = []
    for card in queue:
        def build_word_entry(c):
            if direction == 'random':
                chosen = SRSService.get_random_direction()
            else:
                chosen = direction
            return {'card_id': c.id, 'mode': 'word', 'direction': chosen}
        def build_context_entry(c):
            # Context questions always use logical 'context' direction marker
            return {'card_id': c.id, 'mode': 'context', 'direction': 'context'}

        if context_mode == 'combined' and card.context_hint and card.example_sentence:
            session_cards.append(build_context_entry(card))
            session_cards.append(build_word_entry(card))
        else:
            if context_mode == 'context':
                session_cards.append(build_context_entry(card))
            else:
                session_cards.append(build_word_entry(card))
    
    # Shuffle the session cards for combined mode
    if context_mode == 'combined':
        random.shuffle(session_cards)
    
    # Store session in Flask session
    session['learning_session'] = {
        'chapter_id': chapter_id,
        'cards': session_cards,
        'context_mode': context_mode,
        'current_index': 0,
        'correct_count': 0,
        'total_count': len(session_cards),
        'wrong_cards': [],  # Track wrong cards for recap mode
        'is_recap': False   # Flag to identify recap sessions
    }
    
    return redirect(url_for('learning.review_card'))

@learning_bp.route('/review')
def review_card():
    """Show current card for review"""
    if 'learning_session' not in session:
        flash('No active learning session', 'error')
        return redirect(url_for('main.dashboard'))
    
    session_data = session['learning_session']
    
    # Check if session is complete
    if session_data['current_index'] >= len(session_data['cards']):
        return redirect(url_for('learning.session_complete'))
    
    # Get current card and presentation mode
    card_info = session_data['cards'][session_data['current_index']]
    card_id = card_info['card_id']
    presentation_mode = card_info['mode']
    
    card = VocabularyCard.query.get_or_404(card_id)
    
    # Determine direction and question/answer based on presentation mode / stored direction
    stored_direction = card_info.get('direction')
    if presentation_mode == 'context':
        question = card.source_word
        answer = card.example_sentence
        question_lang = card.chapter.source_language
        answer_lang = card.chapter.target_language
        review_direction = 'context'
        show_context_hint = True
    else:
        # Per-card direction should always be present; fallback to source_to_target as safe default
        if stored_direction is None:
            stored_direction = 'source_to_target'
        
        review_direction = stored_direction
        if review_direction == 'source_to_target':
            question = card.source_word
            answer = card.target_word
            question_lang = card.chapter.source_language
            answer_lang = card.chapter.target_language
        elif review_direction == 'target_to_source':
            question = card.target_word
            answer = card.source_word
            question_lang = card.chapter.target_language
            answer_lang = card.chapter.source_language
        else:  # Unexpected token, default safe
            question = card.source_word
            answer = card.target_word
            question_lang = card.chapter.source_language
            answer_lang = card.chapter.target_language
        show_context_hint = False
    
    return render_template('learning/review.html',
                         card=card,
                         chapter=card.chapter,
                         question=question,
                         answer=answer,
                         question_lang=question_lang,
                         answer_lang=answer_lang,
                         direction=review_direction,
                         presentation_mode=presentation_mode,
                         show_context_hint=show_context_hint,
                         progress=session_data['current_index'] + 1,
                         total=session_data['total_count'])

@learning_bp.route('/answer', methods=['POST'])
def submit_answer():
    """Submit answer for current card"""
    if 'learning_session' not in session:
        flash('No active learning session', 'error')
        return redirect(url_for('main.dashboard'))
    
    card_id = request.form.get('card_id')
    card = VocabularyCard.query.get_or_404(card_id)
    correct = request.form.get('correct') == 'true'
    direction = request.form.get('direction')
    
    session_data = session['learning_session']
    is_recap = session_data.get('is_recap', False)
    
    # Only update SRS data for word mode and non-recap sessions.
    # Context mode and recap sessions never impact SRS scheduling.
    if direction != 'context' and not is_recap:
        # Update SRS data
        card.update_srs(correct)
        
        # Record review history
        review = ReviewHistory(
            card_id=card.id,
            correct=correct,
            direction=direction
        )
        
        db.session.add(review)
        db.session.commit()
    
    # Update session data
    if correct:
        session_data['correct_count'] += 1
    else:
        # Track wrong cards for recap mode (even during recap to allow multiple rounds)
        card_info = session_data['cards'][session_data['current_index']]
        # Ensure we keep original per-card direction if available
        wrong_direction = card_info.get('direction', direction)
        session_data['wrong_cards'].append({
            'card_id': int(card_id),  # Explicit int cast for type safety
            'direction': wrong_direction,
            'mode': card_info['mode']
        })
    
    session_data['current_index'] += 1
    session['learning_session'] = session_data
    
    return jsonify({'success': True})

@learning_bp.route('/session-complete')
def session_complete():
    """Show session completion summary"""
    if 'learning_session' not in session:
        flash('No session data found', 'error')
        return redirect(url_for('main.dashboard'))
    
    session_data = session['learning_session']
    chapter = Chapter.query.get_or_404(session_data['chapter_id'])
    
    # Calculate session stats
    accuracy = round((session_data['correct_count'] / session_data['total_count']) * 100, 1)
    wrong_count = len(session_data.get('wrong_cards', []))

    # If no wrong cards remain we can safely clear the session immediately
    if wrong_count == 0:
        session.pop('learning_session', None)
    
    return render_template('learning/complete.html',
                         chapter=chapter,
                         correct_count=session_data['correct_count'],
                         total_count=session_data['total_count'],
                         accuracy=accuracy,
                         wrong_count=wrong_count,
                         has_wrong_cards=wrong_count > 0)

@learning_bp.route('/chapter/<int:chapter_id>/recap')
def start_recap(chapter_id):
    """Start a recap session with wrong cards from previous session"""
    if 'learning_session' not in session:
        flash('No previous session found for recap', 'error')
        return redirect(url_for('chapters.view_chapter', chapter_id=chapter_id))
    
    session_data = session['learning_session']
    
    # Verify chapter matches
    if session_data.get('chapter_id') != chapter_id:
        flash('Session chapter mismatch', 'error')
        return redirect(url_for('chapters.view_chapter', chapter_id=chapter_id))
    
    wrong_cards = session_data.get('wrong_cards', [])
    
    if not wrong_cards:
        flash('No wrong cards to recap', 'info')
        # Clear session and redirect
        session.pop('learning_session', None)
        return redirect(url_for('chapters.view_chapter', chapter_id=chapter_id))
    
    # Create new recap session with wrong cards
    chapter = Chapter.query.get_or_404(chapter_id)
    
    # Create new session with wrong cards - maintaining their original direction and mode
    session['learning_session'] = {
        'chapter_id': chapter_id,
        'cards': wrong_cards,  # Each entry already contains its own direction
        'context_mode': session_data.get('context_mode', 'combined'),
        'current_index': 0,
        'correct_count': 0,
        'total_count': len(wrong_cards),
        'wrong_cards': [],
        'is_recap': True
    }
    
    flash(f'Recapping {len(wrong_cards)} card(s) you got wrong', 'info')
    return redirect(url_for('learning.review_card'))

@learning_bp.route('/session/end')
def end_session():
    """End session and clear session data"""
    session.pop('learning_session', None)
    flash('Session ended', 'info')
    return redirect(url_for('main.dashboard'))

@learning_bp.route('/api/answer', methods=['POST'])
def api_submit_answer():
    """API endpoint for submitting answers (AJAX)"""
    data = request.get_json()
    card_id = data.get('card_id')
    correct = data.get('correct')
    direction = data.get('direction')
    
    if not all([card_id, correct is not None, direction]):
        return jsonify({'error': 'Missing required data'}), 400
    
    card = VocabularyCard.query.get_or_404(card_id)
    
    # Update session data if active
    if 'learning_session' in session:
        session_data = session['learning_session']
        is_recap = session_data.get('is_recap', False)

        # Only update SRS data for word mode and non-recap sessions
        if direction != 'context' and not is_recap:
            card.update_srs(correct)
            review = ReviewHistory(
                card_id=card.id,
                correct=correct,
                direction=direction
            )
            db.session.add(review)
            db.session.commit()

        # Track results & wrong answers
        if correct:
            session_data['correct_count'] += 1
        else:
            card_info = session_data['cards'][session_data['current_index']]
            wrong_direction = card_info.get('direction', direction)
            session_data['wrong_cards'].append({
                'card_id': int(card_id),  # Explicit int cast for type safety
                'direction': wrong_direction,
                'mode': card_info['mode']
            })

        session_data['current_index'] += 1
        session['learning_session'] = session_data
    
    return jsonify({'success': True})