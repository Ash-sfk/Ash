import logging
import random
import json
import requests
from pyrogram.types import Message
from config import Config

logger = logging.getLogger(__name__)

async def is_admin(client, chat_id, user_id):
    """Check if a user is an admin in the chat"""
    try:
        # Check if user is in the hardcoded admin list
        if user_id in Config.ADMIN_IDS:
            return True
            
        # Check admin status in the chat
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False

async def get_target_user(client, message):
    """Get the target user from a command (either by reply or mention)"""
    # If replying to a message, get that user
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
        
    # If mentioning a user with @ notation
    if len(message.command) > 1:
        username = message.command[1]
        if username.startswith('@'):
            username = username[1:]
            
        try:
            return await client.get_users(username)
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None
            
    # If mentioning with text_mention entity
    if message.entities:
        for entity in message.entities:
            if entity.type == "text_mention":
                return entity.user
                
    return None

def pretty_time(seconds):
    """Convert seconds to a human-readable time format"""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minutes"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours} hours, {minutes} minutes"

async def get_fortune(username):
    """Generate a personalized fortune/prophecy using Gemini API"""
    if not Config.GEMINI_KEY:
        return None
        
    try:
        # Prepare the prompt for Gemini API
        prompt = (
            f"Generate a short, whimsical fortune or prophecy for a user named {username}. "
            "Use a fairy-tale style with references to Cinderella themes like glass slippers, "
            "pumpkins, fairy godmothers, princes/princesses, royal balls, or midnight magic. "
            "Keep it positive, G-rated, and under 100 words. No hashtags or emojis."
        )
        
        # Make API request to Gemini
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={Config.GEMINI_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 100,
                "topP": 0.95,
                "topK": 40
            }
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            response_json = response.json()
            try:
                fortune = response_json["candidates"][0]["content"]["parts"][0]["text"]
                # Clean up any extra quotes or formatting
                fortune = fortune.strip().strip('"')
                return fortune
            except (KeyError, IndexError) as e:
                logger.error(f"Error parsing Gemini API response: {e}")
                return None
        else:
            logger.error(f"Gemini API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error generating fortune: {e}")
        return None

def generate_royal_invite(group_name, invite_link):
    """Generate a fancy royal invitation message"""
    invitation_templates = [
        "👑 **ROYAL INVITATION** 👑\n\n"
        "By decree of the Royal Court,\n"
        "You are cordially invited to join:\n\n"
        "🏰 **{group_name}** 🏰\n\n"
        "The kingdom awaits your presence!\n"
        "🔮 {invite_link}",
        
        "✨ **Hear ye, hear ye!** ✨\n\n"
        "The Royal Family of\n"
        "🏰 **{group_name}** 🏰\n\n"
        "Requests your presence at the grand ball.\n"
        "Your glass carriage awaits:\n"
        "👠 {invite_link}",
        
        "🧚‍♀️ **Bibbidi-Bobbidi-Boo!** 🧚‍♀️\n\n"
        "The Fairy Godmother has prepared\n"
        "a magical evening for you at:\n\n"
        "✨ **{group_name}** ✨\n\n"
        "Don't be late! Remember, the spell breaks at midnight:\n"
        "🎃 {invite_link}"
    ]
    
    template = random.choice(invitation_templates)
    return template.format(group_name=group_name, invite_link=invite_link)
