import os
import random
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from gtts import gTTS
import google.generativeai as genai
from elevenlabs import set_api_key, generate as eleven_generate
import requests
from pytube import YouTube

# ===== CONFIG ===== #
API_ID = int(os.getenv("API_ID", "24694023"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "ash_yv")

# ===== DATABASES ===== #
TRUTHS = [...]
DARES = [...]
ROASTS = [...]
RIDDLES = {
    "I speak without a mouth": "echo",
    "The more you take, the more you leave behind": "footsteps",
}

# ===== INIT ===== #
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")
set_api_key(ELEVENLABS_API_KEY)
app = Client("CinderellaAI", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ===== FUNCTIONS ===== #
async def text_to_voice(text: str) -> str:
    try:
        audio = eleven_generate(
            text=text,
            voice="Rachel",
            model="eleven_monolingual_v2"
        )
        filename = f"voice_{random.randint(1000,9999)}.mp3"
        with open(filename, "wb") as f:
            f.write(audio)
        return filename
    except Exception as e:
        tts = gTTS(text=text, lang='hi')
        filename = f"voice_{random.randint(1000,9999)}.mp3"
        tts.save(filename)
        return filename

async def generate_response(prompt: str) -> str:
    try:
        resp = model.generate_content(
            "Respond as 'Cinderella AI' … "
            f"User asked: {prompt}"
        )
        return resp.text or "Oops! 🪄"
    except Exception as e:
        return f"Error: {e}"

async def download_reel(url: str) -> str | None:
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(file_extension='mp4').first()
        fn = f"reel_{random.randint(1000,9999)}.mp4"
        stream.download(filename=fn)
        return fn
    except Exception:
        return None

# ===== HANDLERS ===== #
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text("✨ Namaste! …")

@app.on_message(filters.command("speech"))
async def speech(client, msg: Message):
    if len(msg.command) < 2:
        return await msg.reply_text("Usage: /speech [text]")
    txt = " ".join(msg.command[1:])
    vf = await text_to_voice(txt)
    await msg.reply_voice(vf, caption=txt)
    os.remove(vf)

# ... keep building rest of commands similarly: /truth, /dare, /roast, /riddle, /answer, /reel ...

@app.on_message(filters.text & (filters.mentioned | filters.private))
async def chat(client, msg: Message):
    if msg.text.startswith("/"): return
    reply = await generate_response(msg.text)
    vf = None
    if random.random() < 0.3:
        vf = await text_to_voice(reply)
        await msg.reply_voice(vf, caption=reply)
        os.remove(vf)
    else:
        await msg.reply_text(reply)

# ===== RUN ===== #
if __name__ == "__main__":
    print("CINDERELLA AI LIVE")
    app.run()
