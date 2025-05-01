# Cinderella Bot Deployment Guide

This guide will help you deploy the Cinderella Bot on your own server or hosting platform.

## Required Dependencies

Make sure you have Python 3.8+ installed and install the following packages:

```bash
pip install pyrogram==2.0.106 tgcrypto==1.2.5 python-dotenv==1.1.0 requests==2.32.3 psutil==7.0.0
```

## Configuration

1. Create a `.env` file in the root directory with the following variables:
   ```
   API_ID=your_api_id
   API_HASH=your_api_hash
   BOT_TOKEN=your_bot_token
   BOT_USERNAME=your_bot_username
   ADMIN_IDS=comma,separated,admin,ids
   GEMINI_KEY=optional_google_ai_key
   ```

2. Make sure the `cinderella_db.json` file exists and is writable.

## Running the Bot

Simply run the main Python file:

```bash
python main.py
```

## Project Structure

- `main.py`: Main entry point for the bot
- `config.py`: Configuration and settings
- `handlers/`: Command handlers for different categories
  - `admin_commands.py`: Admin and moderation commands
  - `voice_commands.py`: Voice chat and audio features
  - `game_commands.py`: Interactive games
  - `entertainment_commands.py`: Fun commands
  - `utility_commands.py`: Utility features
- `utils/`: Helper modules
  - `database.py`: Database operations
  - `helpers.py`: Utility functions

## Features Overview

### 👑 Royal Group Management (Admin-Only)
- `/curse [@user]`: Warn a user (3 curses = ban)
- `/banish [@user]`: Ban user from kingdom
- `/silence [@user]`: Mute user temporarily
- `/royal_rules`: Set group rules
- `/pardon [@user]`: Unban/unmute user

### 🎤 Voice Chat Magic
- `/joinball`: Join royal ball (voice chat)
- `/midnight`: Play clock chimes (reset roles)
- `/sing [song]`: Play Disney songs

### 🔮 Enchanted Games
- `/slipper`: Find hidden glass slipper
- `/pumpkin`: Grow virtual pumpkin coach
- `/fortune`: Get fairy godmother's prophecy

### 🎭 Royal Entertainment
- `/roast [@user]`: "Thou shalt be roasted! 🔥"
- `/mice`: Send mouse helpers to clean chat
- `/invite`: Share magical invite link

### ⚙️ Utility Commands
- `/status`: Check bot health/uptime
- `/help`: Show all commands
- `/magic`: Toggle special effects

## Enabling Full Voice Chat Functionality with Female Voice

The current implementation has voice chat features in simulation mode. To enable actual voice functionality with a female voice:

### Required Dependencies

```bash
# Install system dependencies (Ubuntu/Debian)
apt-get update && apt-get install -y ffmpeg python3-dev build-essential

# Install PyTgCalls and TTS packages
pip install py-tgcalls==0.9.7 pydub gTTS
```

### Code Modifications

1. Update `handlers/voice_commands.py`:

