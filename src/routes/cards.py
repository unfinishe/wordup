from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from src.models import Chapter, VocabularyCard, db
from src.services.srs import SRSService

cards_bp = Blueprint('cards', __name__)

@cards_bp.route('/chapter/<int:chapter_id>')
def list_cards(chapter_id):
    """List all cards in a chapter"""
    chapter = Chapter.query.get_or_404(chapter_id)
    cards = VocabularyCard.query.filter_by(chapter_id=chapter_id).all()
    
    return render_template('cards/list.html', chapter=chapter, cards=cards)

@cards_bp.route('/chapter/<int:chapter_id>/new', methods=['GET', 'POST'])
def new_card(chapter_id):
    """Create new vocabulary card"""
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if request.method == 'POST':
        source_word = request.form.get('source_word', '').strip()
        target_word = request.form.get('target_word', '').strip()
        example_sentence = request.form.get('example_sentence', '').strip()
        context_hint = request.form.get('context_hint', '').strip()
        
        if not all([source_word, target_word]):
            flash('Source and target words are required', 'error')
            return render_template('cards/form.html', chapter=chapter)
        
        card = VocabularyCard(
            source_word=source_word,
            target_word=target_word,
            example_sentence=example_sentence if example_sentence else None,
            context_hint=context_hint if context_hint else '',
            chapter_id=chapter_id,
            box_level=1,
            next_review=datetime.utcnow()
        )
        
        db.session.add(card)
        db.session.commit()
        
        flash(f'Card "{source_word} → {target_word}" created successfully', 'success')
        return redirect(url_for('cards.list_cards', chapter_id=chapter_id))
    
    return render_template('cards/form.html', chapter=chapter)

@cards_bp.route('/<int:card_id>')
def view_card(card_id):
    """View card details"""
    card = VocabularyCard.query.get_or_404(card_id)
    return render_template('cards/detail.html', card=card)

@cards_bp.route('/<int:card_id>/edit', methods=['GET', 'POST'])
def edit_card(card_id):
    """Edit vocabulary card"""
    card = VocabularyCard.query.get_or_404(card_id)
    
    if request.method == 'POST':
        card.source_word = request.form.get('source_word', '').strip()
        card.target_word = request.form.get('target_word', '').strip()
        card.example_sentence = request.form.get('example_sentence', '').strip() or None
        card.context_hint = request.form.get('context_hint', '').strip()
        
        if not all([card.source_word, card.target_word]):
            flash('Source and target words are required', 'error')
            return render_template('cards/form.html', card=card)
        
        db.session.commit()
        flash('Card updated successfully', 'success')
        return redirect(url_for('cards.view_card', card_id=card.id))
    
    return render_template('cards/form.html', card=card)

@cards_bp.route('/<int:card_id>/delete', methods=['POST'])
def delete_card(card_id):
    """Delete vocabulary card"""
    card = VocabularyCard.query.get_or_404(card_id)
    chapter_id = card.chapter_id
    
    db.session.delete(card)
    db.session.commit()
    
    flash('Card deleted successfully', 'success')
    return redirect(url_for('cards.list_cards', chapter_id=chapter_id))

@cards_bp.route('/bulk-import/chapter/<int:chapter_id>', methods=['GET', 'POST'])
def bulk_import(chapter_id):
    """Bulk import cards from text"""
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if request.method == 'POST':
        text_data = request.form.get('text_data', '').strip()
        
        if not text_data:
            flash('Please provide card data', 'error')
            return render_template('cards/bulk_import.html', chapter=chapter)
        
        # Parse format: "source_word | target_word | example_sentence | context_hint"
        lines = text_data.split('\n')
        imported_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            parts = [part.strip() for part in line.split('|')]
            if len(parts) < 2:
                continue
                
            source_word = parts[0]
            target_word = parts[1]
            example_sentence = parts[2] if len(parts) > 2 and parts[2] else None
            context_hint = parts[3] if len(parts) > 3 and parts[3] else ''
            
            card = VocabularyCard(
                source_word=source_word,
                target_word=target_word,
                example_sentence=example_sentence,
                context_hint=context_hint,
                chapter_id=chapter_id,
                box_level=1,
                next_review=datetime.utcnow()
            )
            
            db.session.add(card)
            imported_count += 1
        
        if imported_count > 0:
            db.session.commit()
            flash(f'Successfully imported {imported_count} cards', 'success')
        else:
            flash('No valid cards found to import', 'warning')
        
        return redirect(url_for('cards.list_cards', chapter_id=chapter_id))
    
    return render_template('cards/bulk_import.html', chapter=chapter)