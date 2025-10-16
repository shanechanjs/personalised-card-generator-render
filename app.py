#!/usr/bin/env python3
"""
Flask Web Application for Personalised Card Generator

A web interface that allows users to upload images and generate personalised trading cards
using AI-generated meme names and descriptions.
"""

import os
# Disable Flask's automatic dotenv loading to prevent Unicode errors
os.environ['FLASK_SKIP_DOTENV'] = '1'

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from urllib.parse import unquote
from werkzeug.utils import secure_filename
import json

# Try to import make_card module, but don't fail if it's not available
try:
    from make_card import generate_card_web
    CARD_GENERATION_AVAILABLE = True
    print("Card generation module loaded successfully")
except ImportError as e:
    print(f"Warning: Could not import make_card module: {e}")
    CARD_GENERATION_AVAILABLE = False
    # Create a dummy function for when card generation is not available
    def generate_card_web(uploaded_file, traits, custom_descriptor=None):
        return {'success': False, 'error': 'Card generation not available - API keys not configured'}
# Load API keys from environment variables (required for Render deployment)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# For local development, try to load from API_KEYS.py if environment variables are not set
if not OPENAI_API_KEY or not GEMINI_API_KEY:
    try:
        from API_KEYS import OPENAI_API_KEY as LOCAL_OPENAI_KEY, GEMINI_API_KEY as LOCAL_GEMINI_KEY
        if not OPENAI_API_KEY:
            OPENAI_API_KEY = LOCAL_OPENAI_KEY
            os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
        if not GEMINI_API_KEY:
            GEMINI_API_KEY = LOCAL_GEMINI_KEY
            os.environ['GEMINI_API_KEY'] = GEMINI_API_KEY
        print("API keys loaded from API_KEYS.py for local development")
    except ImportError:
        print("API_KEYS.py not found, using environment variables only")

# Verify API keys are available
if not OPENAI_API_KEY or not GEMINI_API_KEY:
    print("WARNING: API keys not found. Set OPENAI_API_KEY and GEMINI_API_KEY environment variables.")
    print("For Render deployment, add these as environment variables in your Render service settings.")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Production configuration
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
else:
    app.config['DEBUG'] = True

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with upload form."""
    # For Render health checks, return a simple response if it's a health check request
    if request.headers.get('User-Agent', '').startswith('Render-Health-Check'):
        return jsonify({'status': 'healthy', 'message': 'Personalised Card Generator is running'}), 200
    
    # Return the template with external CSS and JS
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for Render deployment."""
    return jsonify({
        'status': 'healthy',
        'message': 'Personalised Card Generator is running',
        'api_keys_configured': bool(OPENAI_API_KEY and GEMINI_API_KEY),
        'card_generation_available': CARD_GENERATION_AVAILABLE,
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'port': os.environ.get('PORT', '5000')
    }), 200

@app.route('/test')
def test_endpoint():
    """Simple test endpoint to verify the app is working."""
    return jsonify({
        'message': 'App is working!',
        'timestamp': str(os.environ.get('PORT', '5000')),
        'status': 'ok'
    }), 200

@app.route('/debug')
def debug_endpoint():
    """Debug endpoint to check API key configuration."""
    return jsonify({
        'openai_key_configured': bool(OPENAI_API_KEY),
        'openai_key_length': len(OPENAI_API_KEY) if OPENAI_API_KEY else 0,
        'openai_key_prefix': OPENAI_API_KEY[:10] + '...' if OPENAI_API_KEY else 'None',
        'gemini_key_configured': bool(GEMINI_API_KEY),
        'gemini_key_length': len(GEMINI_API_KEY) if GEMINI_API_KEY else 0,
        'card_generation_available': CARD_GENERATION_AVAILABLE,
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'all_env_vars': {k: v for k, v in os.environ.items() if 'API' in k or 'KEY' in k}
    }), 200

@app.route('/test-api')
def test_api():
    """Test OpenAI API connection."""
    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say 'API test successful'"}],
            max_tokens=10
        )
        
        return jsonify({
            'success': True,
            'response': response.choices[0].message.content,
            'model_used': 'gpt-4o',
            'openai_version': openai.__version__
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__,
            'openai_version': openai.__version__ if 'openai' in locals() else 'unknown'
        }), 500

