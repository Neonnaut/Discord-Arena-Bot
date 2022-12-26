import os
from dotenv import load_dotenv
import logging
# -
load_dotenv()

DISCORD_CLIENT = os.getenv("DISCORD_CLIENT")

# Gsheets
GSHEETS_KEY = {
    "private_key": os.getenv("PRIVATE_KEY"),
    "client_email": os.getenv("CLIENT_EMAIL"),
    "token_uri": "https://oauth2.googleapis.com/token"
}
WORKBOOK_KEY = "1JEwnfr0EWAltG9QdXzfox5ujuaaFhbtPWLUFH4kovhs"

DEFAULT_PROFILE_PICTURE = "https://cdn.discordapp.com/attachments/1001705046213398530/1036511658773839902/unknown.png"

# Emojis
CHECK = '✅'
ERR = '❌'
WARN = '⚠'
INFO = '💠'

class LoggerFormatter(logging.Formatter):
    """Logging Formatter to add colours and count warning / errors"""

    grey = "\x1b[38;20m"
    cyan = "\033[96m"
    yellow = "\033[33;21m"
    red = "\033[31;21m"
    bold_red = "\033[31;1m"
    magenta = "\033[35m"
    reset = "\033[0m"

    #time = '%(asctime)s.%(msecs)03d '
    time = '%(asctime)s '
    level = '%(levelname)s '
    message = '%(message)s \033[35m%(filename)s:%(funcName)s:%(lineno)d\033[0m'

    FORMATS = {
        logging.DEBUG: time + grey + level + reset + "   " + message,
        logging.INFO: time + cyan + level + reset + "    " + message,
        logging.WARNING: time + yellow + level + " " + reset + message,
        logging.ERROR: time + red + level + "   " + reset + message,
        logging.CRITICAL: time + bold_red + level + "" + reset + message
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)