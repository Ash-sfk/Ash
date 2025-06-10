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

# Initialize APIs
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")
eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Pyrogram Client (critical for Render)
app = Client(
    "CinderellaAI",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
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
    "The more you take, the more you leave behind": "footsteps",
    "What has keys but no locks?": "piano"
}

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
            f.write(audio)
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
async def start(_, message: Message):
    await message.reply_text(
        "✨ *Namaste! I'm Cinderella AI* ✨\n\n"
        "🎙️ /speech [text]\n"
        "🎮 /truth /dare /roast /riddle\n"
        "📥 /reel [URL]\n"
        "👑 Owner: @ash_yv"
    )

# [Add all other command handlers here exactly as before]

# ===== RUN BOT ===== #
print("╔══════════════════════╗\n║   CINDERELLA AI LIVE   ║\n╚══════════════════════╝")
app.run()
