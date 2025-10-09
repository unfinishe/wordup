from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    """Application factory pattern"""
    # Get the directory of this file (src/) and set template/static paths relative to it
    app_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(__name__, 
                template_folder=os.path.join(app_dir, 'templates'),
                static_folder=os.path.join(app_dir, 'static'))
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Set database URI - handle both absolute and relative paths
    os.makedirs(app.instance_path, exist_ok=True)
    default_db_path = f'sqlite:///{app.instance_path}/wordup.db'
    
    # Get database URL from environment or use default
    database_url = os.getenv('DATABASE_URL', default_db_path)
    
    # If the database URL is a relative SQLite path, make it absolute
    if database_url.startswith('sqlite:///') and not os.path.isabs(database_url[10:]):
        # Extract the relative path (skip 'sqlite:///')
        relative_path = database_url[10:]
        # Make it absolute by joining with the app root directory
        app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        absolute_path = os.path.join(app_root, relative_path)
        database_url = f'sqlite:///{absolute_path}'
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    from src.models import db
    db.init_app(app)
    
    # Register blueprints
    from src.routes.main import main_bp
    from src.routes.chapters import chapters_bp
    from src.routes.cards import cards_bp
    from src.routes.learning import learning_bp
    from src.routes.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(chapters_bp, url_prefix='/chapters')
    app.register_blueprint(cards_bp, url_prefix='/cards')
    app.register_blueprint(learning_bp, url_prefix='/learn')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Create tables
    with app.app_context():
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        db.create_all()
    
    return app