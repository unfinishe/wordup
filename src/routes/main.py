import os

from flask import Blueprint, render_template, send_from_directory, current_app, abort
from src.models import Chapter, db, AppConfig
from src.services.srs import SRSService
from src.services.theming import get_theming_folder
from src.__version__ import __version__, RELEASE_NAME, BUILD_DATE

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    """Main dashboard showing chapters and statistics"""
    chapters = Chapter.query.all()
    
    # Calculate overall statistics
    total_cards = sum(len(chapter.cards) for chapter in chapters)
    total_due = sum(chapter.get_due_count() for chapter in chapters)
    
    # Get chapters with stats
    chapter_stats = []
    for chapter in chapters:
        stats = SRSService.calculate_chapter_stats(chapter)
        chapter_data = chapter.to_dict()
        chapter_data.update(stats)
        chapter_stats.append(chapter_data)
    
    return render_template('dashboard.html', 
                         chapters=chapter_stats,
                         total_cards=total_cards,
                         total_due=total_due)

@main_bp.route('/help')
def help_page():
    """Help page explaining WordUp usage and Leitner System"""
    version_info = {
        'version': __version__,
        'release_name': RELEASE_NAME,
        'build_date': BUILD_DATE
    }
    return render_template('help.html', version_info=version_info)


@main_bp.route('/theming/background/<path:filename>')
def theming_background(filename):
    config = AppConfig.get_config()
    if not config.theming_background or filename != config.theming_background:
        abort(404)

    folder = get_theming_folder(current_app)
    file_path = os.path.join(folder, filename)
    if not os.path.exists(file_path):
        abort(404)

    return send_from_directory(folder, filename)