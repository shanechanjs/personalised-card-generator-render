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
    
    # Return a beautiful HTML page with full styling
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Personalised Card Generator</title>
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

            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }

            .header {
                text-align: center;
                margin-bottom: 40px;
                padding: 30px 0;
            }

            .title {
                font-family: 'Orbitron', monospace;
                font-size: 3rem;
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
                font-size: 2.5rem;
                animation: pulse 2s infinite;
            }

            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }

            .subtitle {
                font-size: 1.2rem;
                color: #e8e8e8;
                font-weight: 300;
            }

            .main-content {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                backdrop-filter: blur(10px);
            }

            .card-generator {
                max-width: 800px;
                margin: 0 auto;
            }

            .form-section {
                margin-bottom: 40px;
                padding: 30px;
                background: linear-gradient(145deg, #f8f9fa, #e9ecef);
                border-radius: 15px;
                border: 2px solid #e0e0e0;
                transition: all 0.3s ease;
            }

            .form-section:hover {
                border-color: #667eea;
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.1);
            }

            .section-title {
                font-family: 'Orbitron', monospace;
                font-size: 1.5rem;
                color: #4a5568;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .section-description {
                color: #666;
                margin-bottom: 20px;
                font-style: italic;
            }

            .upload-area {
                border: 3px dashed #667eea;
                border-radius: 15px;
                padding: 40px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                position: relative;
                background: linear-gradient(145deg, #f8f9ff, #e8f0ff);
            }

            .upload-area:hover {
                border-color: #5a67d8;
                background: linear-gradient(145deg, #e8f0ff, #d6e3ff);
                transform: translateY(-2px);
            }

            .upload-area.dragover {
                border-color: #4c51bf;
                background: linear-gradient(145deg, #d6e3ff, #c7d2fe);
                transform: scale(1.02);
            }

            .upload-content {
                pointer-events: none;
            }

            .upload-icon {
                font-size: 3rem;
                margin-bottom: 15px;
                opacity: 0.7;
            }

            .upload-text {
                font-size: 1.2rem;
                font-weight: 500;
                color: #4a5568;
                margin-bottom: 5px;
            }

            .upload-hint {
                color: #718096;
                font-size: 0.9rem;
            }

            #imageInput {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                opacity: 0;
                cursor: pointer;
            }

            .image-preview {
                position: relative;
                margin-top: 20px;
                text-align: center;
            }

            .image-preview img {
                max-width: 300px;
                max-height: 300px;
                border-radius: 15px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                border: 3px solid #667eea;
            }

            .remove-image {
                position: absolute;
                top: -10px;
                right: calc(50% - 160px);
                background: #e53e3e;
                color: white;
                border: none;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                cursor: pointer;
                font-size: 1.2rem;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
            }

            .remove-image:hover {
                background: #c53030;
                transform: scale(1.1);
            }

            .traits-container {
                display: grid;
                gap: 20px;
            }

            .trait-input-group {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }

            .trait-input-group label {
                font-weight: 500;
                color: #4a5568;
                font-size: 1rem;
            }

            .trait-input-group input {
                padding: 15px;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-size: 1rem;
                transition: all 0.3s ease;
                background: white;
            }

            .trait-input-group input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
                transform: translateY(-1px);
            }

            .customization-group {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }

            .customization-group label {
                font-weight: 500;
                color: #4a5568;
                font-size: 1rem;
            }

            .customization-group input {
                padding: 15px;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-size: 1rem;
                transition: all 0.3s ease;
                background: white;
            }

            .customization-group input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }

            .hint {
                font-size: 0.9rem;
                color: #718096;
                font-style: italic;
            }

            .form-actions {
                text-align: center;
                margin-top: 40px;
            }

            .generate-btn {
                background: linear-gradient(145deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 20px 40px;
                font-size: 1.2rem;
                font-weight: 600;
                border-radius: 50px;
                cursor: pointer;
                transition: all 0.3s ease;
                display: inline-flex;
                align-items: center;
                gap: 10px;
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
                font-family: 'Orbitron', monospace;
            }

            .generate-btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
                background: linear-gradient(145deg, #5a67d8, #6b46c1);
            }

            .generate-btn:active {
                transform: translateY(-1px);
            }

            .btn-icon {
                font-size: 1.3rem;
            }

            .loading {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 15px;
                color: #667eea;
                font-weight: 500;
                font-size: 1.1rem;
            }

            .spinner {
                width: 30px;
                height: 30px;
                border: 3px solid #e2e8f0;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .result-section {
                margin-top: 40px;
                padding: 30px;
                background: linear-gradient(145deg, #f0fff4, #e6fffa);
                border-radius: 15px;
                border: 2px solid #38b2ac;
                animation: slideIn 0.5s ease-out;
            }

            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .card-preview-container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                align-items: start;
                margin-bottom: 30px;
            }

            .card-preview {
                text-align: center;
            }

            .card-preview img {
                max-width: 100%;
                height: auto;
                border-radius: 15px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.2);
                border: 3px solid #38b2ac;
            }

            .card-info {
                padding: 20px;
                background: white;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }

            .card-info h3 {
                font-family: 'Orbitron', monospace;
                font-size: 1.8rem;
                color: #2d3748;
                margin-bottom: 20px;
                text-align: center;
            }

            .card-stats {
                margin-bottom: 20px;
            }

            .stat-item {
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid #e2e8f0;
            }

            .stat-label {
                font-weight: 500;
                color: #4a5568;
            }

            .stat-value {
                font-weight: 600;
                color: #667eea;
            }

            .card-ability {
                background: linear-gradient(145deg, #f7fafc, #edf2f7);
                padding: 15px;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }

            .ability-name {
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 8px;
                font-size: 1.1rem;
            }

            .ability-description {
                color: #4a5568;
                font-size: 0.95rem;
                line-height: 1.5;
            }

            .card-actions {
                display: flex;
                gap: 15px;
                justify-content: center;
                flex-wrap: wrap;
            }

            .download-btn, .new-card-btn {
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }

            .download-btn {
                background: linear-gradient(145deg, #38b2ac, #319795);
                color: white;
                box-shadow: 0 5px 15px rgba(56, 178, 172, 0.3);
            }

            .download-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(56, 178, 172, 0.4);
            }

            .new-card-btn {
                background: linear-gradient(145deg, #ed8936, #dd6b20);
                color: white;
                box-shadow: 0 5px 15px rgba(237, 137, 54, 0.3);
            }

            .new-card-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(237, 137, 54, 0.4);
            }

            .footer {
                text-align: center;
                margin-top: 40px;
                padding: 30px 0;
            }

            .footer-links {
                margin-bottom: 15px;
            }

            .footer-link {
                color: #e8e8e8;
                text-decoration: none;
                margin: 0 15px;
                font-weight: 500;
                transition: color 0.3s ease;
            }

            .footer-link:hover {
                color: #fff;
                text-shadow: 0 0 5px rgba(255,255,255,0.5);
            }

            .footer-text {
                color: #b0b0b0;
                font-size: 0.9rem;
            }

            .status {
                margin-top: 20px;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                font-weight: 500;
            }

            .success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }

            .error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }

            @media (max-width: 768px) {
                .container {
                    padding: 10px;
                }
                
                .title {
                    font-size: 2rem;
                    flex-direction: column;
                    gap: 10px;
                }
                
                .main-content {
                    padding: 20px;
                }
                
                .form-section {
                    padding: 20px;
                }
                
                .card-preview-container {
                    grid-template-columns: 1fr;
                    gap: 20px;
                }
                
                .card-actions {
                    flex-direction: column;
                    align-items: center;
                }
                
                .download-btn, .new-card-btn {
                    width: 100%;
                    max-width: 300px;
                }
            }

            @media (max-width: 480px) {
                .title {
                    font-size: 1.5rem;
                }
                
                .upload-area {
                    padding: 20px;
                }
                
                .upload-text {
                    font-size: 1rem;
                }
                
                .generate-btn {
                    padding: 15px 30px;
                    font-size: 1rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header class="header">
                <h1 class="title">
                    <span class="title-icon">⚔️</span>
                    Personalised Card Generator
                    <span class="title-icon">🛡️</span>
                </h1>
                <p class="subtitle">Create epic trading cards from your images using AI magic!</p>
            </header>

            <main class="main-content">
                <div class="card-generator">
                    <form id="cardForm" class="generator-form" enctype="multipart/form-data">
                        <div class="form-section">
                            <h2 class="section-title">📸 Upload Character Image</h2>
                            <div class="upload-area" id="uploadArea">
                                <div class="upload-content">
                                    <div class="upload-icon">📁</div>
                                    <p class="upload-text">Click to upload or drag & drop</p>
                                    <p class="upload-hint">PNG, JPG, JPEG, GIF, BMP (max 16MB)</p>
                                </div>
                                <input type="file" id="imageInput" name="image" accept="image/*">
                            </div>
                            <div class="image-preview" id="imagePreview" style="display: none;">
                                <img id="previewImg" src="" alt="Preview">
                                <button type="button" class="remove-image" id="removeImage">✕</button>
                            </div>
                        </div>

                        <div class="form-section">
                            <h2 class="section-title">📝 Character Traits</h2>
                            <p class="section-description">Tell us 5 interesting things about your character. AI will generate a hilarious meme-style card name based on these traits!</p>
                            <div class="traits-container">
                                <div class="trait-input-group">
                                    <label for="trait1">Trait 1:</label>
                                    <input type="text" id="trait1" name="trait1" placeholder="e.g., They have a ridiculously specific collection of vintage hotel soap bars" required>
                                </div>
                                <div class="trait-input-group">
                                    <label for="trait2">Trait 2:</label>
                                    <input type="text" id="trait2" name="trait2" placeholder="e.g., Their phone's autocorrect changes 'the' to 'the magnificent banana-lizard'" required>
                                </div>
                                <div class="trait-input-group">
                                    <label for="trait3">Trait 3:</label>
                                    <input type="text" id="trait3" name="trait3" placeholder="e.g., They can flawlessly imitate the sound of an old-school fax machine" required>
                                </div>
                                <div class="trait-input-group">
                                    <label for="trait4">Trait 4:</label>
                                    <input type="text" id="trait4" name="trait4" placeholder="e.g., Their signature food order is plain buttered toast and milk" required>
                                </div>
                                <div class="trait-input-group">
                                    <label for="trait5">Trait 5:</label>
                                    <input type="text" id="trait5" name="trait5" placeholder="e.g., They have a secret online identity as 'The Doom-Waffle'" required>
                                </div>
                            </div>
                        </div>

                        <div class="form-section">
                            <h2 class="section-title">🎨 Card Customization (Optional)</h2>
                            <div class="customization-group">
                                <label for="custom_descriptor">Custom Card Descriptor:</label>
                                <input type="text" id="custom_descriptor" name="custom_descriptor" placeholder="e.g., Epic Fighter, Mystic Mage, Legendary Hero">
                                <p class="hint">Note: Card names are AI-generated based on your traits. This field is for additional customization only.</p>
                            </div>
                        </div>

                        <div class="form-actions">
                            <button type="submit" class="generate-btn" id="generateBtn">
                                <span class="btn-text">Generate Card</span>
                                <span class="btn-icon">✨</span>
                            </button>
                            <div class="loading" id="loading" style="display: none;">
                                <div class="spinner"></div>
                                <span>Generating your epic card...</span>
                            </div>
                        </div>
                    </form>

                    <div class="result-section" id="resultSection" style="display: none;">
                        <h2 class="section-title">🎴 Your Generated Card</h2>
                        <div class="card-preview-container">
                            <div class="card-preview" id="cardPreview">
                                <img id="generatedCard" src="" alt="Generated Card">
                            </div>
                            <div class="card-info" id="cardInfo">
                                <h3 id="characterName"></h3>
                                <div class="card-stats" id="cardStats"></div>
                                <div class="card-ability" id="cardAbility"></div>
                            </div>
                        </div>
                        <div class="card-actions">
                            <button class="download-btn" id="downloadBtn">
                                <span class="btn-icon">⬇️</span>
                                Download Card
                            </button>
                            <button class="new-card-btn" id="newCardBtn">
                                <span class="btn-icon">🔄</span>
                                Create Another Card
                            </button>
                        </div>
                    </div>
                </div>
            </main>

            <footer class="footer">
                <div class="footer-links">
                    <a href="/gallery" class="footer-link">View Gallery</a>
                    <a href="#" class="footer-link" onclick="showHelp()">Help</a>
                </div>
                <p class="footer-text">Powered by AI Magic ✨</p>
            </footer>
        </div>

        <script>
            document.addEventListener('DOMContentLoaded', function() {
                console.log('DOM loaded, initializing Personalised Card Generator...');
                
                // DOM elements
                const form = document.getElementById('cardForm');
                const imageInput = document.getElementById('imageInput');
                const uploadArea = document.getElementById('uploadArea');
                const imagePreview = document.getElementById('imagePreview');
                const previewImg = document.getElementById('previewImg');
                const removeImageBtn = document.getElementById('removeImage');
                const generateBtn = document.getElementById('generateBtn');
                const loading = document.getElementById('loading');
                const resultSection = document.getElementById('resultSection');
                const generatedCard = document.getElementById('generatedCard');
                const characterName = document.getElementById('characterName');
                const cardStats = document.getElementById('cardStats');
                const cardAbility = document.getElementById('cardAbility');
                const downloadBtn = document.getElementById('downloadBtn');
                const newCardBtn = document.getElementById('newCardBtn');

                // Store uploaded file globally for reliable access
                let uploadedFile = null;

                // File upload handling
                imageInput.addEventListener('change', handleImageUpload);
                uploadArea.addEventListener('click', () => {
                    console.log('Upload area clicked, triggering file input...');
                    imageInput.click();
                });
                uploadArea.addEventListener('dragover', handleDragOver);
                uploadArea.addEventListener('dragleave', handleDragLeave);
                uploadArea.addEventListener('drop', handleDrop);
                removeImageBtn.addEventListener('click', removeImage);

                // Form submission
                form.addEventListener('submit', handleFormSubmit);
                console.log('Event listeners attached successfully');

                // Button events
                downloadBtn.addEventListener('click', downloadCard);
                newCardBtn.addEventListener('click', resetForm);

                // Image upload functions
                function handleImageUpload(event) {
                    console.log('Image upload triggered, files:', event.target.files);
                    const file = event.target.files[0];
                    if (file) {
                        console.log('File selected:', file.name, 'Size:', file.size, 'Type:', file.type);
                        uploadedFile = file; // Store globally
                        processImageFile(file);
                    } else {
                        console.log('No file selected');
                    }
                }

                function handleDragOver(event) {
                    event.preventDefault();
                    uploadArea.classList.add('dragover');
                }

                function handleDragLeave(event) {
                    event.preventDefault();
                    uploadArea.classList.remove('dragover');
                }

                function handleDrop(event) {
                    event.preventDefault();
                    uploadArea.classList.remove('dragover');
                    
                    const files = event.dataTransfer.files;
                    console.log('Files dropped:', files.length);
                    if (files.length > 0) {
                        console.log('Processing dropped file:', files[0].name);
                        uploadedFile = files[0]; // Store globally
                        
                        // Update the file input element with the dropped file
                        const dataTransfer = new DataTransfer();
                        dataTransfer.items.add(files[0]);
                        imageInput.files = dataTransfer.files;
                        
                        processImageFile(files[0]);
                    }
                }

                function processImageFile(file) {
                    console.log('Processing image file:', file.name);
                    
                    // Validate file type
                    if (!file.type.startsWith('image/')) {
                        console.error('Invalid file type:', file.type);
                        showError('Please select a valid image file.');
                        return;
                    }

                    // Validate file size (16MB max)
                    if (file.size > 16 * 1024 * 1024) {
                        console.error('File too large:', file.size);
                        showError('File size must be less than 16MB.');
                        return;
                    }

                    console.log('File validation passed, creating preview...');
                    
                    // Create preview
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        console.log('File preview created successfully');
                        previewImg.src = e.target.result;
                        imagePreview.style.display = 'block';
                        uploadArea.style.display = 'none';
                    };
                    reader.onerror = function(e) {
                        console.error('Error reading file:', e);
                        showError('Error reading the selected file.');
                    };
                    reader.readAsDataURL(file);
                }

                function removeImage() {
                    console.log('Removing image...');
                    imageInput.value = '';
                    uploadedFile = null; // Clear stored file
                    imagePreview.style.display = 'none';
                    uploadArea.style.display = 'block';
                }

                // Form submission
                function handleFormSubmit(event) {
                    console.log('Form submission triggered');
                    event.preventDefault();

                    try {
                        // Validate form
                        console.log('Validating form...');
                        if (!validateForm()) {
                            console.log('Form validation failed');
                            return;
                        }

                        console.log('Form validation passed, preparing submission...');

                        // Show loading state
                        showLoading(true);

                        // Prepare form data
                        const formData = new FormData(form);
                        
                        // Ensure we have the uploaded file
                        if (uploadedFile) {
                            formData.set('image', uploadedFile);
                            console.log('File added to FormData:', uploadedFile.name);
                        } else {
                            console.error('No uploaded file found!');
                            showLoading(false);
                            showError('No image file selected. Please upload an image.');
                            return;
                        }

                        // Log form data contents for debugging
                        console.log('FormData contents:');
                        for (let [key, value] of formData.entries()) {
                            if (value instanceof File) {
                                console.log(`${key}: File(${value.name}, ${value.size} bytes)`);
                            } else {
                                console.log(`${key}: ${value}`);
                            }
                        }

                        // Submit form via AJAX
                        console.log('Submitting form to /generate...');
                        fetch('/generate', {
                            method: 'POST',
                            body: formData
                        })
                        .then(response => {
                            console.log('Response received:', response.status, response.statusText);
                            if (!response.ok) {
                                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                            }
                            return response.json();
                        })
                        .then(data => {
                            console.log('Response data:', data);
                            showLoading(false);
                            
                            if (data.success) {
                                console.log('Card generation successful!');
                                showResult(data);
                            } else {
                                console.error('Card generation failed:', data.error);
                                showError(data.error || 'An error occurred while generating the card.');
                            }
                        })
                        .catch(error => {
                            console.error('Request failed:', error);
                            showLoading(false);
                            showError('Network error: ' + error.message);
                        });
                    } catch (error) {
                        console.error('Form submission error:', error);
                        showLoading(false);
                        showError('An unexpected error occurred: ' + error.message);
                    }
                }

                function validateForm() {
                    console.log('Validating form...');
                    
                    // Check if image is selected (use stored file)
                    if (!uploadedFile) {
                        console.log('Validation failed: No image file');
                        showError('Please select an image file.');
                        return false;
                    }

                    // Check if all traits are filled
                    for (let i = 1; i <= 5; i++) {
                        const traitInput = document.getElementById(`trait${i}`);
                        if (!traitInput.value.trim()) {
                            console.log(`Validation failed: Trait ${i} is empty`);
                            showError(`Please fill in trait ${i}.`);
                            traitInput.focus();
                            return false;
                        }
                    }

                    console.log('Form validation passed');
                    return true;
                }

                function showLoading(show) {
                    if (show) {
                        generateBtn.style.display = 'none';
                        loading.style.display = 'flex';
                        resultSection.style.display = 'none';
                    } else {
                        generateBtn.style.display = 'inline-flex';
                        loading.style.display = 'none';
                    }
                }

                function showResult(data) {
                    // Display generated card
                    # generatedCard.src = `/card/${encodeURIComponent(data.filename)}`;
                    generatedCard.src = `${encodeURIComponent(data.filename)}`;
                    generatedCard.alt = `${data.character_name} Card`;
                    
                    // Display character name
                    characterName.textContent = data.character_name;
                    
                    // Display card stats
                    displayCardStats(data.card_data);
                    
                    // Display card ability
                    displayCardAbility(data.card_data);
                    
                    // Store filename for download
                    generatedCard.dataset.filename = data.filename;
                    
                    // Show result section
                    resultSection.style.display = 'block';
                    resultSection.scrollIntoView({ behavior: 'smooth' });
                    
                    // Auto-download the generated card
                    setTimeout(() => {
                        downloadCard(data.filename);
                    }, 500); // Small delay to ensure image is loaded
                }

                function displayCardStats(cardData) {
                    let stats = [];
                    
                    // Display different stats based on card type
                    if (cardData.card_type === 'Monster') {
                        stats = [
                            { label: 'Type', value: cardData.monster_type || 'Effect' },
                            { label: 'Attribute', value: cardData.attribute || 'DARK' },
                            { label: 'Level', value: cardData.level || 4 },
                            { label: 'ATK', value: cardData.attack || 0 },
                            { label: 'DEF', value: cardData.defense || 0 }
                        ];
                    } else if (cardData.card_type === 'Spell') {
                        stats = [
                            { label: 'Card Type', value: 'Spell Card' },
                            { label: 'Spell Type', value: cardData.spell_type || 'Normal' }
                        ];
                    } else if (cardData.card_type === 'Trap') {
                        stats = [
                            { label: 'Card Type', value: 'Trap Card' },
                            { label: 'Trap Type', value: cardData.trap_type || 'Normal' }
                        ];
                    }

                    cardStats.innerHTML = stats.map(stat => `
                        <div class="stat-item">
                            <span class="stat-label">${stat.label}</span>
                            <span class="stat-value">${stat.value}</span>
                        </div>
                    `).join('');
                }

                function displayCardAbility(cardData) {
                    const effectDesc = cardData.effect_description || 'No effect.';
                    const cardType = cardData.card_type || 'Monster';
                    const titleText = 'Deets/Lore';
                    
                    cardAbility.innerHTML = `
                        <div class="ability-name">${titleText}</div>
                        <div class="ability-description">${effectDesc}</div>
                    `;
                }

                function downloadCard(filename) {
                    // Get filename from the generated card's dataset
                    const cardImg = document.getElementById('generatedCard');
                    const filenameToDownload = cardImg && cardImg.dataset.filename ? cardImg.dataset.filename : null;
                    
                    if (filenameToDownload) {
                        console.log('Downloading card:', filenameToDownload);
                        window.open(`/download/${encodeURIComponent(filenameToDownload)}`, '_blank');
                    } else {
                        console.error('No filename found for download');
                        showError('Unable to download card. Please try generating again.');
                    }
                }

                function resetForm() {
                    console.log('Resetting form...');
                    
                    // Reset form
                    form.reset();
                    
                    // Reset image preview and stored file
                    removeImage();
                    
                    // Hide result section
                    resultSection.style.display = 'none';
                    
                    // Scroll to top
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                    
                    console.log('Form reset complete');
                }

                function showError(message) {
                    console.error('Showing error:', message);
                    
                    // Create or update error message
                    let errorDiv = document.getElementById('errorMessage');
                    if (!errorDiv) {
                        errorDiv = document.createElement('div');
                        errorDiv.id = 'errorMessage';
                        errorDiv.style.cssText = `
                            background: #fed7d7;
                            color: #c53030;
                            padding: 15px;
                            border-radius: 10px;
                            margin: 20px 0;
                            border: 1px solid #feb2b2;
                            text-align: center;
                            font-weight: 500;
                            position: relative;
                            z-index: 1000;
                        `;
                        form.insertBefore(errorDiv, form.firstChild);
                    }
                    
                    errorDiv.innerHTML = `
                        <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
                            <span style="font-size: 1.2em;">⚠️</span>
                            <span>${message}</span>
                            <button onclick="this.parentElement.parentElement.style.display='none'" 
                                    style="background: none; border: none; color: #c53030; font-size: 1.2em; cursor: pointer; margin-left: 10px;">✕</button>
                        </div>
                    `;
                    errorDiv.style.display = 'block';
                    
                    // Scroll to error message
                    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    
                    // Auto-hide after 8 seconds
                    setTimeout(() => {
                        if (errorDiv.style.display !== 'none') {
                            errorDiv.style.display = 'none';
                        }
                    }, 8000);
                }

                // Help modal functions
                window.showHelp = function() {
                    alert('How to Use the Personalised Card Generator:\\n\\n1. Upload an Image: Choose a clear image of your character. Supported formats: PNG, JPG, JPEG, GIF, BMP (max 16MB).\\n\\n2. Enter Character Traits: Write 5 interesting, creative things about your character. Be imaginative and specific!\\n\\n3. Customize (Optional): Add a custom descriptor for your card name, or leave blank for auto-generation.\\n\\n4. Generate & Download: Click "Generate Card" and wait for AI to create your epic trading card!');
                };

                // Add some visual feedback for form interactions
                const inputs = document.querySelectorAll('input[type="text"]');
                inputs.forEach(input => {
                    input.addEventListener('focus', function() {
                        this.parentElement.style.transform = 'translateY(-2px)';
                        this.parentElement.style.boxShadow = '0 5px 15px rgba(102, 126, 234, 0.1)';
                    });
                    
                    input.addEventListener('blur', function() {
                        this.parentElement.style.transform = 'translateY(0)';
                        this.parentElement.style.boxShadow = 'none';
                    });
                });

                // Add animation to buttons
                const buttons = document.querySelectorAll('button');
                buttons.forEach(button => {
                    button.addEventListener('mouseenter', function() {
                        this.style.transform = 'translateY(-2px)';
                    });
                    
                    button.addEventListener('mouseleave', function() {
                        this.style.transform = 'translateY(0)';
                    });
                });
            });
        </script>
    </body>
    </html>
    """
    return html_content

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
        
        # Generate the card
        result = generate_card_web(image_file, traits, custom_descriptor)
        
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
