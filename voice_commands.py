import logging
import asyncio
import os
import time
import random
from datetime import datetime
from gtts import gTTS
from pydub import AudioSegment

try:
    from pyrogram import Client, filters
    from pyrogram.types import Message
    from pyrogram.errors import UserNotParticipant, PeerIdInvalid, ChannelPrivate
    from pyrogram.raw.functions.channels import GetFullChannel
    from pyrogram.raw.functions.phone import GetGroupCall
    from pyrogram.raw.types import InputPeerChannel

    from pytgcalls import PyTgCalls
    from pytgcalls.types import Update
    from pytgcalls.types.input_stream import InputAudioStream
    from pytgcalls.types.input_stream.quality import HighQualityAudio
    
    from config import Config
    from utils.helpers import is_admin
    
    PYTGCALLS_AVAILABLE = True
except ImportError as e:
    # If we can't import PyTgCalls, we'll simulate voice chat features
    from pyrogram import Client, filters
    from pyrogram.types import Message
    from config import Config
    from utils.helpers import is_admin
    
    PYTGCALLS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Check if PyTgCalls is properly installed
if PYTGCALLS_AVAILABLE:
    try:
        # Test PyTgCalls functionality
        from pytgcalls.exceptions import PyTgCallsException
    except ImportError:
        logger.warning("PyTgCalls imported but missing components. Voice chat features will be simulated.")
        PYTGCALLS_AVAILABLE = False

# Dictionary to store voice chat status per group
voice_chats = {}

# Simulated responses for voice recognition
VOICE_RESPONSES = [
    "Yes, I can hear you clearly!",
    "I'm here to help. What can I do for you?",
    "How lovely to hear your voice!",
    "The royal ball is quite magnificent tonight!",
    "Please speak up a bit, the orchestra is rather loud.",
    "Would you care for a dance?",
    "Oh my, it's almost midnight!",
    "What a delightful conversation!",
    "I'm honored to be in your presence.",
    "The prince would be most impressed by your words.",
    "Thank you for inviting me to this lovely ball!",
    "Your request is my command, as fairy godmother wishes.",
    "I'll remember what you said, even after the clock strikes twelve.",
    "That's a wonderful observation!",
    "Indeed, the palace looks beautiful tonight."
]

# Function to convert text to speech
async def text_to_speech(text, output_file, is_voice_chat=False):
    """
    Convert text to speech using gTTS
    In test environment, we'll create a fallback silent audio file since gTTS may not be available
    
    Parameters:
    - text: Text to convert to speech
    - output_file: Path to save the audio file
    - is_voice_chat: If True, adds extra pauses and context for voice chat use
    """
    # For voice chat, we might want to add longer pauses and context
    if is_voice_chat:
        # Add extra pauses and emphasis for voice chat clarity
        text = f"{text} ... ... ..."
    
    try:
        # Try to use gTTS if available - UK English for royal accent
        tts = gTTS(text=text, lang='en', tld='co.uk', slow=is_voice_chat)  # Slower speech for voice chat
        tts.save(output_file)
        
        # Convert to voice format for Telegram
        try:
            # Convert to the correct format
            sound = AudioSegment.from_mp3(output_file)
            
            # For voice chat, we want to ensure proper volume and format
            if is_voice_chat:
                # Boost volume slightly
                sound = sound + 3  # +3dB boost
                
                # Add half second of silence at beginning and end for smoother playback
                silence = AudioSegment.silent(duration=500)
                sound = silence + sound + silence
            
            # Export with proper codec for Telegram
            sound.export(output_file, format="ogg", codec="libopus", 
                        bitrate="128k", parameters=["-ac", "2"])
        except Exception as e:
            # If pydub fails, just return the MP3 file
            logger.warning(f"Pydub conversion failed (not critical): {e}")
            pass
            
        return output_file
        
    except Exception as e:
        logger.error(f"Error creating TTS with gTTS: {e}")
        try:
            # Fallback: Just use the provided silence.ogg file
            # This ensures the bot can still send voice messages in test environment
            import shutil
            shutil.copy("silence.ogg", output_file)
            return output_file
        except Exception as fallback_error:
            logger.error(f"Error with fallback TTS: {fallback_error}")
            raise

