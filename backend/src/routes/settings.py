from flask import Blueprint, request, jsonify
import os
import json

settings_bp = Blueprint('settings', __name__)

# Store API keys in memory (in production, use secure storage)
# Initialize from environment variables (Railway or local)
api_keys = {
    'openai': os.environ.get('OPENAI_API_KEY', ''),
    'aws_access_key': os.environ.get('AWS_ACCESS_KEY_ID', ''),
    'aws_secret_key': os.environ.get('AWS_SECRET_ACCESS_KEY', ''),
    'aws_region': os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'),
    'ai_provider': os.environ.get('AI_PROVIDER', 'openai')
}

# Log initial configuration (without sensitive data)
print(f"API Keys initialized - OpenAI: {bool(api_keys['openai'])}, AWS: {bool(api_keys['aws_access_key'])}")

@settings_bp.route('/settings/api-keys', methods=['POST'])
def save_api_keys():
    """Save API keys configuration."""
    global api_keys
    try:
        data = request.get_json()
        
        # Update API keys
        api_keys.update(data)
        
        # Set environment variables for OpenAI
        if data.get('openai'):
            os.environ['OPENAI_API_KEY'] = data['openai']
        
        # Set environment variables for AWS
        if data.get('aws_access_key'):
            os.environ['AWS_ACCESS_KEY_ID'] = data['aws_access_key']
        if data.get('aws_secret_key'):
            os.environ['AWS_SECRET_ACCESS_KEY'] = data['aws_secret_key']
        if data.get('aws_region'):
            os.environ['AWS_DEFAULT_REGION'] = data['aws_region']
        
        return jsonify({
            'message': 'API keys saved successfully',
            'provider': api_keys.get('ai_provider', 'openai')
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/settings/test-ai', methods=['POST'])
def test_ai_connection():
    """Test AI service connection."""
    try:
        data = request.get_json()
        provider = data.get('provider', 'openai')
        
        if provider == 'openai':
            # Test OpenAI connection
            api_key = data.get('openai')
            if not api_key:
                return jsonify({
                    'success': False,
                    'message': 'OpenAI API key is required'
                }), 400
            
            # Set temporary API key for testing
            try:
                import openai
                from openai import OpenAI
                
                # Create client with just the API key
                client = OpenAI(api_key=api_key)
                
                # Make a minimal API call to test connection
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
                
                return jsonify({
                    'success': True,
                    'message': 'OpenAI connection successful!'
                }), 200
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'OpenAI connection failed: {str(e)}'
                }), 200
                
        elif provider == 'aws_nova':
            # Test AWS Bedrock connection
            access_key = data.get('aws_access_key')
            secret_key = data.get('aws_secret_key')
            region = data.get('aws_region', 'us-east-1')
            
            if not access_key or not secret_key:
                return jsonify({
                    'success': False,
                    'message': 'AWS credentials are required'
                }), 400
            
            try:
                import boto3
                
                # Create Bedrock client
                client = boto3.client(
                    'bedrock-runtime',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    region_name=region
                )
                
                # Test with a minimal request
                response = client.invoke_model(
                    modelId='anthropic.claude-instant-v1',
                    body=json.dumps({
                        'prompt': '\n\nHuman: test\n\nAssistant:',
                        'max_tokens_to_sample': 10
                    }),
                    contentType='application/json'
                )
                
                return jsonify({
                    'success': True,
                    'message': 'AWS Bedrock connection successful!'
                }), 200
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'AWS Bedrock connection failed: {str(e)}'
                }), 200
        
        return jsonify({
            'success': False,
            'message': 'Invalid provider'
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Connection test failed: {str(e)}'
        }), 500

@settings_bp.route('/settings/api-keys', methods=['GET'])
def get_api_keys():
    """Get current API keys configuration (without sensitive data)."""
    return jsonify({
        'ai_provider': api_keys.get('ai_provider', 'openai'),
        'openai_configured': bool(api_keys.get('openai')),
        'aws_configured': bool(api_keys.get('aws_access_key') and api_keys.get('aws_secret_key')),
        'aws_region': api_keys.get('aws_region', 'us-east-1')
    }), 200

def get_current_api_keys():
    """Get current API keys for internal use."""
    return api_keys