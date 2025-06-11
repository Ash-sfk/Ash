import os
import random
import re
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from gtts import gTTS
import google.generativeai as genai
from elevenlabs.client import ElevenLabs
import requests
from pytube import YouTube

# ===== CONFIG ===== #
API_ID = int(os.getenv('API_ID', 24694023))  # Convert to int
API_HASH = os.getenv('API_HASH', "5577696a88c6b197fdbdf299a396aa63")
BOT_TOKEN = os.getenv('BOT_TOKEN', "")  # MUST set in Render
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', "")
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', "")
OWNER_USERNAME = os.getenv('OWNER_USERNAME', "ash_yv")

# ===== INITIALIZE ===== #
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")
eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY) if ELEVENLABS_API_KEY else None

app = Client(
    "CinderellaAI",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=enums.ParseMode.MARKDOWN,
    in_memory=True  # Critical for Render
)

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

# ===== CORE FUNCTIONS ===== #
async def text_to_voice(text: str) -> str:
    try:
        if eleven_client:
            audio = eleven_client.generate(
                text=text,
                voice="Rachel",
                model="eleven_monolingual_v2"
            )
            filename = f"voice_{random.randint(1000,9999)}.mp3"
            with open(filename, "wb") as f:
                f.write(audio)
            return filename
    except Exception as e:
        print(f"ElevenLabs error: {e}, using gTTS")
    tts = gTTS(text=text, lang='hi', slow=False)
    filename = f"voice_{random.randint(1000,9999)}.mp3"
    tts.save(filename)
    return filename

# ... [Keep ALL your original command handlers unchanged] ...

if __name__ == "__main__":
    print("""
    ╔══════════════════════╗
    ║   CINDERELLA AI LIVE   ║
    ╚══════════════════════╝
    """)
    app.run()
