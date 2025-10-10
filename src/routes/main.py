from flask import Blueprint, render_template
from src.models import Chapter, db
from src.services.srs import SRSService
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