```python
# At the top, modify the imports
try:
    import asyncio
    import os
    import re
    from pyrogram import Client, filters
    from pyrogram.types import Message
    from pyrogram.raw.functions.channels import GetFullChannel
    from pyrogram.raw.functions.phone import GetGroupCall, JoinGroupCall, LeaveGroupCall
    from pyrogram.raw.types import InputPeerChannel
    from pyrogram.errors import ChannelPrivate
    
    from gtts import gTTS
    from pydub import AudioSegment
    import random
    import time
    
    from pytgcalls import PyTgCalls
    from pytgcalls.types import Update
    from pytgcalls.types.input_stream import InputAudioStream
    from pytgcalls.types.input_stream.quality import HighQualityAudio
    
    from utils.database import update_group_data, get_group_data
    from config import Config
    
    PYTGCALLS_AVAILABLE = True
except ImportError:
    PYTGCALLS_AVAILABLE = False
    from pyrogram import Client, filters
    from pyrogram.types import Message
    from utils.database import update_group_data, get_group_data
    from config import Config

# Add these functions:
async def text_to_speech(text, output_file):
    """Convert text to speech using gTTS (Google Text-to-Speech)"""
    tts = gTTS(text=text, lang='en', tld='co.uk', slow=False)  # Using UK English for more "royal" accent
    tts.save(output_file)
    
    # Convert to the correct format for Telegram voice chats
    sound = AudioSegment.from_mp3(output_file)
    sound.export(output_file, format="ogg", codec="libopus", 
                bitrate="128k", parameters=["-ac", "2"])
    return output_file

# Modify the register_voice_handlers function:
def register_voice_handlers(app: Client):
    """Register all voice-related command handlers"""
    
    # Initialize PyTgCalls if available
    if PYTGCALLS_AVAILABLE:
        call_py = PyTgCalls(app)
        
        # Voice chat status tracker
        active_calls = {}
        
        @call_py.on_stream_end()
        async def on_stream_end(client, update: Update):
            """Handle when a stream ends"""
            chat_id = update.chat_id
            if chat_id in active_calls:
                del active_calls[chat_id]
                
        call_py.start()
    else:
        active_calls = {}

    # Replace the joinball_handler function:
    @app.on_message(filters.command("joinball") & filters.group)
    async def joinball_handler(client: Client, message: Message):
        """Join a voice chat"""
        chat_id = message.chat.id
        
        if not PYTGCALLS_AVAILABLE:
            await message.reply("🎵 The royal orchestra would love to join the ball, but the musicians are still rehearsing!\n\nVoice chat features are simulated in this version.")
            return
            
        try:
            # Get full channel info to access the voice chat
            chat = await client.resolve_peer(chat_id)
            if not isinstance(chat, InputPeerChannel):
                await message.reply("🏰 This command works only in groups!")
                return
                
            full_chat = await client.send(GetFullChannel(channel=chat))
            if not hasattr(full_chat.full_chat, 'call') or not full_chat.full_chat.call:
                await message.reply("👑 There is no royal ball (voice chat) in progress! Ask the admins to start one.")
                return
                
            # Get voice chat details
            call = await client.send(GetGroupCall(
                call=full_chat.full_chat.call,
                limit=1
            ))
            
            # Join the voice chat
            await call_py.join_group_call(
                chat_id,
                InputAudioStream(
                    "silence.ogg",  # A silent audio file
                    HighQualityAudio(),
                )
            )
            
            active_calls[chat_id] = {"joined_at": time.time()}
            
            # Create and play welcome speech
            welcome_text = "Greetings, royal subjects! Cinderella has arrived at the ball. How may I assist you this fine evening?"
            audio_file = await text_to_speech(welcome_text, f"welcome_{chat_id}.ogg")
            
            await call_py.change_stream(
                chat_id,
                InputAudioStream(
                    audio_file,
                    HighQualityAudio(),
                )
            )
            
            await message.reply("👗 Cinderella has arrived at the royal ball! Use /sing to request a song or /midnight to end the ball.")
            
        except Exception as e:
            await message.reply(f"👑 The royal carriage broke down! Could not join the voice chat: {str(e)}")

    # Update the sing_handler function:
    @app.on_message(filters.command("sing") & filters.group)
    async def sing_handler(client: Client, message: Message):
        """Play Disney songs in voice chat"""
        chat_id = message.chat.id
        
        if not PYTGCALLS_AVAILABLE:
            await message.reply("🎵 The royal orchestra would love to play a song, but they're still rehearsing!\n\nVoice chat features are simulated in this version.")
            return
            
        if chat_id not in active_calls:
            await message.reply("👑 I must join the ball first! Use /joinball to invite me.")
            return
            
        # Get requested song
        if len(message.command) > 1:
            song_name = message.command[1].lower()
            if song_name in Config.DISNEY_SONGS:
                song_url = Config.DISNEY_SONGS[song_name]
                try:
                    # Play the song
                    await call_py.change_stream(
                        chat_id,
                        InputAudioStream(
                            song_url,
                            HighQualityAudio(),
                        )
                    )
                    await message.reply(f"🎵 Now singing: {song_name.replace('-', ' ').title()}! Enjoy the royal music!")
                except Exception as e:
                    await message.reply(f"👑 The royal orchestra seems to be having trouble: {str(e)}")
            else:
                songs_list = ", ".join([f"`{song.replace('-', ' ')}`" for song in Config.DISNEY_SONGS.keys()])
                await message.reply(f"🎵 I don't know that song! Here are the songs I can sing:\n{songs_list}")
        else:
            # If no song specified, speak a message
            try:
                speech_text = "What song would you like me to sing? You can choose from Bibbidi Bobbidi Boo, A Dream Is A Wish, or So This Is Love."
                audio_file = await text_to_speech(speech_text, f"song_help_{chat_id}.ogg")
                
                await call_py.change_stream(
                    chat_id,
                    InputAudioStream(
                        audio_file,
                        HighQualityAudio(),
                    )
                )
                
                songs_list = ", ".join([f"`{song.replace('-', ' ')}`" for song in Config.DISNEY_SONGS.keys()])
                await message.reply(f"🎵 Please specify a song to sing. Available songs:\n{songs_list}")
            except Exception as e:
                await message.reply(f"👑 My voice seems to be a bit hoarse today: {str(e)}")

    # Update the midnight_handler function:
    @app.on_message(filters.command("midnight") & filters.group)
    async def midnight_handler(client: Client, message: Message):
        """Play midnight chimes and reset voice chat"""
        chat_id = message.chat.id
        
        if not PYTGCALLS_AVAILABLE:
            await message.reply("🕛 The clock cannot strike midnight yet! Voice chat features are simulated in this version.")
            return
            
        if chat_id not in active_calls:
            await message.reply("👑 I must first join the ball! Use /joinball to invite me.")
            return
            
        try:
            # Speak farewell message
            farewell_text = "The clock strikes midnight! I must depart now. Farewell, everyone!"
            audio_file = await text_to_speech(farewell_text, f"midnight_{chat_id}.ogg")
            
            await call_py.change_stream(
                chat_id,
                InputAudioStream(
                    audio_file,
                    HighQualityAudio(),
                )
            )
            
            # Wait for the audio to finish (approximately)
            await asyncio.sleep(5)
            
            # Leave the voice chat
            await call_py.leave_group_call(chat_id)
            if chat_id in active_calls:
                del active_calls[chat_id]
                
            await message.reply("🕛 The clock strikes midnight! Cinderella has left the ball!")
            
        except Exception as e:
            await message.reply(f"👑 The royal carriage is having trouble: {str(e)}")

    # Add a new command for speaking in voice chat
    @app.on_message(filters.command("speak") & filters.group)
    async def speak_handler(client: Client, message: Message):
        """Speak a message in the voice chat"""
        chat_id = message.chat.id
        
        if not PYTGCALLS_AVAILABLE:
            await message.reply("👑 My royal voice isn't ready yet! Voice chat features are simulated in this version.")
            return
            
        if chat_id not in active_calls:
            await message.reply("👑 I must first join the ball! Use /joinball to invite me.")
            return
            
        if len(message.command) > 1:
            # Get the text to speak
            text = " ".join(message.command[1:])
            
            try:
                # Convert text to speech
                audio_file = await text_to_speech(text, f"speech_{chat_id}_{int(time.time())}.ogg")
                
                # Play the speech
                await call_py.change_stream(
                    chat_id,
                    InputAudioStream(
                        audio_file,
                        HighQualityAudio(),
                    )
                )
                
                await message.reply("👑 Speaking in my royal voice!")
                
            except Exception as e:
                await message.reply(f"👑 I seem to have lost my voice: {str(e)}")
        else:
            await message.reply("👑 Please provide something for me to say!")
```

