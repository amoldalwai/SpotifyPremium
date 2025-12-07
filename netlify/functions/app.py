import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import the Flask app and serverless-wsgi
from app import app
import serverless_wsgi

def handler(event, context):
    """Netlify serverless function handler using serverless-wsgi"""
    return serverless_wsgi.handle_request(app, event, context)
