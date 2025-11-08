from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from datetime import datetime
from src.models import Chapter, VocabularyCard, ReviewHistory, AppConfig, db
import json
import io
import zipfile
from werkzeug.utils import secure_filename
import tempfile
import os

from src.services.theming import (
    delete_background_image,
    get_theming_folder,
    save_background_image,
)

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
def admin_dashboard():
    """Admin dashboard showing export/import options"""
    chapters = Chapter.query.all()
    config = AppConfig.get_config()
    background_url = None
    if config.theming_background:
        background_url = url_for('main.theming_background', filename=config.theming_background)
    theming_folder = get_theming_folder(current_app)
    
    # Calculate overall statistics
    total_chapters = len(chapters)
    total_cards = sum(len(chapter.cards) for chapter in chapters)
    total_reviews = ReviewHistory.query.count()
    
    stats = {
        'total_chapters': total_chapters,
        'total_cards': total_cards,
        'total_reviews': total_reviews
    }
    
    return render_template(
        'admin/dashboard.html',
        chapters=chapters,
        stats=stats,
        theming_config=config,
        background_url=background_url,
        theming_folder=theming_folder
    )


@admin_bp.route('/theming', methods=['GET', 'POST'])
def theming_settings():
    """Manage theming settings."""
    config = AppConfig.get_config()
    background_url = None
    if config.theming_background:
        background_url = url_for('main.theming_background', filename=config.theming_background)

    if request.method == 'POST':
        action = request.form.get('action', 'save')

        if action == 'remove':
            delete_background_image(current_app, config.theming_background)
            config.theming_background = None
            config.theming_enabled = False
            db.session.commit()
            flash('Background image removed and theming disabled.', 'success')
            return redirect(url_for('admin.theming_settings'))

        enable_theming = bool(request.form.get('enable_theming'))
        uploaded_file = request.files.get('background_image')

        if uploaded_file and uploaded_file.filename:
            try:
                new_filename = save_background_image(current_app, uploaded_file)
            except ValueError as exc:
                db.session.rollback()
                flash(str(exc), 'error')
                return redirect(url_for('admin.theming_settings'))

            delete_background_image(current_app, config.theming_background)
            config.theming_background = new_filename
            background_url = url_for('main.theming_background', filename=config.theming_background)

        config.theming_enabled = enable_theming and bool(config.theming_background)
        db.session.commit()

        if enable_theming and not config.theming_background:
            flash('Upload a background image before enabling theming.', 'error')
        else:
            flash('Theming settings updated successfully.', 'success')

        return redirect(url_for('admin.theming_settings'))

    theming_folder = get_theming_folder(current_app)

    return render_template(
        'admin/theming.html',
        config=config,
        background_url=background_url,
        theming_folder=theming_folder
    )

@admin_bp.route('/export/chapter/<int:chapter_id>')
def export_chapter(chapter_id):
    """Export a single chapter with all its data"""
    chapter = Chapter.query.get_or_404(chapter_id)
    
    # Prepare chapter data
    chapter_data = {
        'chapter': {
            'name': chapter.name,
            'source_language': chapter.source_language,
            'target_language': chapter.target_language,
            'created_at': chapter.created_at.isoformat() if chapter.created_at else None
        },
        'cards': [],
        'review_history': []
    }
    
    # Add vocabulary cards
    for card in chapter.cards:
        card_data = {
            'source_word': card.source_word,
            'target_word': card.target_word,
            'example_sentence': card.example_sentence,
            'context_hint': card.context_hint,
            'box_level': card.box_level,
            'next_review': card.next_review.isoformat() if card.next_review else None
        }
        chapter_data['cards'].append(card_data)
        
        # Add review history for this card
        reviews = ReviewHistory.query.filter_by(card_id=card.id).all()
        for review in reviews:
            review_data = {
                'card_source_word': card.source_word,  # For reference during import
                'card_target_word': card.target_word,  # For reference during import
                'review_date': review.reviewed_at.isoformat(),
                'correct': review.correct,
                'direction': review.direction
            }
            chapter_data['review_history'].append(review_data)
    
    # Create JSON response
    filename = f"wordup_chapter_{secure_filename(chapter.name)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Create file-like object
    json_data = json.dumps(chapter_data, indent=2, ensure_ascii=False)
    file_obj = io.BytesIO(json_data.encode('utf-8'))
    
    return send_file(
        file_obj,
        as_attachment=True,
        download_name=filename,
        mimetype='application/json'
    )

