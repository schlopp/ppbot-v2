import typing

import discord

__all__ = ("send_or_edit_response",)


async def send_or_edit_response(interaction: discord.Interaction, **kwargs) -> None:
    """
    Sends or edits an interaction response, depending on if it's already been responded too.

    Params:
        interaction (discord.Interaction): The interaction to send or edit.
        **kwargs: Any keyword arguments to pass to the interaction's send or edit method.
    """

    if interaction.response.is_done():
        return await interaction.edit_original_message(**kwargs)
    await interaction.response.send_message(**kwargs)
