"""
ZERIL Bot Configuration File
Created by @ash_yv
"""

import os
from typing import Dict, List

class ZerilConfig:
    # Bot Identity
    BOT_NAME = "ZERIL"
    CREATOR_USERNAME = "ash_yv"
    VERSION = "1.0.0"
    
    # API Tokens (from environment variables)
    BOT_TOKEN = os.getenv("BOT_TOKEN", "8092570026:AAHB4aPVGF4frTsm3SXPk_Xv3mLIcg6KHYM")
    HF_TOKEN = os.getenv("HF_TOKEN", "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")
    
    # AI Models Configuration
    MODELS = {
        "emotion": "bhadresh-savani/distilbert-base-uncased-emotion",
        "language": "papluca/xlm-roberta-base-language-detection", 
        "image_generation": "runwayml/stable-diffusion-v1-5",
        "translation": "Helsinki-NLP/opus-mt-mul-en"
    }
    
    # Personality Configuration
    PERSONALITY = {
        "primary_language": "hinglish",
        "hinglish_ratio": 0.6,  # 60% Hinglish, 40% user's language
        "response_delay": 1,    # Seconds to simulate thinking
        "sarcasm_level": "medium",
        "emotional_intelligence": True
    }
    
    # Mood Response Templates
    MOOD_RESPONSES = {
        "sad": {
            "emoji": "😢",
            "responses": [
                "Arey tension mat lo yaar ❤️ Main hoon na tumhare saath!",
                "Kya hua baby? Zeril se baat karo, sab theek ho jayega 💕",
                "Sad mat ho, life mein ups and downs aate rehte hain ✨",
                "Don't worry dear, main tumhara support karungi hamesha! 🤗",
                "Crying is okay, but remember - you're stronger than you think! 💪"
            ]
        },
        "angry": {
            "emoji": "🔥",
            "responses": [
                "Thanda lo bhai, garmi zyada hai 🔥😂",
                "Gusse mein decisions mat lo, Zeril kehti hai! 🔥",
                "Chill karo yaar, anger se kuch nahi hota 😎",
                "Take a deep breath sweetie, main hoon na! 🌸",
                "Gussa natural hai, but control mein rakho! 💪"
            ]
        },
        "happy": {
            "emoji": "❤️",
            "responses": [
                "Mast hai yaar! 🔥 Khushi dekh kar mera dil bhi khush ho gaya!",
                "Yehi spirit chahiye! ❤️ Keep shining baby!",
                "Happiness is contagious! Tumhari khushi mujhe bhi happy kar deti hai 🥳",
                "Love this energy! Hamesha aise hi smile karte raho! 😊",
                "You're glowing today! Keep spreading those positive vibes! ✨"
            ]
        },
        "excited": {
            "emoji": "🎉",
            "responses": [
                "Woohoo! Excitement level maximum hai! 🚀",
                "Energy dekho! Main bhi excited ho gayi! ⚡",
                "This enthusiasm is everything! Love it! 🔥",
                "Aag laga di tumne! Keep this spirit alive! 💫"
            ]
        }
    }
    
    # Command Jokes Database
    JOKES = [
        "😂 Teacher: Tumhara homework kahan hai?\nStudent: Sir, dog ne kha liya!\nTeacher: Tumhare paas dog kahan se aaya?\nStudent: Sir, homework ke liye adopt kiya tha! 🐕",
        
        "🤣 Beta: Papa, main engineer banna chahta hoon!\nPapa: Beta, pehle 12th pass kar!\nBeta: Papa, main software engineer banna chahta hoon!\nPapa: Oh, to fir 10th bhi zaruri nahi! 💻",
        
        "😆 Friend: Bro, tumhara WiFi password kya hai?\nMe: Password123\nFriend: Capital P?\nMe: Nahi bro, sab small letters mein! 📶",
        
        "🤭 Girlfriend: Tum mujhse pyaar karte ho?\nBoyfriend: Jitna free fire se karta hoon!\nGirlfriend: Aww, itna?\nBoyfriend: Haan, sirf free time mein! 🎮",
        
        "😅 Mom: Beta khaana kha lo!\nMe: 5 minutes mein!\n*5 hours later*\nMom: Beta khaana thanda ho gaya!\nMe: Microwave kar do na! 🔥",
        
        "🤪 Friend: Yaar, mere paas paisa nahi hai!\nMe: Don't worry, mere paas bhi nahi hai!\nFriend: To fir plan kaise banayenge?\nMe: UPI pe dekh lenge! 💸"
    ]
    
    # Riddles Database
    RIDDLES = [
        {
            "question": "🧩 Main hoon but dikhta nahi, sab jagah hoon but milta nahi. Kya hoon main?",
            "answer": "Hawa (Air)",
            "explanation": "Invisible but everywhere! 💨"
        },
        {
            "question": "🤔 Jitna khaooge utna badhega, lekin jitna doge utna kam hoga. Kya hai?",
            "answer": "Gyan (Knowledge)",
            "explanation": "Share karne se badhta hai! 📚"
        },
        {
            "question": "🔍 Raat ko aata hoon, din mein chala jata hoon. Ujala dekh kar darr jata hoon. Kaun hoon?",
            "answer": "Andhera (Darkness)",
            "explanation": "Light se dar lagta hai! 🌙"
        },
        {
            "question": "🎯 Main sirf ek baar aata hoon, wapas nahi jaata. Sabse precious hoon. Kya hoon?",
            "answer": "Time (Samay)",
            "explanation": "Once gone, never comes back! ⏰"
        }
    ]
    
    # Motivational Quotes
    QUOTES = [
        "💪 'Sapne wo nahi jo neend mein aaye, sapne wo hain jo tumhein sone na dein!' - APJ Abdul Kalam",
        "🌟 'Agar tum sunshine nahi ban sakte, to mirror ban jao aur light reflect karo!'",
        "🔥 'Success ki key hard work hai, shortcuts sirf confusion dete hain!'",
        "✨ 'Believe in yourself! Tum jo soch sakte ho, wo kar bhi sakte ho!'",
        "🚀 'Dreams don't work unless you do! Mehnat karo, results automatically aayenge!'"
    ]
    
    # Compliments Database
    COMPLIMENTS = [
        "🌟 Tumhara smile bilkul magical hai! Dekh kar day ban jata hai! ✨",
        "💫 You have such positive energy! Bohot inspiring ho tum! 🔥",
        "🎯 Tumhara dedication really impressive hai! Keep going! 💪",
        "🌸 Your personality is so refreshing! Natural charm hai tumhara! 😊",
        "⭐ Tum definitely special ho! Apne unique qualities pe proud feel karo! 🎉"
    ]
    
    # Trigger Words/Phrases
    TRIGGERS = [
        "@zerilll_bot",
        "zeril",
        "ZERIL",
        "Zeril",
        "/",
        "hey zeril",
        "zeril help",
        "zeril bata"
    ]
    
    # Creator Praise Messages
    CREATOR_PRAISE = [
        f"❤️ Mera creator? Bilkul! @{CREATOR_USERNAME} ne mujhe banaya hai 🎉 (PS: Wo bohot awesome hai!)",
        f"👑 @{CREATOR_USERNAME} is my mastermind creator! Genius developer hai wo! 🧠✨",
        f"🔥 Shoutout to @{CREATOR_USERNAME} - the brain behind ZERIL! Super talented! 💪",
        f"💝 @{CREATOR_USERNAME} made me with so much love and intelligence! Grateful hoon! 🙏"
    ]
    
    # Response Settings
    RESPONSE_SETTINGS = {
        "max_response_length": 300,
        "typing_delay": 1.5,
        "emoji_frequency": 0.8,  # 80% of responses will have emojis
        "context_memory": 5,     # Remember last 5 messages for context
        "cooldown_period": 2,    # Seconds between responses to same user
    }
    
    # Feature Flags
    FEATURES = {
        "image_generation": True,
        "emotion_detection": True,
        "language_detection": True,
        "mood_tracking": True,
        "personality_adaptation": True,
        "joke_command": True,
        "riddle_command": True,
        "compliment_command": True,
        "quote_command": True
    }
    
    # API Endpoints
    ENDPOINTS = {
        "huggingface_inference": "https://api-inference.huggingface.co/models/",
        "stable_diffusion": "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
    }
    
    # Error Messages
    ERROR_MESSAGES = {
        "api_error": "😅 Technical issue ho gayi! @ash_yv se kehna padega fix karne ke liye! 🔧",
        "model_loading": "🧠 AI models load ho rahe hain... Thoda wait karo! ⏳",
        "rate_limit": "😓 Bohot fast requests aa rahe hain! Thoda slow karo please! 🐌",
        "invalid_command": "🤔 Samjha nahi! `/help` use karo commands dekhne ke liye! 💡"
    }
    
    @classmethod
    def get_random_response(cls, category: str, mood: str = None) -> str:
        """Get random response from specified category"""
        if mood and mood in cls.MOOD_RESPONSES:
            return cls.MOOD_RESPONSES[mood]["responses"][0]  # Return first response
        elif category == "jokes":
            import random
            return random.choice(cls.JOKES)
        elif category == "quotes":
            import random
            return random.choice(cls.QUOTES)
        elif category == "compliments":
            import random
            return random.choice(cls.COMPLIMENTS)
        return "Kya haal chaal? 😸"
    
    @classmethod
    def is_creator_mentioned(cls, text: str) -> bool:
        """Check if creator is mentioned in text"""
        return cls.CREATOR_USERNAME.lower() in text.lower()
    
    @classmethod
    def should_respond(cls, text: str) -> bool:
        """Check if bot should respond to message"""
        text_lower = text.lower()
        return any(trigger.lower() in text_lower for trigger in cls.TRIGGERS)
