import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.interview import db, Interview, Document, Question, Response
from src.routes.user import user_bp
from src.routes.interview import interview_bp
from src.routes.settings import settings_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Production configuration
IS_PRODUCTION = os.environ.get('RAILWAY_ENVIRONMENT') is not None
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'synergos-ai-secret-key-2024')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure CORS
if IS_PRODUCTION:
    # In production, allow specific origins
    CORS(app, origins=["*"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
         allow_headers=["Content-Type", "Authorization"], supports_credentials=True)
else:
    # In development, allow all origins
    CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
         allow_headers=["Content-Type", "Authorization"])

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(interview_bp, url_prefix='/api')
app.register_blueprint(settings_bp, url_prefix='/api')

# Database configuration
if IS_PRODUCTION:
    # Use PostgreSQL on Railway if available, otherwise SQLite
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Fix postgres:// to postgresql:// for SQLAlchemy compatibility
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Use SQLite as fallback in production
        os.makedirs('/tmp/database', exist_ok=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/database/app.db'
else:
    # Use SQLite for development
    os.makedirs(os.path.join(os.path.dirname(__file__), 'database'), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # Don't serve static files for API routes
    if path.startswith('api/'):
        return "API endpoint not found", 404
        
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = not IS_PRODUCTION
    app.run(host='0.0.0.0', port=port, debug=debug)
