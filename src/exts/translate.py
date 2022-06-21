import json
import logging

import deepl
import interactions
from interactions.ext import enhanced

import src.const
import src.model

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


class Translate(enhanced.EnhancedExtension):
    """An extension dedicated to /translate."""

    def __init__(self, bot: interactions.Client):
        self.bot = bot
        self.translator = deepl.Translator(src.const.AUTH_KEY)

    @enhanced.extension_command()
    @enhanced.autodefer(delay=0)
    async def translate(self, ctx: interactions.CommandContext, **kwargs):
        """A medium set of translaton tools."""
        log.debug("/translate was run, returning result...")

    @translate.subcommand(name="text")
    async def translate_text(
        self,
        ctx: interactions.CommandContext,
        base_res,
        language: enhanced.EnhancedOption(
            str, description="The language to translate to.", autocomplete=True
        ),
        string: enhanced.EnhancedOption(
            str, description='The "string" or text to translate.'
        ) = None,
        message_id: enhanced.EnhancedOption(
            str, description="The ID of the message to translate."
        ) = None,
        mimic: enhanced.EnhancedOption(
            bool, description="Should the response mimic your profile?"
        ) = False,
        formality: enhanced.EnhancedOption(
            str,
            description="How should the response be worded?",
            choices=[
                interactions.Choice(name="Formal (more)", value=deepl.Formality.MORE.value),
                interactions.Choice(name="Informal (less)", value=deepl.Formality.LESS.value),
                interactions.Choice(
                    name="Preserved (default)", value=deepl.Formality.DEFAULT.value
                ),
            ],
        ) = None,
    ):
        """Translates a given message or "string" of text to another language."""
        _error_embed = interactions.Embed()

        if not string and not message_id:
            _error_embed.description = (
                ":x: You must present something to translate: either a message ID, or text."
            )
            await ctx.send(embeds=_error_embed, ephemeral=True)
        elif string and message_id:
            _error_embed.description = ":x: You cannot translate both a message ID and set text. Please choose one over the other."
            await ctx.send(embeds=_error_embed, ephemeral=True)
        else:
            button = interactions.Button(
                style=interactions.ButtonStyle.LINK,
                label="Original message",
                url=f"https://discord.com/channels/{ctx.guild_id}/{ctx.channel_id}/{message_id}",
            )

            if message_id:
                msg = await self.bot._http.get_message(ctx.channel_id, int(message_id))

                if not msg:
                    _error_embed.description = (
                        ":x: The message from the ID provided does not exist."
                    )
                    await ctx.send(embeds=_error_embed, ephemeral=True)
                else:
                    text = msg.get("content")
            else:
                text = string

            if formality:
                try:
                    result = self.translator.translate_text(
                        text, target_lang=language, formality=formality
                    )
                except deepl.DeepLException as error:
                    _error_embed.description = ":x: " + (str(error).split("message: ")[1]).replace(
                        "'", "**"
                    ).replace("target_lang", language.upper())
                    await ctx.send(embeds=_error_embed, ephemeral=True)
            else:
                result = self.translator.translate_text(text, target_lang=language)

            if mimic:
                webhook = interactions.Webhook()
                webhook = await webhook.create(
                    client=self.bot._http,
                    channel_id=int(ctx.channel_id),
                    name="Disword mimicked translation",
                )

                if message_id:
                    await webhook.execute(
                        result.text,
                        username=ctx.author.user.username,
                        avatar_url=ctx.author.user.avatar_url,
                        components=button,
                    )
                else:
                    await webhook.execute(
                        result.text,
                        username=ctx.author.user.username,
                        avatar_url=ctx.author.user.avatar_url,
                    )

                await webhook.delete()
                await ctx.send(":heavy_check_mark: Response has been triggered.", ephemeral=True)
            else:
                if message_id:
                    await ctx.send(result.text, components=button)
                else:
                    await ctx.send(result.text)

    @translate.subcommand(name="automatic")
    async def translate_automatic(
        self,
        ctx: interactions.CommandContext,
        base_res,
        language: enhanced.EnhancedOption(
            str, description="The language to translate to.", autocomplete=True
        ),
    ):
        """Automatically translates messages sent to another language."""
        db = json.loads(open("./db/translation.json", "r").read())
        id: int = str(ctx.author.id)  # convert Snowflake to str

        if db.get(id):
            if db[id]["automatic"]:
                db[id]["automatic"] = False
                await ctx.send(
                    ":heavy_check_mark: Automatic translation has been disabled.", ephemeral=True
                )
            else:
                db[id]["automatic"] = True
                await ctx.send(
                    f":heavy_check_mark: Automatic translation for **{language.upper()}** has been enabled.",
                    ephemeral=True,
                )
        else:
            # FIXME: This is a poor implementation of easily accessing the language data.
            # Yet again, DeepL cannot properly utilise a fucking enum.
            db[id] = src.model.TranslationUser(language=deepl.Language.__dict__[language])
            await ctx.send(
                f":heavy_check_mark: Automatic translation for **{language.upper()}** has been enabled.",
                ephemeral=True,
            )

        db = open("./db/translation.json", "w").write(json.dumps(db, indent=4, sort_keys=True))

    @interactions.extension_autocomplete(command="translate", name="language")
    async def _render_lang_translate(self, ctx: interactions.CommandContext, language: str = ""):
        """
        Renders and presents the list of languages selectable for /translate commands.

        This code works as a crude fuzzy matching algorithm that makes lazy
        comparisons from the focused value given from the Discord API to the known
        list of languages from the DeepL API.
        """
        letters: list = list(language) if language != "" else []
        languages: list[deepl.Language] = [
            lang.capitalize()
            for lang in deepl.Language.__dict__
            if lang.isupper()
            or " ".join(spec.capitalize() for spec in lang.split("_") if "_" in lang)
            for lang in deepl.Language.__dict__
            if lang.isupper()
        ]

        if not letters:
            await ctx.populate(
                [
                    interactions.Choice(name=lang, value=deepl.Language.__dict__[lang.upper()])
                    for lang in languages[0:24]
                ]
            )
        else:
            choices: list = []

            for lang in languages:
                focus: str = "".join(letters)

                if focus.lower() in lang.lower() and len(languages) > 26:
                    choices.append(
                        interactions.Choice(name=lang, value=deepl.Language.__dict__[lang.upper()])
                    )

            await ctx.populate(choices)

    @interactions.extension_listener(name="on_message_create")
    async def _convert_auto_translate(self, message: interactions.Message):
        """
        Converts given messages from users to their desired language.
        """
        db = json.loads(open("./db/translation.json", "r").read())
        id: str = str(message.author.id)  # convert Snowflake to str

        if db.get("id") and db["id"] == id and db["id"]["automatic"]:
            webhook = interactions.Webhook()
            webhook = await webhook.create(
                client=self.bot._http,
                channel_id=int(message.channel_id),
                name="Disword mimicked translation",
            )
            await webhook.execute(
                message.content,
                username=message.author.username,
                avatar_url=message.author.avatar_url,
            )
            await message.delete()
            await webhook.delete()


def setup(bot: interactions.Client):
    Translate(bot)
