import os
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import json
import random
from datetime import datetime
import time

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class ZerilBot:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.hf_token = os.getenv('HUGGINGFACE_TOKEN')  # Free tier token
        self.owner_username = "ash_yv"  # Your username
        self.owner_name = "Ash"
        self.bot_name = "ZERIL"
        
        # Lightweight models for free tier
        self.models = {
            "chat": "microsoft/DialoGPT-small",  # Only 117MB
            "sentiment": "cardiffnlp/twitter-roberta-base-sentiment-latest",  # 50MB
            "translate": "Helsinki-NLP/opus-mt-hi-en"  # 300MB
        }
        
        # Response delay for human-like behavior
        self.response_delay = 1.2
        
        # Mood emojis
        self.mood_emojis = {
            'happy': '❤️',
            'sad': '😢', 
            'angry': '😠',
            'neutral': '😊'
        }
        
        # Hinglish responses
        self.hinglish_responses = {
            'greeting': [
                "Namaste! Kaise ho aap? 🙏",
                "Arre waah! Aaj kya haal hai? 😊",
                "Hello ji! Kya chalra hai? 👋"
            ],
            'owner_praise': [
                "Mere creator @ash_yv toh ekdum jhakaas hai! Unhone mujhe itni mehnat se banaya 🎉",
                "Agar main achhi hu toh sab @ash_yv ki wajah se! 🙏",
                "@ash_yv is my God! Unke bina main kuch bhi nahi ✨"
            ],
            'jokes': [
                "Ek programmer restaurant gaya... Menu dekh ke bola: 'Hello World!' 😂",
                "WhatsApp ka status dekh ke... Lagta hai sabko philosopher ban na hai! 🤪",
                "Mummy: Beta coding seekh lo! Beta: Mummy main already bug-free hu! 🐛"
            ],
            'sarcastic': [
                "Wah bhai wah! Bohot smart ho aap toh 🤓",
                "Haan haan... bilkul genius lagre ho 😏",
                "Arre waah! Aaj kya gyaan pela hai aapne 🙄"
            ]
        }

    async def should_respond(self, message_text: str, chat_type: str) -> bool:
        """Check if bot should respond based on activation rules"""
        message_lower = message_text.lower()
        
        # Always respond to commands
        if message_text.startswith('/'):
            return True
            
        # Respond when tagged or name mentioned
        if any(trigger in message_lower for trigger in ['@zeril', 'zeril', self.bot_name.lower()]):
            return True
            
        # In private chats, respond to everything
        if chat_type == 'private':
            return True
            
        return False

    def get_mood_from_text(self, text: str) -> str:
        """Simple mood detection based on keywords"""
        text_lower = text.lower()
        
        happy_words = ['happy', 'khush', 'achha', 'good', 'great', 'amazing', 'lol', 'haha']
        sad_words = ['sad', 'dukh', 'upset', 'cry', 'ro', 'pareshan', 'problem']
        angry_words = ['angry', 'gussa', 'mad', 'hate', 'stupid', 'bewakoof']
        
        if any(word in text_lower for word in happy_words):
            return 'happy'
        elif any(word in text_lower for word in sad_words):
            return 'sad'
        elif any(word in text_lower for word in angry_words):
            return 'angry'
        else:
            return 'neutral'

    def generate_hinglish_response(self, user_input: str, mood: str) -> str:
        """Generate contextual Hinglish responses"""
        input_lower = user_input.lower()
        
        # Owner recognition
        if any(word in input_lower for word in ['owner', 'creator', 'maalik', 'banane wala', 'who made you']):
            return random.choice(self.hinglish_responses['owner_praise'])
        
        # Greetings
        if any(word in input_lower for word in ['hello', 'hi', 'namaste', 'hey', 'kaise ho']):
            return random.choice(self.hinglish_responses['greeting'])
        
        # Jokes request
        if any(word in input_lower for word in ['joke', 'funny', 'hasao', 'comedy']):
            return random.choice(self.hinglish_responses['jokes'])
        
        # Mood-based responses
        if mood == 'sad':
            return "Arre yaar! Tension mat lo... Sab theek ho jayega 😢 Main hun na tumhare saath!"
        elif mood == 'angry':
            return "Gussa kyu ho? Chill karo bhai! 😠 Batao kya problem hai?"
        elif mood == 'happy':
            return "Wah! Khushi ki baat hai! ❤️ Main bhi happy hu ab!"
        
        # Default sarcastic response
        return random.choice(self.hinglish_responses['sarcastic'])

    async def hf_api_call(self, model_name: str, payload: dict) -> dict:
        """Make API call to Hugging Face (free tier optimized)"""
        try:
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            url = f"https://api-inference.huggingface.co/models/{model_name}"
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 503:
                # Model is loading, wait and retry
                await asyncio.sleep(20)
                response = requests.post(url, headers=headers, json=payload, timeout=15)
            
            return response.json()
        except Exception as e:
            logger.error(f"HF API call failed: {e}")
            return {"error": str(e)}

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await asyncio.sleep(self.response_delay)
        
        welcome_msg = f"""
🚀 **ZERIL BOT ACTIVATED!**

Namaste! Main ZERIL hu, tumhara naya Hinglish dost! 🙏

**Kaise use karu?**
• Mera naam lo: "ZERIL kya hal hai?"
• Tag karo: @ZERIL 
• Commands use karo: /help

**Mere creator:** @{self.owner_username} (Ash bhai) ✨

Chalo, baat karte hai! 😊
        """
        
        keyboard = [[InlineKeyboardButton("🎯 Commands", callback_data='help')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        await asyncio.sleep(self.response_delay)
        
        help_text = """
🎯 **ZERIL COMMANDS**

**🛡️ MODERATION:**
/ban [user] [time] - Ban karo
/mute [user] [time] - Mute karo  
/admins - Admin list

**🎉 ENTERTAINMENT:**
/joke - Funny jokes
/speak_cow [text] - Cow style
/speak_pony [text] - Pony style

**⚙️ UTILITIES:**
/img [prompt] - Image generate
/tts [text] - Voice message
/run [code] - Code execute

**❤️ SPECIAL:**
/flames @user1 @user2 - Love calculator
/setbio [text] - Bio set karo

**Bas mera naam lo aur main aa jaunga! 😊**
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def joke_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /joke command"""
        await asyncio.sleep(self.response_delay)
        joke = random.choice(self.hinglish_responses['jokes'])
        await update.message.reply_text(joke)

    async def img_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /img command"""
        if not context.args:
            await update.message.reply_text("Arre bhai! Kya banana hai batao!\nExample: /img beautiful sunset")
            return
        
        prompt = " ".join(context.args)
        
        # Add Indian style to prompt
        enhanced_prompt = f"Indian style, vibrant colors, {prompt}, high quality, detailed"
        
        await update.message.reply_text("🎨 Image bana raha hu... Thoda wait karo!")
        
        try:
            payload = {"inputs": enhanced_prompt}
            result = await self.hf_api_call("runwayml/stable-diffusion-v1-5", payload)
            
            if "error" in result:
                await update.message.reply_text("😅 Sorry yaar! Image nahi ban pai. Kuch aur try karo!")
            else:
                await update.message.reply_text("🎉 Ye lo tumhara image!")
                
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            await update.message.reply_text("🤖 Technical problem hai! @ash_yv ko batao!")

    async def flames_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /flames command"""
        if len(context.args) < 2:
            await update.message.reply_text("Arre! Do naam chahiye!\nExample: /flames @user1 @user2")
            return
        
        user1, user2 = context.args[0], context.args[1]
        compatibility = random.randint(60, 99)
        
        await asyncio.sleep(self.response_delay)
        
        result = f"""
💘 **FLAMES RESULT**

{user1} ❤️ {user2}

**Compatibility: {compatibility}%**

{self.get_flames_message(compatibility)}
        """
        
        await update.message.reply_text(result, parse_mode='Markdown')

    def get_flames_message(self, score: int) -> str:
        """Get FLAMES message based on score"""
        if score >= 90:
            return "🔥 Perfect match! Shaadi kab hai? 💒"
        elif score >= 80:
            return "💕 Bohot achha compatibility! Love birds lag rahe ho!"
        elif score >= 70:
            return "😊 Good match! Thoda aur time do relationship ko!"
        else:
            return "🤔 Hmm... Friends better rahenge shayad!"

    async def speak_animal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /speak_cow and /speak_pony commands"""
        command = update.message.text.split()[0][1:]  # Remove /
        
        if not context.args:
            await update.message.reply_text("Kya bolana hai? Text dalo!")
            return
        
        text = " ".join(context.args)
        
        await asyncio.sleep(self.response_delay)
        
        if command == "speak_cow":
            response = f"🐄 Moooo! {text}"
        elif command == "speak_pony":
            response = f"🐴 Neigh! {text}"
        else:
            response = f"🗣️ {text}"
        
        await update.message.reply_text(response)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        if not update.message or not update.message.text:
            return
            
        message_text = update.message.text
        chat_type = update.message.chat.type
        user = update.message.from_user
        
        # Check if should respond
        if not await self.should_respond(message_text, chat_type):
            return
        
        # Special handling for owner
        if user.username == self.owner_username:
            await asyncio.sleep(self.response_delay)
            await update.message.reply_text("🙏 Namaste Ash bhai! Aapka ZERIL hazir hai! Kya kaam hai?")
            return
        
        # Get mood and generate response
        mood = self.get_mood_from_text(message_text)
        mood_emoji = self.mood_emojis.get(mood, '😊')
        
        response = self.generate_hinglish_response(message_text, mood)
        
        # Add mood emoji prefix
        final_response = f"{mood_emoji} {response}"
        
        await asyncio.sleep(self.response_delay)
        await update.message.reply_text(final_response)

    def run(self):
        """Run the bot"""
        app = Application.builder().token(self.bot_token).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("joke", self.joke_command))
        app.add_handler(CommandHandler("img", self.img_command))
        app.add_handler(CommandHandler("flames", self.flames_command))
        app.add_handler(CommandHandler("speak_cow", self.speak_animal_command))
        app.add_handler(CommandHandler("speak_pony", self.speak_animal_command))
        
        # Message handler (must be last)
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Start bot
        print("🚀 ZERIL BOT STARTING...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = ZerilBot()
    bot.run()
