import os
import random
import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from gtts import gTTS
import google.generativeai as genai
from elevenlabs import generate, set_api_key
import requests
from pytube import YouTube

# ===== CONFIG ===== #
API_ID = 24694023
API_HASH = "5577696a88c6b197fdbdf299a396aa63"
BOT_TOKEN = "8070710114:AAHnXSR_4BFBzVzY_TRUm0gauXLsr4DhPok"
GEMINI_API_KEY = "AIzaSyDFhYXGeuzzq5oBvcibvSnxvceGLAast6E"
ELEVENLABS_API_KEY = "sk_6f6ec9f515e7e91e5108271f3e38b4361fcc0bcbf36c2792"
OWNER_USERNAME = "ash_yv"

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
set_api_key(ELEVENLABS_API_KEY)
app = Client("CinderellaAI", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ===== CORE FUNCTIONS ===== #
async def text_to_voice(text: str) -> str:
    """Convert text to voice note using ElevenLabs (fallback to gTTS)"""
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
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    """Welcome message with commands"""
    await message.reply_text(
        "✨ *Namaste! I'm Cinderella AI* ✨\n\n"
        "🎙️ *Voice*: /speech [text]\n"
        "🎮 *Games*:\n"
        "- /truth\n- /dare\n- /roast @user\n- /riddle\n"
        "📥 *Downloads*:\n"
        "- /reel [URL]\n"
        "👑 My owner: @ash_yv"
    )

@app.on_message(filters.command("speech"))
async def speech_command(client, message: Message):
    """Convert text to voice note"""
    if len(message.command) < 2:
        await message.reply_text("Usage: /speech Hello dosto!")
        return
    
    text = " ".join(message.command[1:])
    voice_file = await text_to_voice(text)
    
    if voice_file:
        await message.reply_voice(voice_file, caption=f"🎤: {text}")
        os.remove(voice_file)
    else:
        await message.reply_text("Voice generation failed! Try again later.")

@app.on_message(filters.command("truth"))
async def truth_command(client, message: Message):
    """Send a truth question"""
    await message.reply_text(f"🤔 *Truth*: {random.choice(TRUTHS)}")

@app.on_message(filters.command("dare"))
async def dare_command(client, message: Message):
    """Send a dare challenge"""
    await message.reply_text(f"🔥 *Dare*: {random.choice(DARES)}")

@app.on_message(filters.command("roast") & filters.reply)
async def roast_command(client, message: Message):
    """Roast the replied user"""
    target = message.reply_to_message.from_user
    await message.reply_text(
        f"{target.first_name}, {random.choice(ROASTS)} 😈",
        reply_to_message_id=message.reply_to_message.id
    )

@app.on_message(filters.command("riddle"))
async def riddle_command(client, message: Message):
    """Send a riddle"""
    riddle, answer = random.choice(list(RIDDLES.items()))
    await message.reply_text(f"🧩 *Riddle*: {riddle}\n\nReply /answer to reveal!")
    app.set_data(f"riddle_{message.chat.id}", answer)

@app.on_message(filters.command("answer"))
async def answer_command(client, message: Message):
    """Reveal riddle answer"""
    answer = app.get_data(f"riddle_{message.chat.id}")
    if answer:
        await message.reply_text(f"✅ *Answer*: {answer}")
    else:
        await message.reply_text("No active riddle! Use /riddle first.")

@app.on_message(filters.command("reel"))
async def reel_command(client, message: Message):
    """Download Instagram reel"""
    if len(message.command) < 2:
        await message.reply_text("Usage: /reel [URL]")
        return
    
    url = message.command[1]
    msg = await message.reply_text("📥 Downloading reel...")
    
    reel_file = await download_reel(url)
    if reel_file:
        await msg.edit_text("✅ Uploading...")
        await message.reply_video(reel_file)
        os.remove(reel_file)
    else:
        await msg.edit_text("❌ Failed to download reel!")

# ===== SMART INTERACTIONS ===== #
@app.on_message(filters.regex(r"(owner|creator|malik|who made you)", re.IGNORECASE))
async def owner_handler(client, message: Message):
    """Respond to owner queries"""
    response = f"My beloved creator is @{OWNER_USERNAME}! ❤️"
    if random.random() < 0.4:  # 40% voice response
        voice_file = await text_to_voice(response)
        await message.reply_voice(voice_file, caption=response)
        os.remove(voice_file)
    else:
        await message.reply_text(response)

@app.on_message(filters.text & (filters.mentioned | filters.private))
async def chat_handler(client, message: Message):
    """Smart replies when mentioned"""
    if message.text.startswith("/"):
        return
    
    reply = await generate_response(message.text)
    if random.random() < 0.3:  # 30% voice notes
        voice_file = await text_to_voice(reply)
        await message.reply_voice(voice_file, caption=reply)
        os.remove(voice_file)
    else:
        await message.reply_text(reply)

# ===== RUN BOT ===== #
print("""
╔══════════════════════╗
║   CINDERELLA AI LIVE   ║
╚══════════════════════╝
""")
app.run()
