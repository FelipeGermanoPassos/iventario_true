import sys
import os
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path to import app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger.info("Starting application initialization...")
logger.info(f"Python path: {sys.path}")
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Environment variables: VERCEL={os.environ.get('VERCEL')}, DATABASE_URL={'SET' if os.environ.get('DATABASE_URL') else 'NOT SET'}")
logger.info(f"Python path: {sys.path}")
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Environment variables: VERCEL={os.environ.get('VERCEL')}, DATABASE_URL={'SET' if os.environ.get('DATABASE_URL') else 'NOT SET'}")

app = None
init_error = None

try:
    logger.info("Importing create_app...")
    from app import create_app
    
    logger.info("Calling create_app()...")
    app = create_app()
    
    logger.info("Application created successfully!")
    
    # Test health endpoint
    @app.route('/api/test')
    def api_test():
        return {'status': 'ok', 'message': 'API is running'}
        
except Exception as e:
    init_error = {
        'error': str(e),
        'type': type(e).__name__,
        'traceback': traceback.format_exc()
    }
    logger.error(f"Failed to initialize app: {init_error}")
    
    # If create_app fails, create minimal Flask app to show error
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    @app.route('/api')
    @app.route('/api/test')
    @app.route('/health')
    def error_handler():
        return jsonify({
            'status': 'error',
            'message': 'Failed to initialize application',
            'details': init_error
        }), 500

# Always export app variable for Vercel
if app is None:
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def fallback():
        return jsonify({
            'status': 'error', 
            'message': 'Application failed to initialize',
            'details': init_error
        }), 500
