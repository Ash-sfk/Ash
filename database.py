import json
import os
import logging
import time
from config import Config

logger = logging.getLogger(__name__)

# In-memory data storage
_db = {
    "users": {},      # user_data[chat_id][user_id] = {...}
    "groups": {},     # group_data[chat_id] = {...}
    "admins": {},     # admins[chat_id] = [user_id1, user_id2, ...]
    "warnings": {},   # warnings[chat_id][user_id] = count
    "rules": {}       # rules[chat_id] = "rules text"
}

def init_database():
    """Initialize the database from file"""
    if os.path.exists(Config.DB_PATH):
        try:
            with open(Config.DB_PATH, 'r') as f:
                global _db
                _db = json.load(f)
            logger.info(f"Database loaded from {Config.DB_PATH}")
        except Exception as e:
            logger.error(f"Error loading database: {e}")
    else:
        logger.info("No database file found, starting with empty database")
        _save_database()

def _save_database():
    """Save the database to file"""
    try:
        with open(Config.DB_PATH, 'w') as f:
            json.dump(_db, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving database: {e}")
        return False

# User data functions
def get_user_data(chat_id, user_id):
    """Get user data, with defaults if not found"""
    chat_id = str(chat_id)
    user_id = str(user_id)
    
    if chat_id not in _db["users"]:
        _db["users"][chat_id] = {}
        
    if user_id not in _db["users"][chat_id]:
        _db["users"][chat_id][user_id] = {
            "coins": 0,
            "luck": 50,
            "found_slippers": 0,
            "pumpkins_grown": 0,
            "last_fortune": 0,
            "created_at": time.time()
        }
        
    return _db["users"][chat_id][user_id]

def update_user_data(chat_id, user_id, data):
    """Update user data and save to database"""
    chat_id = str(chat_id)
    user_id = str(user_id)
    
    if chat_id not in _db["users"]:
        _db["users"][chat_id] = {}
        
    _db["users"][chat_id][user_id] = data
    _save_database()
    return True

def get_user_stats():
    """Get all users in the database"""
    all_users = set()
    for chat_id in _db["users"]:
        for user_id in _db["users"][chat_id]:
            all_users.add(user_id)
    return all_users

# Group data functions
def get_group_data(chat_id):
    """Get group data, with defaults if not found"""
    chat_id = str(chat_id)
    
    if chat_id not in _db["groups"]:
        _db["groups"][chat_id] = {
            "created_at": time.time(),
            "total_messages": 0,
            "games_played": 0,
            "settings": {
                "welcome_enabled": True,
                "games_enabled": True
            }
        }
        
    return _db["groups"][chat_id]

def update_group_data(chat_id, data):
    """Update group data and save to database"""
    chat_id = str(chat_id)
    _db["groups"][chat_id] = data
    _save_database()
    return True

def get_group_stats():
    """Get all groups in the database"""
    return list(_db["groups"].keys())

# Admin management functions
async def update_admins(client, chat_id):
    """Update the admin list for a chat"""
    chat_id = str(chat_id)
    
    try:
        # Get all admins in the chat
        admins = []
        async for admin in client.get_chat_members(int(chat_id), filter="administrators"):
            admins.append(str(admin.user.id))
            
        # Update admin list
        _db["admins"][chat_id] = admins
        _save_database()
        return True
    except Exception as e:
        logger.error(f"Error updating admins: {e}")
        return False

def get_admins(chat_id):
    """Get list of admin user IDs for a chat"""
    chat_id = str(chat_id)
    
    if chat_id not in _db["admins"]:
        _db["admins"][chat_id] = []
        
    # Combine with default admin list
    return _db["admins"][chat_id] + [str(admin_id) for admin_id in Config.ADMIN_IDS]

# Warning/curse management functions
def get_warnings(chat_id, user_id):
    """Get number of warnings for a user"""
    chat_id = str(chat_id)
    user_id = str(user_id)
    
    if chat_id not in _db["warnings"]:
        _db["warnings"][chat_id] = {}
        
    return _db["warnings"][chat_id].get(user_id, 0)

def add_warning(chat_id, user_id):
    """Add a warning for a user"""
    chat_id = str(chat_id)
    user_id = str(user_id)
    
    if chat_id not in _db["warnings"]:
        _db["warnings"][chat_id] = {}
        
    current = _db["warnings"][chat_id].get(user_id, 0)
    _db["warnings"][chat_id][user_id] = current + 1
    _save_database()
    
    return _db["warnings"][chat_id][user_id]

def remove_warning(chat_id, user_id, all_warnings=False):
    """Remove a warning for a user"""
    chat_id = str(chat_id)
    user_id = str(user_id)
    
    if chat_id not in _db["warnings"]:
        return 0
        
    if user_id not in _db["warnings"][chat_id]:
        return 0
        
    if all_warnings:
        _db["warnings"][chat_id][user_id] = 0
    else:
        current = _db["warnings"][chat_id].get(user_id, 0)
        _db["warnings"][chat_id][user_id] = max(0, current - 1)
        
    _save_database()
    return _db["warnings"][chat_id][user_id]

# Rules management functions
def set_rules(chat_id, rules_text):
    """Set rules for a chat"""
    chat_id = str(chat_id)
    _db["rules"][chat_id] = rules_text
    _save_database()
    return True

def get_rules(chat_id):
    """Get rules for a chat"""
    chat_id = str(chat_id)
    return _db["rules"].get(chat_id, "")
