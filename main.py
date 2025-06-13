import os
import logging
import asyncio
import time
import random
from datetime import datetime, timedelta
import requests
import json
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError
import io
import base64
from PIL import Image

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ZerilBot:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.hf_token = os.getenv('HUGGING_FACE_TOKEN')
        self.owner_username = "ash_yv"
        self.bot_username = "ZERIL"
        
        # Hugging Face API endpoints
        self.hf_api_base = "https://api-inference.huggingface.co/models/"
        self.models = {
            "chat": "microsoft/DialoGPT-medium",
            "sentiment": "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "image": "stabilityai/stable-diffusion-2-1",
            "tts": "espnet/kan-bayashi_ljspeech_vits"
        }
        
        # Jokes database
        self.jokes = [
            "Ek programmer restaurant gaya... Menu dekh ke bola: 'Hello World!' 😂",
            "WhatsApp ne Status feature banaya... Ab sab Facebook ko copy kar rahe hai! 🤪",
            "Coding karte time sabse zyada tension kya hai? 'It works on my machine' 😅",
            "Backend developer frontend dekh ke bola: 'Ye kya tamasha hai!' 🤦‍♂️",
            "Git push karte time dar lagta hai... Kahin kuch break na ho jaye! 😰"
        ]
        
        # Mood emojis
        self.mood_emojis = {
            'happy': '❤️',
            'sad': '😢',
            'angry': '😠',
            'neutral': '😊'
        }

    def get_headers(self):
        return {"Authorization": f"Bearer {self.hf_token}"}

    async def hf_api_call(self, model_name, payload):
        """Make API call to Hugging Face"""
        try:
            url = f"{self.hf_api_base}{self.models[model_name]}"
            response = requests.post(url, headers=self.get_headers(), json=payload, timeout=30)
            return response.json()
        except Exception as e:
            logger.error(f"HF API call failed: {e}")
            return None

    def should_respond(self, message_text, is_mention=False, is_reply=False):
        """Check if bot should respond"""
        triggers = ['zeril', 'ZERIL', '@zeril', f'@{self.bot_username.lower()}']
        return (is_mention or is_reply or 
                any(trigger in message_text.lower() for trigger in triggers) or
                message_text.startswith('/'))

    def get_mood_from_text(self, text):
        """Simple mood detection"""
        happy_words = ['happy', 'good', 'great', 'awesome', 'nice', 'khush', 'accha', 'badhiya']
        sad_words = ['sad', 'bad', 'terrible', 'upset', 'dukhi', 'pareshan', 'bura']
        angry_words = ['angry', 'mad', 'frustrated', 'gussa', 'naraz', 'irritated']
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in happy_words):
            return 'happy'
        elif any(word in text_lower for word in sad_words):
            return 'sad'
        elif any(word in text_lower for word in angry_words):
            return 'angry'
        return 'neutral'

    def generate_hinglish_response(self, user_message, user_name, mood='neutral'):
        """Generate Hinglish response based on context"""
        mood_prefix = self.mood_emojis.get(mood, '😊')
        
        # Owner recognition
        if user_name.lower() == self.owner_username.lower():
            owner_responses = [
                f"{mood_prefix} Ash bhai! Aap aa gaye! Kya haal hai? ✨",
                f"{mood_prefix} Mere creator @{self.owner_username}! Aapka intezaar kar raha tha! 🙏",
                f"{mood_prefix} Boss! Aaj kya kaam hai? Ready hun main! 💪"
            ]
            return random.choice(owner_responses)
        
        # General responses based on mood
        responses = {
            'happy': [
                f"{mood_prefix} Wah bhai! Maja aa gaya sunke! Keep it up! 🎉",
                f"{mood_prefix} Bahut badhiya! Aur batao kya chal raha hai? 😄",
                f"{mood_prefix} Khushi ki baat hai! Share karo apni positivity! ✨"
            ],
            'sad': [
                f"{mood_prefix} Arre yaar, kya hua? Sab theek ho jayega, tension mat lo! 🤗",
                f"{mood_prefix} Don't worry! Mushkil waqt guzar jayega. Main hu na! 💪",
                f"{mood_prefix} Sad mat ho, life mein ups downs aate rehte hai! 🌈"
            ],
            'angry': [
                f"{mood_prefix} Arre bhai, gussa kyu? Chill karo! 😎",
                f"{mood_prefix} Take a deep breath! Sab handle ho jayega! 🧘‍♂️",
                f"{mood_prefix} Anger management karo yaar! Peace! ✌️"
            ],
            'neutral': [
                f"{mood_prefix} Kya baat hai! Kaise ho aap? 😊",
                f"{mood_prefix} Haan bolo, main sun raha hun! 👂",
                f"{mood_prefix} Sup! Kya chal raha hai aaj? 🤔"
            ]
        }
        
        return random.choice(responses.get(mood, responses['neutral']))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        welcome_msg = """
🤖 **ZERIL Bot Activated!** 

Namaste! Main ZERIL hun, tumhara desi Telegram bot! 

**Commands:**
• `/joke` - Funny jokes sunao!
• `/img [prompt]` - Image banao
• `/speak_cow [text]` - Cow ki awaaz mein bolo
• `/flames @user1 @user2` - Love compatibility check
• `/ban @user` - Ban karo (admin only)
• `/admins` - Group admins list

**Special Features:**
- Mera naam mention karo (@ZERIL) ya tag karo to main reply karunga!
- Hinglish mein baat karta hun! 
- Mood ke hisaab se react karta hun!

Made with ❤️ by @ash_yv
        """
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')

    async def joke_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a random joke"""
        await asyncio.sleep(1.2)  # Human-like delay
        joke = random.choice(self.jokes)
        await update.message.reply_text(f"😂 **Joke Time!**\n\n{joke}")

    async def image_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate image using Hugging Face"""
        if not context.args:
            await update.message.reply_text("❗ Prompt dalo yaar! Example: /img sunset over mountains")
            return
            
        prompt = " ".join(context.args)
        # Add Indian style to prompt
        enhanced_prompt = f"Indian style, vibrant colors, {prompt}"
        
        # NSFW filter
        nsfw_words = ['nude', 'naked', 'sexy', 'porn', 'adult']
        if any(word in prompt.lower() for word in nsfw_words):
            await update.message.reply_text("😳 Arey bhai! Family group hai ye! Clean images only! 🙏")
            return
        
        await update.message.reply_text("🎨 Image bana raha hun... Thoda wait karo!")
        
        try:
            result = await self.hf_api_call("image", {"inputs": enhanced_prompt})
            if result and isinstance(result, list) and len(result) > 0:
                # Handle image response (this is simplified - actual implementation would handle bytes)
                await update.message.reply_text(f"✅ Image ready! Prompt: {prompt}\n(Image generation temporarily disabled on free tier)")
            else:
                await update.message.reply_text("😅 Image nahi ban paya! Try again later!")
        except Exception as e:
            await update.message.reply_text("❌ Image generation mein problem! Technical issue hai!")

    async def speak_cow_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Speak like a cow"""
        if not context.args:
            text = "Moooo! Kya baat hai!"
        else:
            text = " ".join(context.args)
        
        cow_response = f"🐄 **Cow Mode Activated!**\nMoooo! {text} Moooo! 🐄"
        await update.message.reply_text(cow_response)

    async def flames_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """FLAMES compatibility game"""
        if len(context.args) < 2:
            await update.message.reply_text("❗ Do names chahiye! Example: /flames @user1 @user2")
            return
        
        name1 = context.args[0].replace('@', '')
        name2 = context.args[1].replace('@', '')
        
        # Generate random compatibility
        compatibility = random.randint(70, 99)
        results = ['Friends', 'Lovers', 'Affection', 'Marriage', 'Enemies', 'Soulmates']
        result = random.choice(results)
        
        flames_msg = f"""
