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
- **✅ Testing Suite**: Comprehensive pytest-based tests with 39% coverage and fixtures

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
tests/                  # Comprehensive test suite with pytest
├── conftest.py         # Test fixtures and configuration
├── test_app.py         # Application and database tests
├── test_models.py      # Model functionality and validation tests
├── test_routes.py      # Route and HTTP response tests
└── test_srs.py         # SRS service logic and algorithm tests
scripts/
├── run_tests.sh        # Test execution script with coverage
├── create_release.sh   # Automated release workflow (includes tests)
└── sync_version.py     # Version synchronization utility
main.py                 # Application entry point with environment configuration
pyproject.toml          # Dependencies, project metadata, and pytest configuration
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
- **Install dependencies**: `uv install` or `uv sync` (includes test dependencies)
- **Run application**: `uv run main.py` or `uv run python main.py`
- **Run tests**: `./scripts/run_tests.sh` or `PYTHONPATH=. uv run pytest -v`
- **Environment setup**: Copy `.env.example` to `.env` and configure
- **Database**: Automatically created on first run via SQLAlchemy
- **Development**: Flask debug mode enabled via `FLASK_DEBUG=true` in .env
- **Release workflow**: `./scripts/create_release.sh <version>` (automatically runs tests)

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

## Testing & Quality Assurance

### Automated Testing (MANDATORY)
WordUp has a comprehensive test suite that **MUST be maintained and extended** for all changes:

- **Test Coverage**: Currently 39% with focus on core business logic
- **Test Framework**: pytest with Flask-testing and coverage reporting
- **Test Types**: Unit tests for models, services, routes, and application
- **CI Integration**: Tests run automatically during release process

### Testing Requirements for Code Changes

**🚨 CRITICAL: All code changes require corresponding tests**

#### When Adding New Features:
1. **Write tests FIRST** (TDD approach preferred)
2. **Test both positive and negative cases**
3. **Include edge cases and error conditions**
4. **Maintain or improve coverage percentage**

#### When Modifying Existing Code:
1. **Run existing tests first**: `./scripts/run_tests.sh`
2. **Update affected tests** to match new behavior
3. **Add tests for new functionality or edge cases**
4. **Verify all tests pass before committing**

#### Test Categories to Include:
- **Model Tests** (`tests/test_models.py`): Database operations, validation, relationships
- **Service Tests** (`tests/test_srs.py`): Business logic, algorithms, calculations
- **Route Tests** (`tests/test_routes.py`): HTTP responses, form handling, authentication
- **Integration Tests** (`tests/test_app.py`): Application setup, database connections

### Testing Best Practices

#### Test Fixtures and Data:
- Use `conftest.py` fixtures for consistent test data
- **Database isolation**: Each test uses clean database state
- **SQLAlchemy sessions**: Proper session management with cleanup
- **Timezone handling**: Use `datetime.now(timezone.utc)` consistently

#### Test Structure:
```python
def test_feature_description(app, sample_chapter):
    """Clear description of what is being tested."""
    with app.app_context():
        # Arrange: Set up test data
        
        # Act: Execute the functionality
        
        # Assert: Verify expected outcomes
```

#### DateTime Handling:
- **ALWAYS use timezone-aware datetime objects**
- Import: `from datetime import datetime, timezone`
- Create: `datetime.now(timezone.utc)` instead of `datetime.utcnow()`
- Handle database naive datetimes with `.replace(tzinfo=timezone.utc)`
- **Note**: All deprecation warnings have been eliminated (Python 3.12+ compatible)

### Test Execution Commands:
```bash
# Quick test run with coverage
./scripts/run_tests.sh

# Run specific test categories
PYTHONPATH=. uv run pytest tests/test_models.py -v
PYTHONPATH=. uv run pytest tests/test_srs.py -v
PYTHONPATH=. uv run pytest tests/test_routes.py -v

# Run with coverage details
PYTHONPATH=. uv run pytest --cov=src --cov-report=html --cov-report=term-missing
```

### Code Quality Standards
- **Database Integrity**: Foreign key constraints and proper relationships
- **Error Handling**: Graceful error messages and rollback protection
- **Responsive Design**: Mobile and desktop browser compatibility
- **Type Safety**: SQLAlchemy model validation and constraint checking
- **Security**: Input validation and sanitization in forms

## AI Development Guidelines

### Code Change Protocol
When implementing features or fixes, follow this workflow:

1. **Assess Test Impact**: Identify which tests might be affected
2. **Run Current Tests**: Execute `./scripts/run_tests.sh` to establish baseline
3. **Implement Changes**: Make code modifications with testing in mind
4. **Write/Update Tests**: Add tests for new functionality, update existing tests
5. **Verify Test Suite**: Ensure all tests pass with `PYTHONPATH=. uv run pytest -v`
6. **Check Coverage**: Maintain or improve coverage percentage

### Test-First Development
For new features, prioritize this approach:
1. **Write failing tests** that describe the desired behavior
2. **Implement minimal code** to make tests pass
3. **Refactor and optimize** while keeping tests green
4. **Add edge case tests** for robustness

### File Modification Guidelines
- **Models** (`src/models/__init__.py`): Add corresponding tests in `test_models.py`
- **Services** (`src/services/srs.py`): Add business logic tests in `test_srs.py`
- **Routes** (`src/routes/*.py`): Add HTTP tests in `test_routes.py`
- **Templates/Static**: Add integration tests for user workflows

### Database Changes
- **Schema modifications**: Update fixtures in `conftest.py`
- **New models**: Create comprehensive CRUD tests
- **Relationship changes**: Test cascade behavior and constraints
- **Migration needs**: Consider data migration scripts

### Common Pitfalls to Avoid
- **Skipping tests**: Never implement features without corresponding tests
- **Breaking existing tests**: Always run test suite before and after changes
- **Timezone issues**: Use timezone-aware datetime objects consistently
- **Test data pollution**: Ensure proper fixture cleanup and isolation
- **Coverage regression**: Don't merge code that significantly reduces coverage

---

For major changes, update this file and `README.md` to keep agent guidance current.
