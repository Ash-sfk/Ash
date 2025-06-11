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

# ... [Keep all your existing command handlers unchanged] ...

if __name__ == "__main__":
    print("""
    ╔══════════════════════╗
    ║   CINDERELLA AI LIVE   ║
    ╚══════════════════════╝
    """)
    app.run()
