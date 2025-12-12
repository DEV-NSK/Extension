from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database.models import db
from routes.chat import chat_bp
from routes.tracking import tracking_bp
from sqlalchemy import text
import logging
import os

def create_app():
    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configure CORS
    CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)
    
    # Initialize database
    db.init_app(app)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Check Gemini API key
    if not Config.GEMINI_API_KEY or Config.GEMINI_API_KEY == 'your_actual_gemini_api_key_here':
        logger.warning("⚠️ WARNING: Gemini API key is not configured!")
        logger.warning("Please add your Gemini API key to the .env file")
        logger.warning("Get API key from: https://ai.google.dev/")
    else:
        logger.info("✅ Gemini API key is configured")
    
    # Register blueprints
    app.register_blueprint(chat_bp)
    app.register_blueprint(tracking_bp)
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        gemini_status = "configured" if Config.GEMINI_API_KEY and Config.GEMINI_API_KEY != 'your_actual_gemini_api_key_here' else "not_configured"
        
        return jsonify({
            "status": "healthy", 
            "service": "browser-extension-backend",
            "database": "connected",
            "gemini_ai": gemini_status,
            "endpoints": {
                "chat": "/api/chat/send",
                "tracking": "/api/track/activity",
                "history": "/api/chat/history/<user_id>",
                "summary": "/api/track/summary/<user_id>"
            }
        })
    
    def check_db_connection():
        """Check if database connection is working"""
        try:
            with app.app_context():
                db.session.execute(text('SELECT 1'))
            return True
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            return False
    
    # Initialize database tables (with error handling)
    try:
        with app.app_context():
            # Test connection first
            logger.info("Testing database connection...")
            db.session.execute(text('SELECT 1'))
            logger.info("Database connection successful!")
            
            # Create tables
            logger.info("Creating database tables...")
            db.create_all()
            logger.info("Database tables created successfully!")
            
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        logger.error("Please check your MySQL configuration...")
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    print(f"\n{'='*60}")
    print("BROWSER EXTENSION BACKEND STARTING")
    print(f"{'='*60}")
    print(f"API Server: http://localhost:{port}")
    print(f"Health Check: http://localhost:{port}/api/health")
    print(f"Gemini AI Status: {'✅ Configured' if Config.GEMINI_API_KEY and Config.GEMINI_API_KEY != 'your_actual_gemini_api_key_here' else '❌ NOT CONFIGURED'}")
    print(f"{'='*60}\n")
    
    app.run(debug=True, host='0.0.0.0', port=port)