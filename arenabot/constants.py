import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_CLIENT = os.getenv("DISCORD_CLIENT")
PREFIX = '!!'
TESTING = True if os.getenv("TESTING") == 'True' else False

# Emojis
CHECK = ':white_check_mark:'
ERR = ':x:'
WARN = ':warning:'
INFO = ':information_source:'

DEFAULT_PROFILE_PICTURE = "https://cdn.discordapp.com/attachments/1001705046213398530/1036511658773839902/unknown.png"