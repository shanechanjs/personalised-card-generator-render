# Personalised Card Generator

An AI-powered web application that generates personalized trading cards based on photos and personality traits. Create hilarious, meme-worthy character cards with AI-generated names and descriptions!

## Features

- 🎨 Upload any photo and transform it into a custom card
- 🤖 AI-generated creative card names and descriptions using OpenAI GPT-4o
- 🎭 20 unique personality types with custom color schemes and visual effects
- 📊 Dynamic stats based on personality traits (e.g., "Chaos", "Rizz", "Drama Level")
- 💾 Save and download generated cards
- 🖼️ Gallery view of all created cards
- 🚀 **Live Demo**: Deployed on Render with free HTTPS

## Technology Stack

- **Backend**: Python, Flask
- **AI**: OpenAI GPT-4o API
- **Image Processing**: Pillow (PIL)
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Render.com (Free HTTPS, automatic deployments!)

## Local Development

### Prerequisites

- Python 3.11+
- OpenAI API key
- Gemini API key (optional)

### Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `API_KEYS.py` file:
   ```python
   OPENAI_API_KEY = "your-openai-api-key"
   GEMINI_API_KEY = "your-gemini-api-key"
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
- `OPENAI_API_KEY`: Your OpenAI API key (starts with `sk-`)
- `GEMINI_API_KEY`: Your Gemini API key (optional)
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

## Project Structure

```
├── app.py                 # Flask web application
├── make_card.py          # Card generation logic
├── requirements.txt      # Python dependencies
├── render.yaml          # Render deployment config
├── templates/           # HTML templates
│   ├── index.html       # Main upload page
│   └── gallery.html     # Card gallery
├── static/              # CSS and JavaScript
│   ├── style.css
│   └── script.js
├── Generated_Cards/     # Output directory
├── Original_Photos/     # Uploaded images
├── RENDER_QUICKSTART.md  # Quick deployment guide
└── RENDER_DEPLOYMENT.md  # Detailed deployment guide
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

1. **"Failed to generate card data"** - Check that your OpenAI API key is correctly set in Render environment variables
2. **"API test failed"** - Verify your API key is valid and has sufficient credits
3. **Image upload issues** - Ensure file is under 16MB and in supported format (PNG, JPG, JPEG, GIF, BMP)
4. **App sleeps frequently** - This is normal for free tier (sleeps after 15 min inactivity)

### Getting Help:

- Check Render logs for detailed error messages
- Use the `/debug` endpoint to verify configuration
- Ensure all environment variables are set correctly

## License

This project is for educational and entertainment purposes.

## Credits

Inspired by trading card games and meme culture. This is a fun project for creating personalized character cards!

