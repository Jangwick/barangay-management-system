from flask import Flask, session, request
from models import db
from config import Config
from datetime import datetime
from flask_login import LoginManager
from models.user import User, ROLE_ADMIN

# Import routes
from routes.main import main
from routes.residents import residents_bp
from routes.officials import officials_bp
from routes.documents import documents_bp
from routes.projects import projects_bp
from routes.auth import auth_bp
from routes.admin import admin_bp

# Import utility functions
from utils import format_currency, calculate_age

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Set up login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(residents_bp)
    app.register_blueprint(officials_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    
    # Add template context processors for global access in templates
    @app.context_processor
    def utility_processor():
        return {
            'format_currency': format_currency,
            'calculate_age': calculate_age,
            'now': datetime.now()  # Add current datetime to all templates
        }
    
    return app

def create_admin_user(app):
    """Create an admin user if none exists"""
    with app.app_context():
        # Check if any admin users exist
        admin_exists = User.query.filter_by(role=ROLE_ADMIN).first() is not None
        
        if not admin_exists:
            # Create default admin account
            User.create_admin(
                username='admin',
                email='admin@example.com',
                password='admin123',  # This should be changed immediately after first login
                first_name='System',
                last_name='Administrator'
            )
            print("Default admin user created. Please change the password immediately.")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    
    # Create default admin if needed
    create_admin_user(app)
    
    app.run(debug=True)
