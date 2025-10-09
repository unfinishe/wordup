# Copilot Instructions for WordUp

## Project Overview
- **WordUp** is a complete Python web-based vocabulary trainer using the Leitner Spaced Repetition System (SRS) for effective language learning.
- Fully implemented Flask application with SQLAlchemy ORM, featuring multi-language support, context hints, chapter organization, and comprehensive progress tracking.
- Includes admin panel for data export/import, box-specific practice modes, and responsive web interface.
- Data is stored in SQLite with configurable database paths. Project managed with `uv` for dependency management.

## Architecture & Implementation Status
- **✅ COMPLETE**: Full Flask web application with all core features implemented
- **✅ Database**: SQLAlchemy models for chapters, vocabulary cards, review history, and SRS data
- **✅ Web Interface**: Responsive templates with CSS styling and JavaScript interactions
- **✅ Learning System**: Complete Leitner system with 5-box progression and smart scheduling
- **✅ Admin Features**: Export/import functionality for backup and data migration

## Key Files & Structure
```
src/
├── app.py              # Flask application factory with blueprint registration
├── models/__init__.py  # SQLAlchemy models (Chapter, VocabularyCard, ReviewHistory)
├── routes/             # Flask blueprints for different features
│   ├── main.py         # Dashboard and help pages
│   ├── chapters.py     # Chapter CRUD and statistics
│   ├── cards.py        # Vocabulary card management and bulk import
│   ├── learning.py     # Learning sessions and SRS logic
│   └── admin.py        # Export/import and admin functions
├── services/
│   └── srs.py          # Leitner system implementation and statistics
├── templates/          # Jinja2 templates organized by feature
├── static/             # CSS and JavaScript assets
main.py                 # Application entry point with environment configuration
pyproject.toml          # Dependencies and project metadata
.env.example            # Environment variable template
```

## Core Features (All Implemented)
- **Multi-Language Support**: Chapters with source/target language pairs
- **Vocabulary Management**: CRUD operations, bulk import, context hints
- **Leitner SRS System**: 5-box progression with automatic scheduling
- **Learning Modes**: Due cards, practice mode, box-specific practice
- **Progress Tracking**: Success rates, box distribution, review history
- **Admin Panel**: Export/import chapters with full data preservation
- **Context Hints**: Additional descriptive information for word pairs
- **Responsive Design**: Mobile-friendly interface with modern styling

## Database Schema
```sql
-- Chapters: Organize vocabulary by topic/language pair
chapters (id, name, source_language, target_language, created_at)

-- Vocabulary Cards: Word pairs with SRS tracking
vocabulary_cards (id, chapter_id, source_word, target_word, 
                 example_sentence, context_hint, box_level, next_review, created_at)

-- Review History: Track learning progress
review_history (id, card_id, correct, direction, reviewed_at)
```

## Developer Workflows
- **Install dependencies**: `uv install` or `uv sync`
- **Run application**: `uv run main.py` or `uv run python main.py`
- **Environment setup**: Copy `.env.example` to `.env` and configure
- **Database**: Automatically created on first run via SQLAlchemy
- **Development**: Flask debug mode enabled via `FLASK_DEBUG=true` in .env

## Configuration
Environment variables (see `.env.example`):
- `SECRET_KEY`: Flask secret key for sessions
- `DATABASE_URL`: SQLite database path (relative or absolute)
- `WORDUP_HOST`: Server host (default: 127.0.0.1)
- `WORDUP_PORT`: Server port (default: 5000)
- `FLASK_DEBUG`: Enable debug mode for development

## Extension Points
- **SRS Algorithms**: Modify `src/services/srs.py` for different spaced repetition approaches
- **Export Formats**: Add new formats in `src/routes/admin.py`
- **Learning Modes**: Extend practice options in `src/routes/learning.py`
- **UI Themes**: Customize CSS variables in `src/static/style.css`
- **Language Processing**: Add text processing in vocabulary import/export

## Testing & Quality
- **Manual Testing**: Use admin import/export for data validation
- **Database Integrity**: Foreign key constraints and proper relationships
- **Error Handling**: Graceful error messages and rollback protection
- **Responsive Design**: Tested on mobile and desktop browsers

---

For major changes, update this file and `README.md` to keep agent guidance current.
