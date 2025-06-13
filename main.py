import os
import logging
import asyncio
import random
import re
from datetime import datetime
from typing import Optional, Dict, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from diffusers import StableDiffusionPipeline
import requests
import json

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ZerilBot:
    def __init__(self, token: str, hf_token: str):
        self.token = token
        self.hf_token = hf_token
        self.owner_username = "ash_yv"
        
        # Initialize AI models
        self.setup_models()
        
        # Bot personality data
        self.mood_responses = {
            "sad": {
                "prefix": "😢",
                "responses": [
                    "Arey tension mat lo yaar ❤️ Main hoon na tumhare saath!",
                    "Kya hua baby? Zeril se baat karo, sab theek ho jayega 💕",
                    "Sad mat ho, life mein ups and downs aate rehte hain ✨"
                ]
            },
            "angry": {
                "prefix": "🔥", 
                "responses": [
                    "Thanda lo bhai, garmi zyada hai 🔥😂",
                    "Gusse mein decisions mat lo, Zeril kehti hai! 🔥",
                    "Chill karo yaar, anger se kuch nahi hota 😎"
                ]
            },
            "happy": {
                "prefix": "❤️",
                "responses": [
                    "Mast hai yaar! 🔥 Khushi dekh kar mera dil bhi khush ho gaya!",
                    "Yehi spirit chahiye! ❤️ Keep shining baby!",
                    "Happiness is contagious! Tumhari khushi mujhe bhi happy kar deti hai 🥳"
                ]
            }
        }

    def setup_models(self):
        """Initialize AI models"""
        try:
            # Emotion detection model
            self.emotion_classifier = pipeline(
                "text-classification",
                model="bhadresh-savani/distilbert-base-uncased-emotion",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Language detection
            self.lang_detector = pipeline(
                "text-classification",
                model="papluca/xlm-roberta-base-language-detection",
                device=0 if torch.cuda.is_available() else -1
            )
            
            logger.info("✅ AI models loaded successfully!")
            
        except Exception as e:
            logger.error(f"❌ Model loading failed: {e}")
            self.emotion_classifier = None
            self.lang_detector = None

    def detect_emotion(self, text: str) -> str:
        """Detect emotion from text"""
        if not self.emotion_classifier:
            return "happy"
            
        try:
            result = self.emotion_classifier(text)
            emotion = result[0]['label'].lower()
            
            # Map emotions to our mood system
            if emotion in ['sadness', 'fear', 'disgust']:
                return "sad"
            elif emotion in ['anger']:
                return "angry"
            else:
                return "happy"
                
        except Exception as e:
            logger.error(f"Emotion detection error: {e}")
            return "happy"

    def detect_language(self, text: str) -> str:
        """Detect language of input text"""
        if not self.lang_detector:
            return "en"
            
        try:
            result = self.lang_detector(text)
            return result[0]['label']
        except:
            return "en"

    def should_respond(self, text: str) -> bool:
        """Check if bot should respond to message"""
        triggers = [
            "@zerilll_bot",
            "zeril",
            "ZERIL",
            "/",
        ]
        
        text_lower = text.lower()
        return any(trigger.lower() in text_lower for trigger in triggers)

    def generate_response(self, text: str, emotion: str) -> str:
        """Generate contextual response based on emotion"""
        mood_data = self.mood_responses.get(emotion, self.mood_responses["happy"])
        
        # Check for owner mention
        if self.owner_username.lower() in text.lower():
            return f"❤️ Mera creator? Bilkul! @{self.owner_username} ne mujhe banaya hai 🎉 (PS: Wo bohot awesome hai!)"
        
        # Generate response
        base_response = random.choice(mood_data["responses"])
        
        # Add contextual elements
        if "help" in text.lower() or "madad" in text.lower():
            base_response += " Batao kya chahiye? Main yahan hoon! 🤖"
        
        return base_response

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_name = update.effective_user.first_name
        
        welcome_text = f"""
❤️ **Namaste {user_name}! Main ZERIL hoon!** 

🤖 **About Me:**
• Tumhari friendly AI assistant
• Created by @{self.owner_username} 
• Hinglish mein baat karti hoon
• Emotional support deti hoon

🔥 **Meri Powers:**
• `/joke` - Funny jokes sunata hoon
• `/riddle` - Riddles deta hoon  
• `/image` - AI images banata hoon
• `/mood` - Tumhara mood check karta hoon
• `/help` - Complete command list

💕 **How to Talk:**
Just mention "ZERIL" ya tag karo @zerilll_bot
Main samjh jaunga tumhara mood aur response dunga!

Ready to chat? Kya haal chaal? 😸
        """
        
        keyboard = [
            [InlineKeyboardButton("🔥 Commands", callback_data="commands")],
            [InlineKeyboardButton("❤️ About Creator", callback_data="creator")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🤖 **ZERIL - Command List**

**🎯 Basic Commands:**
• `/start` - Welcome message
• `/help` - Ye message
• `/mood` - Mood check karta hoon
• `/status` - Bot status

**🎮 Fun Commands:**
• `/joke` - Random joke
• `/riddle` - Brain teasers
• `/quote` - Motivational quotes
• `/compliment` - Tareef karta hoon

**🎨 Creative Commands:**
• `/image [prompt]` - AI image generate
• `/story` - Random story

**💬 Chat Features:**
• Mention "ZERIL" for responses
• Tag @zerilll_bot 
• Emotional support (sad/angry/happy)
• Hinglish conversations

**👑 Owner:** @ash_yv

Koi problem? Just type "ZERIL help me!" 😊
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def joke_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /joke command"""
        jokes = [
            "😂 Teacher: Tumhara homework kahan hai?\nStudent: Sir, dog ne kha liya!\nTeacher: Tumhare paas dog kahan se aaya?\nStudent: Sir, homework ke liye adopt kiya tha! 🐕",
            
            "🤣 Beta: Papa, main engineer banna chahta hoon!\nPapa: Beta, pehle 12th pass kar!\nBeta: Papa, main software engineer banna chahta hoon!\nPapa: Oh, to fir 10th bhi zaruri nahi! 💻",
            
            "😆 Friend: Bro, tumhara WiFi password kya hai?\nMe: Password123\nFriend: Capital P?\nMe: Nahi bro, sab small letters mein! 📶",
            
            "🤭 Girlfriend: Tum mujhse pyaar karte ho?\nBoyfriend: Jitna free fire se karta hoon!\nGirlfriend: Aww, itna?\nBoyfriend: Haan, sirf free time mein! 🎮"
        ]
        
        joke = random.choice(jokes)
        await update.message.reply_text(f"🔥 ZERIL ka joke time!\n\n{joke}")

    async def riddle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /riddle command"""
        riddles = [
            {
                "question": "🧩 Main hoon but dikhta nahi, sab jagah hoon but milta nahi. Kya hoon main?",
                "answer": "Hawa (Air)"
            },
            {
                "question": "🤔 Jitna khaooge utna badhega, lekin jitna doge utna kam hoga. Kya hai?",
                "answer": "Gyan (Knowledge)"
            },
            {
                "question": "🔍 Raat ko aata hoon, din mein chala jata hoon. Ujala dekh kar darr jata hoon. Kaun hoon?",
                "answer": "Andhera (Darkness)"
            }
        ]
        
        riddle = random.choice(riddles)
        
        keyboard = [[InlineKeyboardButton("🔓 Answer Dikhao", callback_data=f"answer_{riddles.index(riddle)}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🧠 **ZERIL ka Brain Teaser:**\n\n{riddle['question']}\n\nSoch kar batao! 🤓",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def mood_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /mood command"""
        user_name = update.effective_user.first_name
        
        # Simulate mood analysis
        moods = ["happy", "excited", "thoughtful", "energetic", "creative", "chill"]
        current_mood = random.choice(moods)
        
        mood_responses = {
            "happy": f"❤️ {user_name}, tumhara mood bilkul mast hai! Khushi ka vibe aa raha hai! 🌟",
            "excited": f"🔥 {user_name}, excitement level maximum hai! Energy bohot high hai! ⚡",
            "thoughtful": f"🤔 {user_name}, aaj kuch deep thoughts chal rahe hain. Philosopher mode on! 💭",
            "energetic": f"⚡ {user_name}, energy levels peak pe hain! Ready to conquer the world! 🚀",
            "creative": f"🎨 {user_name}, creative vibes strong hain! Kuch artistic karne ka mood hai! ✨",
            "chill": f"😎 {user_name}, super chill and relaxed hai. Perfect zen mode! 🧘‍♀️"
        }
        
        response = mood_responses.get(current_mood, mood_responses["happy"])
        await update.message.reply_text(response)

    async def image_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /image command"""
        if not context.args:
            await update.message.reply_text(
                "🎨 Image banane ke liye prompt do!\n\nExample: `/image beautiful sunset over mountains`"
            )
            return
        
        prompt = " ".join(context.args)
        
        # Send processing message
        processing_msg = await update.message.reply_text("🎨 ZERIL image bana rahi hai... Wait karo! ⏳")
        
        try:
            # Use Hugging Face API for image generation (free tier)
            response = await self.generate_image_hf(prompt)
            
            if response:
                await update.message.reply_photo(
                    photo=response,
                    caption=f"🔥 **ZERIL ne banaya!**\n\n**Prompt:** {prompt}\n\n*Created by @{self.owner_username}'s ZERIL* ❤️",
                    parse_mode='Markdown'
                )
                await processing_msg.delete()
            else:
                await processing_msg.edit_text("😅 Sorry! Image generation mein problem aa gayi. Thodi der baad try karo!")
                
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            await processing_msg.edit_text("😅 Technical issue! @ash_yv se kehna padega fix karne ke liye! 🔧")

    async def generate_image_hf(self, prompt: str) -> Optional[str]:
        """Generate image using Hugging Face API"""
        try:
            API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            
            payload = {"inputs": prompt}
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"HF API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return None

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        if not update.message or not update.message.text:
            return
            
        text = update.message.text
        user_name = update.effective_user.first_name
        
        # Check if should respond
        if not self.should_respond(text):
            return
        
        # Add thinking delay for realism
        await asyncio.sleep(1)
        
        # Detect emotion and generate response
        emotion = self.detect_emotion(text)
        response = self.generate_response(text, emotion)
        
        # Send response
        await update.message.reply_text(response)

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button presses"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "commands":
            await query.message.reply_text("Use `/help` command for complete list! 🤖")
            
        elif query.data == "creator":
            await query.message.reply_text(
                f"👑 **ZERIL ki Creator**\n\n"
                f"@{self.owner_username} - The mastermind behind me! 🧠\n"
                f"Bilkul awesome developer hai! 🔥❤️"
            )
            
        elif query.data.startswith("answer_"):
            riddles = [
                "Hawa (Air) - Invisible but everywhere! 💨",
                "Gyan (Knowledge) - Share karne se badhta hai! 📚", 
                "Andhera (Darkness) - Light se dar lagta hai! 🌙"
            ]
            
            riddle_index = int(query.data.split("_")[1])
            if riddle_index < len(riddles):
                await query.message.reply_text(f"✅ **Answer:** {riddles[riddle_index]}")

    def run(self):
        """Start the bot"""
        application = Application.builder().token(self.token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("joke", self.joke_command))
        application.add_handler(CommandHandler("riddle", self.riddle_command))
        application.add_handler(CommandHandler("mood", self.mood_command))
        application.add_handler(CommandHandler("image", self.image_command))
        application.add_handler(CallbackQueryHandler(self.button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        logger.info("🚀 ZERIL Bot is starting...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    # Get tokens from environment variables
    BOT_TOKEN = os.getenv("BOT_TOKEN", "8092570026:AAHB4aPVGF4frTsm3SXPk_Xv3mLIcg6KHYM")
    HF_TOKEN = os.getenv("HF_TOKEN", "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")
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found!")
        return
    
    # Create and run bot
    bot = ZerilBot(BOT_TOKEN, HF_TOKEN)
    bot.run()

if __name__ == "__main__":
    main()
