# Personalised Card Generator

An AI-powered web application that generates personalized trading cards based on photos and personality traits. Create hilarious, meme-worthy character cards with AI-generated names and descriptions!

## Features

- 🎨 Upload any photo and transform it into a custom card
- 🤖 AI-generated creative card names and descriptions using **dual LLM system** (Gemini primary, OpenAI fallback)
- 🎭 20 unique personality types with custom color schemes and visual effects
- 📊 Dynamic stats based on personality traits (e.g., "Chaos", "Rizz", "Drama Level")
- 💾 Save and download generated cards
- 🖼️ Gallery view of all created cards
- 🚀 **Live Demo**: Deployed on Render with free HTTPS
- 🔄 **Resilient AI**: Automatic fallback between LLM providers for maximum reliability

## Technology Stack

- **Backend**: Python, Flask (modular architecture)
- **AI**: Google Gemini 1.5 Flash (primary) + OpenAI GPT-4o (fallback)
- **Image Processing**: Pillow (PIL)
- **Frontend**: HTML, CSS, JavaScript (separated templates and static assets)
- **Deployment**: Render.com (Free HTTPS, automatic deployments!)

## Local Development

### Prerequisites

- Python 3.11+
- **Gemini API key** (primary LLM service)
- **OpenAI API key** (fallback LLM service)

### Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `API_KEYS.py` file:
   ```python
   GEMINI_API_KEY = "your-gemini-api-key"  # Primary LLM service
   OPENAI_API_KEY = "your-openai-api-key"  # Fallback LLM service
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser to `http://localhost:5000`

## Deployment

### Render.com (Recommended - Free HTTPS!)

**Best deployment option - secure, reliable, and easy!**

- 📖 **Quick Start**: [RENDER_QUICKSTART.md](RENDER_QUICKSTART.md) (15 minutes)
- 📋 **Detailed Guide**: [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) (30 minutes)

**Why Render:**
- ✅ **Free HTTPS** included (secure!)
- ✅ **Automatic deployments** from GitHub
- ✅ **Easy environment variable management**
- ✅ **Good free tier** with 750 hours/month
- ✅ **Real-time logs** and monitoring
- ✅ **Simple configuration**

**What you need:**
- GitHub account (free)
- Render account (free)
- OpenAI API key
- Push code to GitHub, Render auto-deploys!

**Note**: Free tier apps sleep after 15 min of inactivity (normal for free hosting)

### Environment Variables for Render

Set these in your Render service:
- `GEMINI_API_KEY`: Your Gemini API key (primary LLM service)
- `OPENAI_API_KEY`: Your OpenAI API key (fallback LLM service, starts with `sk-`)
- `FLASK_ENV`: Set to `production`

## Usage

1. **Upload a Photo**: Choose an image of a person or character (PNG, JPG, JPEG, GIF, BMP - max 16MB)
2. **Enter 5 Facts**: Provide personality traits, quirks, or characteristics (be creative and specific!)
3. **Generate**: Click "Generate Card" and wait for AI magic (usually 10-30 seconds)
4. **Download**: Save your custom card or view it in the gallery

### Example Facts:
- "He's terrified of a 'girly' workout despite being an avid tennis player"
- "His daily themed outfits are a spectacle - friends joke he's cosplaying as LHL"
- "He has a meme-worthy disdain for pickleball, calling it a sport for 'OLDIES'"
- "He's the group's 'Community Mom' who fosters connections with matcha lattes"
- "He creates personalized coding roadmaps for freshmen and shares academic regrets as advice"

### Tips for Best Results:
- Use clear, high-quality images with good lighting
- Be creative and specific with your facts - the more unique, the better!
- Use humor and personality traits that capture the essence of your character
- Shorter facts work best (the AI will generate better descriptions)
- The card generator works best with headshots or close-up photos

## Card Types

The app features 20 unique personality types across 4 categories:

### Vibe & Atmosphere
- Mood, Vibe, Spicy, Juice

### Digital & Logic
- NPC, Glitch, Lag, Ping, Debug, Firewall

### Ego & Status
- Main, Flex, IYKYK, Cringe

### Action & Conflict
- Clapback, Sus, Cap, Send

### Movement & Avoidance
- Ghost, Simp

Each type has its own color scheme, visual effects, and personality!

## LLM Fallback System

The application uses a robust dual-LLM architecture for maximum reliability:

### Primary Service: Google Gemini 1.5 Flash
- **Fast and efficient** for most card generation requests
- **Cost-effective** with generous free tier
- **High-quality** creative output for personality cards

### Fallback Service: OpenAI GPT-4o
- **Automatic fallback** when Gemini is unavailable
- **Proven reliability** for complex creative tasks
- **Consistent quality** as backup option

### How It Works:
1. **Primary Attempt**: Try Gemini API first
2. **Automatic Fallback**: If Gemini fails, automatically switch to OpenAI
3. **Seamless Experience**: Users don't notice the switch
4. **Comprehensive Logging**: All API calls and fallbacks are logged

### Benefits:
- ✅ **99.9% uptime** with dual provider redundancy
- ✅ **Cost optimization** using cheaper Gemini as primary
- ✅ **Quality assurance** with OpenAI as reliable backup
- ✅ **Transparent operation** with detailed logging

