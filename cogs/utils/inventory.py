import typing
from dataclasses import dataclass

import voxelbotutils as vbu

from . import LootableItem


class InventoryWrapper:
    def __init__(
        self,
        bot: vbu.Bot,
        db: vbu.DatabaseConnection,
        user_id: int,
        update_values: typing.Optional[bool] = False,
    ):
        self.bot = bot
        self.db = db
        self.user_id = user_id
        self.update_values = update_values

    async def __aenter__(self) -> Inventory:
        v = await self.db("SELECT * FROM user_inv WHERE user_id=$1", self.user_id)
        items = []
        for i in v:
            try:
                items.append(LootableItem.from_item(self.bot, self.bot.items["all"][i["item_id"]]))
            except KeyError:
                pass
        return Inventory(self.user_id, *items)


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

    async def update_values(self, db: vbu.DatabaseConnection):
        """
        Update the database with the inventory's values
        """

        await db.conn.executemany(
            """
            INSERT into user_inv VALUES ($1, $2, $3) ON CONFLICT DO UPDATE
            SET amount = $3
            """,
            *((self.user_id, x.id, x.amount) for x in self.items)
        )
