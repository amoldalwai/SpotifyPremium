from flask import Flask, render_template, request, jsonify, Response
import requests
import json
from datetime import datetime, timedelta
import re
import base64
import urllib3
from Crypto.Cipher import DES
from Crypto.Util.Padding import unpad
import yt_dlp
import traceback
from fuzzywuzzy import fuzz
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import the main app
from app import app

def handler(event, context):
    """Netlify serverless function handler"""
    from werkzeug.wrappers import Request, Response as WerkzeugResponse
    from io import BytesIO
    
    # Extract request details from Netlify event
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    headers = event.get('headers', {})
    query_params = event.get('queryStringParameters') or {}
    body = event.get('body', '')
    is_base64 = event.get('isBase64Encoded', False)
    
    if is_base64:
        import base64
        body = base64.b64decode(body)
    
    # Build query string
    query_string = '&'.join([f'{k}={v}' for k, v in query_params.items()]) if query_params else ''
    
    # Create WSGI environ
    environ = {
        'REQUEST_METHOD': method,
        'SCRIPT_NAME': '',
        'PATH_INFO': path,
        'QUERY_STRING': query_string,
        'CONTENT_TYPE': headers.get('content-type', ''),
        'CONTENT_LENGTH': str(len(body)) if body else '0',
        'SERVER_NAME': 'netlify',
        'SERVER_PORT': '443',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': BytesIO(body.encode() if isinstance(body, str) else body),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    # Add headers
    for key, value in headers.items():
        key = key.upper().replace('-', '_')
        if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            key = f'HTTP_{key}'
        environ[key] = value
    
    # Call Flask app
    response_data = []
    response_status = [200]
    response_headers = []
    
    def start_response(status, headers):
        response_status[0] = int(status.split()[0])
        response_headers.extend(headers)
        return response_data.append
    
    app_response = app(environ, start_response)
    
    # Build response body
    response_body = b''.join(app_response)
    
    # Convert headers to dict
    response_headers_dict = {}
    for key, value in response_headers:
        response_headers_dict[key] = value
    
    return {
        'statusCode': response_status[0],
        'headers': response_headers_dict,
        'body': response_body.decode('utf-8', errors='replace')
    }
