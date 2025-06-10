import os
import random
import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from gtts import gTTS
import google.generativeai as genai
from elevenlabs.client import ElevenLabs
import requests
from pytube import YouTube

# ===== CONFIG ===== #
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
OWNER_USERNAME = "ash_yv"

# Initialize clients
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")
eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)  # v1.x syntax

# Pyrogram client with in_memory session (critical for Render)
app = Client(
    "CinderellaAI",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True  # ← Fixes session storage issues
)

# ===== GAME DATABASES ===== #
TRUTHS = ["What's your most embarrassing Google search?", ...]  # Keep your existing lists
DARES = ["Send your most cringe childhood photo!", ...]
ROASTS = ["You're like a broken pencil... pointless!", ...]
RIDDLES = {"I speak without a mouth": "echo", ...}

# ===== CORE FUNCTIONS ===== #
async def text_to_voice(text: str) -> str:
    try:
        audio = eleven_client.generate(
            text=text,
            voice="Rachel",
            model="eleven_monolingual_v2"
        )
        filename = f"voice_{random.randint(1000,9999)}.mp3"
        with open(filename, "wb") as f:
            f.write(audio)  # Works with ElevenLabs v1.x
        return filename
    except Exception as e:
        print(f"Voice error: {e}, using gTTS")
        tts = gTTS(text=text, lang='hi')
        filename = f"voice_{random.randint(1000,9999)}.mp3"
        tts.save(filename)
        return filename

async def download_reel(url: str) -> str:
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(file_extension='mp4').first()
        filename = f"reel_{random.randint(1000,9999)}.mp4"
        stream.download(filename=filename)
        return filename
    except Exception as e:
        print(f"Reel error: {e}")
        return None

# ===== COMMAND HANDLERS ===== #
@app.on_message(filters.command("start"))
async def start(_, m: Message):
    await m.reply_text(
        "✨ *Namaste! I'm Cinderella AI* ✨\n\n"
        "🎙️ /speech [text]\n"
        "🎮 /truth /dare /roast /riddle\n"
        "📥 /reel [URL]\n"
        "👑 Owner: @ash_yv"
    )

# [Keep ALL other command handlers unchanged]
# @app.on_message(filters.command("truth")) ... etc.

# ===== RUN BOT ===== #
if __name__ == "__main__":
    print("╔══════════════════════╗\n║   CINDERELLA AI LIVE   ║\n╚══════════════════════╝")
    app.run()
