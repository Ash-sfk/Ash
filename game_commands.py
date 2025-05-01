import random
import logging
import asyncio
import json
import time
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from utils.database import (
    get_user_data,
    update_user_data,
    get_group_data,
    update_group_data
)
from utils.helpers import get_fortune

logger = logging.getLogger(__name__)

# Track slipper game status
slipper_games = {}

# Track pumpkin growth
pumpkin_gardens = {}

# Track fortune cooldowns
fortune_cooldowns = {}

def register_game_handlers(app: Client):
    """Register all game-related command handlers"""

    @app.on_message(filters.command("slipper") & filters.group)
    async def slipper_handler(client: Client, message: Message):
        """Start a glass slipper hunt game"""
        chat_id = message.chat.id
        
        # Check if there's already an active game
        if chat_id in slipper_games and slipper_games[chat_id]["active"]:
            time_left = int(slipper_games[chat_id]["end_time"] - time.time())
            if time_left > 0:
                await message.reply(f"🔍 A royal hunt for the glass slipper is already in progress!\n"
                                  f"Time remaining: {time_left} seconds")
                return
        
        # Start a new game
        row_count = 3
        col_count = 3
        
        # For testing purposes, we'll hide the slipper in a fixed location
        # This makes it easier to find during testing
        # In production, you'd use: slipper_pos = (random.randint(0, row_count-1), random.randint(0, col_count-1))
        slipper_pos = (1, 1)  # Middle position for easy testing
        
        slipper_games[chat_id] = {
            "active": True,
            "slipper_pos": slipper_pos,
            "start_time": time.time(),
            "end_time": time.time() + 60,  # Game lasts 60 seconds
            "participants": {},
            "message_id": None
        }
        
        # Create the game board
        keyboard = []
        for i in range(row_count):
            row = []
            for j in range(col_count):
                # Hide the actual position from players
                button_text = "👑"
                row.append(InlineKeyboardButton(
                    button_text,
                    callback_data=f"slipper_guess_{i}_{j}"
                ))
            keyboard.append(row)
            
        # Add a button to end the game early
        keyboard.append([InlineKeyboardButton("End Hunt", callback_data="slipper_end")])
        
        # Send the game message
        game_message = await message.reply(
            "🏰 **Royal Glass Slipper Hunt!**\n\n"
            "The Prince has hidden a glass slipper in his castle!\n"
            "Be the first to find it and win 100 royal coins!\n\n"
            "Click on the 👑 buttons to search for the slipper!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        slipper_games[chat_id]["message_id"] = game_message.id
        
        # Set a timer to end the game
        asyncio.create_task(_end_slipper_game(client, chat_id, game_message.id))

    async def _end_slipper_game(client, chat_id, message_id, winner=None):
        """End the slipper game after timeout or when someone wins"""
        # If winner is provided, don't sleep - the game is already won
        if not winner:
            await asyncio.sleep(60)  # Wait for 60 seconds
        
        # Only proceed if the game is still active
        if chat_id in slipper_games and slipper_games[chat_id]["active"]:
            slipper_games[chat_id]["active"] = False
            
            if winner:
                # Someone found the slipper
                try:
                    await client.edit_message_text(
                        chat_id,
                        message_id,
                        f"🎉 The glass slipper has been found by {winner.mention}!\n"
                        f"They have been awarded 100 royal coins and a special role!"
                    )
                except Exception as e:
                    # If editing fails, send a new message
                    logger.error(f"Error editing message: {e}")
                    await client.send_message(
                        chat_id,
                        f"🎉 The glass slipper has been found by {winner.mention}!\n"
                        f"They have been awarded 100 royal coins and a special role!"
                    )
                
                # Award the prize to the winner
                user_data = get_user_data(chat_id, winner.id)
                user_data["coins"] = user_data.get("coins", 0) + 100
                user_data["found_slippers"] = user_data.get("found_slippers", 0) + 1
                update_user_data(chat_id, winner.id, user_data)
                
                # TODO: Implement role assignment if bot has permission
            else:
                # No one found the slipper
                row, col = slipper_games[chat_id]["slipper_pos"]
                try:
                    await client.edit_message_text(
                        chat_id,
                        message_id,
                        f"⏰ Time's up! No one found the glass slipper!\n"
                        f"It was hidden at position [{row+1}, {col+1}].\n"
                        f"The Prince will continue his search elsewhere."
                    )
                except Exception as e:
                    # If editing fails, send a new message
                    logger.error(f"Error editing message: {e}")
                    await client.send_message(
                        chat_id,
                        f"⏰ Time's up! No one found the glass slipper!\n"
                        f"It was hidden at position [{row+1}, {col+1}].\n"
                        f"The Prince will continue his search elsewhere."
                    )

    @app.on_callback_query(filters.regex(r"^slipper_guess_(\d+)_(\d+)$"))
    async def slipper_guess_callback(client, callback_query):
        """Handle slipper game guesses"""
        chat_id = callback_query.message.chat.id
        user = callback_query.from_user
        
        # Check if the game is active
        if chat_id not in slipper_games or not slipper_games[chat_id]["active"]:
            await callback_query.answer("This glass slipper hunt has already ended!", show_alert=True)
            return
            
        # Extract the guessed position
        match = callback_query.data.split("_")
        guessed_row, guessed_col = int(match[2]), int(match[3])
        slipper_row, slipper_col = slipper_games[chat_id]["slipper_pos"]
        
        # Record the participant
        if user.id not in slipper_games[chat_id]["participants"]:
            slipper_games[chat_id]["participants"][user.id] = 1
        else:
            slipper_games[chat_id]["participants"][user.id] += 1
            
        # Check if the guess is correct
        if (guessed_row, guessed_col) == (slipper_row, slipper_col):
            # Correct guess!
            slipper_games[chat_id]["active"] = False
            await callback_query.answer("👠 You found the glass slipper! It's a perfect fit!", show_alert=True)
            
            # End the game with a winner
            await _end_slipper_game(client, chat_id, callback_query.message.id, user)
        else:
            # Wrong guess
            distance = abs(guessed_row - slipper_row) + abs(guessed_col - slipper_col)
            
            if distance == 1:
                hint = "You're very close! The slipper is just one step away!"
            elif distance <= 2:
                hint = "Getting warmer! The slipper is nearby."
            else:
                hint = "You're far from the slipper. Keep searching!"
                
            await callback_query.answer(f"❌ No glass slipper here! {hint}", show_alert=True)

    @app.on_callback_query(filters.regex(r"^slipper_end$"))
    async def slipper_end_callback(client, callback_query):
        """Handle early ending of slipper game"""
        chat_id = callback_query.message.chat.id
        
        # Check if the game is active
        if chat_id not in slipper_games or not slipper_games[chat_id]["active"]:
            await callback_query.answer("This glass slipper hunt has already ended!", show_alert=True)
            return
            
        # End the game early
        slipper_games[chat_id]["active"] = False
        row, col = slipper_games[chat_id]["slipper_pos"]
        
        await client.edit_message_text(
            chat_id,
            callback_query.message.id,
            f"🛑 The glass slipper hunt was ended early!\n"
            f"The slipper was hidden at position [{row+1}, {col+1}].\n"
            f"Better luck next time!"
        )
        
        await callback_query.answer("You've ended the glass slipper hunt early.", show_alert=True)

    @app.on_message(filters.command("pumpkin") & filters.group)
    async def pumpkin_handler(client: Client, message: Message):
        """Grow a virtual pumpkin coach"""
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        user_data = get_user_data(chat_id, user_id)
        
        # Check if user already has a pumpkin growing
        if user_id in pumpkin_gardens.get(chat_id, {}):
            pumpkin = pumpkin_gardens[chat_id][user_id]
            
            # Check if pumpkin is ready for harvest
            current_time = time.time()
            grow_time = current_time - pumpkin["plant_time"]
            
            if grow_time >= pumpkin["grow_duration"]:
                # Pumpkin is ready for harvest!
                pumpkin_size = pumpkin["base_size"] + int(grow_time / 3600)  # Grow 1 size per hour
                max_size = 10
                pumpkin_size = min(pumpkin_size, max_size)
                
                # Award coins based on pumpkin size
                reward = pumpkin_size * 10
                user_data["coins"] = user_data.get("coins", 0) + reward
                user_data["pumpkins_grown"] = user_data.get("pumpkins_grown", 0) + 1
                update_user_data(chat_id, user_id, user_data)
                
                # Remove the pumpkin from the garden
                del pumpkin_gardens[chat_id][user_id]
                
                pumpkin_emoji = "🎃" * pumpkin_size
                await message.reply(
                    f"✨ Your pumpkin has grown into a magnificent coach! {pumpkin_emoji}\n"
                    f"Size: {pumpkin_size}/10\n"
                    f"The Fairy Godmother rewards you with {reward} royal coins!\n"
                    f"You can plant a new pumpkin now with /pumpkin"
                )
            else:
                # Pumpkin is still growing
                hours_left = (pumpkin["grow_duration"] - grow_time) / 3600
                minutes_left = (hours_left - int(hours_left)) * 60
                
                current_size = pumpkin["base_size"] + int(grow_time / 3600)
                pumpkin_emoji = "🌱" if current_size < 2 else "🎃" * current_size
                
                await message.reply(
                    f"{pumpkin_emoji} Your pumpkin is still growing!\n"
                    f"Current size: {current_size}/10\n"
                    f"Time until fully grown: {int(hours_left)}h {int(minutes_left)}m\n"
                    f"Check back later to harvest your magical coach!"
                )
        else:
            # Plant a new pumpkin
            if chat_id not in pumpkin_gardens:
                pumpkin_gardens[chat_id] = {}
                
            # Base size and growth duration varies by user's "gardening skill"
            gardening_skill = user_data.get("pumpkins_grown", 0)
            base_size = 1 + min(gardening_skill // 3, 5)  # Max base size of 6
            grow_duration = max(6 - gardening_skill // 5, 1) * 3600  # At least 1 hour, max 6 hours
            
            pumpkin_gardens[chat_id][user_id] = {
                "plant_time": time.time(),
                "grow_duration": grow_duration,
                "base_size": base_size
            }
            
            hours = grow_duration / 3600
            
            await message.reply(
                f"🌱 You've planted a magical pumpkin seed!\n"
                f"Base size: {base_size}/10\n"
                f"It will take about {int(hours)} hours to grow into a coach.\n"
                f"Check back with /pumpkin to see its progress!"
            )

    @app.on_message(filters.command("fortune") & filters.group)
    async def fortune_handler(client: Client, message: Message):
        """Get a daily prophecy from the fairy godmother"""
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        # For testing purposes, skip the cooldown check
        # This will allow users to get multiple fortunes during testing
        
        # Get the user's name
        user_name = message.from_user.first_name
        
        # Use the fallback fortunes since Gemini API might not be available
        # These are Disney and Cinderella themed fortunes
        fortunes = [
            "A stroke of luck will come your way when the clock strikes twelve.",
            "Be careful not to lose your glass slippers at the next ball.",
            "A royal opportunity awaits - don't let it turn into a pumpkin!",
            "Someone from your past may return with an old shoe.",
            "Kindness to small creatures will bring unexpected rewards.",
            "A fairy godmother figure will appear when you least expect it.",
            "Your true worth will be recognized by someone important.",
            "Don't judge a beast by its appearance - look for the beauty within.",
            "A journey over water will lead to a happy ending.",
            "The one who truly deserves you will find you, no matter what.",
            "Have courage and be kind, and good fortune will follow.",
            "Dreams really do come true if you believe in them.",
            "Magic is all around you, if you just believe.",
            "A grand ball is in your future - prepare to dance!",
            "Even the smallest of animals can be your greatest allies.",
            f"Remember, {user_name}, a dream is a wish your heart makes.",
            "Midnight isn't the end of magic - it's just the beginning of a new chapter.",
            "Trust in yourself, and others will trust in you as well.",
            "Your kindness today will be rewarded with a coach, not a pumpkin.",
            "Singing with birds will bring unexpected joy into your life."
        ]
        
        # Select a random fortune
        fortune_text = random.choice(fortunes)
        
        # Set cooldown for this user (for normal operation)
        cooldown_key = f"{chat_id}_{user_id}"
        current_time = datetime.now()
        fortune_cooldowns[cooldown_key] = current_time
        
        # Get user data and update luck
        user_data = get_user_data(chat_id, user_id)
        old_luck = user_data.get("luck", 0)
        new_luck = random.randint(1, 100)
        user_data["luck"] = new_luck
        update_user_data(chat_id, user_id, user_data)
        
        # Determine luck change emoji
        if new_luck > old_luck:
            luck_change = f"⬆️ +{new_luck - old_luck}"
        elif new_luck < old_luck:
            luck_change = f"⬇️ -{old_luck - new_luck}"
        else:
            luck_change = "↔️ No change"
        
        await message.reply(
            f"🔮 **The Fairy Godmother's Prophecy for {user_name}**\n\n"
            f"{fortune_text}\n\n"
            f"**Luck Rating**: {new_luck}/100 ({luck_change})\n"
            f"*This magic will last for 12 hours, but you can try again anytime.*"
        )

    return app
