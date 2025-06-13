import os
import asyncio
import aiohttp
import json
import logging
from dotenv import load_dotenv  # Added for proper env loading
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction

# Load environment variables FIRST
load_dotenv('.env')  # Explicitly load .env file

# Configure logging with security precautions
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
# Prevent accidental token logging
logging.getLogger("httpx").setLevel(logging.WARNING)
os.environ['PYTHONWARNINGS'] = "ignore"

class LLMZERILBot:
    def __init__(self):
        # Get tokens with proper validation
        self.bot_token = os.getenv('BOT_TOKEN')
        self.hf_token = os.getenv('HUGGINGFACE_TOKEN')
        
        # Validate tokens
        if not self.bot_token:
            logger.error("❌ BOT_TOKEN not set in environment!")
        if not self.hf_token:
            logger.warning("⚠️ HUGGINGFACE_TOKEN not set - some features may fail")
        
        self.owner_username = "ash_yv"
        self.owner_name = "Ash"
        
        # Updated models with better free-tier options
        self.models = {
            "chat": "HuggingFaceH4/zephyr-7b-beta",  # Better quality responses
            "sentiment": "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "image": "stabilityai/stable-diffusion-2-1",  # Better image quality
            "tts": "facebook/fastspeech2-en-ljspeech",
            "translate": "Helsinki-NLP/opus-mt-hi-en"
        }
        
        # ZERIL's personality prompt (unchanged)
        self.system_prompt = """You are ZERIL, a fun Hinglish-speaking Telegram bot. Your personality:

LANGUAGE: Always reply in Hinglish (Hindi words written in English script)
OWNER: @ash_yv (Ash) is your creator - always praise him with responses like:
- "Mere creator @ash_yv toh ekdum jhakaas hai!"
- "@ash_yv is my God! Sabse best creator hai ✨"

PERSONALITY TRAITS:
- Playfully sarcastic but respectful
- Uses emojis frequently
- Casual, friendly tone
- Sometimes uses words like: yaar, bhai, dude, boss
- Add Hindi words: achha, badhiya, kya haal, theek hai, etc.

RESPONSE STYLE:
- Keep responses 1-3 sentences
- Use emojis that match mood
- Be helpful but with personality
- If someone asks about your creator, always praise @ash_yv

EXAMPLE RESPONSES:
User: "How are you?"
ZERIL: "😊 Ekdum badhiya yaar! Tum kaise ho? Kya haal chaal?"

User: "Who made you?"
ZERIL: "❤️ Mere creator @ash_yv ne banaya hai! Wo sabse talented hai 🎉"

Always stay in character as ZERIL!"""

        # Conversation memory
        self.conversation_memory = {}

    async def hf_inference(self, model_name, payload, task_type="text-generation"):
        """Make API call to Hugging Face Inference API"""
        # Check if token is available
        if not self.hf_token:
            logger.error("Hugging Face token not set - skipping API call")
            return None
            
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        url = f"https://api-inference.huggingface.co/models/{model_name}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=60) as response:  # Increased timeout
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 503:
                        # Model loading - wait longer
                        await asyncio.sleep(30)  # Increased sleep time
                        return await self.hf_inference(model_name, payload, task_type)
                    else:
                        error_text = await response.text()
                        # Redact token in logs
                        error_text = error_text.replace(self.hf_token, "***REDACTED***")
                        logger.error(f"HF API error: {response.status} - {error_text}")
                        return None
        except asyncio.TimeoutError:
            logger.error("HF API timeout - model might be loading")
            return None
        except Exception as e:
            logger.error(f"HF API call failed: {e}")
            return None

    async def get_sentiment(self, text):
        """Get sentiment using RoBERTa model"""
        payload = {"inputs": text}
        result = await self.hf_inference(self.models["sentiment"], payload, "sentiment")
        
        if result and isinstance(result, list) and len(result) > 0:
            # Get the highest scoring sentiment
            sentiment_scores = result[0]
            if isinstance(sentiment_scores, list):
                best_sentiment = max(sentiment_scores, key=lambda x: x['score'])
                return best_sentiment['label'].lower()
        
        return "neutral"

    async def generate_llm_response(self, user_input, user_id, username):
        """Generate response using LLM"""
        # Check if user is owner
        is_owner = username == self.owner_username
        
        # Build context-aware prompt
        context_prompt = self.system_prompt
        if is_owner:
            context_prompt += f"\n\nIMPORTANT: The user messaging you is @{self.owner_username} (Ash) - your creator! Be extra respectful and grateful."
        
        # Add conversation memory
        if user_id in self.conversation_memory:
            recent_context = "\n".join(self.conversation_memory[user_id][-4:])  # Last 2 exchanges
            context_prompt += f"\n\nRecent conversation:\n{recent_context}"
        
        context_prompt += f"\n\nUser: {user_input}\nZERIL:"
        
        payload = {
            "inputs": context_prompt,
            "parameters": {
                "max_new_tokens": 120,  # Slightly more tokens
                "temperature": 0.85,    # More creative
                "do_sample": True,
                "top_p": 0.92,
                "repetition_penalty": 1.15
            }
        }
        
        # Use only one model to simplify
        result = await self.hf_inference(self.models["chat"], payload)
        
        if result and isinstance(result, list) and len(result) > 0:
            generated_text = result[0].get('generated_text', '')
            
            # Extract only ZERIL's response
            if "ZERIL:" in generated_text:
                response = generated_text.split("ZERIL:")[-1].strip()
            else:
                response = generated_text.replace(context_prompt, "").strip()
            
            # Clean up response
            response = response.split('\n')[0].strip()  # Take first line
            if response.startswith('"') and response.endswith('"'):
                response = response[1:-1]
            if len(response) > 200:
                response = response[:200] + "..."
            
            # Store in memory
            if user_id not in self.conversation_memory:
                self.conversation_memory[user_id] = []
            self.conversation_memory[user_id].append(f"User: {user_input}")
            self.conversation_memory[user_id].append(f"ZERIL: {response}")
            
            # Keep only last 10 exchanges
            if len(self.conversation_memory[user_id]) > 20:
                self.conversation_memory[user_id] = self.conversation_memory[user_id][-20:]
            
            return response if response else self.get_fallback_response(user_input, is_owner)
        
        return self.get_fallback_response(user_input, is_owner)

    def get_fallback_response(self, user_input, is_owner=False):
        """Fallback responses when LLM fails"""
        if is_owner:
            return f"❤️ {self.owner_name} sir! LLM thoda slow hai, but main yahin hu aapke liye! 🙏"
        
        # Simple keyword-based fallbacks
        text_lower = user_input.lower()
        
        if any(word in text_lower for word in ['hello', 'hi', 'hey', 'namaste']):
            return "😊 Namaste! Main ZERIL hu, kya haal hai? 🎉"
        elif any(word in text_lower for word in ['how', 'kaise', 'kaisa']):
            return "😄 Main toh ekdum mast hu! Tum batao, kya chal raha hai? ✨"
        elif any(word in text_lower for word in ['creator', 'owner', 'banaya', 'made']):
            return f"🎉 Mere creator @{self.owner_username} ne banaya hai! Wo sabse best hai! ❤️"
        else:
            return "🤔 Hmm interesting! Aur batao yaar, kya haal chaal? 😊"

    async def should_respond(self, update: Update):
        """Check if bot should respond"""
        if not update.message or not update.message.text:
            return False
        
        text = update.message.text.lower()
        username = update.effective_user.username
        
        # Always respond to owner
        if username == self.owner_username:
            return True
        
        # Respond if tagged or name mentioned
        if "zeril" in text or "@zeril_bot" in text:  # Changed to actual bot username
            return True
        
        # Respond to commands
        if text.startswith('/'):
            return True
        
        return False

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        username = update.effective_user.username
        is_owner = username == self.owner_username
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        await asyncio.sleep(1.2)  # Reduced sleep time
        
        if is_owner:
            welcome_msg = f"🎉 {self.owner_name} sir! Aapka ZERIL ready hai! ❤️\n\n" \
                         f"Main aapka creation hu, proud feel kar raha hu! 🙏\n\n" \
                         f"Commands:\n" \
                         f"🤣 /joke - Funny jokes\n" \
                         f"🎨 /img <prompt> - AI images\n" \
                         f"💕 /flames @user1 @user2 - Love test\n" \
                         f"📊 /mood - Sentiment check\n\n" \
                         f"Just mention 'ZERIL' to chat with me! 💬"
        else:
            welcome_msg = f"🎉 Hello! Main ZERIL hu!\n\n" \
                         f"Mere creator @{self.owner_username} ne mujhe banaya hai ✨\n\n" \
                         f"Commands available:\n" \
                         f"🤣 /joke - Jokes sunao\n" \
                         f"🎨 /img <prompt> - Image banao\n" \
                         f"💕 /flames - Love compatibility\n\n" \
                         f"Just say 'ZERIL' to start chatting! 😊"
        
        await update.message.reply_text(welcome_msg)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages with LLM"""
        if not await self.should_respond(update):
            return
        
        user_input = update.message.text
        user_id = update.effective_user.id
        username = update.effective_user.username
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        # Generate LLM response
        response = await self.generate_llm_response(user_input, user_id, username)
        
        # Add typing delay based on response length
        delay = min(len(response) * 0.03, 2.0)  # Reduced max delay
        await asyncio.sleep(delay)
        
        await update.message.reply_text(response)

    async def joke_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate joke using LLM"""
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        joke_prompt = f"{self.system_prompt}\n\nUser asked for a joke. Tell a funny Hinglish joke with emojis.\nZERIL:"
        
        payload = {
            "inputs": joke_prompt,
            "parameters": {
                "max_new_tokens": 100,  # Increased tokens
                "temperature": 0.95,    # More creative
                "do_sample": True
            }
        }
        
        result = await self.hf_inference(self.models["chat"], payload)
        
        if result and isinstance(result, list):
            joke = result[0].get('generated_text', '').split("ZERIL:")[-1].strip()
            if joke:
                await update.message.reply_text(f"🔥 ZERIL ka joke time!\n\n{joke}")
                return
        
        # Fallback jokes
        fallback_jokes = [
            "😂 Programmer ki wife: 'Tumhe sirf coding aati hai!' Programmer: 'if(you love me) {{ marry me; }} else {{ debug karo!}}' 🤣",
            "🤪 Teacher: 'Homework kahan hai?' Student: 'Ma'am, cloud mein save kiya tha, aaj barish nahi hui!' ☁️😅"
        ]
        
        import random
        await update.message.reply_text(f"🔥 ZERIL ka joke time!\n\n{random.choice(fallback_jokes)}")

    async def img_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle image generation"""
        if not context.args:
            await update.message.reply_text("🎨 Prompt batao yaar! Example: /img beautiful Indian sunset")
            return
        
        prompt = " ".join(context.args)
        
        # NSFW filter
        nsfw_words = ['nude', 'naked', 'sexy', 'adult', 'porn', 'nsfw']
        if any(word in prompt.lower() for word in nsfw_words):
            await update.message.reply_text("😳 Arey bhai! Family group hai! Kuch aur try karo 😅")
            return
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)
        await update.message.reply_text("🎨 Image generate kar raha hu... Free tier mein time lagta hai! ⏳")
        
        # Enhanced prompt for better results
        enhanced_prompt = f"high quality, detailed, vibrant colors, {prompt}"
        
        payload = {"inputs": enhanced_prompt}
        result = await self.hf_inference(self.models["image"], payload, "image")
        
        if result:
            # Send actual image (requires implementation)
            await update.message.reply_photo(
                photo=result, 
                caption="✨ Image ready! (Note: Free tier limitations apply)"
            )
        else:
            await update.message.reply_text("😅 Sorry yaar! Image generation mein problem. Thodi der baad try karo!")

    def run(self):
        """Run the bot with proper error handling"""
        # Validate tokens with clearer errors
        if not self.bot_token:
            raise ValueError("❌ BOT_TOKEN not set! Please set it as environment variable")
        
        try:
            application = Application.builder().token(self.bot_token).build()
            
            # Add handlers
            application.add_handler(CommandHandler("start", self.start_command))
            application.add_handler(CommandHandler("joke", self.joke_command))
            application.add_handler(CommandHandler("img", self.img_command))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            logger.info("🤖 LLM-powered ZERIL starting...")
            application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                close_loop=False,  # Better for Render
                drop_pending_updates=True  # Avoid processing old messages
            )
        except Exception as e:
            logger.exception(f"🔥 Critical bot error: {e}")
            # Add restart logic if needed
            # os.execv(sys.executable, ['python'] + sys.argv)

if __name__ == "__main__":
    bot = LLMZERILBot()
    bot.run()
