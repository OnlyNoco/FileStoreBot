import logging
import os
from logging.handlers import RotatingFileHandler

# Bot Configuration
LOG_FILE_NAME = "bot.log"
#PORT = '5010'
PORT = int(os.getenv("PORT", 5010))
OWNER_ID = 5296584067

MSG_EFFECT = 5046509860389126442

SHORT_URL = "linkshortify.com" # shortner url 
SHORT_API = "" 
SHORT_TUT = "https://t.me/How_to_Download_7x/26"

# Bot Configuration
SESSION = "onlynoco"
TOKEN = os.environ.get("TOKEN", "0")
API_ID = "26254064"
API_HASH = "72541d6610ae7730e6135af9423b319c"
WORKERS = 5

DB_URI = "mongodb+srv://teamprosperpay:AbidAbdullah199@cluster0.z93fita.mongodb.net/"
DB_NAME = "Cluster0"

FSUBS = [[-1002372552947, True, 10]] # Force Subscription Channels [channel_id, request_enabled, timer_in_minutes]
# Database Channel (Primary)
DB_CHANNEL = -1002689479503
# Multiple Database Channels (can be set via bot settings)
# DB_CHANNELS = {
#     "-1002595092736": {"name": "Primary DB", "is_primary": True, "is_active": True},
#     "-1001234567890": {"name": "Secondary DB", "is_primary": False, "is_active": True}
# }
# Auto Delete Timer (seconds)
AUTO_DEL = 1800
# Admin IDs
ADMINS = [5296584067]
CAPTION = ""
# Bot Settings
DISABLE_BTN = True
PROTECT = True

# Messages Configuration
MESSAGES = {
    "START": "<b>›› ʜᴇʏ {first} ~<blockquote>ɪ'ᴍ ʏᴀᴛᴏ, ᴏᴡɴᴇᴅ ʙʏ <a href='https://t.me/OnlyNoco'>ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>. ɪ ʜᴇʟᴘ ʏᴏᴜ ꜰɪɴᴅ ᴀɴɪᴍᴇ & ʜᴇɴᴛᴀɪ ᴄᴏɴᴛᴇɴᴛ ꜰᴀsᴛ ᴀɴᴅ ᴇᴀsɪʟʏ.</blockquote></b>",
    "FSUB": "<b><blockquote>›› ʜᴇʏ ×</blockquote>ʏᴏᴜʀ ꜰɪʟᴇ ɪs ʀᴇᴀᴅʏ, ʙᴜᴛ ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴊᴏɪɴᴇᴅ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ʏᴇᴛ. ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ᴜsɪʙɢ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs ᴛᴏ ɢᴇᴛ ғɪʟᴇ ᴀᴄᴄᴇss.</b>",
    "ABOUT": "<b>›› ᴀʙᴏᴜᴛ ᴍᴇ:<blockquote expandable>◧ ᴏᴡɴᴇʀ: <a href='https://t.me/OnlyNoco'>ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>\n◧ ᴏᴜʀ sᴇʀᴠɪᴄᴇs ~\n⊡ <a href='https://t.me/HeavenlySubs'>ʙᴀᴛᴛʟᴇ ᴛʜʀᴏᴜɢʜ ᴛʜᴇ ʜᴇᴀᴠᴇɴs</a>\n⊡ <a href='https://t.me/FinishedAnimeCrisp'>ꜰɪɴɪsʜᴇᴅ ᴀɴɪᴍᴇ</a>\n⊡ <a href='https://t.me/OngoingAnimeCrisp'>ᴏɴɢᴏɪɴɢ ᴀɴɪᴍᴇ</a>\n⊡ <a href='https://t.me/CrispIndex'>ᴀɴɪᴍᴇ ɪɴᴅᴇx</a>\n⊡ <a href='https://t.me/+O7PeEMZOAoMzYzVl'>ʜᴇɴᴛᴀɪ ᴄʀɪsᴘ</a>\n⊡ <a href='https://t.me/DisscusionAnimeCrisp'>ᴅɪsᴄᴜssɪᴏɴ ɢʀᴏᴜᴘ</a>\n\n♧ ᴊᴏɪɴ ᴜs ꜰᴏʀ ᴏʀɢᴀɴɪᴢᴇᴅ ᴍᴜʟᴛɪ ǫᴜᴀʟɪᴛʏ ᴀɴɪᴍᴇ ᴄᴏɴᴛᴇɴᴛ ♧</blockquote></b>",
    "REPLY": "<b>›› ᴊᴏɪɴ ᴜs ꜰᴏʀ ᴍᴏʀᴇ - <a href='https://t.me/FinishedAnimeCrisp'>ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ᴠɪsɪᴛ</a></b>",
    "SHORT_MSG": "<b>📊 ʜᴇʏ {first},\n\n‼️ ɢᴇᴛ ᴀʟʟ ꜰɪʟᴇs ɪɴ ᴀ sɪɴɢʟᴇ ʟɪɴᴋ ‼️\n\n⌯ ʏᴏᴜʀ ʟɪɴᴋ ɪs ʀᴇᴀᴅʏ — ᴛᴀᴘ ᴏɴ ‘ᴏᴘᴇɴ ʟɪɴᴋ’ ᴛᴏ ᴠɪᴇᴡ.</b>",
    "START_PHOTO": "https://graph.org/file/510affa3d4b6c911c12e3.jpg",
    "FSUB_PHOTO": "https://telegra.ph/file/7a16ef7abae23bd238c82-b8fbdcb05422d71974.jpg",
    "SHORT_PIC": "https://telegra.ph/file/7a16ef7abae23bd238c82-b8fbdcb05422d71974.jpg",
    "SHORT": "https://telegra.ph/file/8aaf4df8c138c6685dcee-05d3b183d4978ec347.jpg"
}

def LOGGER(name: str, client_name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        f"[%(asctime)s - %(levelname)s] - {client_name} - %(name)s - %(message)s",
        datefmt='%d-%b-%y %H:%M:%S'
    )
    file_handler = RotatingFileHandler(LOG_FILE_NAME, maxBytes=50_000_000, backupCount=10)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
