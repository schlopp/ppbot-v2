import typing
from io import StringIO

import discord

__all__ = ("codeblock",)

ZERO_WIDTH_SPACE = "\u200B"


def codeblock(
    content: str,
    *,
    max_chars: typing.Optional[int] = 2000,
    filename_extension: typing.Optional[str],
) -> typing.Union[str, discord.File]:
    """
    Put code in a code block.

    Args:
        content (`str`): The content of the code block.
        max_chars (`int`, optional): The maximum number of characters allowed in the code block.
        filename_extension (`str`): The extension of the file.
    Returns:
        `str`: The code block.
        or `discord.File`: The code block as a file. (only if content exceeds max_chars)
    """

    if max_chars is not None and len(content) + 20 > max_chars:
        f = StringIO()
        f.write(content)
        f.seek(0)
        return discord.File(f, "output.{}".format(filename_extension))

    return "```{}\n{}```".format(
        filename_extension, content.replace("`", ZERO_WIDTH_SPACE + "​`")
    )
