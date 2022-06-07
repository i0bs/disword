import interactions
import yaml
from interactions.ext import enhanced

with open("./db/help.yaml", "r") as file:
    print(yaml.safe_load(file))


class Help(enhanced.EnhancedExtension):
    """An extension dedicated to /help."""

    def __init__(self, bot: interactions.Client):
        self.bot = bot

    @enhanced.extension_command()
    async def help(
        self,
        ctx: interactions.CommandContext,
        command: enhanced.EnhancedOption(
            str,
            description="Look for how to use a specific command.",
            choices=[
                interactions.Choice(name="/help", value="help"),
                interactions.Choice(name="/privacy-policy", value="privacy_policy"),
                interactions.Choice(name="/translate", value="translate"),
                interactions.Choice(name="/usage", value="usage"),
            ],
        ) = None,
    ):
        """Provides extensive information on how to use the bot."""
        ...  # TODO: work on YAML parser.


def setup(bot: interactions.Client):
    Help(bot)
