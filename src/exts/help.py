import interactions as i
import yaml

import src.model


class Help(i.Extension):
    """An extension dedicated to /help."""

    def __init__(self, bot: i.Client):
        self.bot = bot

    @i.extension_command(
        name="help",
        description="Provides extensive information on how to use the bot.",
        options=[
            i.Option(
                type=i.OptionType.STRING,
                name="command",
                description="Look for how to use a specific command.",
                choices=[
                    i.Choice(name="/help", value="help"),
                    i.Choice(name="/privacy-policy", value="privacy-policy"),
                    i.Choice(name="/translate", value="translate"),
                    i.Choice(name="/usage", value="usage"),
                ],
                required=False,
            ),
        ],
    )
    async def _help(
        self,
        ctx: i.CommandContext,
        command: str = None,
    ):
        table: dict = yaml.safe_load(open("./db/help.yaml", "r").read())
        commands: list = [
            src.model.HelpTable(
                name=f"/{cmd}",
                description=table[cmd]["description"],
                explanation=table[cmd]["explanation"],
                examples=table[cmd]["examples"],
            )
            for cmd in table
        ]
        embed = i.Embed(title="Help")
        menu = i.SelectMenu(
            options=[
                i.SelectOption(
                    label="/translate text",
                    value="translate_text",
                    description='Translates a given message or "string" of text to another language.',
                ),
                i.SelectOption(
                    label="/translate automatic",
                    value="translate_automatic",
                    description="Automatically translates messages sent to another language.",
                ),
            ],
            placeholder="Select a command for more help.",
            custom_id="help_selection",
            disabled=True,
        )

        if command is None:
            [
                [embed.add_field(name=cmd.name, value=cmd.description, inline=False)]
                for cmd in commands
            ]
        else:
            for cmd in commands:
                if command == cmd.name.removeprefix("/"):
                    cmd.examples[0] = f"• {cmd.examples[0]}"
                    embed.add_field(
                        name=cmd.name,
                        value=f"{cmd.description}\n\n" + "\n• ".join(cmd.examples),
                        inline=False,
                    )
                    break
                elif command == "translate":
                    menu.disabled = False

        if menu.disabled:
            await ctx.send(embeds=embed)
        else:
            await ctx.send(embeds=embed, components=menu)

    @i.extension_component("help_selection")
    async def _select_translate_help(self, ctx: i.ComponentContext, option: list):
        embed = i.Embed(title="Help")

        if option[0] == "translate_text":
            embed.add_field(
                name="/translate text",
                value="\n".join(
                    [
                        "The `/translate text` command is the most powerful and simplified command Disword provides to users. "
                        "By default, you will be required to supply only one of two inputs: `string` if you want to convert a set "
                        "of text by itself, and `message_id` if you want to translate an existing message.\n",
                        "In order to use `message_id` specifically, you must have **Developer Mode** enabled in your settings. "
                        "This is accessible by going to User Settings > Advanced.\n",
                        '• `/translate text language: "de" string: "hello world"` will translate the contents into German.',
                        '• `/translate text language: "de" message_id: "991384835790753843"` will translate the message of its ID given into German.',
                    ]
                ),
            )
        elif option[0] == "translate_automatic":
            embed.add_field(
                name="/translate automatic",
                value="\n".join(
                    [
                        "The `/translate automatic` command is the second most powerful and simplified command offered. "
                        "Have you ever been tired of having to rapid-fire numerous slash commands to have a conversation with "
                        "someone in another language? Well, now you no longer need to. With this command, you can toggle your "
                        "messages to be sent in any other language. Your messages will be deleted through this and sent as "
                        "**webhooks** instead, which take on the appearance of your username and profile image. The image will "
                        "additionally adapt to your server profile if you have one set!\n",
                        "Disword requires the **Manage Messages** permission solely for this reason.\n",
                        '• `/translate automatic language: "de"` will toggle you as a user for whether you want your messages to be sent '
                        "in German or not.",
                    ]
                ),
            )

        await ctx.send(embeds=embed)


def setup(bot: i.Client):
    Help(bot)