## Project Structure

```
├── app.py                      # Flask web application (backend only)
├── make_card.py               # Card generation orchestration
├── llm_api.py                 # LLM service integration (Gemini + OpenAI fallback)
├── card_styles.py             # Style configuration and color schemes
├── card_graphics.py           # Image manipulation and card rendering
├── API_KEYS.py                # Local API keys (DO NOT COMMIT)
├── requirements.txt           # Python dependencies
├── render.yaml               # Render deployment config
├── .gitignore                # Git ignore file
├── .gitattributes            # Git line ending settings
├── README.md                 # This file
├── REFACTORING_GUIDE.md      # Technical documentation for modular architecture
├── RENDER_QUICKSTART.md      # Quick deployment guide (15 min)
├── RENDER_DEPLOYMENT.md      # Detailed deployment guide (30 min)
├── RENDER_READY.md           # Deployment overview
├── templates/                # HTML templates
│   ├── index.html            # Main upload page
│   └── gallery.html          # Card gallery
├── static/                   # Static assets
│   ├── css/
│   │   └── styles.css        # Main stylesheet
│   └── js/
│       └── main.js           # Frontend JavaScript
├── Generated_Cards/          # Output directory (generated)
├── Original_Photos/          # Uploaded images (generated)
└── __pycache__/              # Python cache (generated)
```

## Debug & Testing

The app includes several debug endpoints for troubleshooting:

- `/health` - Check app status and API key configuration
- `/test-api` - Test OpenAI API connection
- `/debug` - Detailed API key and environment information

## Security

- API keys are stored as environment variables in production
- `API_KEYS.py` is excluded from version control via `.gitignore`
- User uploads are validated for file type and size (max 16MB)
- All user input is sanitized and validated

## Troubleshooting

### Common Issues:

1. **"Failed to generate card data"** 
   - Check that both Gemini and OpenAI API keys are correctly set in Render environment variables
   - Verify your API keys have credits available
   - Check logs to see which LLM service failed and why
   - Try with a smaller image file

2. **"API test failed"** 
   - Verify both your Gemini and OpenAI API keys are valid
   - Check your API accounts have available credits
   - Ensure the keys have not been compromised or revoked
   - The app will automatically fallback between services

3. **Image upload issues** 
   - Ensure file is under 16MB 
   - Use supported formats: PNG, JPG, JPEG, GIF, BMP
   - Try uploading again with a clear, high-quality image

4. **App sleeps frequently** 
   - This is normal for free tier (sleeps after 15 min inactivity)
   - First load after sleep takes ~30 seconds
   - Subscribe to paid tier to eliminate sleep periods

5. **Gallery page is empty**
   - Generated cards are stored in the `Generated_Cards/` directory
   - Ensure the app has write permissions
   - Check Render logs for file system errors

### Getting Help:

- **Check Render logs**: Go to your Render service → "Logs" tab for detailed error messages
- **Use the debug endpoint**: Visit `/debug` on your deployed app to verify configuration
- **Verify environment variables**: Check that all API keys are set correctly in Render settings
- **Test API connection**: Visit `/test-api` to verify your API keys work
- **Review app.py logs**: Watch real-time logs for error messages during card generation

### Advanced Debugging:

```bash
# For local development issues
python app.py --debug

# Check if all dependencies are installed
pip list

# Test OpenAI connection locally
python -c "import openai; print('OpenAI imported successfully')"

# Verify PIL/Pillow installation
python -c "from PIL import Image; print('Pillow imported successfully')"
```

## License

This project is for educational and entertainment purposes.

## Credits

Inspired by trading card games and meme culture. This is a fun project for creating personalized character cards!

## Technology Details

### Backend Architecture:
- **Flask**: Lightweight web framework for Python with modular design
- **Dual LLM System**: Google Gemini 1.5 Flash (primary) + OpenAI GPT-4o (fallback)
- **Modular Design**: Separated concerns with dedicated modules for LLM, styles, and graphics
- **Pillow (PIL)**: Python Imaging Library for card image generation and manipulation
- **Gunicorn**: WSGI HTTP Server for production deployment

### Frontend Features:
- **Separated Templates**: Clean HTML templates with external CSS/JS
- **Drag-and-drop** image upload
- **Real-time** preview and validation
- **Responsive design** that works on mobile and desktop
- **Progress indicators** for long-running operations
- **Gallery view** with pagination support

### Deployment:
- **Render.com**: Free HTTPS, automatic CI/CD from GitHub
- **Environment-based configuration** for security
- **Health check endpoints** for monitoring
- **Automatic file handling** for generated cards and uploads

## Future Enhancements

Potential features for future versions:
- [ ] Social media sharing integration
- [ ] Custom card templates and themes
- [ ] Batch card generation
- [ ] Card editing and customization after generation
- [ ] User authentication and saved collections
- [ ] API endpoint for programmatic access
- [ ] More personality types and categories
- [ ] Card animation and interactive features

## Support & Contribution

If you encounter issues or have suggestions:
1. Check the troubleshooting section
2. Review existing GitHub issues
3. Create a new issue with detailed description
4. Share feedback on features you'd like to see

---

**Made with ❤️ and AI Magic ✨**

Last updated: October 2025


