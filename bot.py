import os
import random
import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from gtts import gTTS
import google.generativeai as genai
from elevenlabs.client import ElevenLabs  # Updated import for v1.x
import requests
from pytube import YouTube

# ===== CONFIG (SECURE) ===== #
API_ID = int(os.environ.get("API_ID"))  # From Render Environment Variables
API_HASH = os.environ.get("API_HASH")  # From Render
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # From Render
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")  # From Render
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")  # From Render
OWNER_USERNAME = "ash_yv"  # Public username

# Initialize ElevenLabs client
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)  # Updated for v1.x

# ===== GAME DATABASES ===== #
TRUTHS = [
    "What's your most embarrassing Google search?",
    "Have you ever pretended to like a gift?",
    "What's the weirdest thing you've done for money?"
]

DARES = [
    "Send your most cringe childhood photo!",
    "Do 10 pushups right now!",
    "Sing a Bollywood song in voice chat!"
]

ROASTS = [
    "You're like a broken pencil... pointless!",
    "Is your WiFi weak or are you just boring?",
    "Even Siri ignores your questions!"
]

RIDDLES = {
    "I speak without a mouth": "echo",
    "The more you take, the more you leave behind": "footsteps"
}

# ===== INITIALIZE ===== #
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")
app = Client("CinderellaAI", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ===== CORE FUNCTIONS ===== #
async def text_to_voice(text: str) -> str:
    """Convert text to voice note using ElevenLabs (fallback to gTTS)"""
    try:
        audio = client.generate(  # Updated for ElevenLabs v1.x
            text=text,
            voice="Rachel",
            model="eleven_monolingual_v2"
        )
        filename = f"voice_{random.randint(1000,9999)}.mp3"
        with open(filename, "wb") as f:
            f.write(audio)  # Note: ElevenLabs v1.x may return different audio format
        return filename
    except Exception as e:
        print(f"ElevenLabs error: {e}, using gTTS")
        tts = gTTS(text=text, lang='hi', slow=False)
        filename = f"voice_{random.randint(1000,9999)}.mp3"
        tts.save(filename)
        return filename

async def generate_response(prompt: str) -> str:
    """Generate AI response with Gemini"""
    try:
        response = model.generate_content(
            "Respond as 'Cinderella AI' - a witty bilingual (Hinglish/English) Telegram bot. "
            "Rules:\n"
            "1. Use emojis and be playful\n"
            "2. For owner questions, mention @ash_yv\n"
            "3. Keep responses under 2 sentences\n\n"
            f"User asked: {prompt}"
        )
        return response.text or "Oops! My magic failed! 🪄"
    except Exception as e:
        return f"Error: {str(e)}"

async def download_reel(url: str) -> str:
    """Download Instagram reel"""
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(file_extension='mp4').first()
        filename = f"reel_{random.randint(1000,9999)}.mp4"
        stream.download(filename=filename)
        return filename
    except Exception as e:
        print(f"Reel download error: {e}")
        return None

# ===== COMMAND HANDLERS ===== #
# [Keep ALL your existing command handlers unchanged]
# @app.on_message(filters.command("start")) etc...
# ...

# ===== RUN BOT ===== #
print("""
╔══════════════════════╗
║   CINDERELLA AI LIVE   ║
╚══════════════════════╝
""")
app.run()
