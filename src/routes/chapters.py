from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from src.models import Chapter, VocabularyCard, db
from src.services.srs import SRSService

chapters_bp = Blueprint('chapters', __name__)

@chapters_bp.route('/')
def list_chapters():
    """List all chapters"""
    chapters = Chapter.query.all()
    chapter_data = []
    
    for chapter in chapters:
        stats = SRSService.calculate_chapter_stats(chapter)
        data = chapter.to_dict()
        data.update(stats)
        chapter_data.append(data)
    
    return render_template('chapters/list.html', chapters=chapter_data)

@chapters_bp.route('/new', methods=['GET', 'POST'])
def new_chapter():
    """Create new chapter"""
    if request.method == 'POST':
        name = request.form.get('name')
        source_language = request.form.get('source_language')
        target_language = request.form.get('target_language')
        
        if not all([name, source_language, target_language]):
            flash('All fields are required', 'error')
            return render_template('chapters/form.html')
        
        chapter = Chapter(
            name=name,
            source_language=source_language,
            target_language=target_language
        )
        
        db.session.add(chapter)
        db.session.commit()
        
        flash(f'Chapter "{name}" created successfully', 'success')
        return redirect(url_for('chapters.list_chapters'))
    
    return render_template('chapters/form.html')

@chapters_bp.route('/<int:chapter_id>')
def view_chapter(chapter_id):
    """View chapter details"""
    chapter = Chapter.query.get_or_404(chapter_id)
    stats = SRSService.calculate_chapter_stats(chapter)
    
    return render_template('chapters/detail.html', chapter=chapter, stats=stats)

@chapters_bp.route('/<int:chapter_id>/edit', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    """Edit chapter"""
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if request.method == 'POST':
        chapter.name = request.form.get('name')
        chapter.source_language = request.form.get('source_language')
        chapter.target_language = request.form.get('target_language')
        
        db.session.commit()
        flash('Chapter updated successfully', 'success')
        return redirect(url_for('chapters.view_chapter', chapter_id=chapter.id))
    
    return render_template('chapters/form.html', chapter=chapter)

@chapters_bp.route('/<int:chapter_id>/delete', methods=['POST'])
def delete_chapter(chapter_id):
    """Delete chapter"""
    chapter = Chapter.query.get_or_404(chapter_id)
    chapter_name = chapter.name
    
    db.session.delete(chapter)
    db.session.commit()
    
    flash(f'Chapter "{chapter_name}" deleted successfully', 'success')
    return redirect(url_for('chapters.list_chapters'))

@chapters_bp.route('/<int:chapter_id>/reset-stats', methods=['POST'])
def reset_chapter_stats(chapter_id):
    """Reset all statistics for a chapter"""
    chapter = Chapter.query.get_or_404(chapter_id)
    
    # Reset all cards to box 1 and clear review history
    for card in chapter.cards:
        card.box_level = 1
        card.next_review = datetime.utcnow()
        # Clear review history
        for review in card.reviews:
            db.session.delete(review)
    
    db.session.commit()
    flash(f'Statistics reset for chapter "{chapter.name}"', 'success')
    return redirect(url_for('chapters.view_chapter', chapter_id=chapter.id))