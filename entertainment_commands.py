import random
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
import asyncio
from config import Config
from utils.helpers import generate_royal_invite

logger = logging.getLogger(__name__)

def register_entertainment_handlers(app: Client):
    """Register all entertainment command handlers"""

    @app.on_message(filters.command("roast") & filters.group)
    async def roast_handler(client: Client, message: Message):
        """Roast a user with royal sass"""
        # Get the target user (either replied-to or mentioned)
        if message.reply_to_message and message.reply_to_message.from_user:
            target_user = message.reply_to_message.from_user
        elif len(message.command) > 1 and message.entities:
            # Try to get the mentioned user
            for entity in message.entities:
                if entity.type == "mention":
                    username = message.text[entity.offset+1:entity.offset+entity.length]
                    try:
                        target_user = await client.get_users(username)
                        break
                    except:
                        target_user = None
                elif entity.type == "text_mention":
                    target_user = entity.user
                    break
            else:
                target_user = None
        else:
            # No target specified, roast the sender
            target_user = message.from_user
            
        if not target_user:
            await message.reply("🧙‍♀️ Who shall I roast? Please reply to someone or mention them!")
            return
            
        # List of royal roasts
        royal_roasts = [
            "Even the ugliest stepsister has more charm than {name}.",
            "If {name} were a shoe, they'd be the one that doesn't fit.",
            "The royal guards called - they want {name} to stop scaring the castle mice.",
            "Not even the Fairy Godmother's strongest magic could make {name} royal material.",
            "{name}'s fashion sense is so outdated, it belongs in 'once upon a time'.",
            "If midnight struck and {name} turned into a pumpkin, it would be an improvement.",
            "{name} dances like they have two left glass slippers.",
            "Even Lucifer the cat wouldn't bother chasing {name} around the castle.",
            "The magic mirror said {name} is the fairest of all... at being unfair.",
            "If {name} were invited to the ball, the Prince would flee at midnight.",
            "{name} has the grace of a pumpkin rolling down the palace steps.",
            "Bibbidi-Bobbidi-Boo! I just turned {name} into what they truly are - a royal fool!",
            "Not even the fairy godmother could transform {name} into someone charming.",
            "{name} is about as useful as a glass slipper in a foot race.",
            "If brains were pumpkins, {name} wouldn't have enough seeds to make a pie."
        ]
        
        # Select a random roast and format it with the target's name
        roast = random.choice(royal_roasts).format(name=target_user.first_name)
        
        # Send the roast with royal flair
        await message.reply(f"👑 *Ahem* Royal decree states: {roast} 🔥")

    @app.on_message(filters.command("mice") & filters.group)
    async def mice_handler(client: Client, message: Message):
        """Send mouse helpers to clean the chat"""
        # Animation frames for mice cleaning
        frames = [
            "🐭              ",
            "🐭🐭            ",
            "🐭🐭🐭          ",
            "  🐭🐭🐭        ",
            "    🐭🐭🐭      ",
            "      🐭🐭🐭    ",
            "        🐭🐭🐭  ",
            "          🐭🐭🐭",
            "            🐭🐭",
            "              🐭",
            "               🧹",
            "              🧹 ",
            "             🧹  ",
            "            🧹   ",
            "           🧹    ",
            "          🧹     ",
            "         🧹      ",
            "        🧹       ",
            "       🧹        ",
            "      🧹         ",
            "     🧹          ",
            "    🧹           ",
            "   🧹            ",
            "  🧹             ",
            " 🧹              ",
            "🧹               ",
            "✨✨✨✨✨✨✨✨✨✨✨"
        ]
        
        # Send initial message
        mice_msg = await message.reply("🐭 The royal mice are coming to clean the chat!")
        
        # Animate the mice cleaning
        for frame in frames:
            try:
                await mice_msg.edit(f"🧚‍♀️ *Bibbidi-Bobbidi-Boo!*\n\n{frame}")
                await asyncio.sleep(0.5)
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except Exception as e:
                logger.error(f"Error in mice animation: {e}")
                break
                
        # Final message after cleaning
        try:
            await mice_msg.edit(
                "✨ The royal mice have finished cleaning!\n"
                "The chat is now sparkling like the palace ballroom! ✨🐭"
            )
            
            # Try to delete a few messages above if bot has permission
            if message.reply_to_message:
                # Count how many messages to clean
                to_delete = []
                try:
                    async for msg in client.get_chat_history(
                        message.chat.id, 
                        limit=10, 
                        offset_id=message.reply_to_message.id
                    ):
                        if msg.id != mice_msg.id and msg.id != message.id:
                            to_delete.append(msg.id)
                            
                    # Delete the messages
                    if to_delete:
                        await client.delete_messages(message.chat.id, to_delete)
                except Exception as e:
                    logger.error(f"Error deleting messages: {e}")
                    
        except Exception as e:
            logger.error(f"Error in mice final message: {e}")

    @app.on_message(filters.command("invite") & filters.group)
    async def invite_handler(client: Client, message: Message):
        """Generate and share a fancy invite link for the group"""
        try:
            # Get the chat link
            chat = await client.get_chat(message.chat.id)
            
            if chat.username:
                invite_link = f"https://t.me/{chat.username}"
            else:
                # Try to create an invite link if the bot has permission
                try:
                    invite_link = await client.export_chat_invite_link(message.chat.id)
                except Exception as e:
                    logger.error(f"Could not create invite link: {e}")
                    await message.reply(
                        "🔮 The Fairy Godmother cannot create a magical invite! "
                        "Please ensure I have permission to generate invite links."
                    )
                    return
            
            # Generate a royal invitation
            royal_invite = generate_royal_invite(chat.title, invite_link)
            
            # Send the invitation
            await message.reply(royal_invite)
            
        except Exception as e:
            logger.error(f"Error creating invite: {e}")
            await message.reply(
                "🧙‍♀️ The royal scribe is having trouble preparing the invitation. "
                "Please try again later."
            )

    return app
