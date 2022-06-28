import deepl
import interactions as i
from interactions.ext import enhanced

import src.const


class Usage(enhanced.EnhancedExtension):
    """An extension dedicated to /usage."""

    def __init__(self, bot: i.Client):
        self.bot = bot
        self.translator = deepl.Translator(src.const.AUTH_KEY)

    @enhanced.extension_command()
    @enhanced.autodefer(delay=0)
    async def usage(self, ctx: i.CommandContext):
        """Provides statistics on the bot's usage."""
        use: deepl.Usage = self.translator.get_usage()

        def create_bar(count: int, limit: int, length: int = 10) -> str:
            quota: int | float = count / limit
            bar: str = ""

            for step in range(length):
                if round(quota, 1) <= 1 / length * step:
                    bar += "░"
                else:
                    bar += "▓"

            bar = bar + f" **{round(quota * 100)}%**"
            return bar

        embed = i.Embed(
            title="Usage",
            fields=[
                i.EmbedField(
                    name="Character limit",
                    value=create_bar(use.character.count, use.character.limit)
                    + f"\n({use.character.count}/{use.character.limit})",
                )
            ],
        )
        await ctx.send(embeds=embed)


def setup(bot: i.Client):
    Usage(bot)