2. Create a silent audio file needed for voice chat initialization:

```bash
# Generate a 1-second silent audio file
ffmpeg -f lavfi -i anullsrc=r=48000:cl=mono -t 1 -c:a libopus -b:a 128k silence.ogg
```

3. Update your environment variables:

```
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
BOT_USERNAME=your_bot_username
ADMIN_IDS=comma,separated,admin,ids
GEMINI_KEY=optional_google_ai_key
```

4. Update the `config.py` with real song URLs:

```python
# Voice chat settings
MAX_SONG_DURATION = 300  # 5 minutes in seconds
DISNEY_SONGS = {
    "bibbidi-bobbidi-boo": "https://example.com/path/to/bibbidi-bobbidi-boo.ogg",
    "a-dream-is-a-wish": "https://example.com/path/to/a-dream-is-a-wish.ogg",
    "so-this-is-love": "https://example.com/path/to/so-this-is-love.ogg",
}
```

5. Make sure to host your song files somewhere accessible or include them in your project.

### Voice Chat Commands

With these modifications, you'll have the following voice chat features with a female voice:

- `/joinball`: Bot joins voice chat and introduces herself with a female voice
- `/sing [song]`: Bot sings the requested Disney song
- `/midnight`: Bot says goodbye in voice chat and leaves
- `/speak [text]`: New command! Makes the bot speak any text with a female voice

### Troubleshooting Voice Features

If you encounter issues with voice chat features:

1. Check that all system dependencies are installed (ffmpeg, etc.)
2. Ensure PyTgCalls is properly installed and compatible with your Pyrogram version
3. Verify that the bot has permission to join voice chats in the group
4. Check the audio file paths and formats
5. Make sure your hosting provider allows audio processing

## General Troubleshooting

If you encounter any issues:
1. Check that all required environment variables are set correctly
2. Ensure the bot has the necessary permissions in Telegram groups
3. Look for error messages in the console output
4. Verify that you have a stable internet connection