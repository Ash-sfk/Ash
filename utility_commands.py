import time
import logging
import platform
import psutil
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from utils.database import get_user_stats, get_group_stats

logger = logging.getLogger(__name__)

# Track bot start time
START_TIME = time.time()

def register_utility_handlers(app: Client):
    """Register all utility command handlers"""

    @app.on_message(filters.command("help"))
    async def help_handler(client: Client, message: Message):
        """Show help and command list"""
        # Different help message for private chats vs groups
        is_private = message.chat.type == "private"
        
        # Help categories
        categories = {
            "👑 Group Management": [
                ("/curse [@user]", "Warn a user (3 curses = ban)"),
                ("/banish [@user]", "Ban user from kingdom"),
                ("/silence [@user]", "Mute user temporarily"),
                ("/royal_rules", "Set or view group rules"),
                ("/pardon [@user]", "Unban/unmute user")
            ],
            "🎤 Voice Chat Magic": [
                ("/joinball", "Join royal ball (voice chat)"),
                ("/speak [text]", "Talk with a female voice in chat"),
                ("/midnight", "Play clock chimes (reset roles)"),
                ("/sing [song]", "Play Disney songs")
            ],
            "🔮 Enchanted Games": [
                ("/slipper", "Find hidden glass slipper"),
                ("/pumpkin", "Grow virtual pumpkin coach"),
                ("/fortune", "Get fairy godmother's prophecy")
            ],
            "🎭 Royal Entertainment": [
                ("/roast [@user]", "Roast a user with royal sass"),
                ("/mice", "Send mouse helpers to clean chat"),
                ("/invite", "Share magical invite link")
            ],
            "⚙️ Utility Commands": [
                ("/status", "Check bot health/uptime"),
                ("/help", "Show this help message"),
                ("/magic", "Toggle special effects")
            ]
        }
        
        if not is_private:
            # In groups, show a compact help message with a button to PM
            help_text = (
                "👑 **Cinderella Bot Commands**\n\n"
                "• Group Management: `/curse`, `/banish`, `/silence`, etc.\n"
                "• Voice Chat: `/joinball`, `/speak`, `/sing`, `/midnight`\n"
                "• Games: `/slipper`, `/pumpkin`, `/fortune`\n"
                "• Entertainment: `/roast`, `/mice`, `/invite`\n"
                "• Utility: `/status`, `/help`, `/magic`\n\n"
                "Click the button below for detailed help!"
            )
            
            # Create button to open PM with the bot
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "📨 Message me for detailed help",
                    url=f"https://t.me/{Config.BOT_USERNAME}?start=help"
                )]
            ])
            
            await message.reply(help_text, reply_markup=keyboard)
            
        else:
            # In private, show a detailed help message
            help_text = f"👑 **Welcome to {Config.BOT_NAME}!**\n\n"
            help_text += "Here are all the magical commands you can use:\n\n"
            
            for category, commands in categories.items():
                help_text += f"**{category}**\n"
                for cmd, desc in commands:
                    help_text += f"• `{cmd}` - {desc}\n"
                help_text += "\n"
                
            help_text += (
                "✨ **Note**: Admin commands (👑) require proper permissions.\n"
                "For voice chat commands (🎤), I need to be made admin.\n\n"
                "Add me to your group: "
                f"[Click here](https://t.me/{Config.BOT_USERNAME}?startgroup=true)"
            )
            
            await message.reply(help_text)

    @app.on_message(filters.command("status"))
    async def status_handler(client: Client, message: Message):
        """Show bot status and system info"""
        # Calculate uptime
        uptime = int(time.time() - START_TIME)
        uptime_str = str(timedelta(seconds=uptime))
        
        # Get system info
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        python_version = platform.python_version()
        
        # Get bot stats
        total_users = len(get_user_stats())
        total_groups = len(get_group_stats())
        
        status_text = (
            "🏰 **Cinderella Bot Status**\n\n"
            f"**Uptime**: `{uptime_str}`\n"
            f"**CPU Usage**: `{cpu_usage}%`\n"
            f"**RAM Usage**: `{ram_usage}%`\n"
            f"**Python Version**: `{python_version}`\n"
            f"**Pyrogram Version**: `{Client.__version__}`\n\n"
            f"**Total Users**: `{total_users}`\n"
            f"**Total Groups**: `{total_groups}`\n\n"
            "✨ The magic is running smoothly!"
        )
        
        await message.reply(status_text)

    @app.on_message(filters.command("magic") & filters.group)
    async def magic_handler(client: Client, message: Message):
        """Toggle special effects for the user"""
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        # This would normally update user preferences in the database
        # For now, we'll just acknowledge the command
        
        # In a real implementation, you would:
        # 1. Check current user preferences
        # 2. Toggle the "special_effects" setting
        # 3. Save to database
        
        await message.reply(
            "✨ *Bibbidi-Bobbidi-Boo!* ✨\n\n"
            "Your magical preferences have been updated!\n"
            "Special effects will be customized for your royal experience."
        )

    @app.on_message(filters.new_chat_members)
    async def welcome_handler(client: Client, message: Message):
        """Welcome new members with a royal greeting"""
        # Check if the bot itself is being added
        new_members = message.new_chat_members
        bot_being_added = any(member.is_self for member in new_members)
        
        if bot_being_added:
            # Bot is being added to a group
            await message.reply(
                "👑 **Royal Announcement!** 👑\n\n"
                f"*{Config.BOT_NAME}* has arrived at the ball!\n\n"
                "I am here to manage your kingdom with magical powers:\n"
                "• 👑 Royal group management\n"
                "• 🎤 Voice chat magic\n"
                "• 🔮 Enchanted games\n"
                "• 🎭 Royal entertainment\n\n"
                "Please make me an admin so my magic can work properly!\n"
                "Use /help to see all my magical commands."
            )
        else:
            # Regular users being added
            if len(new_members) == 1:
                # Single member welcome
                user = new_members[0]
                await message.reply(
                    f"👑 Welcome to the royal ball, {user.mention}! 👑\n\n"
                    f"The kingdom of {message.chat.title} welcomes you with open arms!\n"
                    "Remember to follow the royal rules and enjoy your stay.\n\n"
                    "Use /help to see all the magical commands available!"
                )
            else:
                # Multiple members welcome
                mentions = ", ".join([member.mention for member in new_members])
                await message.reply(
                    f"👑 Welcome to the royal ball! 👑\n\n"
                    f"The kingdom welcomes our new guests: {mentions}\n"
                    f"We hope you enjoy your time in {message.chat.title}!\n\n"
                    "Use /help to see all the magical commands available!"
                )

    @app.on_message(filters.left_chat_member)
    async def goodbye_handler(client: Client, message: Message):
        """Say goodbye to members leaving the chat"""
        # Check if the leaving member is the bot itself
        if message.left_chat_member.is_self:
            # Bot was removed from the group
            return
            
        # Regular user leaving
        user = message.left_chat_member
        
        await message.reply(
            f"🎭 {user.mention} has left the ball before midnight!\n"
            "Perhaps they lost their glass slipper somewhere else..."
        )

    @app.on_message(filters.private & filters.command("start"))
    async def start_handler(client: Client, message: Message):
        """Handle start command in private chat"""
        args = message.command
        
        if len(args) > 1 and args[1] == "help":
            # Redirect to help command
            await help_handler(client, message)
            return
            
        # Regular start message
        start_text = (
            f"👑 **Welcome to {Config.BOT_NAME}!** 👑\n\n"
            "I'm your magical assistant, ready to transform your Telegram group "
            "into a royal kingdom!\n\n"
            "**My magical powers include:**\n"
            "• 👑 Royal group management\n"
            "• 🎤 Voice chat enchantments\n"
            "• 🔮 Magical games and fortunes\n"
            "• 🎭 Royal entertainment\n\n"
            "Add me to your group to experience the magic!\n"
            "Use /help to see all my commands."
        )
        
        # Create keyboard with add to group button
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "🏰 Add me to your Kingdom!",
                url=f"https://t.me/{Config.BOT_USERNAME}?startgroup=true"
            )],
            [InlineKeyboardButton(
                "📚 Help & Commands",
                callback_data="help_command"
            )]
        ])
        
        await message.reply(start_text, reply_markup=keyboard)

    @app.on_callback_query(filters.regex(r"^help_command$"))
    async def help_callback(client, callback_query):
        """Handle help button callback"""
        await callback_query.answer()
        await help_handler(client, callback_query.message)

    return app
