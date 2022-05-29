"""
The bot's constants. This stores the token and extensions
needed to run a bot instance.
"""
import os

import dotenv

TOKEN = dotenv.get_key("../.env", "token")
EXTENSIONS = [file.replace(".py", "") for file in os.listdir("exts") if not file.startswith("_")]
