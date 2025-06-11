import os
import random
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from gtts import gTTS
import google.generativeai as genai
from elevenlabs import generate, set_api_key
import requests
from pytube import YouTube
import aiohttp

# ===== CONFIG ===== #
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
OWNER_USERNAME = "ash_yv"

# Initialize APIs
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")
set_api_key(ELEVENLABS_API_KEY)

app = Client(
    "CinderellaUltimate",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True  # Critical for Render
)

# ===== DATABASES ===== #
TRUTHS = ["What's your most embarrassing Google search?", ...]  # Keep your originals
DARES = ["Do 10 pushups now!", ...]
ROASTS = ["You're like a broken pencil... pointless!", ...]
RIDDLES = {"I speak without a mouth": "echo", ...}

# ===== CRAZY NEW FEATURES ===== #
async def get_meme():
    """NEW: Fetch random meme from Reddit"""
    async with aiohttp.ClientSession() as session:
        async with session.get("https://meme-api.com/gimme") as resp:
            return (await resp.json())["url"]

async def fake_ban_user(client: Client, message: Message):
    """NEW: Prank command that sends a fake ban animation"""
    drama = await message.reply_animation(
        animation="https://telegra.ph/file/4a783a6a119a7b935a7c9.mp4",
        caption="🚨 *User Banned Forever!* 🚨\n\nJust kidding! 😜"
    )
    await asyncio.sleep(5)
    await drama.delete()

# ===== CORE FUNCTIONALITY ===== #
@app.on_message(filters.command("start"))
async def start(_, m: Message):
    await m.reply_text(
        "✨ *Ultimate Cinderella AI* ✨\n\n"
        "🎙️ /speech [text]\n"
        "🎮 /truth /dare /roast /riddle\n"
        "📥 /reel [URL]\n"
        "😂 /meme - Random dank meme\n"
        "🔨 /fakeban - Prank your friends!\n"
        "👑 Owner: @ash_yv",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Add Me To Group", url=f"http://t.me/{BOT_TOKEN.split(':')[0]}?startgroup=true")
        ]])
    )

@app.on_message(filters.command("meme"))
async def meme_cmd(_, m: Message):
    """NEW: Meme command handler"""
    meme = await get_meme()
    await m.reply_photo(photo=meme, caption="Here's your dank meme! 😂")

@app.on_message(filters.command("fakeban") & filters.reply)
async def fakeban_cmd(client, m: Message):
    """NEW: Fake ban handler"""
    await fake_ban_user(client, m)

# ===== ORIGINAL COMMANDS ===== #
# @app.on_message(filters.command("speech"))  # Keep all original handlers
# @app.on_message(filters.command("truth"))
# ... (Paste all your existing command handlers here exactly as before)

if __name__ == "__main__":
    print("╔══════════════════════╗\n║   ULTIMATE BOT ACTIVATED   ║\n╚══════════════════════╝")
    app.run()
