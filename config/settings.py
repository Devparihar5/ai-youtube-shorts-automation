"""
YouTube Shorts Automation - Configuration
All settings in one place. Fill in your API keys.
"""

import os
from pathlib import Path

# Load .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).resolve().parent.parent / ".env"
    if _env_path.exists():
        load_dotenv(_env_path)
except ImportError:
    pass  # python-dotenv is optional

# ============================================================
# PROJECT PATHS
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output"
TEMPLATES_DIR = BASE_DIR / "templates"
LOGS_DIR = BASE_DIR / "logs"

# Create dirs if missing
for d in [ASSETS_DIR, OUTPUT_DIR, TEMPLATES_DIR, LOGS_DIR]:
    d.mkdir(exist_ok=True)

# ============================================================
# FREE API KEYS (Get these for free)
# ============================================================

# Pexels - Free stock video/images
# Sign up: https://www.pexels.com/api/
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "QQiaLu3hY6CyKsB3JnttbUutfzGxwxXGeBBdkJ7UPszx8d5V1GhH2Hbx")

# Pixabay - Free stock video/images (backup)
# Sign up: https://pixabay.com/api/docs/
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "QQiaLu3hY6CyKsB3JnttbUutfzGxwxXGeBBdkJ7UPszx8d5V1GhH2Hbx")

# YouTube Data API - Free quota (10,000 units/day)
# Setup: https://console.cloud.google.com
# Enable: YouTube Data API v3
# Create: OAuth 2.0 Client ID (Desktop app)
# Download: client_secret.json → put in config/ folder
YOUTUBE_CLIENT_SECRET_FILE = str(BASE_DIR / "config" / "client_secret.json")
YOUTUBE_TOKEN_FILE = str(BASE_DIR / "config" / "youtube_token.json")

# ============================================================
# GEMINI AI
# Get a free API key from Google AI Studio: https://aistudio.google.com/apikey
# ============================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_URL = os.getenv("GEMINI_URL", "https://generativelanguage.googleapis.com/v1beta/models")

# ============================================================
# LANGUAGE SETTINGS
# ============================================================
CONTENT_LANGUAGE = "hindi"  # "hindi" or "english"
# Hindi me scripts likhega, Hinglish style (Hindi + English mix)
# Jo Indian audience ko sabse zyada pasand aata hai

# ============================================================
# FREE VOICE (edge-tts - Microsoft Edge TTS, completely free)
# pip install edge-tts
# ============================================================
VOICE_NAME = "hi-IN-MadhurNeural"  # Hindi male - deep dramatic voice
# Other options:
# "hi-IN-SwaraNeural"         - Hindi female
# "en-US-ChristopherNeural"   - English male dramatic
# "en-US-JennyNeural"         - English female
# "en-IN-PrabhatNeural"       - Indian English male

# ============================================================
# VIDEO SETTINGS
# ============================================================
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920  # 9:16 vertical for Shorts
VIDEO_FPS = 30
VIDEO_MAX_DURATION = 59  # YouTube Shorts limit
VIDEO_TARGET_DURATION = 35  # Target length (longer = more watch time)
FONT_SIZE = 48  # Subtitle font size (smaller for Hindi = more readable)
FONT_COLOR = "white"
FONT_BORDER_COLOR = "black"
FONT_BORDER_WIDTH = 4
SUBTITLE_STYLE = "bold"  # bold subtitles for professional look
BACKGROUND_MUSIC_VOLUME = 0.12  # 12% volume for bg music (slightly louder)

# ============================================================
# CONTENT NICHES (Hindi audience - India focused)
# ============================================================
NICHES = [
    {
        "name": "AI & Technology",
        "keywords": ["AI", "artificial intelligence", "technology", "ChatGPT", "automation", "future tech", "robots"],
        "subreddits": ["technology", "artificial", "MachineLearning", "ChatGPT"],
    },
    {
        "name": "Money & Business",
        "keywords": ["money", "business", "wealth", "finance", "startup", "investing", "rich", "billionaire"],
        "subreddits": ["business", "Entrepreneur", "finance", "investing"],
    },
    {
        "name": "Psychology & Mind",
        "keywords": ["psychology", "mind tricks", "brain", "dark psychology", "manipulation", "confidence", "body language"],
        "subreddits": ["psychology", "todayilearned", "LifeProTips"],
    },
    {
        "name": "Shocking Facts",
        "keywords": ["shocking facts", "amazing facts", "unknown facts", "did you know", "unbelievable", "mystery"],
        "subreddits": ["todayilearned", "Damnthatsinteresting", "interestingasfuck"],
    },
    {
        "name": "Motivation & Success",
        "keywords": ["motivation", "success", "mindset", "discipline", "habits", "billionaire lifestyle"],
        "subreddits": ["GetMotivated", "selfimprovement", "Entrepreneur"],
    },
]

# ============================================================
# SCHEDULING
# ============================================================
VIDEOS_PER_DAY = 4
SCHEDULE_INTERVAL_HOURS = 6  # Every 6 hours = 4 videos/day
UPLOAD_HOUR_START = 7  # Upload window start (AM)
UPLOAD_HOUR_END = 21  # Upload window end (PM)

# ============================================================
# LOGGING
# ============================================================
LOG_FILE = str(LOGS_DIR / "automation.log")
LOG_LEVEL = "INFO"