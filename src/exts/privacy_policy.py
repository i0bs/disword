import interactions as i
from interactions.ext import enhanced


class PrivacyPolicy(enhanced.EnhancedExtension):
    """An extension dedicated to /privacy-policy."""

    def __init__(self, bot: i.Client):
        self.bot = bot

    @enhanced.extension_command(name="privacy-policy")
    async def privacy_policy(self, ctx: i.CommandContext, *args, **kwargs):
        """Provides the privacy policy of Disword."""
        embed = i.Embed(
            title="Privacy policy",
            description=(
                "Discord highly emphasises the safety and privacy of users on their platform. Disword "
                "respects this with complacency to the "
                "[Discord Developer Policy](https://discord.com/developers/docs/policies-and-agreements/developer-policy). "
                "Below is a simplified explanation of our privacy policy which bears no proper legal representation."
            ),
        )
        embed.add_field(
            name="Logging data",
            value="\n".join(
                [
                    "• Messages are cached during `/translate automatic` interaction events while opt-in.",
                    "• The bot's overall guild count is tracked.",
                    "• A guild ID (and message ID if deemed necessary by internal workflow) are logged when an error is found.",
                    "• A channel ID in your guild is saved to track a **webhook ID**, only used for automatic translation events. This is also opt-in.",
                ]
            ),
        )
        embed.add_field(
            name="Presence data",
            value="\n".join(
                [
                    "• A user's locale is checked to display commands in a localised convention.",
                    "• A guild member's bot status is used to determine translation interaction responses.",
                ]
            ),
        )
        await ctx.send(embeds=embed, ephemeral=True)


def setup(bot: i.Client):
    PrivacyPolicy(bot)
