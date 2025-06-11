import os
import random
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from gtts import gTTS
import google.generativeai as genai
from elevenlabs import generate, set_api_key
from pytube import YouTube
import aiohttp

# ===== CONFIG ===== #
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
GEMINI_KEY = os.environ["GEMINI_API_KEY"]
ELEVENLABS_KEY = os.environ["ELEVENLABS_API_KEY"]
OWNER = "ash_yv"

# Initialize APIs
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-pro")
set_api_key(ELEVENLABS_KEY)

app = Client(
    "CinderellaUltimate",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

# ===== GAME DATABASES ===== #
TRUTHS = ["What's your most embarrassing Google search?"]  # Add more
DARES = ["Do 10 pushups now!"]
ROASTS = ["You're like a broken pencil!"]
RIDDLES = {"I speak without a mouth": "echo"}

# ===== CORE FUNCTIONS ===== #
async def text_to_voice(text: str):
    try:
        audio = generate(text=text, voice="Rachel", model="eleven_monolingual_v2")
        filename = f"voice_{random.randint(1000,9999)}.mp3"
        with open(filename, "wb") as f:
            f.write(audio)
        return filename
    except Exception as e:
        print(f"Voice error: {e}")
        tts = gTTS(text=text, lang='hi')
        filename = f"voice_{random.randint(1000,9999)}.mp3"
        tts.save(filename)
        return filename

async def download_reel(url: str):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(file_extension='mp4').first()
        filename = f"reel_{random.randint(1000,9999)}.mp4"
        stream.download(filename=filename)
        return filename
    except Exception as e:
        print(f"Reel error: {e}")
        return None

async def get_meme():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://meme-api.com/gimme") as resp:
            return (await resp.json())["url"]

# ===== COMMAND HANDLERS ===== #
@app.on_message(filters.command("start"))
async def start(_, m: Message):
    await m.reply_text(
        "✨ *Ultimate Cinderella AI* ✨\n\n"
        "🎙️ /speech [text]\n"
        "🎮 /truth /dare /roast /riddle\n"
        "📥 /reel [URL]\n"
        "😂 /meme\n"
        "👑 Owner: @ash_yv"
    )

@app.on_message(filters.command("speech"))
async def speech(_, m: Message):
    if len(m.command) < 2:
        await m.reply_text("Usage: /speech Hello")
        return
    
    voice = await text_to_voice(" ".join(m.command[1:]))
    if voice:
        await m.reply_voice(voice)
        os.remove(voice)

@app.on_message(filters.command("meme"))
async def meme(_, m: Message):
    await m.reply_photo(await get_meme())

# [Add other commands following the same pattern]

if __name__ == "__main__":
    print("✅ BOT STARTED")
    app.run()
