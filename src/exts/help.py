import interactions
import yaml
from interactions.ext import enhanced

import src.model


class Help(enhanced.EnhancedExtension):
    """An extension dedicated to /help."""

    def __init__(self, bot: interactions.Client):
        self.bot = bot

    @enhanced.extension_command(name="help")
    async def _help(
        self,
        ctx: interactions.CommandContext,
        name: enhanced.EnhancedOption(
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
        table: dict = yaml.safe_load(open("./db/help.yaml", "r").read())
        print([table[cmd] for cmd in table])
        commands: list = [
            src.model.HelpTable(
                name=f"/{cmd}",
                description=table[cmd]["description"],
                explanation=table[cmd]["explanation"],
                examples=table[cmd]["examples"],
            )
            for cmd in table
        ]
        embed = interactions.Embed(title="Help")
        menu = interactions.SelectMenu(
            options=[
                interactions.SelectOption(
                    label="/translate text",
                    value="translate_text",
                    description='Translates a given message or "string" of text to another language.',
                    default=True,
                ),
                interactions.SelectOption(
                    label="/translate automatic",
                    value="translate_automatic",
                    description="Automatically translates messages sent to another language.",
                ),
            ],
            custom_id="help_selection",
            disabled=True,
        )

        if not name:
            [
                [embed.add_field(name=cmd.name, value=cmd.description, inline=False)]
                for cmd in commands
            ]
        else:
            for cmd in commands:
                if name == cmd.name:
                    embed.add_field(
                        name=cmd.name,
                        value=f"{cmd.description}\n\n" + "\n".join(cmd.examples),
                        inline=False,
                    )
                elif name == "translate":
                    menu.disabled = False

        if menu.disabled:
            await ctx.send(embeds=embed)
        else:
            await ctx.send(embeds=embed, components=menu)


def setup(bot: interactions.Client):
    Help(bot)
