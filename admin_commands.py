import time
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.errors import UserAdminInvalid, ChatAdminRequired, PeerIdInvalid
from config import Config
from utils.database import (
    get_warnings,
    add_warning,
    remove_warning,
    set_rules,
    get_rules,
    get_admins,
    update_admins
)
from utils.helpers import is_admin, get_target_user, pretty_time

logger = logging.getLogger(__name__)

def register_admin_handlers(app: Client):
    """Register all admin command handlers"""

    @app.on_message(filters.command("curse") & filters.group)
    async def curse_handler(client: Client, message: Message):
        """Warn a user. After 3 warnings, they get banned."""
        # Check if sender is admin
        if not await is_admin(client, message.chat.id, message.from_user.id):
            await message.reply("🔒 Only the royal court may cast curses!")
            return
        
        # Get the target user
        target_user = await get_target_user(client, message)
        if not target_user:
            await message.reply("🧙‍♀️ You must mention or reply to someone to curse them!")
            return
            
        # Check if target is an admin
        if await is_admin(client, message.chat.id, target_user.id):
            await message.reply("👑 The royal court cannot be cursed!")
            return
            
        # Add warning to the user
        warnings = add_warning(message.chat.id, target_user.id)
        
        if warnings >= Config.MAX_WARNINGS:
            # Ban user after max warnings
            try:
                await client.ban_chat_member(message.chat.id, target_user.id)
                await message.reply(f"⚡ The clock has struck midnight for {target_user.mention}! "
                                   f"After {warnings} curses, they've been banished from the kingdom!")
                # Reset warnings after banishment
                remove_warning(message.chat.id, target_user.id, all_warnings=True)
            except (UserAdminInvalid, ChatAdminRequired) as e:
                await message.reply("❌ I don't have the royal authority to banish members!")
                logger.error(f"Failed to ban user: {e}")
        else:
            await message.reply(f"⚠️ {target_user.mention} has been cursed! "
                               f"Curse count: {warnings}/{Config.MAX_WARNINGS}\n"
                               f"Royal mercy can be granted with /pardon")

    @app.on_message(filters.command("banish") & filters.group)
    async def banish_handler(client: Client, message: Message):
        """Ban a user from the group"""
        # Check if sender is admin
        if not await is_admin(client, message.chat.id, message.from_user.id):
            await message.reply("🔒 Only the royal court may banish subjects!")
            return
        
        # Get target user
        target_user = await get_target_user(client, message)
        if not target_user:
            await message.reply("🧙‍♀️ You must mention or reply to someone to banish them!")
            return
            
        # Check if target is an admin
        if await is_admin(client, message.chat.id, target_user.id):
            await message.reply("👑 The royal court cannot be banished!")
            return
            
        try:
            await client.ban_chat_member(message.chat.id, target_user.id)
            await message.reply(f"🔮 {target_user.mention} has been banished from the kingdom! "
                               f"Their carriage has turned back into a pumpkin.")
        except (UserAdminInvalid, ChatAdminRequired) as e:
            await message.reply("❌ I don't have the royal authority to banish members!")
            logger.error(f"Failed to ban user: {e}")

    @app.on_message(filters.command("silence") & filters.group)
    async def silence_handler(client: Client, message: Message):
        """Mute a user temporarily"""
        # Check if sender is admin
        if not await is_admin(client, message.chat.id, message.from_user.id):
            await message.reply("🔒 Only the royal court may silence subjects!")
            return
        
        # Get target user
        target_user = await get_target_user(client, message)
        if not target_user:
            await message.reply("🧙‍♀️ You must mention or reply to someone to silence them!")
            return
            
        # Check if target is an admin
        if await is_admin(client, message.chat.id, target_user.id):
            await message.reply("👑 The royal court cannot be silenced!")
            return
            
        # Parse duration (default: 1 hour)
        duration = Config.MUTE_DURATION  # Default
        args = message.command[1:]
        if len(args) > 0 and not message.reply_to_message:
            # If replying, the first arg is the username, so skip it
            try:
                time_arg = args[0] if not message.reply_to_message else args[0]
                if time_arg[-1] == 'h':
                    duration = int(time_arg[:-1]) * 3600
                elif time_arg[-1] == 'm':
                    duration = int(time_arg[:-1]) * 60
                elif time_arg[-1] == 'd':
                    duration = int(time_arg[:-1]) * 86400
                else:
                    duration = int(time_arg) * 60  # Assume minutes if no unit
            except (ValueError, IndexError):
                # Invalid time format, use default
                pass
                
        until_date = int(time.time() + duration)
        
        try:
            # Mute the user
            await client.restrict_chat_member(
                message.chat.id, 
                target_user.id,
                ChatPermissions(
                    can_send_messages=False,
                    can_send_media=False,
                    can_send_polls=False,
                    can_add_web_page_previews=False,
                    can_change_info=False,
                    can_invite_users=False,
                    can_pin_messages=False
                ),
                until_date=until_date
            )
            
            duration_str = pretty_time(duration)
            await message.reply(f"🤫 {target_user.mention} has been silenced for {duration_str}!\n"
                               f"Their voice will return at the stroke of midnight.")
        except (UserAdminInvalid, ChatAdminRequired) as e:
            await message.reply("❌ I don't have the royal authority to silence members!")
            logger.error(f"Failed to mute user: {e}")

    @app.on_message(filters.command("royal_rules") & filters.group)
    async def royal_rules_handler(client: Client, message: Message):
        """Set or display group rules"""
        chat_id = message.chat.id
        
        # Display rules if no arguments provided
        if len(message.command) == 1:
            rules = get_rules(chat_id)
            if rules:
                await message.reply(f"📜 **Royal Decree**\n\n{rules}")
            else:
                await message.reply("📜 No royal decrees have been proclaimed yet.")
            return
            
        # Set rules (admin only)
        if not await is_admin(client, chat_id, message.from_user.id):
            await message.reply("🔒 Only the royal court may set kingdom rules!")
            return
            
        # Get rules text from command
        rules_text = " ".join(message.command[1:])
        set_rules(chat_id, rules_text)
        
        await message.reply(f"📜 **New Royal Decree Proclaimed!**\n\n{rules_text}\n\n"
                           f"All kingdom subjects must obey these rules or face the royal punishment!")

    @app.on_message(filters.command("pardon") & filters.group)
    async def pardon_handler(client: Client, message: Message):
        """Unban/unmute a user"""
        # Check if sender is admin
        if not await is_admin(client, message.chat.id, message.from_user.id):
            await message.reply("🔒 Only the royal court may pardon subjects!")
            return
        
        # Get target user
        target_user = await get_target_user(client, message)
        if not target_user:
            await message.reply("🧙‍♀️ You must mention or reply to someone to pardon them!")
            return
            
        try:
            # Try to unban the user
            await client.unban_chat_member(message.chat.id, target_user.id)
            # Remove all warnings
            remove_warning(message.chat.id, target_user.id, all_warnings=True)
            # Unmute (give full permissions back)
            await client.restrict_chat_member(
                message.chat.id,
                target_user.id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media=True,
                    can_send_polls=True,
                    can_add_web_page_previews=True,
                    can_change_info=True,
                    can_invite_users=True,
                    can_pin_messages=True
                )
            )
            
            await message.reply(f"✨ The fairy godmother has granted mercy to {target_user.mention}!\n"
                               f"Their curses have been lifted and they may return to the kingdom.")
        except Exception as e:
            await message.reply(f"✨ Attempted to pardon {target_user.mention}.\n"
                               f"If they were banned, they can now return to the kingdom.")
            logger.error(f"Error in pardon: {e}")

    @app.on_message(filters.command("log_curse") & filters.group)
    async def log_curse_handler(client: Client, message: Message):
        """Show warning logs for users in the group"""
        # Check if sender is admin
        if not await is_admin(client, message.chat.id, message.from_user.id):
            await message.reply("🔒 Only the royal court may view the curse logs!")
            return
            
        # Update admin list for this chat
        await update_admins(client, message.chat.id)
        
        # TODO: Implement proper warning logs
        await message.reply("📜 The royal scribe is still learning to track curses. "
                          "This feature will be available in a future update!")


    @app.on_chat_member_updated()
    async def admin_tracker(client, chat_member_updated):
        """Track admin changes in groups"""
        chat_id = chat_member_updated.chat.id
        await update_admins(client, chat_id)

    return app
