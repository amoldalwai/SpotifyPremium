import sys
from pathlib import Path

# Add project root to Python path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from app import app

# Import serverless-wsgi
try:
    import serverless_wsgi
    
    def handler(event, context):
        return serverless_wsgi.handle_request(app, event, context)
        
except ImportError:
    # Fallback if serverless-wsgi is not available
    def handler(event, context):
        from werkzeug.serving import WSGIRequestHandler
        from io import BytesIO
        
        # Simple WSGI handler
        path = event.get('path', '/')
        method = event.get('httpMethod', 'GET')
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        with app.test_client() as client:
            # Make request using Flask test client
            response = client.open(
                path=path,
                method=method,
                headers=[(k, v) for k, v in headers.items()],
                data=body
            )
            
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data(as_text=True)
            }
