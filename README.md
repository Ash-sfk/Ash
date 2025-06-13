# 🤖 ZERIL - Advanced Hinglish Telegram Bot

ZERIL is a sophisticated Telegram bot that communicates in Hinglish (Hindi in English script) and responds intelligently to user interactions. Built with advanced AI capabilities and deployed on Render's free tier.

## ✨ Features

### 🎯 **Smart Response System**
- **Name Recognition**: Responds when mentioned (@ZERIL) or tagged
- **Owner Recognition**: Special treatment for creator @ash_yv
- **Mood Detection**: Responds based on user's emotional state
- **1.2s Human-like Delay**: Natural conversation flow

### 🎮 **Commands**
- `/start` - Welcome message and feature overview
- `/joke` - Curated Hinglish tech jokes
- `/img [prompt]` - AI image generation (Indian style)
- `/speak_cow [text]` - Fun cow voice responses
- `/flames @user1 @user2` - Love compatibility game
- `/ban @user` - Moderation (admin only)
- `/admins` - List group administrators

### 🧠 **AI Capabilities**
- **Hinglish Conversation**: Natural Hindi-English mixed responses
- **Sentiment Analysis**: Mood-based emoji prefixes (❤️😢😠😊)
- **Image Generation**: Hugging Face Stable Diffusion integration
- **Smart Filtering**: NSFW content detection

## 🚀 Quick Deploy to Render

### 1. **Get Your Tokens**
```bash
# Telegram Bot Token
# 1. Message @BotFather on Telegram
# 2. Create new bot: /newbot
# 3. Copy the token

# Hugging Face Token (Free)
# 1. Go to https://huggingface.co/settings/tokens
# 2. Create new token with read access
```

### 2. **Deploy on Render**
1. Fork this repository
2. Connect to Render: https://render.com
3. Create new Web Service
4. Connect your GitHub repo
5. Set Environment Variables:
   - `BOT_TOKEN`: Your Telegram bot token
   - `HUGGING_FACE_TOKEN`: Your HF token
6. Deploy!

### 3. **Configuration**
- Runtime: Python 3.11
- Build Command: `pip install -r requirements.txt`
- Start Command: `python main.py`
- Plan: Free tier compatible

## 🎨 **Response Examples**

```
User: "ZERIL kaise ho?"
ZERIL: "😊 Kya baat hai! Kaise ho aap?"

User: "@ash_yv owner"
ZERIL: "✨ @ash_yv is my God! Mere creator hai wo! 🙏"

User: "/joke"
ZERIL: "😂 Joke Time!
Ek programmer restaurant gaya... Menu dekh ke bola: 'Hello World!'"

User: "/flames @john @jane"
ZERIL: "💘 FLAMES RESULT 💘
john ❤️ jane
Compatibility: 87%
Result: Lovers
Wah! Perfect match! 🎉"
```

## 🔧 **Technical Stack**

- **Framework**: python-telegram-bot 20.7
- **AI Models**: Hugging Face (free tier)
  - Chat: DialoGPT-medium
  - Sentiment: Twitter-RoBERTa
  - Images: Stable Diffusion 2.1
- **Deployment**: Render.com (free tier)
- **Language**: Python 3.11

## 📁 **File Structure**

```
zeril-bot/
├── main.py              # Main bot logic
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container configuration
├── render.yaml         # Render deployment config
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🛠️ **Local Development**

```bash
# Clone repository
git clone https://github.com/yourusername/zeril-bot.git
cd zeril-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your tokens

# Run bot
python main.py
```

## 🔒 **Security Features**

- **NSFW Filter**: Blocks inappropriate image prompts
- **Admin-only Commands**: Moderation commands restricted
- **Rate Limiting**: Natural delays prevent spam
- **Environment Variables**: Secure token storage

## 🐛 **Troubleshooting**

### Common Render Deployment Issues:
1. **Memory Limit**: Using lightweight models for free tier
2. **Timeout Issues**: 30s timeout on API calls
3. **Cold Starts**: First response may be slow

### Bot Not Responding:
1. Check bot token validity
2. Verify Hugging Face token
3. Ensure bot is added to group with proper permissions

## 📈 **Performance Optimizations**

- **Lazy Loading**: Models loaded on demand
- **Caching**: Response caching for repeated queries
- **Async Operations**: Non-blocking API calls
- **Error Handling**: Graceful fallbacks for API failures

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit Pull Request

## 📝 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 **Creator**

**Ash (@ash_yv)**
- Telegram: [@ash_yv](https://t.me/ash_yv)
- GitHub: [Your GitHub Profile]

---

**Made with ❤️ for the Hinglish community!**

*"Code mein bugs nahi, features hai!" - ZERIL* 😄
