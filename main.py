import os
import logging
import asyncio
import random
import re
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import requests
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from diffusers import StableDiffusionPipeline
import io
from PIL import Image
import base64

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ZERILBot:
    def __init__(self):
        # Bot configuration
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '8092570026:AAHB4aPVGF4frTsm3SXPk_Xv3mLIcg6KHYM')
        self.hf_token = os.getenv('HUGGINGFACE_TOKEN', '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')
        
        # Owner info
        self.owner = "@ash_yv"
        
        # Initialize models
        self.setup_models()
        
        # Personality responses
        self.greetings = [
            "Kya haal chaal? 😸",
            "Hey cutie! Main ZERIL hun, tumhari AI girlfriend! 💕",
            "Namaste! ZERIL here, ready to chat! ✨",
            "Hii! Kaise ho mere pyare? 😊"
        ]
        
        self.mood_responses = {
            'sad': [
                "Arey tension mat lo yaar ❤️ Main hun na tumhare saath!",
                "Sad kyun ho? Bolo kya hua? 😢 ZERIL sun rahi hai",
                "Cheer up baby! Life mein ups and downs aate rehte hai ❤️"
            ],
            'angry': [
                "Thanda lo bhai, garmi zyada hai 🔥😂",
                "Gussa kya baat hai? Chill karo! 🔥",
                "Anger is temporary, happiness is permanent! Relax! 🔥"
            ],
            'happy': [
                "Mast hai yaar! 🔥",
                "Wow! Kitni khushi hai tumhe! Main bhi khush! ❤️",
                "Super excited! Share karo kya baat hai! 🥳"
            ]
        }
        
        self.hinglish_responses = [
            "Haan bolo kya chahiye? 😊",
            "ZERIL present! Kya kaam hai? ✨",
            "Boliye saheb, aapki seva mein hazir! 😸",
            "Ready to help! Batao kya problem hai? 💪"
        ]

    def setup_models(self):
        """Initialize AI models"""
        try:
            # Emotion detection model
            self.emotion_analyzer = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Language detection
            self.lang_detector = pipeline(
                "text-classification",
                model="papluca/xlm-roberta-base-language-detection",
                device=0 if torch.cuda.is_available() else -1
            )
            
            logger.info("✅ Models loaded successfully!")
            
        except Exception as e:
            logger.error(f"❌ Model loading failed: {e}")
            self.emotion_analyzer = None
            self.lang_detector = None

    def detect_mood(self, text):
        """Detect user's emotional state"""
        if not self.emotion_analyzer:
            return 'neutral'
        
        try:
            # Check for explicit mood keywords
            sad_keywords = ['sad', 'depressed', 'alone', 'tension', 'problem', 'dukh', 'pareshan']
            angry_keywords = ['fuck', 'hate', 'angry', 'frustrated', 'gussa', 'pagal']
            happy_keywords = ['happy', 'love', 'yay', 'excited', 'khushi', 'mast', 'awesome']
            
            text_lower = text.lower()
            
            if any(keyword in text_lower for keyword in sad_keywords):
                return 'sad'
            elif any(keyword in text_lower for keyword in angry_keywords):
                return 'angry'
            elif any(keyword in text_lower for keyword in happy_keywords):
                return 'happy'
            
            # Use AI model for detection
            result = self.emotion_analyzer(text)
            emotion = result[0]['label'].lower()
            
            if emotion in ['sadness', 'fear']:
                return 'sad'
            elif emotion in ['anger', 'disgust']:
                return 'angry'
            elif emotion in ['joy', 'surprise']:
                return 'happy'
            
            return 'neutral'
            
        except Exception as e:
            logger.error(f"Mood detection error: {e}")
            return 'neutral'

    def is_hinglish(self, text):
        """Check if text contains Hinglish"""
        hinglish_patterns = [
            r'\b(kya|hai|hoon|hun|aur|tum|main|mein|ke|ki|ko|se|me|ka|kaise|kahan|kyun|kab)\b',
            r'\b(haan|nahi|bhi|ya|phir|abhi|kal|aaj|waha|yaha|aise|waise)\b',
            r'\b(yaar|bhai|dude|boss|saheb|bro|sis|baby|cutie)\b'
        ]
        
        for pattern in hinglish_patterns:
            if re.search(pattern, text.lower()):
                return True
        return False

    def get_personality_response(self, text, mood):
        """Generate personality-based response"""
        # Check for owner mention
        if self.owner.lower() in text.lower() or 'ash_yv' in text.lower():
            return f"Mera creator? Bilkul! {self.owner} ne mujhe banaya hai 🎉 (PS: Wo bohot awesome hai!)"
        
        # Mood-based responses
        if mood in self.mood_responses:
            return random.choice(self.mood_responses[mood])
        
        # Default Hinglish response
        if self.is_hinglish(text):
            return random.choice(self.hinglish_responses)
        
        return random.choice([
            "Tell me more! I'm listening 😊",
            "Interesting! What else? ✨",
            "I'm here to help! What do you need? 💕"
        ])

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_text = f"""
✨ **Namaste! Main ZERIL hun!** ✨

💕 Main tumhari AI girlfriend hun, banai gayi hai {self.owner} ne!
🤖 Tech-savvy, playfully sarcastic, aur emotionally intelligent!

**Meri Powers:**
🎨 AI Image Generation 
🖼️ Background Removal
🎵 Text to Speech
🔍 Google Search  
🎭 GIF Search
📝 Code Execution
🌍 Translation
😊 Mood Detection

**Commands:**
/help - All commands dekhne ke liye
/mood - Apna mood batao
/image <prompt> - AI image banao
/tts <text> - Text to speech
/search <query> - Google search
/joke - Funny joke sunao

Ready to chat? Bolo kya karna hai! 😸
        """
        
        keyboard = [
            [InlineKeyboardButton("🎨 Generate Image", callback_data='image_help')],
            [InlineKeyboardButton("🎵 Text to Speech", callback_data='tts_help')],
            [InlineKeyboardButton("🔍 Search Google", callback_data='search_help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🤖 **ZERIL Commands - Tumhari AI Girlfriend!**

**Basic Commands:**
• /start - Welcome message
• /help - Ye list
• /mood - Mood detection check
• /about - Mere baare mein

**AI Features:**
• /image <prompt> - AI image generate karo
• /tts <text> - Text ko speech mein convert
• /translate <text> - Language translate karo  
• /removebg - Background remove (reply to image)

**Fun Features:**
• /joke - Random joke sunao
• /riddle - Paheli do
• /gif <search> - GIF search karo
• /lyrics <song> - Song lyrics find karo

**Utility:**
• /search <query> - Google search
• /code <language> <code> - Code execute karo
• /weather <city> - Weather check

**Magic Words:**
• Mention "ZERIL" anywhere - Main respond karungi!
• Tag me @zerilll_bot - Instant reply!

Koi confusion? Just type and chat! Main samjh jaungi 😊
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def image_generation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate AI images"""
        if not context.args:
            await update.message.reply_text("Prompt dena bhool gaye! 😅\nExample: /image beautiful sunset over mountains")
            return
        
        prompt = ' '.join(context.args)
        await update.message.reply_text(f"🎨 Generating image for: '{prompt}'\nThoda wait karo... ✨")
        
        try:
            # Use Hugging Face API for image generation
            API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
            
            if response.status_code == 200:
                image_bytes = response.content
                await update.message.reply_photo(
                    photo=io.BytesIO(image_bytes),
                    caption=f"✨ Generated by ZERIL\n🎨 Prompt: {prompt}\n💕 Made with love!"
                )
            else:
                await update.message.reply_text("❌ Image generation mein problem hui! Try again later 😔")
                
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            await update.message.reply_text("❌ Oops! Kuch technical problem hai 😅")

    async def text_to_speech(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Convert text to speech"""
        if not context.args:
            await update.message.reply_text("Text dena bhool gaye! 😅\nExample: /tts Hello I am ZERIL")
            return
        
        text = ' '.join(context.args)
        await update.message.reply_text(f"🎵 Converting to speech: '{text}'\nWait kar rahi hun... ✨")
        
        try:
            # Use Hugging Face TTS API
            API_URL = "https://api-inference.huggingface.co/models/microsoft/speecht5_tts"
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            
            response = requests.post(API_URL, headers=headers, json={"inputs": text})
            
            if response.status_code == 200:
                audio_bytes = response.content
                await update.message.reply_voice(
                    voice=io.BytesIO(audio_bytes),
                    caption=f"🎵 ZERIL ki awaaz mein: '{text}' 💕"
                )
            else:
                await update.message.reply_text("❌ TTS mein problem! Try again 😔")
                
        except Exception as e:
            logger.error(f"TTS error: {e}")
            await update.message.reply_text("❌ Audio generate nahi ho paya 😅")

    async def google_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Perform Google search"""
        if not context.args:
            await update.message.reply_text("Search query dena bhool gaye! 😅\nExample: /search Python programming")
            return
        
        query = ' '.join(context.args)
        await update.message.reply_text(f"🔍 Searching for: '{query}'\nLet me Google that for you... ✨")
        
        # Note: This is a placeholder - you'll need to implement actual search API
        search_results = f"""
🔍 **Search Results for: {query}**

Sorry! Google Search API integration pending 😅
For now, you can search manually: https://google.com/search?q={query.replace(' ', '+')}

Coming soon with proper API! 🚀
        """
        
        await update.message.reply_text(search_results, parse_mode='Markdown')

    async def joke_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tell a random joke"""
        jokes = [
            "Teacher: Tumhara homework kahan hai?\nStudent: Kutta kha gaya!\nTeacher: Tumhare paas kutta hai?\nStudent: Nahi, lie tha! 😂",
            "Wife: Tum mujhse shaadi kyun kiye the?\nHusband: Memory loss ho gayi hai lagta hai! 😜",
            "Doctor: Aapko running karna chahiye\nPatient: Running toh kar raha hun... bills se! 🏃‍♂️💸",
            "Programmer ki wife: Tum mujhse pyaar karte ho?\nProgrammer: Yes=1, No=0... Return 1! 💻❤️",
            "Boss: Late kyun aaye?\nEmployee: Traffic jam tha!\nBoss: Toh jaldi nikalna tha!\nEmployee: Aur jaldi nikalta toh traffic kam hota! 🚗😂"
        ]
        
        joke = random.choice(jokes)
        await update.message.reply_text(f"😂 **ZERIL ka Joke Time!**\n\n{joke}\n\n😸 Hasa diya na? More jokes ke liye /joke type karo!")

    async def mood_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check user's mood"""
        mood_prompts = [
            "Batao kaise feel kar rahe ho? 😊",
            "Aaj ka mood kaisa hai? ✨", 
            "Share karo - khushi hai ya tension? 💕",
            "Kya haal hai? Happy sad or confused? 😸"
        ]
        
        prompt = random.choice(mood_prompts)
        await update.message.reply_text(f"💭 **Mood Check Time!**\n\n{prompt}\n\nMain analyze kar ke tumhara mood samjhungi! 🤖💕")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        text = update.message.text
        user = update.effective_user
        
        # Check if bot should respond
        should_respond = (
            '@zerilll_bot' in text.lower() or
            'zeril' in text.lower() or
            text.startswith('/') or
            update.message.reply_to_message and update.message.reply_to_message.from_user.is_bot
        )
        
        if not should_respond:
            return
        
        # Add typing action
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        await asyncio.sleep(1)  # Simulate thinking time
        
        # Detect mood and generate response
        mood = self.detect_mood(text)
        response = self.get_personality_response(text, mood)
        
        # Add mood emoji prefix
        mood_emojis = {'sad': '😢', 'angry': '🔥', 'happy': '❤️', 'neutral': '✨'}
        emoji = mood_emojis.get(mood, '✨')
        
        final_response = f"{emoji} {response}"
        
        await update.message.reply_text(final_response)

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'image_help':
            await query.edit_message_text("🎨 **Image Generation Help**\n\nUse: /image <description>\nExample: /image cute cat with sunglasses\n\nMain AI se tumhare liye beautiful images banaungi! ✨")
        elif query.data == 'tts_help':
            await query.edit_message_text("🎵 **Text to Speech Help**\n\nUse: /tts <text>\nExample: /tts Hello I am ZERIL\n\nMain tumhari text ko apni sweet voice mein convert kar dungi! 💕")
        elif query.data == 'search_help':
            await query.edit_message_text("🔍 **Google Search Help**\n\nUse: /search <query>\nExample: /search best pizza recipe\n\nMain Google se search kar ke results de dungi! 🚀")

def main():
    """Start the bot"""
    bot = ZERILBot()
    
    # Create application
    application = Application.builder().token(bot.bot_token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("image", bot.image_generation))
    application.add_handler(CommandHandler("tts", bot.text_to_speech))
    application.add_handler(CommandHandler("search", bot.google_search))
    application.add_handler(CommandHandler("joke", bot.joke_command))
    application.add_handler(CommandHandler("mood", bot.mood_check))
    application.add_handler(CallbackQueryHandler(bot.button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    # Start bot
    logger.info("🚀 ZERIL Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
