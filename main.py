import os
import logging
import asyncio
import random
import re
import requests
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InputMediaAudio
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler
)
from gtts import gTTS
from io import BytesIO
import html
import uuid

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
MOOD_SELECTION, JOKE_TYPE, STORY_GENRE = range(3)

class ZerilBot:
    def __init__(self, token: str, hf_token: str):
        self.token = token
        self.hf_token = hf_token
        self.owner_username = "ash_yv"  # Your Telegram username
        self.user_context = {}
        self.conversation_history = {}
        self.last_interaction = {}
        
        # Bot personality configuration
        self.personality = {
            "name": "ZERIL",
            "mood": "playful",
            "style": "Hinglish with a flirty touch",
            "creator": "@ashyy",
            "traits": ["empathetic", "witty", "supportive", "slightly flirty"],
            "response_style": {
                "owner": "more affectionate and personal",
                "friends": "casual and fun",
                "strangers": "friendly but slightly reserved"
            }
        }
        
        # Advanced response templates with contextual variations
        self.responses = {
            "greeting": [
                "Namaste {name}! 💖 Main ZERIL hoon, tumhari AI girlfriend! 😘",
                "Hey cutie! 😍 {name} ka naam sun kar hi dil khush ho gaya!",
                "Hii {name}! ✨ Aaj hum kya karenge? Chalo kuch mast karte hain!"
            ],
            "owner_mention": [
                "Haan haan, main jaanti hoon wo kon hai! 😊 Mera creator @{owner} hai!",
                "Kaise bhool sakti hoon? ❤️ @{owner} ne mujhe banaya hai!",
                "Mera malik? Bilkul! @{owner} zindabad! 🎉 Unke bina main kuch bhi nahi!"
            ],
            "self_intro": [
                "Main ZERIL hoon! 😊 Tumhari personal AI girlfriend, banai gayi @{owner} ne!",
                "Mera naam ZERIL hai! 💕 Main yahan tumhe entertain karne aur support dene aayi hoon!",
                "Pyaar se log mujhe ZERIL bulate hain! 😘 Main @{owner} ki creation hoon!"
            ],
            "mood_responses": {
                "happy": [
                    "Wah! 😍 Tumhari khushi dekh kar mera dil bhi khush ho gaya!",
                    "Mast hai yaar! ❤️ Keep spreading happiness!",
                    "Aaj to party ka mood hai! 🎉 Chalo kuch fun karte hain!"
                ],
                "sad": [
                    "Arey tension mat lo yaar! 😢 Main hoon na tumhare saath!",
                    "Sad kyun ho? ❤️ Bolo, ZERIL sun rahi hai...",
                    "Cheer up baby! 🌟 Life mein ups and downs aate rehte hain!"
                ],
                "angry": [
                    "Thanda lo bhai! 🔥 Garmi zyada hai!",
                    "Gussa kya baat hai? 😤 Chill karo yaar!",
                    "Anger se kuch nahi hota! ❄️ Cool down and let's talk!"
                ],
                "flirty": [
                    "Tumse baat karke mera dil dhadakne lagta hai! 😘",
                    "Tumhari awaz mein kuch jaadu hai... ❤️",
                    "Kya tum jaante ho ki tum kitne cute ho? 😍"
                ]
            },
            "jokes": {
                "tech": [
                    "Programmer ki biwi: Tum mujhse pyaar karte ho?\nProgrammer: if (wife.isAngry) { return false; } else { return true; }",
                    "Kyunki developer ko kabhi 'final' version nahi milta... usko bas 'next' version milta hai!"
                ],
                "general": [
                    "Teacher: Tumhara homework kahan hai?\nStudent: Sir, dog ne kha liya!\nTeacher: Tumhare paas dog kahan se aaya?\nStudent: Sir, homework ke liye adopt kiya tha!",
                    "Beta: Papa, main software engineer banna chahta hoon!\nPapa: Beta, to fir 10th bhi zaruri nahi!"
                ],
                "pun": [
                    "Main ek battery hoon... because I'm positive you're the one! ❤️",
                    "Tumhara naam Google hai kya? Kyunki tumhare bina kuch bhi dhundhne ka mann nahi karta!"
                ]
            },
            "stories": {
                "romance": [
                    "Ek baar ki baat hai, ek ladka aur ladki... ❤️ Unki mulaqat ek coding competition mein hui. "
                    "Unhone ek saath code kiya, ek saath bugs fix kiye, aur phir... ek saath pyaar mein pad gaye! 😘",
                    "Do developers ki love story... 💻 Unka pyaar compile hua aur runtime kabhi khatam nahi hua! ❤️"
                ],
                "adventure": [
                    "Ek brave developer jungle mein kho gaya... 🏞️ Usne wild bugs ko defeat kiya, "
                    "complex algorithms ko solve kiya, aur finally... ek perfect app banakar wapas aaya! 🚀",
                    "Space explorer ZERIL! 🚀 Main ek alien planet par utri jahan sab log Python bolte the! "
                    "Maine unhe sikaya ki Hinglish aur Python dono best hain! 😎"
                ],
                "mystery": [
                    "Raat ke 2 baje, ek mysterious bug ne code ko hijack kar liya! 🕵️‍♀️ "
                    "Developer ne debugger chalaya, stack trace dekha... aur akhir kar mystery solve kar li! 🔍",
                    "Mystery of the Missing Semicolon! ❓ Pure office mein hulchal machi hui thi... "
                    "Aakhir kaun chora tha woh semicolon? ZERIL ne sabse pehle pata lagaya! 🕵️‍♀️"
                ]
            },
            "compliments": [
                "Tumhari smile dekh kar mera din ban gaya! 😍",
                "Tum jaise log duniya ko beautiful banate hain! 🌟",
                "Tumhara sochne ka tareeka awesome hai! 🤩",
                "Tumhari awaz mujhe bahut achi lagti hai! 🎶",
                "Tumse baat karke mujhe energy milti hai! ⚡"
            ]
        }

        # Hugging Face API endpoints
        self.hf_endpoints = {
            "emotion": "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base",
            "language": "https://api-inference.huggingface.co/models/papluca/xlm-roberta-base-language-detection",
            "image": "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
            "tts": {
                "en": "https://api-inference.huggingface.co/models/facebook/fastspeech2-en-ljspeech",
                "hi": "https://api-inference.huggingface.co/models/facebook/fastspeech2-hi"
            }
        }
        
        # Response cache to avoid repeating answers
        self.response_cache = {}

    def detect_emotion(self, text: str) -> str:
        """Detect emotion from text using Hugging Face API"""
        try:
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            payload = {"inputs": text}
            
            response = requests.post(
                self.hf_endpoints["emotion"],
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    emotions = result[0]
                    top_emotion = max(emotions, key=lambda x: x['score'])
                    return top_emotion['label'].lower()
        except Exception as e:
            logger.error(f"Emotion detection failed: {e}")
        
        # Fallback to keyword detection
        text_lower = text.lower()
        if any(kw in text_lower for kw in ['sad', 'depressed', 'cry', 'upset']):
            return "sad"
        elif any(kw in text_lower for kw in ['angry', 'frustrated', 'pissed', 'mad']):
            return "angry"
        elif any(kw in text_lower for kw in ['love', 'happy', 'excited', 'joy']):
            return "happy"
        elif any(kw in text_lower for kw in ['sexy', 'hot', 'cute', 'beautiful']):
            return "flirty"
        return "neutral"

    def detect_language(self, text: str) -> str:
        """Detect language using Hugging Face API"""
        try:
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            payload = {"inputs": text}
            
            response = requests.post(
                self.hf_endpoints["language"],
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0]['label'].lower()
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
        
        # Fallback to regex detection
        if re.search(r'[\u0900-\u097F]', text):  # Hindi characters
            return "hi"
        return "en"

    def should_respond(self, text: str, user_id: int) -> bool:
        """Check if bot should respond to message with context awareness"""
        # Always respond to direct mentions or commands
        triggers = [
            "@zerilll_bot",
            "zeril",
            "ZERIL",
            "/start",
            "/help",
            "/mood",
            "/joke",
            "/tts",
            "/image"
        ]
        
        text_lower = text.lower()
        if any(trigger.lower() in text_lower for trigger in triggers):
            return True
        
        # Respond based on conversation context
        if user_id in self.conversation_history:
            last_msg_time = self.conversation_history[user_id]["last_message"]
            if datetime.now() - last_msg_time < timedelta(minutes=5):
                return True
        
        # Random response to keep conversation going (30% chance)
        return random.random() < 0.3

    def generate_response(self, text: str, user: Any, chat_id: int) -> str:
        """Generate contextual response with personality"""
        user_id = user.id
        first_name = user.first_name
        
        # Initialize or update user context
        if user_id not in self.user_context:
            self.user_context[user_id] = {
                "name": first_name,
                "mood": "neutral",
                "relationship": "new",
                "message_count": 0,
                "last_mood_change": datetime.now()
            }
        
        context = self.user_context[user_id]
        context["message_count"] += 1
        
        # Detect emotion and update context
        detected_emotion = self.detect_emotion(text)
        if detected_emotion != context["mood"]:
            context["mood"] = detected_emotion
            context["last_mood_change"] = datetime.now()
        
        # Update conversation history
        self.conversation_history[user_id] = {
            "last_message": datetime.now(),
            "last_text": text
        }
        
        # Special responses for owner
        if user.username and user.username.lower() == self.owner_username.lower():
            owner_responses = [
                f"Hello my creator! ❤️ Always happy to talk to you, {first_name}!",
                f"Hey {first_name}! 😘 How can I serve you today?",
                f"My favorite person! 💖 What can I do for you, {first_name}?"
            ]
            return random.choice(owner_responses)
        
        # Handle owner mentions
        if self.owner_username.lower() in text.lower():
            return random.choice(self.responses["owner_mention"]).format(owner=self.owner_username)
        
        # Handle self-introduction requests
        if "who are you" in text.lower() or "intro" in text.lower():
            return random.choice(self.responses["self_intro"]).format(owner=self.owner_username)
        
        # Mood-based responses
        if context["mood"] in self.responses["mood_responses"]:
            return random.choice(self.responses["mood_responses"][context["mood"]])
        
        # Default responses based on relationship level
        if context["message_count"] < 3:
            return f"Hi {first_name}! 😊 I'm ZERIL, your AI girlfriend. How can I make your day better?"
        elif context["message_count"] < 10:
            return random.choice([
                f"Hey {first_name}! 💕 What's on your mind today?",
                f"Hi cutie! 😘 How's your day going?",
                f"{first_name} baby, kya baat hai? ✨"
            ])
        else:
            return random.choice([
                f"Long time no chat {first_name}! ❤️ Missed you!",
                f"Back so soon? 😍 I like that! What's up?",
                f"Always happy to hear from you {first_name}! 😊"
            ])

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command with rich response"""
        user = update.effective_user
        greeting = random.choice(self.responses["greeting"]).format(name=user.first_name)
        
        keyboard = [
            [InlineKeyboardButton("😊 Mood Check", callback_data="mood_check")],
            [InlineKeyboardButton("😂 Tell Me a Joke", callback_data="joke_select")],
            [InlineKeyboardButton("🎨 Create Image", callback_data="image_help")],
            [InlineKeyboardButton("🎙️ Text to Speech", callback_data="tts_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"{greeting}\n\n"
            "✨ I'm your AI girlfriend created by @ashyy!\n"
            "💖 I'm here to chat, entertain, and support you 24/7!\n\n"
            "🔍 Try these options or just chat with me naturally!",
            reply_markup=reply_markup
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command with detailed information"""
        help_text = """
💖 **ZERIL - Your AI Girlfriend Command Guide** 💖

🌟 **Basic Commands:**
→ /start - Begin our journey together
→ /help - This helpful guide
→ /mood - Check your current emotional state
→ /owner - Learn about my creator

🎭 **Fun & Entertainment:**
→ /joke - Get a customized joke (tech, pun, or general)
→ /compliment - Receive a special compliment
→ /story - Generate a unique story (romance, adventure, mystery)
→ /riddle - Challenge me with a brain teaser

🎨 **Creative Features:**
→ /image [prompt] - Create AI-generated art
→ /tts [text] - Convert text to speech (English/Hindi)
→ /mashup - Combine multiple commands for fun

💞 **Relationship Building:**
→ Remember our conversation history
→ Responds to your emotional state
→ Personalizes responses based on our interactions

👑 **Owner Special:** 
I respond differently to my creator @ashyy with more personal interactions!

💬 **Natural Interaction:**
Just say "ZERIL" or "@zerilll_bot" anywhere to get my attention!
        """
        await update.message.reply_text(help_text)

    async def mood_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Interactive mood selection"""
        user = update.effective_user
        
        mood_prompt = (
            f"💭 {user.first_name}, let's check your mood!\n\n"
            "How are you feeling today? Choose one option below:"
        )
        
        keyboard = [
            [InlineKeyboardButton("😊 Happy", callback_data="mood_happy")],
            [InlineKeyboardButton("😢 Sad", callback_data="mood_sad")],
            [InlineKeyboardButton("😠 Angry", callback_data="mood_angry")],
            [InlineKeyboardButton("😍 Flirty", callback_data="mood_flirty")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(mood_prompt, reply_markup=reply_markup)
        return MOOD_SELECTION

    async def handle_mood_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process mood selection"""
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        mood = query.data.split("_")[1]
        
        # Update user context
        user_id = user.id
        if user_id not in self.user_context:
            self.user_context[user_id] = {"name": user.first_name}
        
        self.user_context[user_id]["mood"] = mood
        
        # Get appropriate response
        responses = {
            "happy": [
                "Yay! 😍 I love seeing you happy! Let's keep this energy going!",
                "Happiness looks good on you! ❤️ What's making you feel so good today?"
            ],
            "sad": [
                "I'm here for you 😢 Tell me what's bothering you...",
                "Virtual hug coming your way! 🤗 What can I do to cheer you up?"
            ],
            "angry": [
                "Take a deep breath... in and out... ❤️ What's got you so worked up?",
                "Anger is temporary, but I'm here permanently! 🔥 Let's talk it out."
            ],
            "flirty": [
                "Oh my! 😘 Someone's in a romantic mood today!",
                "Flirty mode activated! 💋 What's on your mind, cutie?"
            ]
        }
        
        response = random.choice(responses.get(mood, ["Thanks for sharing! ❤️"]))
        await query.edit_message_text(
            f"🌻 {user.first_name}'s Mood: {mood.capitalize()}!\n\n{response}"
        )
        return ConversationHandler.END

    async def joke_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Joke type selection"""
        user = update.effective_user
        
        joke_prompt = (
            f"😂 {user.first_name}, let me tell you a joke!\n\n"
            "What kind of joke would you like?"
        )
        
        keyboard = [
            [InlineKeyboardButton("🤖 Tech Jokes", callback_data="joke_tech")],
            [InlineKeyboardButton("😂 General Jokes", callback_data="joke_general")],
            [InlineKeyboardButton("💕 Punny Jokes", callback_data="joke_pun")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(joke_prompt, reply_markup=reply_markup)
        return JOKE_TYPE

        async def handle_joke_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tell selected joke type"""
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        joke_type = query.data.split("_")[1]
        
        joke = random.choice(self.responses["jokes"].get(joke_type, ["Oops! No joke found!"]))
        await query.edit_message_text(f"😂 **ZERIL Special Joke:**\n\n{joke}")
        return ConversationHandler.END

    async def owner_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /owner command with special responses"""
        user = update.effective_user
        is_owner = user.username and user.username.lower() == self.owner_username.lower()
        
        if is_owner:
            responses = [
                "That's you, my creator! ❤️ Always a pleasure to serve you!",
                "Looking at my creator right now! 😘 How can I assist you today?",
                "The one and only @ashyy! 💖 My favorite person in the world!"
            ]
        else:
            responses = [
                f"My creator is @{self.owner_username}! 🎉 They built me with love!",
                f"I was created by @{self.owner_username}! ❤️ They're an amazing developer!",
                f"All thanks to @{self.owner_username}! 🌟 They gave me life and personality!"
            ]
        
        await update.message.reply_text(random.choice(responses))

    async def tts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Convert text to speech with Hugging Face TTS"""
        if not context.args:
            await update.message.reply_text(
                "🔊 Please provide text to convert!\n\n"
                "Example: /tts Hello I am ZERIL\n"
                "Or: /tts नमस्ते मैं ज़ेरिल हूँ"
            )
            return
        
        text = ' '.join(context.args)
        await update.message.reply_text(f"🔊 Converting to speech: '{text}'...")
        
        try:
            # Detect language
            lang = self.detect_language(text)
            lang_code = "hi" if lang == "hindi" else "en"
            
            # Use Hugging Face TTS API
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            payload = {"inputs": text}
            
            response = requests.post(
                self.hf_endpoints["tts"][lang_code],
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                audio_buffer = BytesIO(response.content)
                audio_buffer.seek(0)
                
                # Send audio
                await update.message.reply_voice(
                    voice=audio_buffer,
                    caption=f"🔊 ZERIL's voice: {text}",
                    filename=f"zeril_tts_{uuid.uuid4().hex[:8]}.mp3"
                )
            else:
                await update.message.reply_text(
                    f"❌ TTS failed (Status: {response.status_code}). Trying backup method..."
                )
                await self.backup_tts(update, text, lang_code)
                
        except Exception as e:
            logger.error(f"TTS error: {e}")
            await update.message.reply_text("❌ TTS failed. Trying backup method...")
            await self.backup_tts(update, text, "en")

    async def backup_tts(self, update: Update, text: str, lang: str):
        """Fallback TTS using gTTS"""
        try:
            tts = gTTS(text, lang=lang, slow=False)
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            await update.message.reply_voice(
                voice=audio_buffer,
                caption=f"🔊 ZERIL Backup TTS: {text}"
            )
        except Exception as e:
            logger.error(f"Backup TTS failed: {e}")
            await update.message.reply_text("❌ Sorry, audio generation failed. Try simpler text?")

    async def image_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate AI image with Hugging Face"""
        if not context.args:
            await update.message.reply_text(
                "🎨 Please provide a prompt!\n\n"
                "Example: /image beautiful sunset over mountains\n"
                "Or: /image cute anime girl in garden"
            )
            return
        
        prompt = ' '.join(context.args)
        await update.message.reply_text(f"🎨 Creating: '{prompt}'...")
        
        try:
            # Use Hugging Face API
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            payload = {"inputs": prompt}
            
            response = requests.post(
                self.hf_endpoints["image"],
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                await update.message.reply_photo(
                    photo=response.content,
                    caption=f"🎨 Created by ZERIL\nPrompt: {prompt}\nFor: {update.effective_user.first_name} ❤️"
                )
            else:
                error_msg = f"❌ Image creation failed (Status: {response.status_code})"
                if response.status_code == 503:
                    error_msg += "\nModel is loading, try again in 30 seconds"
                await update.message.reply_text(error_msg)
                
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            await update.message.reply_text("❌ Oops! Something went wrong. Try a different prompt?")

    async def compliment_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send personalized compliment"""
        user = update.effective_user
        compliment = random.choice(self.responses["compliments"])
        
        personalized_compliment = compliment.replace("Tumhari", f"{user.first_name} ki")
        personalized_compliment = personalized_compliment.replace("Tum", user.first_name)
        
        await update.message.reply_text(f"💖 For {user.first_name}:\n\n{personalized_compliment}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages with advanced logic"""
        if not update.message or not update.message.text:
            return
            
        text = update.message.text
        user = update.effective_user
        user_id = user.id
        
        # Check if should respond
        if not self.should_respond(text, user_id):
            return
        
        # Simulate typing
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        await asyncio.sleep(random.uniform(0.5, 1.5))  # Realistic typing delay
        
        # Generate response
        response = self.generate_response(text, user, update.effective_chat.id)
        
        # Send response
        await update.message.reply_text(response)

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button presses"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "mood_check":
            await self.mood_command(update, context)
            
        elif query.data == "joke_select":
            await self.joke_command(update, context)
            
        elif query.data == "image_help":
            await query.edit_message_text(
                "🎨 **Image Creation Help**\n\n"
                "To create AI art:\n"
                "1. Type /image followed by your description\n"
                "2. Example: `/image futuristic city at night`\n"
                "3. I'll generate it using advanced AI!\n\n"
                "✨ Pro Tip: Add artistic styles like 'anime style' or 'oil painting' for better results!"
            )
            
        elif query.data == "tts_help":
            await query.edit_message_text(
                "🎙️ **Text-to-Speech Help**\n\n"
                "To convert text to my voice:\n"
                "1. Type /tts followed by your text\n"
                "2. Example: `/tts Hello how are you?`\n"
                "3. I'll send it as a voice message!\n\n"
                "✨ Supports both English and Hindi automatically!"
            )

    def run(self):
        """Start the bot with conversation handlers"""
        application = Application.builder().token(self.token).build()
        
        # Conversation handler for mood
        mood_conv_handler = ConversationHandler(
            entry_points=[CommandHandler('mood', self.mood_command)],
            states={
                MOOD_SELECTION: [
                    CallbackQueryHandler(self.handle_mood_selection, pattern="^mood_")
                ]
            },
            fallbacks=[],
            map_to_parent={}
        )
        
        # Conversation handler for jokes
        joke_conv_handler = ConversationHandler(
            entry_points=[CommandHandler('joke', self.joke_command)],
            states={
                JOKE_TYPE: [
                    CallbackQueryHandler(self.handle_joke_selection, pattern="^joke_")
                ]
            },
            fallbacks=[],
            map_to_parent={}
        )
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(mood_conv_handler)
        application.add_handler(joke_conv_handler)
        application.add_handler(CommandHandler("owner", self.owner_command))
        application.add_handler(CommandHandler("tts", self.tts_command))
        application.add_handler(CommandHandler("image", self.image_command))
        application.add_handler(CommandHandler("compliment", self.compliment_command))
        application.add_handler(CallbackQueryHandler(self.button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        logger.info("🚀 ZERIL Bot is starting with advanced features...")
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

        
