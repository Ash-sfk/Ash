import os
import random
import re
import asyncio
import aiohttp
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from gtts import gTTS
import google.generativeai as genai
from elevenlabs import generate, set_api_key
import requests
from pytube import YouTube
from datetime import datetime

# ===== CONFIGURATION ===== #
class Config:
    API_ID = int(os.environ.get("API_ID", 0))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
    OWNER_USERNAME = "ash_yv"

# ===== DATABASES ===== #
class Database:
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

# ===== CORE FUNCTIONALITY ===== #
class CinderellaBot:
    def __init__(self):
        self.app = Client(
            "CinderellaProMax",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            in_memory=True,
            plugins=dict(root="plugins")
        )
        
        # Initialize APIs
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-pro")
        set_api_key(Config.ELEVENLABS_API_KEY)
        
        # Register handlers
        self.register_handlers()
    
    async def text_to_voice(self, text: str) -> str:
        """Convert text to voice with fallback"""
        try:
            audio = generate(
                text=text,
                voice="Rachel",
                model="eleven_monolingual_v2"
            )
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
    
    async def download_reel(self, url: str) -> str:
        """Download Instagram reel"""
        try:
            yt = YouTube(url)
            stream = yt.streams.filter(file_extension='mp4').first()
            filename = f"reel_{random.randint(1000,9999)}.mp4"
            stream.download(filename=filename)
            return filename
        except Exception as e:
            print(f"Reel error: {e}")
            return None
    
    async def get_meme(self):
        """Fetch random meme from API"""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://meme-api.com/gimme") as resp:
                return (await resp.json())["url"]
    
    def register_handlers(self):
        # ===== COMMAND HANDLERS ===== #
        @self.app.on_message(filters.command("start"))
        async def start(_, message: Message):
            await message.reply_text(
                "✨ *Ultimate Cinderella AI* ✨\n\n"
                "🎙️ /speech [text] - Text to voice\n"
                "🎮 /truth - Random question\n"
                "🎮 /dare - Challenge\n"
                "🔥 /roast - Savage reply\n"
                "🧩 /riddle - Brain teaser\n"
                "📥 /reel [url] - Download IG reels\n"
                "😂 /meme - Random meme\n"
                "👑 Owner: @ash_yv",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Add to Group", 
                        url=f"http://t.me/{Config.BOT_TOKEN.split(':')[0]}?startgroup=true")
                ]]),
                parse_mode=enums.ParseMode.MARKDOWN
            )
        
        @self.app.on_message(filters.command("speech"))
        async def speech_handler(_, message: Message):
            if len(message.command) < 2:
                await message.reply_text("Usage: /speech Hello world!")
                return
            
            text = " ".join(message.command[1:])
            voice_file = await self.text_to_voice(text)
            
            if voice_file:
                await message.reply_voice(voice_file, caption=f"🎤: {text}")
                os.remove(voice_file)
        
        # [Add all other command handlers following the same pattern]
        # @self.app.on_message(filters.command("truth"))
        # @self.app.on_message(filters.command("dare"))
        # etc...
        
        @self.app.on_message(filters.command("meme"))
        async def meme_handler(_, message: Message):
            meme_url = await self.get_meme()
            await message.reply_photo(
                photo=meme_url,
                caption="Here's your dank meme! 😂"
            )
    
    def run(self):
        print("╔══════════════════════╗\n║   BOT STARTED SUCCESSFULLY   ║\n╚══════════════════════╝")
        self.app.run()

if __name__ == "__main__":
    bot = CinderellaBot()
    bot.run()
