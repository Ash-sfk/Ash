import os
import logging
from pyrogram import Client, idle
from pyrogram.types import BotCommand
from config import Config
from utils.database import init_database
from handlers.admin_commands import register_admin_handlers
from handlers.voice_commands import register_voice_handlers
from handlers.game_commands import register_game_handlers
from handlers.entertainment_commands import register_entertainment_handlers
from handlers.utility_commands import register_utility_handlers

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot commands to be displayed in the command menu
COMMANDS = [
    BotCommand("help", "Show all available commands"),
    BotCommand("status", "Check bot health/uptime"),
    BotCommand("magic", "Toggle special effects"),
    BotCommand("roast", "Roast a user with royal sass"),
    BotCommand("mice", "Send mouse helpers to clean chat"),
    BotCommand("invite", "Share magical invite link"),
    BotCommand("slipper", "Find hidden glass slipper"),
    BotCommand("pumpkin", "Grow virtual pumpkin coach"),
    BotCommand("fortune", "Get fairy godmother's prophecy"),
    BotCommand("joinball", "Join royal ball (voice chat)"),
    BotCommand("midnight", "Play clock chimes (reset roles)"),
    BotCommand("sing", "Play Disney songs"),
]

# Admin commands not shown in the general command menu
ADMIN_COMMANDS = [
    BotCommand("curse", "Warn a user (3 curses = ban)"),
    BotCommand("banish", "Ban user from kingdom"),
    BotCommand("silence", "Mute user temporarily"),
    BotCommand("royal_rules", "Set group rules"),
    BotCommand("pardon", "Unban/unmute user"),
]

async def main():
    """Initialize and start the Cinderella Bot"""
    # Initialize bot
    bot = Client(
        "CinderellaBot",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
        plugins=dict(root="plugins")
    )
    
    # Initialize database
    init_database()
    
    # Register all command handlers
    register_admin_handlers(bot)
    register_voice_handlers(bot)
    register_game_handlers(bot)
    register_entertainment_handlers(bot)
    register_utility_handlers(bot)
    
    # Start the bot
    await bot.start()
    logger.info("✨ Cinderella Bot is ready for the ball! ✨")
    
    # Set bot commands
    await bot.set_bot_commands(COMMANDS)
    
    # Keep the bot running
    await idle()
    
    # Stop the bot when script is interrupted
    await bot.stop()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
