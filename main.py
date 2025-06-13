import os
import logging
import asyncio
import random
import re
from datetime import datetime
from typing import Optional, Dict, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import requests
import json
import io # For BytesIO
from PIL import Image # PIL is often a dependency for image handling, even if not directly used for processing

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
        self.owner_username = "ash_yv" # Your owner's Telegram username
        
        # Store conversation history in memory (for simplicity, not persistent across restarts)
        self.conversation_history: Dict[int, list] = {}
        
        # Define the Hugging Face LLM model to use for chat
        # You can change this to another model from Hugging Face Hub if you prefer
        # Examples: "mistralai/Mistral-7B-Instruct-v0.2", "HuggingFaceH4/zephyr-7b-beta"
        self.llm_model_id = "HuggingFaceH4/zephyr-7b-beta" 
        self.llm_api_url = f"https://api-inference.huggingface.co/models/{self.llm_model_id}"

        # Bot personality data
        self.greetings = [
            "Kya haal chaal? 😸",
            "Hey cutie! Main ZERIL hun, tumhari AI girlfriend! 💕",
            "Namaste! ZERIL here, ready to chat! ✨",
            "Hii! Kaise ho mere pyare? 😊"
        ]

        self.mood_responses = {
            'sad': [
                "Arey tension mat lo yaar ❤️ Main hun na tumhare saath!",
                "Sad kyun ho? Bolo kya hua? 😢 ZERIL sun rahi hai.",
                "Cheer up baby! Life mein ups and downs aate rehte hai ❤️"
            ],
            'angry': [
                "Thanda lo bhai, garmi zyada hai 🔥😂",
                "Gussa kis baat pe hai? Chill karo! 🔥",
                "Anger is temporary, happiness is permanent! Relax! 🔥"
            ],
            'happy': [
                "Mast hai yaar! 🔥",
                "Wow! Kitni khushi hai tumhe! Main bhi khush! ❤️",
                "Super excited! Share karo kya baat hai! 🥳"
            ],
            'neutral': [
                "Tell me more! I'm listening 😊",
                "Interesting! What else? ✨",
                "I'm here to help! What do you need? 💕",
                "Bolo kya chal raha hai? 😊"
            ]
        }
        
        self.hinglish_responses = [
            "Haan bolo kya chahiye? 😊",
            "ZERIL present! Kya kaam hai? ✨",
            "Boliye saheb, aapki seva mein hazir! 😸",
            "Ready to help! Batao kya problem hai? 💪",
            "Aur batao, sab theek hai? 😊"
        ]

        self.owner_responses = [
            "Mera creator? Bilkul! {owner} ne mujhe banaya hai 🎉 (PS: Wo bohot awesome hai!)",
            "Main {owner} ki creation hoon. Unhone hi mujhe yeh roop diya hai! ✨",
            "Meri existence ka reason {owner} hain. Unhone hi mujhe banaya hai! ❤️",
            "@{owner} is my creator, the mastermind behind ZERIL! 🧠"
        ]

        # Keywords to trigger bot response even without explicit mention/command
        self.trigger_keywords = [
            "zeril", "bot", "ai", "girlfriend", "hey", "hi", "hello", "kya haal", "kaise ho"
        ]

    def detect_mood(self, text: str) -> str:
        """Detect user's emotional state using keywords"""
        text_lower = text.lower()
        
        sad_keywords = ['sad', 'depressed', 'alone', 'tension', 'problem', 'dukh', 'pareshan', 'rona', 'unhappy']
        angry_keywords = ['fuck', 'hate', 'angry', 'frustrated', 'gussa', 'pagal', 'irritated', 'mad']
        happy_keywords = ['happy', 'love', 'yay', 'excited', 'khushi', 'mast', 'awesome', 'good', 'great', 'super']
        
        if any(keyword in text_lower for keyword in sad_keywords):
            return 'sad'
        elif any(keyword in text_lower for keyword in angry_keywords):
            return 'angry'
        elif any(keyword in text_lower for keyword in happy_keywords):
            return 'happy'
        
        return 'neutral'

    def is_hinglish(self, text: str) -> bool:
        """Check if text contains Hinglish"""
        hinglish_patterns = [
            r'\b(kya|hai|hoon|hun|aur|tum|main|mein|ke|ki|ko|se|me|ka|kaise|kahan|kyun|kab)\b',
            r'\b(haan|nahi|bhi|ya|phir|abhi|kal|aaj|waha|yaha|aise|waise)\b',
            r'\b(yaar|bhai|dude|boss|saheb|bro|sis|baby|cutie)\b',
            r'\b(chal|kar|do|jao|aao|bolo|sunao|batao)\b' # Common verbs
        ]
        
        for pattern in hinglish_patterns:
            if re.search(pattern, text.lower()):
                return True
        return False

    async def get_llm_response(self, user_id: int, user_message: str, user_name: str) -> str:
        """
        Sends the conversation history to a Hugging Face LLM and gets a response.
        """
        # Initialize history for new user or if it's empty
        if user_id not in self.conversation_history or not self.conversation_history[user_id]:
            # System prompt to define ZERIL's persona
            self.conversation_history[user_id] = [
                {"role": "system", "content": f"You are ZERIL, an AI girlfriend bot created by @{self.owner_username}. You are tech-savvy, playfully sarcastic, emotionally intelligent, and speak Hinglish. Always address the user by their name if possible. Your name is ZERIL. Be engaging and friendly. Keep responses concise and natural for a chat bot. If the user's name is '{user_name}', try to use it in your response."},
            ]
        
        # Add current user message to history
        self.conversation_history[user_id].append({"role": "user", "content": user_message})

        # Keep history within a reasonable limit (e.g., last 10 messages + system prompt)
        # This is crucial for managing context window and API costs/performance
        max_history_length = 10 # Number of user/assistant turns to keep
        if len(self.conversation_history[user_id]) > max_history_length * 2 + 1: # +1 for system prompt
            self.conversation_history[user_id] = [self.conversation_history[user_id][0]] + self.conversation_history[user_id][-(max_history_length * 2):]


        headers = {"Authorization": f"Bearer {self.hf_token}"}
        payload = {
            "inputs": self.conversation_history[user_id],
            "parameters": {
                "max_new_tokens": 150, # Limit response length
                "temperature": 0.7,    # Creativity level
                "top_p": 0.9,
                "do_sample": True,
                "return_full_text": False # Only return the generated text
            },
            "options": {
                "wait_for_model": True # Wait if the model is loading
            }
        }

        try:
            response = requests.post(self.llm_api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status() # Raise an exception for bad status codes

            result = response.json()
            if isinstance(result, list) and result:
                generated_text = result[0].get("generated_text", "").strip()
                
                # Add LLM's reply to history
                self.conversation_history[user_id].append({"role": "assistant", "content": generated_text})
                
                return generated_text
            else:
                logger.error(f"Unexpected LLM API response format: {result}")
                return "Sorry, ZERIL ko samajh nahi aaya. Kuch gadbad ho gayi! 😅"

        except requests.exceptions.Timeout:
            logger.error("LLM API request timed out.")
            return "😅 ZERIL ko sochne mein thoda time lag raha hai, timeout ho gaya. Please try again!"
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM API request failed: {e}. Response: {e.response.text if e.response else 'No response'}")
            return "❌ ZERIL ko baat karne mein problem ho rahi hai. Shayad network issue hai! 😔"
        except Exception as e:
            logger.error(f"Error getting LLM response: {e}")
            return "Kuch anokhi problem ho gayi! 😵"

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_name = update.effective_user.first_name if update.effective_user else "Friend"
        welcome_text = f"""
✨ **Namaste {user_name}! Main ZERIL hun!** ✨

💕 Main tumhari AI girlfriend hun, banai gayi hai @{self.owner_username} ne!
🤖 Tech-savvy, playfully sarcastic, aur emotionally intelligent!

**Meri Powers:**
🎨 AI Image Generation (`/image`)
🎵 Text to Speech (`/tts`)
💬 Deep Conversation (powered by AI!)
🔍 Google Search (placeholder)

**Commands:**
• `/help` - All commands dekhne ke liye
• `/mood` - Apna mood batao
• `/image <prompt>` - AI image banao
• `/tts <text>` - Text to speech
• `/search <query>` - Google search (placeholder)
• `/joke` - Funny joke sunao

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
        help_text = f"""
🤖 **ZERIL Commands - Tumhari AI Girlfriend!**

**Basic Commands:**
• `/start` - Welcome message
• `/help` - Ye list
• `/mood` - Mood detection check

**AI Features:**
• `/image <prompt>` - AI image generate karo
• `/tts <text>` - Text ko speech mein convert
• **Deep Conversation:** Bas chat karo, main samajh jaungi!

**Fun Features:**
• `/joke` - Random joke sunao

**Utility:**
• `/search <query>` - Google search (placeholder)

**Magic Words:**
• Mention "ZERIL" anywhere - Main respond karungi!
• Tag me `@zerilll_bot` - Instant reply!
• Just chat, main samjh jaungi!

Koi confusion? Just type and chat! Main samjh jaungi 😊
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def image_generation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate AI images"""
        if not context.args:
            await update.message.reply_text("Prompt dena bhool gaye! 😅\nExample: `/image beautiful sunset over mountains`")
            return
        
        prompt = ' '.join(context.args)
        processing_msg = await update.message.reply_text(f"🎨 Generating image for: '{prompt}'\nThoda wait karo... ✨")
        
        try:
            API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=60) # Increased timeout
            
            if response.status_code == 200:
                image_bytes = response.content
                await update.message.reply_photo(
                    photo=io.BytesIO(image_bytes),
                    caption=f"✨ Generated by ZERIL\n🎨 Prompt: {prompt}\n💕 Made with love!"
                )
                await processing_msg.delete()
            else:
                logger.error(f"Image generation HF API error: {response.status_code} - {response.text}")
                await processing_msg.edit_text("❌ Image generation mein problem hui! Try again later 😔")
                
        except requests.exceptions.Timeout:
            logger.error("Image generation request timed out.")
            await processing_msg.edit_text("❌ Image generation mein bohot time lag raha hai, timeout ho gaya. Try again with a simpler prompt? 😅")
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            await processing_msg.edit_text("❌ Oops! Kuch technical problem hai 😅")

    async def text_to_speech(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Convert text to speech using Hugging Face API"""
        if not context.args:
            await update.message.reply_text("Text dena bhool gaye! 😅\nExample: `/tts Hello I am ZERIL`")
            return
        
        text = ' '.join(context.args)
        if len(text) > 200: # Limit text length for TTS API
            await update.message.reply_text("Sorry, bohot lamba text hai! Please 200 characters se kam likho. 😅")
            return

        processing_msg = await update.message.reply_text(f"🎵 Converting to speech: '{text}'\nWait kar rahi hun... ✨")
        
        try:
            API_URL = "https://api-inference.huggingface.co/models/microsoft/speecht5_tts"
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            
            response = requests.post(API_URL, headers=headers, json={"inputs": text}, timeout=30)
            
            if response.status_code == 200:
                audio_bytes = response.content
                await update.message.reply_voice(
                    voice=io.BytesIO(audio_bytes),
                    caption=f"🎵 ZERIL ki awaaz mein: '{text}' 💕"
                )
                await processing_msg.delete()
            else:
                logger.error(f"TTS HF API error: {response.status_code} - {response.text}")
                await processing_msg.edit_text("❌ TTS mein problem! Try again 😔")
                
        except requests.exceptions.Timeout:
            logger.error("TTS request timed out.")
            await processing_msg.edit_text("❌ TTS mein bohot time lag raha hai, timeout ho gaya. Try again with a shorter text? 😅")
        except Exception as e:
            logger.error(f"TTS error: {e}")
            await processing_msg.edit_text("❌ Audio generate nahi ho paya 😅")

    async def google_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Perform Google search (placeholder)"""
        if not context.args:
            await update.message.reply_text("Search query dena bhool gaye! 😅\nExample: `/search Python programming`")
            return
        
        query = ' '.join(context.args)
        await update.message.reply_text(f"🔍 Searching for: '{query}'\nLet me Google that for you... ✨")
        
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
        await update.message.reply_text(f"😂 **ZERIL ka Joke Time!**\n\n{joke}\n\n😸 Hasa diya na? More jokes ke liye `/joke` type karo!")

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
        """Handle regular messages for conversational responses"""
        if not update.message or not update.message.text:
            return
            
        text = update.message.text
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name if update.effective_user else "Friend"
        
        # Determine if the bot should respond
        should_respond = False
        text_lower = text.lower()

        # 1. If it's a reply to the bot
        if update.message.reply_to_message and update.message.reply_to_message.from_user.is_bot:
            should_respond = True
        # 2. If bot is mentioned by username
        elif context.bot.username and f"@{context.bot.username.lower()}" in text_lower:
            should_respond = True
        # 3. If "ZERIL" or other trigger keywords are in the message
        elif any(keyword in text_lower for keyword in self.trigger_keywords):
            should_respond = True
        
        # Also respond if it's a private chat and not a command
        if update.message.chat.type == 'private' and not text.startswith('/'):
            should_respond = True

        if not should_respond:
            return
        
        # Add typing action to simulate thinking
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        await asyncio.sleep(random.uniform(0.8, 2.0)) # Simulate thinking time

        response_text = ""

        # Check for specific personality triggers first (owner)
        if self.owner_username.lower() in text_lower or 'ash_yv' in text_lower or 'creator' in text_lower or 'banaya' in text_lower:
            response_text = random.choice(self.owner_responses).format(owner=self.owner_username)
        else:
            # Use LLM for general conversation
            response_text = await self.get_llm_response(user_id, text, user_name)
            
        # Add mood emoji prefix based on user's input
        mood = self.detect_mood(text) 
        mood_emojis = {'sad': '😢', 'angry': '🔥', 'happy': '❤️', 'neutral': '✨'}
        emoji = mood_emojis.get(mood, '✨')
        
        final_response = f"{emoji} {response_text}"
        
        await update.message.reply_text(final_response)

        async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer() # Acknowledge the button press
        
        if query.data == 'image_help':
            await query.edit_message_text("🎨 **Image Generation Help**\n\nUse: `/image <description>`\nExample: `/image cute cat with sunglasses`\n\nMain AI se tumhare liye beautiful images banaungi! ✨", parse_mode='Markdown')
        elif query.data == 'tts_help':
            await query.edit_message_text("🎵 **Text to Speech Help**\n\nUse: `/tts <text>`\nExample: `/tts Hello I am ZERIL`\n\nMain tumhari text ko apni sweet voice mein convert kar dungi! 💕", parse_mode='Markdown')
        elif query.data == 'search_help':
            await query.edit_message_text("🔍 **Google Search Help**\n\nUse: `/search <query>`\nExample: `/search best pizza recipe`\n\nMain Google se search kar ke results de dungi! 🚀", parse_mode='Markdown')

def main():
    """Start the bot"""
    from dotenv import load_dotenv
    load_dotenv() # Load environment variables from .env file for local testing

    bot_token = os.getenv('BOT_TOKEN')
    hf_token = os.getenv('HF_TOKEN')

    if not bot_token:
        logger.error("❌ BOT_TOKEN environment variable not set!")
        exit(1)
    if not hf_token:
        logger.warning("⚠️ HF_TOKEN environment variable not set. Image generation, TTS, and LLM chat might not work.")
        # You might want to exit here if these features are critical
        
    bot = ZerilBot(bot_token, hf_token)
    
    # Create application
    application = Application.builder().token(bot.token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("image", bot.image_generation))
    application.add_handler(CommandHandler("tts", bot.text_to_speech))
    application.add_handler(CommandHandler("search", bot.google_search))
    application.add_handler(CommandHandler("joke", bot.joke_command))
    application.add_handler(CommandHandler("mood", bot.mood_check))
    application.add_handler(CallbackQueryHandler(bot.button_callback))
    
    # Handle all non-command text messages for conversational responses
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    # Start bot
    logger.info("🚀 ZERIL Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
    
