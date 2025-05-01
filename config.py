import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Required Telegram API credentials
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    
    # Google AI API for fortune-telling feature
    GEMINI_KEY = os.getenv("GEMINI_KEY", "")
    
    # Bot configurations
    BOT_USERNAME = os.getenv("BOT_USERNAME", "CinderellaBot")
    BOT_NAME = "Cinderella Bot"
    
    # Default admin IDs - these should be populated from environment variables
    # Format: comma-separated list of admin IDs
    ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]
    
    # Database configuration (using simple JSON file for MVP)
    DB_PATH = "cinderella_db.json"
    
    # Voice chat settings
    MAX_SONG_DURATION = 300  # 5 minutes in seconds
    DISNEY_SONGS = {
        "bibbidi-bobbidi-boo": "https://example.com/bibbidi-bobbidi-boo.mp3",
        "a-dream-is-a-wish": "https://example.com/a-dream-is-a-wish.mp3",
        "so-this-is-love": "https://example.com/so-this-is-love.mp3",
    }
    
    # Default warning settings
    MAX_WARNINGS = 3
    MUTE_DURATION = 3600  # 1 hour in seconds
