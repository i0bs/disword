"""
The internal data models of the bot.
These help organise and structure data for our databases
where we store how actions are ran.
"""
import attrs


@attrs.define()
class TranslationUser:
    """Represents a user's state when running translations."""

    id: str = attrs.field()
    """The ID of the user."""
    language: str = attrs.field()
    """The selected language for the user."""
    automatic: bool = attrs.field(default=True)
    """Whether the translation is automatically occuring or not."""


@attrs.define()
class HelpTable:
    """Represents a table of information for a command in /help."""

    name: str = attrs.field()
    """The name of the command."""
    description: str = attrs.field()
    """The description of the command."""
    explanation: str = attrs.field()
    """An explanation of what the command does."""
    examples: list = attrs.field(converter=list)
    """Examples to follow with how to use the command in question."""