@admin_bp.route('/export/all')
def export_all_data():
    """Export all chapters and data as a ZIP file"""
    chapters = Chapter.query.all()
    
    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for chapter in chapters:
            # Prepare chapter data (same as single export)
            chapter_data = {
                'chapter': {
                    'name': chapter.name,
                    'source_language': chapter.source_language,
                    'target_language': chapter.target_language,
                    'created_at': chapter.created_at.isoformat() if chapter.created_at else None
                },
                'cards': [],
                'review_history': []
            }
            
            # Add vocabulary cards and reviews
            for card in chapter.cards:
                card_data = {
                    'source_word': card.source_word,
                    'target_word': card.target_word,
                    'example_sentence': card.example_sentence,
                    'context_hint': card.context_hint,
                    'box_level': card.box_level,
                    'next_review': card.next_review.isoformat() if card.next_review else None
                }
                chapter_data['cards'].append(card_data)
                
                # Add review history
                reviews = ReviewHistory.query.filter_by(card_id=card.id).all()
                for review in reviews:
                    review_data = {
                        'card_source_word': card.source_word,
                        'card_target_word': card.target_word,
                        'review_date': review.reviewed_at.isoformat(),
                        'correct': review.correct,
                        'direction': review.direction
                    }
                    chapter_data['review_history'].append(review_data)
            
            # Add to ZIP
            json_data = json.dumps(chapter_data, indent=2, ensure_ascii=False)
            filename = f"chapter_{secure_filename(chapter.name)}.json"
            zip_file.writestr(filename, json_data.encode('utf-8'))
    
    # Rewind buffer to beginning for reading
    zip_buffer.seek(0)
    
    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name=f"wordup_full_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
        mimetype='application/zip'
    )

@admin_bp.route('/import', methods=['GET', 'POST'])
def import_data():
    """Import chapter data from JSON file"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if not file.filename or not file.filename.lower().endswith(('.json', '.zip')):
            flash('Please upload a JSON or ZIP file', 'error')
            return redirect(request.url)
        
        try:
            if file.filename and file.filename.lower().endswith('.zip'):
                # Handle ZIP file import
                import_count = _import_zip_file(file)
                flash(f'Successfully imported {import_count} chapters from ZIP file', 'success')
            else:
                # Handle single JSON file import
                _import_json_file(file)
                flash('Chapter imported successfully', 'success')
                
        except Exception as e:
            flash(f'Import failed: {str(e)}', 'error')
            db.session.rollback()
        
        return redirect(url_for('admin.admin_dashboard'))
    
    return render_template('admin/import.html')

def _import_json_file(file):
    """Import a single JSON file"""
    data = json.load(file)
    
    # Validate data structure
    if 'chapter' not in data or 'cards' not in data:
        raise ValueError('Invalid file format: missing chapter or cards data')
    
    chapter_info = data['chapter']
    
    # Check if chapter already exists
    existing_chapter = Chapter.query.filter_by(
        name=chapter_info['name'],
        source_language=chapter_info['source_language'],
        target_language=chapter_info['target_language']
    ).first()
    
    if existing_chapter:
        raise ValueError(f'Chapter "{chapter_info["name"]}" already exists')
    
    # Create new chapter
    chapter = Chapter(
        name=chapter_info['name'],
        source_language=chapter_info['source_language'],
        target_language=chapter_info['target_language']
    )
    
    if chapter_info.get('created_at'):
        try:
            chapter.created_at = datetime.fromisoformat(chapter_info['created_at'])
        except:
            pass  # Use default if parsing fails
    
    db.session.add(chapter)
    db.session.flush()  # Get the chapter ID
    
    # Import vocabulary cards
    card_mapping = {}  # Map old card identifiers to new card objects
    
    for card_data in data['cards']:
        card = VocabularyCard(
            chapter_id=chapter.id,
            source_word=card_data['source_word'],
            target_word=card_data['target_word'],
            example_sentence=card_data.get('example_sentence', ''),
            context_hint=card_data.get('context_hint', ''),
            box_level=card_data.get('box_level', 1)
        )
        
        if card_data.get('next_review'):
            try:
                card.next_review = datetime.fromisoformat(card_data['next_review'])
            except:
                pass  # Use default if parsing fails
        
        db.session.add(card)
        
        # Store mapping for review history
        card_key = f"{card_data['source_word']}:{card_data['target_word']}"
        card_mapping[card_key] = card
    
    db.session.flush()  # Get card IDs
    
    # Import review history if available
    if 'review_history' in data:
        for review_data in data['review_history']:
            card_key = f"{review_data['card_source_word']}:{review_data['card_target_word']}"
            if card_key in card_mapping:
                card = card_mapping[card_key]
                
                review = ReviewHistory(
                    card_id=card.id,
                    correct=review_data['correct'],
                    direction=review_data.get('direction', 'source_to_target')
                )
                
                if review_data.get('review_date'):
                    try:
                        review.reviewed_at = datetime.fromisoformat(review_data['review_date'])
                    except:
                        pass  # Use default if parsing fails
                
                db.session.add(review)
    
    db.session.commit()

def _import_zip_file(file):
    """Import multiple chapters from a ZIP file"""
    import_count = 0
    
    with zipfile.ZipFile(file, 'r') as zip_file:
        for filename in zip_file.namelist():
            if filename.endswith('.json'):
                with zip_file.open(filename) as json_file:
                    json_data = json_file.read().decode('utf-8')
                    # Create a file-like object for the JSON data
                    json_file_obj = io.StringIO(json_data)
                    
                    try:
                        _import_json_file(json_file_obj)
                        import_count += 1
                    except ValueError as e:
                        # Skip chapters that already exist or have errors
                        continue
    
    return import_count