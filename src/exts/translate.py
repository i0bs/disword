import deepl
import interactions
from interactions.ext import enhanced

import src.const


class Translate(enhanced.EnhancedExtension):
    """An extension dedicated to /translate."""

    def __init__(self, bot: interactions.Client):
        self.bot = bot
        self.translator = deepl.Translator(src.const.AUTH_KEY)

    @enhanced.extension_command(name="translate")
    @enhanced.autodefer()
    async def translate(self, ctx: interactions.CommandContext):
        pass

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
            int, description="The ID of the message to translate."
        ) = None,
        embed: enhanced.EnhancedOption(
            bool, description="Should the response be formatted as an embed?"
        ) = False,
        formal: enhanced.EnhancedOption(
            bool, description="Should the response preserve the formal tone of the text?"
        ) = False,
    ):
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
            if message_id:
                text = self.bot._http.get_message(ctx.channel.id, message_id)

                if not text:
                    _error_embed.description = (
                        ":x: The message from the ID provided does not exist."
                    )
                    await ctx.send(embeds=_error_embed, ephemeral=True)
            else:
                text = string

            result = self.translator.translate_text(text, target_lang=language, formality=formal)

            if embed:
                _embed = interactions.Embed(
                    description=result.text,
                    author=interactions.EmbedAuthor(
                        name=ctx.author.name,
                        url=f"discord://-/users/{ctx.author.id}",
                        icon_url=ctx.author.avatar,
                    ),
                )
                await ctx.send(embeds=_embed)
            else:
                await ctx.send(result.text)


def setup(bot: interactions.Client):
    Translate(bot)