@app.route('/generate', methods=['POST'])
def generate_card():
    """Handle card generation from uploaded image and traits."""
    print("\n" + "="*50)
    print("CARD GENERATION REQUEST RECEIVED")
    print("="*50)
    
    try:
        # Log request details
        print(f"Request method: {request.method}")
        print(f"Content type: {request.content_type}")
        print(f"Files in request: {list(request.files.keys())}")
        print(f"Form data keys: {list(request.form.keys())}")
        
        # Check if image file is present
        if 'image' not in request.files:
            print("ERROR: No 'image' key in request.files")
            return jsonify({'success': False, 'error': 'No image file provided'})
        
        image_file = request.files['image']
        print(f"Image file: {image_file.filename}, size: {image_file.content_length if hasattr(image_file, 'content_length') else 'unknown'}")
        
        if image_file.filename == '':
            print("ERROR: Empty filename")
            return jsonify({'success': False, 'error': 'No image file selected'})
        
        if not allowed_file(image_file.filename):
            print(f"ERROR: Invalid file type: {image_file.filename}")
            return jsonify({'success': False, 'error': 'Invalid file type. Please upload PNG, JPG, JPEG, GIF, or BMP.'})
        
        # Get traits from form
        print("Extracting traits from form...")
        traits = []
        for i in range(1, 6):
            trait = request.form.get(f'trait{i}', '').strip()
            print(f"Trait {i}: {trait[:50]}{'...' if len(trait) > 50 else ''}")
            if not trait:
                print(f"ERROR: Trait {i} is empty")
                return jsonify({'success': False, 'error': f'Trait {i} is required'})
            traits.append(trait)
        
        # Get optional custom descriptor
        custom_descriptor = request.form.get('custom_descriptor', '').strip()
        print(f"Custom descriptor: {custom_descriptor if custom_descriptor else 'None'}")
        if not custom_descriptor:
            custom_descriptor = None
        
        print("Starting card generation...")
        
        # Check if card generation is available
        if not CARD_GENERATION_AVAILABLE:
            print("ERROR: Card generation not available - API keys not configured")
            return jsonify({'success': False, 'error': 'Card generation not available. Please check API key configuration.'})
        
        # Generate the card with both API keys
        result = generate_card_web(image_file, traits, custom_descriptor, GEMINI_API_KEY, OPENAI_API_KEY)
        
        print(f"Card generation result: {result['success']}")
        if result['success']:
            print(f"Generated filename: {result['filename']}")
            print(f"Character name: {result['character_name']}")
            return jsonify({
                'success': True,
                'card_data': result['card_data'],
                'filename': result['filename'],
                'character_name': result['character_name'],
                'descriptor': result['descriptor']
            })
        else:
            print(f"Card generation failed: {result['error']}")
            return jsonify({'success': False, 'error': result['error']})
            
    except Exception as e:
        print(f"EXCEPTION in generate_card: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'An error occurred: {str(e)}'})
    
    finally:
        print("="*50)
        print("REQUEST PROCESSING COMPLETE")
        print("="*50)

@app.route('/download/<path:filename>')
def download_card(filename):
    """Download a generated card."""
    try:
        print(f"[DOWNLOAD_CARD] Requested filename: {filename}")
        
        # Decode URL-encoded filename if needed
        filename = unquote(filename)
        print(f"[DOWNLOAD_CARD] After URL decode: {filename}")
        
        # Ensure filename is safe
        filename = secure_filename(filename)
        print(f"[DOWNLOAD_CARD] After secure_filename: {filename}")
        
        file_path = os.path.join('Generated_Cards', filename)
        print(f"[DOWNLOAD_CARD] Looking for file at: {file_path}")
        
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            # List files in directory to help debug
            if os.path.exists('Generated_Cards'):
                files = os.listdir('Generated_Cards')
                print(f"[DOWNLOAD_CARD] Files in Generated_Cards: {files}")
            return jsonify({'error': 'File not found'}), 404
            
    except Exception as e:
        print(f"[DOWNLOAD_CARD] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/gallery')
def gallery():
    """Show gallery of previously generated cards."""
    try:
        generated_cards = []
        generated_dir = 'Generated_Cards'
        
        if os.path.exists(generated_dir):
            for filename in os.listdir(generated_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(generated_dir, filename)
                    file_size = os.path.getsize(file_path)
                    generated_cards.append({
                        'filename': filename,
                        'size': file_size,
                        'url': url_for('download_card', filename=filename)
                    })
        
        # Sort by filename
        generated_cards.sort(key=lambda x: x['filename'])
        
        # Create HTML for gallery
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Card Gallery - Personalised Card Generator</title>
            <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }

                body {
                    font-family: 'Roboto', sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: #333;
                    line-height: 1.6;
                }

                .gallery-container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                
                .gallery-header {
                    text-align: center;
                    margin-bottom: 40px;
                    padding: 30px 0;
                }
                
                .gallery-title {
                    font-family: 'Orbitron', monospace;
                    font-size: 2.5rem;
                    font-weight: 900;
                    color: #fff;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                    margin-bottom: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 15px;
                }
                
                .title-icon {
                    font-size: 2rem;
                    animation: pulse 2s infinite;
                }

                @keyframes pulse {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.1); }
                }
                
                .gallery-subtitle {
                    font-size: 1.2rem;
                    color: #e8e8e8;
                    font-weight: 300;
                }
                
                .gallery-content {
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 20px;
                    padding: 40px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    backdrop-filter: blur(10px);
                }
                
                .cards-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    gap: 30px;
                    margin-bottom: 40px;
                }
                
                .card-item {
                    background: white;
                    border-radius: 15px;
                    padding: 20px;
                    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                    transition: all 0.3s ease;
                    text-align: center;
                }
                
                .card-item:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 15px 35px rgba(0,0,0,0.15);
                }
                
                .card-thumbnail {
                    width: 100%;
                    max-width: 250px;
                    height: auto;
                    border-radius: 10px;
                    margin-bottom: 15px;
                    border: 3px solid #667eea;
                }
                
                .card-filename {
                    font-weight: 600;
                    color: #4a5568;
                    margin-bottom: 10px;
                    word-break: break-word;
                }
                
                .card-size {
                    color: #718096;
                    font-size: 0.9rem;
                    margin-bottom: 15px;
                }
                
                .card-actions {
                    display: flex;
                    gap: 10px;
                    justify-content: center;
                }
                
                .btn-small {
                    padding: 8px 16px;
                    border: none;
                    border-radius: 20px;
                    font-size: 0.9rem;
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    text-decoration: none;
                    display: inline-flex;
                    align-items: center;
                    gap: 5px;
                }
                
                .btn-view {
                    background: linear-gradient(145deg, #667eea, #764ba2);
                    color: white;
                }
                
                .btn-download {
                    background: linear-gradient(145deg, #38b2ac, #319795);
                    color: white;
                }
                
                .btn-small:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                }
                
                .empty-gallery {
                    text-align: center;
                    padding: 60px 20px;
                    color: #718096;
                }
                
                .empty-gallery h3 {
                    font-family: 'Orbitron', monospace;
                    color: #4a5568;
                    margin-bottom: 15px;
                }
                
                .back-to-generator {
                    text-align: center;
                    margin-top: 30px;
                }
                
                .back-btn {
                    background: linear-gradient(145deg, #ed8936, #dd6b20);
                    color: white;
                    padding: 15px 30px;
                    border: none;
                    border-radius: 25px;
                    font-size: 1rem;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    text-decoration: none;
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                }
                
                .back-btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 8px 20px rgba(237, 137, 54, 0.4);
                }

                .back-link {
                    display: inline-block;
                    margin-bottom: 20px;
                    color: #e8e8e8;
                    text-decoration: none;
                    font-weight: 500;
                    transition: color 0.3s ease;
                }

                .back-link:hover {
                    color: #fff;
                    text-shadow: 0 0 5px rgba(255,255,255,0.5);
                }

                @media (max-width: 768px) {
                    .gallery-container {
                        padding: 10px;
                    }
                    
                    .gallery-title {
                        font-size: 2rem;
                        flex-direction: column;
                        gap: 10px;
                    }
                    
                    .gallery-content {
                        padding: 20px;
                    }
                    
                    .cards-grid {
                        grid-template-columns: 1fr;
                        gap: 20px;
                    }
                }
            </style>
        </head>
        <body>
            <div class="gallery-container">
                <header class="gallery-header">
                    <h1 class="gallery-title">
                        <span class="title-icon">🎴</span>
                        Card Gallery
                        <span class="title-icon">🎴</span>
                    </h1>
                    <p class="gallery-subtitle">Browse your collection of generated character cards</p>
                </header>

                <main class="gallery-content">
                    <a href="/" class="back-link">← Back to Generator</a>
        """
        
        if generated_cards:
            html_content += '<div class="cards-grid">'
            for card in generated_cards:
                html_content += f'''
                    <div class="card-item">
                        <img src="/card/{card["filename"]}" alt="Generated Card" class="card-thumbnail">
                        <div class="card-filename">{card["filename"]}</div>
                        <div class="card-size">{card["size"] / 1024:.1f} KB</div>
                        <div class="card-actions">
                            <a href="/card/{card["filename"]}" class="btn-small btn-view" target="_blank">
                                👁️ View
                            </a>
                            <a href="/download/{card["filename"]}" class="btn-small btn-download">
                                ⬇️ Download
                            </a>
                        </div>
                    </div>
                '''
            html_content += '</div>'
        else:
            html_content += '''
                <div class="empty-gallery">
                    <h3>No Cards Generated Yet</h3>
                    <p>Your gallery is empty. Start creating amazing character cards!</p>
                </div>
            '''
        
        html_content += '''
                <div class="back-to-generator">
                    <a href="/" class="back-btn">
                        <span class="btn-icon">✨</span>
                        Create New Card
                    </a>
                </div>
            </main>
        </div>
    </body>
    </html>
        '''
        
        return html_content
        
    except Exception as e:
        return jsonify({'error': f'Gallery failed to load: {str(e)}'}), 500

@app.route('/card/<path:filename>')
def view_card(filename):
    """View a generated card without downloading."""
    try:
        print(f"[VIEW_CARD] Requested filename: {filename}")
        
        # Decode URL-encoded filename if needed
        filename = unquote(filename)
        print(f"[VIEW_CARD] After URL decode: {filename}")
        
        # Secure the filename
        filename = secure_filename(filename)
        print(f"[VIEW_CARD] After secure_filename: {filename}")
        
        file_path = os.path.join('Generated_Cards', filename)
        print(f"[VIEW_CARD] Looking for file at: {file_path}")
        print(f"[VIEW_CARD] File exists: {os.path.exists(file_path)}")
        
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            # List files in directory to help debug
            if os.path.exists('Generated_Cards'):
                files = os.listdir('Generated_Cards')
                print(f"[VIEW_CARD] Files in Generated_Cards: {files}")
            return jsonify({'error': 'File not found'}), 404
            
    except Exception as e:
        print(f"[VIEW_CARD] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'View failed: {str(e)}'}), 500

if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs('Original_Photos', exist_ok=True)
    os.makedirs('Generated_Cards', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Get port from environment (for Render) or use default
    port = int(os.environ.get('PORT', 5000))
    
    print("Personalised Card Generator Web Interface")
    print("=" * 40)
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"API Keys configured: {bool(OPENAI_API_KEY and GEMINI_API_KEY)}")
    print(f"Port: {port}")
    print(f"Debug mode: {app.config['DEBUG']}")
    print("=" * 40)
    
    if os.environ.get('FLASK_ENV') == 'production':
        print("Starting production server...")
        print(f"Server running on port {port}")
    else:
        print("Starting Flask development server...")
        print(f"Open your browser and go to: http://localhost:{port}")
    
    print("=" * 40)
    
    try:
        app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
