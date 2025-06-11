import os
import random
import re
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from gtts import gTTS
import google.generativeai as genai
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
import requests
from pytube import YouTube
from threading import Thread
from flask import Flask

# ===== Flask Server for Render Health Check =====
app_flask = Flask(__name__)

@app_flask.route('/health')
def health_check():
    return "OK", 200

def run_flask():
    app_flask.run(host='0.0.0.0', port=10000)

Thread(target=run_flask, daemon=True).start()

# ===== BOT CONFIG ===== #
API_ID = os.getenv('API_ID', 24694023)
API_HASH = os.getenv('API_HASH', "5577696a88c6b197fdbdf299a396aa63")
BOT_TOKEN = os.getenv('BOT_TOKEN', "8070710114:AAHnXSR_4BFBzVzY_TRUm0gauXLsr4DhPok")
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', "AIzaSyDFhYXGeuzzq5oBvcibvSnxvceGLAast6E")
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', "sk_6f6ec9f515e7e91e5108271f3e38b4361fcc0bcbf36c2792")
OWNER_USERNAME = os.getenv('OWNER_USERNAME', "ash_yv")

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

# ===== INITIALIZE CLIENTS ===== #
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")
eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
app = Client(
    "CinderellaAI",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=enums.ParseMode.MARKDOWN
)

# ===== CORE FUNCTIONS ===== #
async def text_to_voice(text: str) -> str:
    try:
        audio = eleven_client.generate(
            text=text,
            voice="Rachel",
            model="eleven_monolingual_v2",
            voice_settings=VoiceSettings(stability=0.35, similarity_boost=0.85)
        )
        filename = f"voice_{random.randint(1000,9999)}.mp3"
        with open(filename, "wb") as f:
            for chunk in audio:
                if chunk:
                    f.write(chunk)
        return filename
    except Exception as e:
        print(f"ElevenLabs error: {e}, using gTTS")
        tts = gTTS(text=text, lang='hi', slow=False)
        filename = f"voice_{random.randint(1000,9999)}.mp3"
        tts.save(filename)
        return filename

async def generate_response(prompt: str) -> str:
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
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        filename = f"reel_{random.randint(1000,9999)}.mp4"
        stream.download(filename=filename)
        return filename
    except Exception as e:
        print(f"Reel download error: {e}")
        return None

# ===== COMMAND HANDLERS ===== #
@app.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply_text(
        "✨ *Namaste! I'm Cinderella AI* ✨\n\n"
        "🎙️ *Voice*: `/speech [text]`\n"
        "🎮 *Games*:\n"
        "- `/truth`\n- `/dare`\n- `/roast @user`\n- `/riddle`\n"
        "📥 *Downloads*:\n"
        "- `/reel [URL]`\n\n"
        "👑 My owner: @ash_yv"
    )

# ... [All other command handlers remain exactly the same as your original] ...

if __name__ == "__main__":
    print("""
    ╔══════════════════════╗
    ║   CINDERELLA AI LIVE   ║
    ╚══════════════════════╝
    """)
    app.run()
