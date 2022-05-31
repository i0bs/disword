"""
The bot runner file. This configures an instance of the bot
and runs it with the appropriate extensions.
"""
import logging
import sys

import interactions

sys.path.append("..")

import const

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger()

bot = interactions.Client(
    const.TOKEN, intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT
)
bot.load("interactions.ext.enhanced", debug_scope=False)
[bot.load(f"exts.{ext}") for ext in const.EXTENSIONS]


@bot.event
async def on_ready():
    log.debug(f"Disword is online.\n> {bot.latency}ms\n> {bot.guilds} guilds")


bot.start()
