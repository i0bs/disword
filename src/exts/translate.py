import io
import json
import logging
import uuid

import attrs
import deepl
import interactions as i
import requests
from interactions.ext import enhanced

import src.const
import src.model

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


class Translate(enhanced.EnhancedExtension):
    """An extension dedicated to /translate."""

    def __init__(self, bot: i.Client):
        self.bot = bot
        self.translator = deepl.Translator(src.const.AUTH_KEY)

    @enhanced.extension_command()
    @enhanced.autodefer(delay=0)
    async def translate(self, ctx: i.CommandContext, **kwargs):
        """A medium set of translaton tools."""
        log.debug("/translate was run, returning result...")

    @translate.subcommand(name="text")
    async def translate_text(
        self,
        ctx: i.CommandContext,
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
                i.Choice(name="Formal (more)", value=deepl.Formality.MORE.value),
                i.Choice(name="Informal (less)", value=deepl.Formality.LESS.value),
                i.Choice(name="Preserved (default)", value=deepl.Formality.DEFAULT.value),
            ],
        ) = None,
    ):
        """Translates a given message or "string" of text to another language."""
        _error_embed = i.Embed()

        if not string and not message_id:
            _error_embed.description = (
                ":x: You must present something to translate: either a message ID, or text."
            )
            await ctx.send(embeds=_error_embed, ephemeral=True)
        elif string and message_id:
            _error_embed.description = ":x: You cannot translate both a message ID and set text. Please choose one over the other."
            await ctx.send(embeds=_error_embed, ephemeral=True)
        else:
            button = i.Button(
                style=i.ButtonStyle.LINK,
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
                webhook = i.Webhook()
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
        ctx: i.CommandContext,
        base_res,
        language: enhanced.EnhancedOption(
            str, description="The language to translate to.", autocomplete=True
        ),
    ):
        """Automatically translates messages sent to another language."""
        db = json.loads(open("./db/translation.json", "r").read())
        id: str = str(ctx.author.id)  # convert Snowflake to str

        if db.get(id):
            if db[id]["automatic"]:
                db[id].update({"automatic": False})
                await ctx.send(
                    ":heavy_check_mark: Automatic translation has been disabled.", ephemeral=True
                )
            else:
                db[id].update({"automatic": True, "language": language})
                await ctx.send(
                    f":heavy_check_mark: Automatic translation for **{language.upper()}** has been enabled.",
                    ephemeral=True,
                )
        else:
            # FIXME: This is a poor implementation of easily accessing the language data.
            # Yet again, DeepL cannot properly utilise a fucking enum.
            for key, val in deepl.Language.__dict__.items():
                if language == val:
                    user = src.model.TranslationUser(
                        int(ctx.author.id), deepl.Language.__dict__[key]
                    )
                    db.update({id: attrs.asdict(user)})
                    break

            await ctx.send(
                f":heavy_check_mark: Automatic translation for **{language.upper()}** has been enabled.",
                ephemeral=True,
            )

        db = open("./db/translation.json", "w").write(json.dumps(db, indent=4, sort_keys=True))

    @translate.subcommand(name="document")
    async def translate_document(
        self,
        ctx: i.CommandContext,
        base_res,
        language: enhanced.EnhancedOption(
            str, description="The language to translate to.", autocomplete=True
        ),
        file: enhanced.EnhancedOption(
            i.File, description="The document you wish to translate. Must be .pdf or .docx."
        ),
    ):
        """Translates a given document file with contents to another language."""
        content = requests.get(file.url).text
        id = uuid.uuid4()
        name = f"{id}.{''.join(file.filename.split('.')[1:])}"
        result = self.translator.translate_text(
            content,
            target_lang=language,
            split_sentences=deepl.SplitSentences.OFF,
            preserve_formatting=True,
        )

        file_to_send = io.StringIO(result.text)
        with file_to_send as f:
            _file = i.File(filename=name, fp=f)
            await ctx.send(files=_file)

    @i.extension_autocomplete(command="translate", name="language")
    async def _render_lang_translate(self, ctx: i.CommandContext, language: str = ""):
        """
        Renders and presents the list of languages selectable for /translate commands.

        This code works as a crude fuzzy matching algorithm that makes lazy
        comparisons from the focused value given from the Discord API to the known
        list of languages from the DeepL API.
        """
        letters: list = list(language) if language != "" else []
        languages: list[str] = [
            lang.capitalize() for lang in deepl.Language.__dict__ if lang.isupper()
        ]
        languages.remove("English")
        languages.remove("Portuguese")

        if not letters:
            await ctx.populate(
                [
                    i.Choice(
                        name=(
                            lang
                            if not lang.startswith("English") and not lang.startswith("Portuguese")
                            else f"{lang.split('_')[0]} {lang.split('_')[1][:1].upper()}{lang.split('_')[1][1:]}"
                        ),
                        value=deepl.Language.__dict__[lang.upper()],
                    )
                    for lang in languages[0:24]
                ]
            )
        else:
            choices: list = []

            for lang in languages:
                focus: str = "".join(letters)

                if focus.lower() in lang.lower() and len(languages) > 26:
                    choices.append(
                        i.Choice(
                            name=(
                                lang
                                if not lang.startswith("English")
                                and not lang.startswith("Portuguese")
                                else f"{lang.split('_')[0]} {lang.split('_')[1][:1].upper()}{lang.split('_')[1][1:]}"
                            ),
                            value=deepl.Language.__dict__[lang.upper()],
                        )
                    )

            await ctx.populate(choices)

    @i.extension_listener(name="on_message_create")
    async def _convert_auto_translate(self, message: i.Message):
        """
        Converts given messages from users to their desired language.
        """
        db = json.loads(open("./db/translation.json", "r").read())
        guilds = json.loads(open("./db/guilds.json", "r").read())
        id: str = str(message.author.id)  # convert Snowflake to str

        for user in db:
            webhook = i.Webhook()

            if user == id and db[id]["automatic"]:
                try:
                    webhook = await webhook.create(
                        client=self.bot._http,
                        channel_id=int(message.channel_id),
                        name="Disword mimicked translation",
                    )
                except TypeError:
                    await self.bot._http.send_message(
                        channel_id=message.channel_id,
                        content="Disword is currently going through a webhook rate limit. Please try again later.",
                    )

                guilds.update({str(message.channel_id): str(webhook.id)})
                guilds = open("./db/guilds.json", "w").write(
                    json.dumps(guilds, indent=4, sort_keys=True)
                )

                result = self.translator.translate_text(
                    message.content, target_lang=db[id]["language"].upper()
                )
                webhook = await webhook.get(
                    client=self.bot._http,
                    webhook_id=guilds[message.channel_id],
                )
                await webhook.execute(
                    result.text,
                    username=message.author.username,
                    avatar_url=message.author.avatar_url,
                )
                await message.delete()


def setup(bot: i.Client):
    Translate(bot)