💘 **FLAMES RESULT** 💘

{name1} ❤️ {name2}

**Compatibility: {compatibility}%**
**Result: {result}**

{random.choice([
    "Wah! Perfect match! 🎉",
    "Hmm... interesting chemistry! 😏",
    "Lagta hai pyaar ho gaya! 💕",
    "Shaadi ki taiyari karo! 💒"
])}
        """
        await update.message.reply_text(flames_msg)

    async def ban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ban user (admin only)"""
        if not update.message.from_user.id in [admin.user.id for admin in await context.bot.get_chat_administrators(update.effective_chat.id)]:
            await update.message.reply_text("❌ Sirf admins ban kar sakte hai!")
            return
        
        if not context.args:
            await update.message.reply_text("❗ User mention karo! Example: /ban @username")
            return
        
        await update.message.reply_text(f"🔨 {context.args[0]} banned! (Demo mode - actual ban disabled)")

    async def admins_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List group admins"""
        try:
            admins = await context.bot.get_chat_administrators(update.effective_chat.id)
            admin_list = []
            for admin in admins:
                name = admin.user.first_name
                if admin.user.username:
                    name += f" (@{admin.user.username})"
                admin_list.append(f"👑 {name}")
            
            admin_text = "**Group Admins:**\n" + "\n".join(admin_list)
            await update.message.reply_text(admin_text, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text("❌ Admin list nahi mil paya!")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        message = update.message
        if not message or not message.text:
            return
        
        user_name = message.from_user.first_name or "Friend"
        username = message.from_user.username or ""
        
        # Check if bot should respond
        is_mention = f"@{self.bot_username.lower()}" in message.text.lower()
        is_reply = message.reply_to_message and message.reply_to_message.from_user.is_bot
        
        if not self.should_respond(message.text, is_mention, is_reply):
            return
        
        # Owner recognition
        if "owner" in message.text.lower() or "creator" in message.text.lower() or "banane wala" in message.text.lower():
            await asyncio.sleep(1.2)
            await message.reply_text(f"✨ @{self.owner_username} is my God! Mere creator hai wo! 🙏")
            return
        
        # Generate response
        mood = self.get_mood_from_text(message.text)
        response = self.generate_hinglish_response(message.text, username, mood)
        
        # Add human-like delay
        await asyncio.sleep(1.2)
        await message.reply_text(response)

    def run(self):
        """Run the bot"""
        if not self.bot_token:
            logger.error("BOT_TOKEN not found!")
            return
        
        # Create application
        application = Application.builder().token(self.bot_token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("joke", self.joke_command))
        application.add_handler(CommandHandler("img", self.image_command))
        application.add_handler(CommandHandler("speak_cow", self.speak_cow_command))
        application.add_handler(CommandHandler("flames", self.flames_command))
        application.add_handler(CommandHandler("ban", self.ban_command))
        application.add_handler(CommandHandler("admins", self.admins_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Start bot
        logger.info("ZERIL Bot starting...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    bot = ZerilBot()
    bot.run()
