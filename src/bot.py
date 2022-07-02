"""
The bot runner file. This configures an instance of the bot
and runs it with the appropriate extensions.
"""
import logging
import sys

import interactions

sys.path.append("..")

import const

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

bot = interactions.Client(
    const.TOKEN, intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT
)
bot.change_presence(
    interactions.ClientPresence(
        activities=[
            interactions.PresenceActivity(
                name="for /help.",
                type=interactions.PresenceActivityType.WATCHING,
            )
        ],
        status=interactions.StatusType.ONLINE,
    )
)
bot.load("exts.help")
bot.load("interactions.ext.enhanced")
[bot.load(f"exts.{ext}") for ext in const.EXTENSIONS if ext != "help"]


@bot.event
async def on_ready():
    log.debug(f"Disword is online.\n> {bot.latency}ms\n> {len(bot.guilds)} guilds")


@bot.command(name="eval")
async def _eval(ctx: interactions.CommandContext):
    """Evaluates and executes given code on the running bot instance."""
    modal = interactions.Modal(
        title="Eval",
        custom_id="eval",
        components=[
            interactions.TextInput(
                style=interactions.TextStyleType.PARAGRAPH,
                label="Code",
                placeholder='print("hello world")',
                custom_id="eval_code",
            ),
        ],
    )
    if int(ctx.author.id) == 242351388137488384:
        await ctx.popup(modal)
    else:
        await ctx.send(":x: You are not allowed to use this command.", ephemeral=True)


@bot.modal("eval")
async def _eval_callback(ctx: interactions.CommandContext, eval_code: str = ""):
    eval(eval_code)
    await ctx.send(":heavy_check_mark: Response has been triggered.", ephemeral=True)


bot.start()