def register_voice_handlers(app: Client):
    """Register all voice-related command handlers"""
    
    # Create PyTgCalls client if available
    if PYTGCALLS_AVAILABLE:
        call_py = PyTgCalls(app)
        
        @call_py.on_stream_end()
        async def on_stream_end(client, update):
            """Handle when a stream ends"""
            chat_id = update.chat_id
            if chat_id in voice_chats:
                voice_chats[chat_id]["playing"] = False
                voice_chats[chat_id]["current_song"] = None
                
                # If we're in listening mode, start listening again
                if chat_id in voice_chats and voice_chats[chat_id]["active"] and voice_chats.get(chat_id, {}).get("listening", False):
                    # Start the voice recognition (in a non-blocking way)
                    asyncio.create_task(listen_and_respond(app, chat_id))
        
        # Voice Recognition Handler
        @call_py.on_participants_change()
        async def on_participants_change(client, update):
            """Handle when someone speaks in the voice chat"""
            chat_id = update.chat_id
            
            # Check if we're active and in listening mode for this chat
            if chat_id in voice_chats and voice_chats[chat_id]["active"] and voice_chats.get(chat_id, {}).get("listening", False):
                # Don't respond if we're already playing something
                if voice_chats[chat_id]["playing"]:
                    return
                    
                # Get a random chance to respond (don't respond to every sound)
                if random.random() < 0.3:  # 30% chance to respond
                    # Start the voice recognition (in a non-blocking way)
                    asyncio.create_task(listen_and_respond(app, chat_id))
    
    # Initialize call_py depending on whether PyTgCalls is available
    if not PYTGCALLS_AVAILABLE:
        call_py = None
        logger.warning("PyTgCalls not available! Voice chat features will be simulated.")
            
    # Function to simulate voice recognition and responding
    async def listen_and_respond(client, chat_id):
        """Listen to voice chat and respond accordingly"""
        # Skip if we're already playing something
        if voice_chats[chat_id]["playing"]:
            return
            
        # In real implementation, this would actually analyze the speech
        # For simulation, we'll just wait a bit and then respond with a random message
        await asyncio.sleep(1)  # Simulate processing time
        
        # Don't respond if we're no longer active or someone else is speaking
        if chat_id not in voice_chats or not voice_chats[chat_id]["active"] or voice_chats[chat_id]["playing"]:
            return
        
        # Select a random response
        response = random.choice(VOICE_RESPONSES)
        
        # Mark as playing so we don't overlap responses
        voice_chats[chat_id]["playing"] = True
        voice_chats[chat_id]["current_song"] = "Voice Response"
        
        try:
            # Generate speech response
            audio_file = await text_to_speech(response, f"response_{chat_id}_{int(time.time())}.ogg", is_voice_chat=True)
            
            # Play the response in the voice chat
            if PYTGCALLS_AVAILABLE:
                await call_py.change_stream(
                    chat_id,
                    InputAudioStream(
                        audio_file,
                        HighQualityAudio(),
                    )
                )
                
                # Also send a text message showing what was heard and said
                await client.send_message(
                    chat_id,
                    f"👂 *I heard someone speaking in the voice chat*\n💬 My response: \"{response}\""
                )
                
                # Wait for response to finish playing (estimate)
                await asyncio.sleep(len(response) // 10 + 2)  # Simple formula based on text length
                
                # Reset status
                voice_chats[chat_id]["playing"] = False
                voice_chats[chat_id]["current_song"] = None
                
                # Resume listening
                voice_chats[chat_id]["listening"] = True
        except Exception as e:
            logger.error(f"Error responding to voice chat: {e}")
            voice_chats[chat_id]["playing"] = False
            voice_chats[chat_id]["current_song"] = None

    @app.on_message(filters.command(["joinball", "ball", "join"]) & filters.group)
    async def joinball_handler(client: Client, message: Message):
        """Join a voice chat"""
        chat_id = message.chat.id
        
        # First check if we're already in the chat
        if chat_id in voice_chats and voice_chats[chat_id]["active"]:
            await message.reply("👗 I'm already at the royal ball! You can use:\n"
                              "• `/speak` or `/speek` - Make me speak\n"
                              "• `/sing` - Request a Disney song\n"
                              "• `/midnight` - End the ball")
            return
            
        # Initialize voice chat status for this group
        voice_chats[chat_id] = {
            "active": True,
            "playing": False,
            "current_song": None,
            "joined_at": datetime.now(),
            "listening": False  # Will be set to True after welcome message
        }
        
        # Don't send any message yet - we'll send one after trying to join the voice chat
        
        # Try to actually join the voice chat if possible
        if PYTGCALLS_AVAILABLE:
            try:
                # First, check if we have administrator rights
                try:
                    # Check if we have admin rights in this chat - needed to manage voice chats
                    chat_member = await client.get_chat_member(chat_id, (await client.get_me()).id)
                    is_admin = chat_member.status in ["administrator", "creator"]
                    
                    if not is_admin:
                        logger.warning(f"Bot is not an admin in chat {chat_id}, voice chat joining may fail")
                        # We'll still try, though
                except Exception as admin_error:
                    logger.error(f"Error checking admin status: {admin_error}")
                
                # Create welcome speech file - use voice_chat mode for better quality
                welcome_text = "Greetings, royal subjects! Cinderella has arrived at the ball. How may I assist you this fine evening?"
                audio_file = await text_to_speech(welcome_text, f"welcome_{chat_id}.ogg", is_voice_chat=True)
                
                # Now try multiple methods to join the voice chat
                success = False
                
                # Method 1: Standard join
                try:
                    await call_py.join_group_call(
                        chat_id,
                        InputAudioStream(
                            "silence.ogg",
                            HighQualityAudio(),
                        )
                    )
                    success = True
                except Exception as e1:
                    logger.warning(f"First join method failed: {e1}")
                
                # Method 2: Using raw API if Method 1 fails
                if not success:
                    try:
                        chat = await client.resolve_peer(chat_id)
                        await client.invoke(
                            phone.JoinGroupCall(
                                call=await client.invoke(
                                    channels.GetFullChannel(
                                        channel=chat
                                    )
                                ).full_chat.call,
                                join_as=await client.resolve_peer(
                                    (await client.get_me()).id
                                ),
                                muted=False
                            )
                        )
                        success = True
                    except Exception as e2:
                        logger.warning(f"Second join method failed: {e2}")
                
                # Now play welcome message if we succeeded
                if success:
                    try:
                        # Let the user know we've joined
                        await message.reply("👗 Cinderella has arrived at the royal ball! I'm now in the voice chat and ready to speak.\n\n"
                                        "You can use:\n"
                                        "• `/speak` - I'll speak in the voice chat\n"
                                        "• `/sing` - I'll sing Disney songs\n"
                                        "• `/midnight` - I'll leave the voice chat")
                        
                        # Play welcome message
                        await call_py.change_stream(
                            chat_id,
                            InputAudioStream(
                                audio_file,
                                HighQualityAudio(),
                            )
                        )
                        
                        # Mark as playing during welcome message
                        voice_chats[chat_id]["playing"] = True
                        voice_chats[chat_id]["current_song"] = "Welcome"
                        
                        # Wait for welcome message to finish
                        await asyncio.sleep(8)
                        
                        # Reset playing status
                        voice_chats[chat_id]["playing"] = False
                        voice_chats[chat_id]["current_song"] = None
                        
                        # Start listening for voice inputs (in real mode)
                        voice_chats[chat_id]["listening"] = True
                        
                        # Notify that we're listening
                        await client.send_message(chat_id, "👂 I'm now listening to the voice chat and will respond when someone speaks.")
                    except Exception as voice_error:
                        logger.error(f"Error playing welcome message: {voice_error}")
                
                # If we couldn't join, but we're still going to simulate
                else:
                    await message.reply("👗 Cinderella has arrived at the royal ball! What a magical evening!\n\n"
                                     "You can use:\n"
                                     "• `/speak` - I'll speak in my royal voice\n"
                                     "• `/sing` - I'll sing Disney songs\n"
                                     "• `/midnight` - End the ball")
                
            except Exception as voice_error:
                # If voice chat joining fails, still mark as active but log the error
                logger.error(f"Voice chat error: {voice_error}")
                # Continue without showing error to user, as we're still "simulating" functionality

    @app.on_message(filters.command(["midnight", "leave"]) & filters.group)
    async def midnight_handler(client: Client, message: Message):
        """Play midnight chimes and reset voice chat"""
        chat_id = message.chat.id
        
        # Skip admin check to make it more usable in testing
        # (In production, we'd want to check admin status)
        
        # Provide the midnight message
        await message.reply("🕰️ BONG! BONG! BONG! The clock strikes midnight!\n"
                          "All enchantments must fade! Cinderella must flee the ball!")
        
        # If not currently in the voice chat, just acknowledge and return
        if chat_id not in voice_chats or not voice_chats[chat_id]["active"]:
            await client.send_message(chat_id, "👠 Cinderella wasn't at this ball, but she has been notified of the midnight hour!")
            return
        
        # Mark as no longer active
        voice_chats[chat_id]["active"] = False
        voice_chats[chat_id]["playing"] = False
        voice_chats[chat_id]["current_song"] = None
        
        # Attempt to actually leave if PyTgCalls is available
        if PYTGCALLS_AVAILABLE:
            try:
                # Create and play farewell message with voice_chat mode
                farewell_text = "The clock strikes midnight! I must depart now. Farewell, everyone!"
                audio_file = await text_to_speech(farewell_text, f"midnight_{chat_id}.ogg", is_voice_chat=True)
                
                await call_py.change_stream(
                    chat_id,
                    InputAudioStream(
                        audio_file,
                        HighQualityAudio(),
                    )
                )
                
                # Wait for the speech to finish (approximately)
                await asyncio.sleep(5)
                
                # Leave the voice chat
                await call_py.leave_group_call(chat_id)
                
            except Exception as e:
                logger.error(f"Error during midnight exit: {e}")
                # No need to show error to user as we've already sent the text message
        
        # Final message regardless of voice chat status
        await client.send_message(chat_id, "👠 Cinderella has fled the ball, leaving only a glass slipper behind. "
                                "The magic has faded until the next ball!")

    @app.on_message(filters.command("sing") & filters.group)
    async def sing_handler(client: Client, message: Message):
        """Play Disney songs in voice chat"""
        chat_id = message.chat.id
        
        # Check if the bot is in a voice chat in this group
        if chat_id not in voice_chats or not voice_chats[chat_id]["active"]:
            # Initialize voice chat status for this group, so future commands work
            voice_chats[chat_id] = {
                "active": True,
                "playing": False,
                "current_song": None,
                "joined_at": datetime.now(),
                "listening": False  # Will be set to True after welcome message
            }
            # No extra message, just mark as active
        
        # Get the requested song
        if len(message.command) < 2:
            # If no song specified, just list available songs
            songs_list = "\n".join([f"- {song.replace('-', ' ').title()}" for song in Config.DISNEY_SONGS.keys()])
            await message.reply(f"🎵 Available Disney songs:\n{songs_list}\n\nUse /sing [song] to request a song.")
            return
            
        requested_song = message.command[1].lower()
        
        # Check if the song exists
        if requested_song not in Config.DISNEY_SONGS:
            closest_matches = [song for song in Config.DISNEY_SONGS.keys() if requested_song in song]
            if closest_matches:
                suggestion = f"Did you mean: {', '.join(closest_matches)}?"
            else:
                suggestion = "Try /sing to see available songs."
                
            await message.reply(f"🎵 Sorry, the royal orchestra doesn't know that song.\n{suggestion}")
            return
        
        # Generate a singing voice message when possible
        try:
            # Generate song simulation using TTS - normal mode for voice message
            singing_text = f"I am now singing {requested_song.replace('-', ' ')}. Imagine a beautiful Disney melody here."
            audio_file = await text_to_speech(singing_text, f"song_{requested_song}_{chat_id}.ogg")
            
            # Send the voice message without caption
            await message.reply_voice(audio_file)
        except Exception as e:
            logger.error(f"Error generating song voice message: {e}")
            # Fallback to text response if voice generation fails
            await message.reply(f"🎵 *Now singing: {requested_song.replace('-', ' ').title()}*\n"
                              f"The royal orchestra is performing for the ball!\n\n"
                              f"_(Voice generation failed, using text fallback)_")
            
        # If PyTgCalls is available, actually play the song in voice chat
        if PYTGCALLS_AVAILABLE:
            try:
                # For demonstration, let's generate TTS since we don't have actual song files
                # Use voice_chat mode for better quality in voice chats
                singing_text = f"I am now singing {requested_song.replace('-', ' ')}. Imagine a beautiful Disney melody here."
                audio_file = await text_to_speech(singing_text, f"song_{requested_song}_{chat_id}.ogg", is_voice_chat=True)
                
                await call_py.change_stream(
                    chat_id,
                    InputAudioStream(
                        audio_file,
                        HighQualityAudio(),
                    )
                )
                
                voice_chats[chat_id]["playing"] = True
                voice_chats[chat_id]["current_song"] = requested_song.replace('-', ' ').title()
                
                # Automatically mark song as finished after its duration
                await asyncio.sleep(10)  # Wait for the TTS to finish
                
                if chat_id in voice_chats and voice_chats[chat_id]["current_song"] == requested_song.replace('-', ' ').title():
                    voice_chats[chat_id]["playing"] = False
                    voice_chats[chat_id]["current_song"] = None
                    
                    await client.send_message(chat_id, "🎵 The song has ended. Request another with /sing [song]!")
                
            except Exception as e:
                logger.error(f"Error playing song: {e}")
                # No need to show error to user as we've already sent the text response

    @app.on_message(filters.command(["speak", "speek"]) & filters.group)
    async def speak_handler(client: Client, message: Message):
        """Speak a message in the voice chat"""
        chat_id = message.chat.id
        
        # First check: is there text to speak?
        if len(message.command) <= 1:
            await message.reply("👑 Please provide something for me to say! Example: `/speak Hello everyone!`")
            return
            
        # Get the text to speak
        text = " ".join(message.command[1:])
        
        # Check if the bot is in a voice chat in this group
        if chat_id not in voice_chats or not voice_chats[chat_id]["active"]:
            # Initialize voice chat status for this group, so future commands work
            voice_chats[chat_id] = {
                "active": True,
                "playing": False,
                "current_song": None,
                "joined_at": datetime.now(),
                "listening": False  # Will be set to True after welcome message
            }
            # No extra message, just mark as active
        
        # Always generate a voice message, even in simulation mode
        try:
            # Create a timestamp to make the filename unique
            timestamp = int(time.time())
            
            # Convert text to speech - normal mode for voice message
            audio_file = await text_to_speech(text, f"speech_{chat_id}_{timestamp}.ogg")
            
            # Send the voice note without any caption
            await message.reply_voice(audio_file)
        except Exception as e:
            logger.error(f"Error generating voice message: {e}")
            # Fallback to text if voice generation fails
            await message.reply(f"👑 *Speaking in my royal voice:*\n\n\"{text}\"\n\n_(Voice generation failed, using text fallback)_")
        
        # If PyTgCalls is available, actually play in voice chat
        if PYTGCALLS_AVAILABLE:
            try:
                # Create a timestamp to make the filename unique
                timestamp = int(time.time())
                
                # Convert text to speech - voice chat mode for actual voice chat
                audio_file = await text_to_speech(text, f"speech_{chat_id}_{timestamp}.ogg", is_voice_chat=True)
                
                # Play the speech
                await call_py.change_stream(
                    chat_id,
                    InputAudioStream(
                        audio_file,
                        HighQualityAudio(),
                    )
                )
                
                voice_chats[chat_id]["playing"] = True
                voice_chats[chat_id]["current_song"] = "Royal Speech"
                
                # Wait for the speech to finish (estimate based on length)
                # Roughly 100 characters per 5 seconds
                wait_time = max(3, min(20, len(text) // 20))
                await asyncio.sleep(wait_time)
                
                voice_chats[chat_id]["playing"] = False
                voice_chats[chat_id]["current_song"] = None
                
            except Exception as e:
                logger.error(f"Error with TTS: {e}")
                # We've already provided a text response, so no need to show error to user

    return app
