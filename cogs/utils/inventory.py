import typing
from dataclasses import dataclass

import voxelbotutils as vbu

from . import LootableItem


@dataclass
class Inventory:
    """
    A user's inventory.

    Attributes:
        user_id (`int`): The user's ID (discord ID)
        items (`list` of `LootableItem`): The user's inventory items.
    """

    user_id: int
    items: typing.List[LootableItem]

    def __init__(self, user_id: int, *items: typing.Iterable[LootableItem]):
        """
        A user's inventory.

        Args:
            user_id (`int`): The user's ID (discord ID)
            items (`iterable` of `LootableItem`): The user's inventory items.
        """

        self.user_id = user_id
        self.items = list(items)