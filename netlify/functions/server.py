import sys
from pathlib import Path

# Add project root to Python path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from app import app

def handler(event, context):
    """Netlify serverless function handler for Flask"""
    try:
        # Get request details
        path = event.get('path', '/')
        method = event.get('httpMethod', 'GET')
        headers = event.get('headers', {})
        query_params = event.get('queryStringParameters') or {}
        body = event.get('body', '')
        is_base64 = event.get('isBase64Encoded', False)
        
        # Decode base64 body if needed
        if is_base64 and body:
            import base64
            body = base64.b64decode(body)
        
        # Build query string
        query_string = '&'.join([f'{k}={v}' for k, v in query_params.items()]) if query_params else ''
        if query_string:
            path = f"{path}?{query_string}"
        
        # Use Flask test client to handle the request
        with app.test_client() as client:
            # Prepare headers as list of tuples
            header_list = [(k, v) for k, v in headers.items()]
            
            # Make the request
            response = client.open(
                path=path,
                method=method,
                headers=header_list,
                data=body,
                content_type=headers.get('content-type', 'text/html')
            )
            
            # Build response headers
            response_headers = {}
            for key, value in response.headers:
                response_headers[key] = value
            
            # Get response body
            response_body = response.get_data(as_text=True)
            
            return {
                'statusCode': response.status_code,
                'headers': response_headers,
                'body': response_body
            }
            
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in handler: {str(e)}")
        print(error_trace)
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': f'{{"error": "{str(e)}"}}'
        }
