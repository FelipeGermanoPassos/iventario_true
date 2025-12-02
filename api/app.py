import sys
import os
import traceback

# Add parent directory to path to import app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import create_app
    
    # Conventional Flask entrypoint for Vercel detection
    app = create_app()
    
    # Test health endpoint
    @app.route('/api/test')
    def api_test():
        return {'status': 'ok', 'message': 'API is running'}
        
except Exception as e:
    # If create_app fails, create minimal Flask app to show error
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    error_details = {
        'error': str(e),
        'type': type(e).__name__,
        'traceback': traceback.format_exc()
    }
    
    @app.route('/')
    @app.route('/api')
    @app.route('/api/test')
    def error_handler():
        return jsonify({
            'status': 'error',
            'message': 'Failed to initialize application',
            'details': error_details
        }), 500
